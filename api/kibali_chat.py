"""API Chat Kibali IA"""
from flask import Blueprint, jsonify, request
import requests
import logging
from config import Config
import sys
from pathlib import Path

# Import du générateur hybride
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from hybrid_ai_generator import HybridAIGenerator
    hybrid_generator = HybridAIGenerator()
    HYBRID_AVAILABLE = True
except Exception as e:
    logging.warning(f"⚠️ Générateur hybride non disponible: {e}")
    hybrid_generator = None
    HYBRID_AVAILABLE = False

chat_routes = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)

@chat_routes.route('/generate-model', methods=['POST'])
def generate_model():
    """Génère un modèle 3D avec le générateur hybride IA (Mistral + CodeLlama)"""
    try:
        if not HYBRID_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Générateur hybride non disponible'
            }), 503
        
        data = request.get_json()
        prompt = data.get('prompt', '')
        object_type = data.get('type', 'object')
        scene_context = data.get('scene_context', None)  # 🔥 NOUVEAU: Contexte de la scène
        
        if not prompt:
            return jsonify({'error': 'Prompt required'}), 400
        
        logger.info(f"🎨 Génération: {prompt}")
        if scene_context:
            logger.info(f"📊 Contexte: {scene_context.get('total_objects', 0)} objet(s)")
        
        # Génération avec contexte
        result = hybrid_generator.generate(prompt, object_type, scene_context)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'model_data': {
                    'code': result.get('code'),
                    'type': result.get('type', 'javascript')
                },
                'analysis': result.get('analysis', {}),
                'method': 'hybrid-ai'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Génération échouée')
            }), 500
            
    except Exception as e:
        logger.error(f'❌ Erreur génération: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@chat_routes.route('/fix-code', methods=['POST'])
def fix_code():
    """Corrige du code JavaScript cassé avec Mistral"""
    try:
        if not HYBRID_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Générateur hybride non disponible'
            }), 503
        
        data = request.get_json()
        broken_code = data.get('code', '')
        error_message = data.get('error', '')
        original_prompt = data.get('prompt', '')
        
        if not broken_code or not error_message:
            return jsonify({'error': 'Code and error required'}), 400
        
        logger.info(f"🔧 Correction de code: {error_message[:50]}...")
        
        # Utilise Mistral pour corriger
        fixed_code = hybrid_generator.fix_code_with_mistral(broken_code, error_message, original_prompt)
        
        return jsonify({
            'success': True,
            'fixed_code': fixed_code
        })
            
    except Exception as e:
        logger.error(f'❌ Erreur correction: {e}')
        return jsonify({'error': str(e)}), 500

@chat_routes.route('/message', methods=['POST'])
def send_message():
    """Envoie un message au chat Kibali"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        context = data.get('context', 'general')
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
        
        # Appel API Kibali
        response = requests.post(
            f'{Config.KIBALI_API_URL}/api/chat',
            json={'message': message, 'context': context},
            timeout=30
        )
        
        if response.ok:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Kibali API error', 'response': 'Mode offline activé'}), 200
            
    except requests.exceptions.RequestException as e:
        logger.warning(f'Kibali offline: {e}')
        return jsonify({
            'success': True,
            'response': f'🤖 Je suis en mode local. Je peux vous aider avec: création 3D, animations, caméra, lumières.'
        })
    except Exception as e:
        logger.error(f'Error in chat: {e}')
        return jsonify({'error': str(e)}), 500

@chat_routes.route('/analyze', methods=['POST'])
def analyze_prompt():
    """Analyse un prompt pour déterminer l'action"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').lower()
        
        # Analyse locale simple
        if any(word in prompt for word in ['reconstruction', 'scan', 'midas']):
            return jsonify({'intent': 'RECONSTRUCTION_3D', 'confidence': 0.9})
        elif any(word in prompt for word in ['personnage', 'character']):
            return jsonify({'intent': 'CREATE_CHARACTER', 'confidence': 0.8})
        elif any(word in prompt for word in ['environnement', 'environment']):
            return jsonify({'intent': 'CREATE_ENVIRONMENT', 'confidence': 0.8})
        else:
            return jsonify({'intent': 'GENERAL', 'confidence': 0.5})
            
    except Exception as e:
        logger.error(f'Error analyzing prompt: {e}')
        return jsonify({'error': str(e)}), 500
