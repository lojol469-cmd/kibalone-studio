"""API Chat Kibali IA"""
from flask import Blueprint, jsonify, request
import requests
import logging
from config import Config

chat_routes = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)

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
