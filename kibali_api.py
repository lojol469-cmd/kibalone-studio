#!/usr/bin/env python3
"""
API Flask pour connecter Kibali-IA avec Kibalone Studio
Expose les fonctions de Kibali comme endpoints API REST
Utilise LangChain pour orchestrer les outils IA
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path
import requests
import json

# Variables globales pour disponibilité des systèmes (DÉFINIR AU DÉBUT!)
DISPATCHER_AVAILABLE = False
ORCHESTRATOR_AVAILABLE = False
LANGCHAIN_AVAILABLE = False

# Ajouter le chemin de kibali-IA - CENTRALISÉ dans Isol
KIBALI_PATH = Path("/home/belikan/Isol/kibali-IA")
sys.path.insert(0, str(KIBALI_PATH))

# Imports de Kibali-IA
from dotenv import load_dotenv
load_dotenv(KIBALI_PATH / ".env")

# Import des configurations
sys.path.insert(0, str(KIBALI_PATH / "kibali_data" / "models"))
from MODEL_PATHS import *

# Imports des fonctionnalités de Kibali
from huggingface_hub import InferenceClient
import torch

# LangChain pour orchestration des outils (OPTIONNEL - dispatcher est prioritaire)
try:
    from langchain.agents import Tool, AgentExecutor, create_react_agent
    from langchain.prompts import PromptTemplate
    from langchain_community.llms import HuggingFaceEndpoint
    LANGCHAIN_AVAILABLE = True
    
    # Import du registry complet des outils
    from kibali_tools_registry import get_all_tools, get_tools_summary, ALL_TOOLS_DEFINITIONS
    print("✅ Kibali Tools Registry chargé")
except ImportError:
    print("⚠️ LangChain non disponible - fonctionnement en mode simple")
    LANGCHAIN_AVAILABLE = False
    ALL_TOOLS_DEFINITIONS = []

# 🚀 DISPATCHER intelligent (BYPASS LANGCHAIN)
try:
    from kibali_dispatcher import KibaliDispatcher
    dispatcher = KibaliDispatcher()
    DISPATCHER_AVAILABLE = True
    print("✅ Kibali Dispatcher chargé")
except ImportError as e:
    print(f"⚠️ Dispatcher non disponible: {e}")
    DISPATCHER_AVAILABLE = False
    dispatcher = None

# 🎭 ORCHESTRATOR + EXECUTOR (Architecture finale!)
try:
    from kibali_orchestrator import orchestrate_prompt
    from kibali_executor import KibaliExecutor, process_prompt_full
    import asyncio
    print("✅ Orchestrator + Executor chargés")
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Orchestrator non disponible: {e}")
    ORCHESTRATOR_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Permet les requêtes depuis le navigateur

# Variables globales
HF_TOKEN = os.getenv("HF_TOKEN")
inference_client = None
# Utilise un modèle RAPIDE pour l'interface temps réel
current_model = "mistralai/Mistral-7B-Instruct-v0.2"  # Plus rapide que Qwen-32B !

# Import du générateur 3D par CODE IA (nouvelle méthode !)
from ai_procedural_3d import generate_3d_by_ai, generate_animation_by_ai, generate_camera_by_ai, init_ai_generator

# 🚀 NOUVEAU: Générateur HYBRIDE Mistral + CodeLlama
from hybrid_ai_generator import generate_hybrid_3d, init_hybrid_generator, fix_broken_code

# 🖼️ NOUVEAU: Analyseur d'images (CLIP + OCR + YOLO)
from image_analyzer_api import init_analyzer

# Import du générateur AVANCÉ avec multi-méthodes
from advanced_3d_generator import generate_advanced_3d

# Import du client TripoSR (isolé avec framework isol)
from triposr_client_hf import TripoSRClientHF

# Initialise le générateur HYBRIDE au démarrage
print("🚀 Initialisation du générateur HYBRIDE IA...")
print("   🧠 Mistral: Raisonnement et analyse")
print("   💻 CodeLlama: Génération de code complexe")
try:
    init_hybrid_generator()
    print("✅ Générateur Hybride prêt !")
except Exception as e:
    print(f"⚠️ Générateur Hybride en mode dégradé: {e}")

# Initialise le client TripoSR HF (démarrage lazy - au premier appel)
triposr_client = TripoSRClientHF()
triposr_initialized = False

# ============================================
# OUTILS LANGCHAIN - ORCHESTRATION IA
# ============================================

def tool_meshy_generate(prompt: str) -> str:
    """Génère un modèle 3D photoréaliste avec Meshy.ai"""
    try:
        response = requests.post(
            'http://localhost:11003/api/text-to-3d-meshy',
            json={'prompt': prompt, 'art_style': 'realistic'},
            timeout=60
        )
        if response.ok:
            data = response.json()
            if data.get('success'):
                return f"✅ Modèle 3D créé: {data.get('model_path', 'generated')}"
            return f"⚠️ {data.get('message', 'Erreur Meshy')}"
        return "❌ API Meshy non disponible"
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

def tool_midas_reconstruct(description: str) -> str:
    """Crée une session de reconstruction 3D multi-vues avec MiDaS"""
    try:
        response = requests.post(
            'http://localhost:11002/api/create_session',
            json={'name': description, 'description': description},
            timeout=10
        )
        if response.ok:
            data = response.json()
            return f"✅ Session reconstruction créée: {data.get('session_id', 'N/A')}"
        return "❌ API MiDaS non disponible"
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

def tool_procedural_generate(prompt: str) -> str:
    """Génère un modèle 3D simple par code procédural"""
    try:
        result = generate_3d_by_ai(prompt, 'character')
        if result.get('success'):
            return f"✅ Code procédural généré: {len(result.get('code', ''))} caractères"
        return "⚠️ Génération procédurale échouée"
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

def tool_analyze_scene(query: str) -> str:
    """Analyse l'état actuel de la scène 3D"""
    # TODO: Connecter à un système de state management
    return "📊 Analyse de scène: 0 objets, caméra à (0,5,15)"

# Définition des outils LangChain
if LANGCHAIN_AVAILABLE:
    # Charge TOUS les outils depuis le registry
    tools = get_all_tools()
    print(f"✅ {len(tools)} outils chargés depuis le registry")
    print(get_tools_summary())
    
    # Template pour l'agent ReAct
    react_template = """Tu es Kibali, un assistant IA expert en création 3D pour Kibalone Studio.
Tu DOIS OBLIGATOIREMENT utiliser les outils disponibles pour TOUTES les demandes.

🎯 RÈGLES CRITIQUES:
1. Pour TOUTE demande d'objet/asset (colonne, terrain, bâtiment, etc.) → COMMENCE PAR FetchCompleteAsset
2. Si aucun asset trouvé → utilise Search3DModels OU SearchTextures
3. Si besoin d'info externe → utilise WebSearch
4. Pour contrôle caméra → utilise les outils Camera*
5. NE RÉPONDS JAMAIS sans avoir essayé au moins UN outil

EXEMPLES D'UTILISATION CORRECTE:
- "mets une colonne" → Action: FetchCompleteAsset, Input: "colonne grecque"
- "crée terrain football" → Action: FetchCompleteAsset, Input: "terrain de football"  
- "cherche texture bois" → Action: SearchTextures, Input: "wood"
- "caméra tourne 360" → Action: CameraOrbit360, Input: duration=8

Outils disponibles:
{tools}

Format de réponse:
Question: la demande de l'utilisateur
Thought: ton raisonnement sur quelle(s) action(s) effectuer
Action: le nom de l'outil à utiliser
Action Input: l'input pour l'outil
Observation: le résultat de l'outil
... (répéter Thought/Action/Action Input/Observation si nécessaire)
Thought: Je sais maintenant quoi répondre
Final Answer: ta réponse finale à l'utilisateur

Question: {input}
{agent_scratchpad}"""

    print("✅ Outils LangChain configurés")
    AGENT_EXECUTOR = None  # Sera initialisé au premier appel
else:
    tools = []
    react_template = None
    AGENT_EXECUTOR = None

# ============================================
# INITIALISATION
# ============================================

def init_kibali():
    """Initialise le système Kibali"""
    global inference_client
    
    try:
        inference_client = InferenceClient(token=HF_TOKEN)
        print("✅ Kibali-IA initialisé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur init Kibali: {e}")
        return False

# ============================================
# ENDPOINTS API
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérifie que l'API est active"""
    return jsonify({
        'status': 'ok',
        'service': 'Kibali-IA API',
        'version': '1.0',
        'model': current_model
    })

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    """
    Analyse une image de référence avec CLIP + OCR + YOLO
    
    Body: {
        "image": "data:image/png;base64,..." ou base64 direct,
        "context": "reference" (optionnel)
    }
    
    Returns: {
        "success": true,
        "analysis": {
            "description": "vehicle (confidence: 0.95)",
            "objects": [{class: "car", confidence: 0.89, bbox: [...]}],
            "text": [{text: "BMW", confidence: 0.92, bbox: [...]}],
            "colors": ["#ff0000", "#000000", "#ffffff"],
            "style": "realistic photo",
            "dimensions": {width: 800, height: 600}
        }
    }
    """
    try:
        data = request.json
        image_data = data.get('image', '')
        
        if not image_data:
            return jsonify({
                'success': False,
                'error': 'No image provided'
            }), 400
        
        print(f"🖼️  Analyse d'image de référence...")
        
        # Initialise l'analyseur si nécessaire
        analyzer = init_analyzer()
        
        # Analyse l'image
        analysis = analyzer.analyze_image(image_data)
        
        print(f"✅ Analyse terminée:")
        print(f"   Description: {analysis['description']}")
        print(f"   Objets détectés: {len(analysis['objects'])}")
        print(f"   Texte trouvé: {len(analysis['text'])}")
        print(f"   Couleurs: {analysis['colors']}")
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f"❌ Erreur analyse image: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint principal pour le chat avec Kibali
    
    Body: {
        "message": "Crée un personnage héroïque",
        "context": "creation",
        "history": []
    }
    """
    try:
        data = request.json
        message = data.get('message', '')
        context = data.get('context', 'general')
        history = data.get('history', [])
        
        print(f"📨 [CHAT] Message reçu: {message[:50]}...")
        
        if not message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Construction du prompt système selon le contexte
        print(f"🔧 [CHAT] Context: {context}")
        system_prompt = get_system_prompt(context)
        
        # Génération de la réponse avec Kibali
        print(f"🤖 [CHAT] Génération réponse Kibali...")
        response = generate_response(message, system_prompt, history)
        print(f"✅ [CHAT] Réponse générée: {len(response['text'])} chars")
        
        return jsonify({
            'success': True,
            'response': response['text'],
            'analysis': response.get('analysis', {}),
            'suggestions': response.get('suggestions', [])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-model', methods=['POST'])
def generate_model():
    """
    Génère un modèle 3D avec le générateur HYBRIDE IA
    🧠 Mistral (raisonnement) + 💻 CodeLlama (code complexe)
    
    Body: {
        "prompt": "un personnage héroïque avec cape",
        "type": "character|object|environment"
    }
    """
    try:
        data = request.json
        prompt = data.get('prompt', '')
        model_type = data.get('type', 'character')
        
        print(f"🚀 [HYBRID-AI] Génération: '{prompt}' (type: {model_type})")
        
        # Utilise le générateur HYBRIDE Mistral + CodeLlama
        result = generate_hybrid_3d(prompt, model_type)
        
        if result.get('success'):
            analysis = result.get('analysis', {})
            print(f"   ✅ Analyse: {analysis.get('object_type')} / {analysis.get('style')}")
            print(f"   ✅ Code: {len(result['code'])} caractères")
            
            return jsonify({
                'success': True,
                'model_data': {
                    'code': result['code'],
                    'type': 'javascript'
                },
                'analysis': analysis,
                'method_used': 'hybrid-mistral-codellama',
                'message': f"✅ Code 3D généré par Mistral + CodeLlama !"
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Erreur génération'),
                'model_data': {'code': result.get('code', ''), 'type': 'javascript'}
            })
        
    except Exception as e:
        print(f"❌ Erreur generate-model: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/fix-code', methods=['POST'])
def fix_code():
    """
    🔧 AUTO-CORRECTION: Mistral corrige le code JavaScript cassé
    
    Body: {
        "code": "le code problématique",
        "error": "message d'erreur JavaScript",
        "prompt": "prompt original"
    }
    """
    try:
        data = request.json
        broken_code = data.get('code', '')
        error_msg = data.get('error', '')
        original_prompt = data.get('prompt', '')
        
        print(f"🔧 [AUTO-FIX] Correction demandée: {error_msg[:50]}")
        
        # Demande à Mistral de corriger
        result = fix_broken_code(broken_code, error_msg, original_prompt)
        
        if result.get('success'):
            print(f"   ✅ Code corrigé: {len(result['fixed_code'])} caractères")
            return jsonify(result)
        else:
            print(f"   ❌ Correction impossible")
            return jsonify(result), 400
        
    except Exception as e:
        print(f"❌ Erreur fix-code: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

    except Exception as e:
        print(f"❌ [HYBRID-AI] Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/orchestrate', methods=['POST'])
def orchestrate():
    """
    🎭 ENDPOINT ORCHESTRÉ - Architecture finale!
    
    Kibali analyse le prompt et ORCHESTRE les 48 outils
    Retourne le plan + logs en temps réel
    
    Body: {
        "prompt": "crée un personnage qui court et saute",
        "execute": true  // false = juste le plan, true = exécution
    }
    """
    try:
        data = request.json
        prompt = data.get('prompt', '')
        execute = data.get('execute', False)
        
        if not prompt:
            return jsonify({'error': 'Prompt vide'}), 400
        
        print(f"\n{'='*60}")
        print(f"🎭 [ORCHESTRATE] Prompt: {prompt}")
        print(f"{'='*60}")
        
        if not ORCHESTRATOR_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Orchestrator non disponible'
            }), 503
        
        # Phase 1: Orchestration (plan)
        orchestration = orchestrate_prompt(prompt)
        
        if not orchestration['understood']:
            return jsonify({
                'success': False,
                'error': 'Prompt non compris',
                'understood': False,
                'prompt': prompt
            })
        
        # Si mode "plan only", retourne juste le plan
        if not execute:
            return jsonify({
                'success': True,
                'understood': True,
                'plan': orchestration['plan'],
                'execution': None,
                'message': f"Plan créé: {len(orchestration['plan']['steps'])} étapes"
            })
        
        # Phase 2: Exécution (appels API réels)
        try:
            # Execute en async
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(process_prompt_full(prompt))
            loop.close()
            
            return jsonify({
                'success': result['success'],
                'understood': True,
                'plan': result['orchestration']['plan'],
                'execution': result['execution'],
                'message': '✅ Exécution terminée' if result['success'] else '⚠️ Erreurs détectées'
            })
        
        except Exception as e:
            print(f"❌ [ORCHESTRATE-EXEC] Erreur: {e}")
            return jsonify({
                'success': False,
                'understood': True,
                'plan': orchestration['plan'],
                'execution': None,
                'error': str(e)
            })
    
    except Exception as e:
        print(f"❌ [ORCHESTRATE] Erreur: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/triposr-generate', methods=['POST'])
def triposr_generate():
    """
    Génère un mesh 3D depuis une image avec TripoSR (isolé)
    
    Body: {
        "image_path": "/path/to/image.png",
        "output_path": "/path/to/output.obj" (optional),
        "resolution": 256 (optional)
    }
    """
    global triposr_initialized
    
    try:
        data = request.json
        image_path = data.get('image_path')
        output_path = data.get('output_path')
        resolution = data.get('resolution', 256)
        
        print(f"🎨 [TripoSR] Demande génération depuis: {image_path}")
        
        if not image_path:
            return jsonify({'error': 'image_path requis'}), 400
        
        # Initialise TripoSR au premier appel
        if not triposr_initialized:
            print("🚀 [TripoSR] Initialisation du service...")
            init_result = triposr_client.initialize()
            
            if not init_result.get('success'):
                return jsonify({
                    'error': f"Échec initialisation TripoSR: {init_result.get('error')}"
                }), 500
            
            triposr_initialized = True
            print(f"✅ [TripoSR] Service prêt sur {init_result.get('device')}")
        
        # Génère le mesh
        print(f"🔄 [TripoSR] Conversion en cours (résolution: {resolution})...")
        result = triposr_client.image_to_3d(
            image_path=image_path,
            output_path=output_path,
            resolution=resolution
        )
        
        if result.get('success'):
            print(f"✅ [TripoSR] Mesh généré: {result.get('output_path')}")
            return jsonify({
                'success': True,
                'mesh_path': result.get('output_path'),
                'vertices': result.get('vertices'),
                'faces': result.get('faces')
            })
        else:
            return jsonify({
                'error': f"Génération échouée: {result.get('error')}"
            }), 500
    
    except Exception as e:
        print(f"❌ [TripoSR] Erreur: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/text-to-3d', methods=['POST'])
def text_to_3d():
    """
    Génère un mesh 3D depuis un prompt texte avec PLUSIEURS MÉTHODES:
    - 'advanced': Code IA avec anatomie détaillée
    - 'grease-pencil': Dessin 2D dans 3D
    - 'blender-style': Modélisation avancée
    - 'auto': Détection automatique
    
    Body: {
        "prompt": "un guerrier avec épée",
        "method": "advanced" (optionnel: advanced, grease-pencil, blender-style, auto)
    }
    """
    try:
        data = request.json
        prompt = data.get('prompt')
        method = data.get('method', 'auto')
        
        print(f"🎨 [3D Avancé] Prompt: {prompt}, Méthode: {method}")
        
        if not prompt:
            return jsonify({'error': 'prompt requis'}), 400
        
        # Génère avec le nouveau système
        result = generate_advanced_3d(prompt, method)
        
        if result.get('success'):
            print(f"✅ [3D Avancé] Généré avec méthode: {result['method']}")
            return jsonify({
                'success': True,
                'code': result['code'],
                'method': result['method'],
                'type': 'javascript'
            })
        else:
            return jsonify({
                'error': f"Génération échouée: {result.get('error')}"
            }), 500
    
    except Exception as e:
        print(f"❌ [3D Avancé] Erreur: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/launch-demo', methods=['POST'])
def launch_demo():
    """
    🎬 Lance la démo MiDaS avec les photos du Château de Sceaux
    Reconstruit le mesh 3D et le charge dans la scène
    
    Body: {
        "num_photos": 3 (optionnel, défaut=3, max=11)
    }
    """
    try:
        data = request.json or {}
        num_photos = min(int(data.get('num_photos', 11)), 11)  # Utilise 11 photos par défaut
        
        print(f"🎬 [DÉMO] Lancement reconstruction château ({num_photos} photos)")
        
        # Import du client MiDaS
        import sys
        from pathlib import Path
        sys.path.insert(0, '/home/belikan/Isol/isol-framework')
        from midas_client import MiDaSClient
        
        # Photos du château
        photos_dir = Path("/home/belikan/Isol/Kibalone-Studio/static/assets/test_images")
        photos = sorted(photos_dir.glob("image_*.jpg"))[:num_photos]
        
        if not photos:
            return jsonify({
                'success': False,
                'error': 'Aucune photo trouvée'
            }), 404
        
        print(f"   📸 {len(photos)} photos sélectionnées")
        
        # Client MiDaS
        client = MiDaSClient()
        
        # Init
        print("   ⚙️  Init MiDaS...")
        init_result = client.initialize()
        if not init_result.get('success'):
            return jsonify({
                'success': False,
                'error': 'MiDaS init failed'
            }), 500
        
        # Reconstruction
        output_path = "/home/belikan/Isol/Kibalone-Studio/outputs/chateau_demo.obj"
        print(f"   🔮 Reconstruction → {output_path}")
        
        result = client.reconstruct_batch(
            image_paths=[str(p) for p in photos],
            preset="photogrammetry",
            output_path=output_path
        )
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', 'Reconstruction failed')
            }), 500
        
        mesh_path = result.get('output_path', output_path)
        vertices = result.get('vertices', 0)
        triangles = result.get('triangles', 0)
        
        print(f"   ✅ Mesh: {vertices} vertices, {triangles} triangles")
        
        # Convertit le chemin absolu en chemin relatif pour le frontend
        # /home/belikan/Isol/Kibalone-Studio/outputs/chateau_demo.obj → /outputs/chateau_demo.obj
        relative_mesh_path = mesh_path.replace('/home/belikan/Isol/Kibalone-Studio', '')
        
        # Génère code Three.js pour charger le mesh
        threejs_code = f"""
// Château de Sceaux - Reconstruction MiDaS ({num_photos} photos)
(function() {{
    const loader = new THREE.OBJLoader();
    addLog('📦 Chargement du mesh...');
    console.log('🔍 Tentative chargement:', '{relative_mesh_path}');
    
    loader.load(
        '{relative_mesh_path}',
        (obj) => {{
            console.log('✅ OBJ chargé:', obj);
            addLog('✅ Mesh chargé avec succès');
            
            // Centre et scale
            const box = new THREE.Box3().setFromObject(obj);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            const scale = 5 / maxDim;
            
            obj.position.sub(center);
            obj.scale.set(scale, scale, scale);
            
            // Matériau pierre
            obj.traverse((child) => {{
                if (child.isMesh) {{
                    child.material = new THREE.MeshStandardMaterial({{
                        color: 0xC8A882,
                        roughness: 0.8,
                        metalness: 0.1
                    }});
                    child.castShadow = true;
                    child.receiveShadow = true;
                }}
            }});
            
            studio.scene.add(obj);
            addLog('✅ Château affiché dans la scène!');
            addLog('📊 {vertices} vertices, {triangles} triangles');
        }},
        (xhr) => {{
            if (xhr.lengthComputable) {{
                const percent = Math.round((xhr.loaded / xhr.total) * 100);
                if (percent % 25 === 0) {{
                    console.log(`Chargement: ${{percent}}%`);
                    addLog(`⏳ Chargement: ${{percent}}%`);
                }}
            }}
        }},
        (error) => {{
            console.error('❌ Erreur OBJLoader:', error);
            console.error('Path tenté:', '{relative_mesh_path}');
            addLog('❌ Erreur chargement mesh');
            addLog('URL: {relative_mesh_path}');
        }}
    );
}})();
"""
        
        return jsonify({
            'success': True,
            'code': threejs_code,
            'type': 'javascript',
            'mesh_path': mesh_path,
            'stats': {
                'photos': len(photos),
                'vertices': vertices,
                'triangles': triangles
            },
            'message': f'🏰 Château reconstruit depuis {len(photos)} photos!'
        })
        
    except Exception as e:
        print(f"❌ [DÉMO] Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload-reconstruct', methods=['POST'])
def upload_reconstruct():
    """
    📤 Upload photos et lance reconstruction MiDaS
    Sauvegarde dans /outputs/ et retourne le chemin du mesh
    
    FormData: files[] - Liste de fichiers image
    """
    try:
        if 'photos' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Aucune photo uploadée'
            }), 400
        
        files = request.files.getlist('photos')
        if len(files) == 0:
            return jsonify({
                'success': False,
                'error': 'Liste de photos vide'
            }), 400
        
        print(f"📤 [UPLOAD] {len(files)} photos reçues")
        
        # Crée un dossier temporaire pour les uploads
        import tempfile
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = Path(tempfile.mkdtemp(prefix=f"upload_{timestamp}_"))
        
        # Sauvegarde les fichiers uploadés
        photo_paths = []
        for i, file in enumerate(files):
            if file.filename:
                ext = Path(file.filename).suffix
                photo_path = temp_dir / f"photo_{i:03d}{ext}"
                file.save(str(photo_path))
                photo_paths.append(photo_path)
                print(f"   📁 Sauvegardé: {photo_path.name}")
        
        if len(photo_paths) == 0:
            shutil.rmtree(temp_dir)
            return jsonify({
                'success': False,
                'error': 'Aucune photo valide'
            }), 400
        
        # Import du client MiDaS
        import sys
        sys.path.insert(0, '/home/belikan/Isol/isol-framework')
        from midas_client import MiDaSClient
        
        # Client MiDaS
        client = MiDaSClient()
        
        # Init
        print("   ⚙️  Init MiDaS...")
        init_result = client.initialize()
        if not init_result.get('success'):
            shutil.rmtree(temp_dir)
            return jsonify({
                'success': False,
                'error': 'MiDaS init failed'
            }), 500
        
        # Reconstruction
        output_filename = f"reconstruction_{timestamp}.obj"
        output_path = f"/home/belikan/Isol/Kibalone-Studio/outputs/{output_filename}"
        print(f"   🔮 Reconstruction → {output_path}")
        
        result = client.reconstruct_batch(
            image_paths=[str(p) for p in photo_paths],
            preset="photogrammetry",
            output_path=output_path
        )
        
        # Nettoyage du dossier temporaire
        shutil.rmtree(temp_dir)
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', 'Reconstruction failed')
            }), 500
        
        mesh_path = result.get('output_path', output_path)
        vertices = result.get('vertices', 0)
        triangles = result.get('triangles', 0)
        
        print(f"   ✅ Mesh: {vertices} vertices, {triangles} triangles")
        print(f"   💾 Sauvegardé: {output_filename}")
        
        # Chemin relatif pour le frontend
        relative_mesh_path = f"/outputs/{output_filename}"
        
        # Génère code Three.js pour charger le mesh
        threejs_code = f"""
(function() {{
    const loader = new THREE.OBJLoader();
    addLog('📦 Chargement du mesh reconstruit...');
    
    loader.load(
        '{relative_mesh_path}',
        (obj) => {{
            const box = new THREE.Box3().setFromObject(obj);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            const scale = 5 / maxDim;
            
            obj.position.sub(center);
            obj.scale.set(scale, scale, scale);
            
            obj.traverse((child) => {{
                if (child.isMesh) {{
                    child.material = new THREE.MeshStandardMaterial({{
                        color: 0x888888,
                        roughness: 0.7,
                        metalness: 0.2
                    }});
                    child.castShadow = true;
                    child.receiveShadow = true;
                }}
            }});
            
            studio.scene.add(obj);
            addLog('✅ Reconstruction affichée!');
            addLog('📊 {vertices} vertices, {triangles} triangles');
            addLog('💾 Sauvegardé: {output_filename}');
        }},
        (xhr) => {{
            if (xhr.lengthComputable) {{
                const percent = Math.round((xhr.loaded / xhr.total) * 100);
                if (percent % 25 === 0) {{
                    addLog(`⏳ Chargement: ${{percent}}%`);
                }}
            }}
        }},
        (error) => {{
            addLog('❌ Erreur chargement mesh');
            console.error('Erreur:', error);
        }}
    );
}})();
"""
        
        return jsonify({
            'success': True,
            'code': threejs_code,
            'type': 'javascript',
            'mesh_path': mesh_path,
            'relative_path': relative_mesh_path,
            'filename': output_filename,
            'stats': {
                'photos': len(photo_paths),
                'vertices': vertices,
                'triangles': triangles
            },
            'message': f'✅ Reconstruction depuis {len(photo_paths)} photos!'
        })
        
    except Exception as e:
        print(f"❌ [UPLOAD] Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/grease-pencil', methods=['POST'])
def grease_pencil():
    """
    Dessine en 2D dans l'espace 3D (style Grease Pencil Blender)
    
    Body: {
        "prompt": "dessine un dragon qui vole",
        "style": "sketch" (optionnel)
    }
    """
    try:
        data = request.json
        prompt = data.get('prompt')
        
        print(f"✏️ [Grease Pencil] Prompt: {prompt}")
        
        if not prompt:
            return jsonify({'error': 'prompt requis'}), 400
        
        # Force la méthode grease-pencil
        result = generate_advanced_3d(prompt, 'grease-pencil')
        
        if result.get('success'):
            print(f"✅ [Grease Pencil] Dessin généré")
            return jsonify({
                'success': True,
                'code': result['code'],
                'method': 'grease-pencil',
                'type': 'javascript'
            })
        else:
            return jsonify({
                'error': f"Génération échouée: {result.get('error')}"
            }), 500
    
    except Exception as e:
        print(f"❌ [Grease Pencil] Erreur: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-prompt', methods=['POST'])
def analyze_prompt():
    """
    Analyse un prompt pour comprendre l'intention ET ORCHESTRER LES OUTILS
    🚀 UTILISE LE DISPATCHER INTELLIGENT (bypass LangChain)
    
    Body: {
        "prompt": "anime le personnage en marchant",
        "context": "animation",
        "use_dispatcher": true  # Active le dispatcher (par défaut)
    }
    """
    try:
        data = request.json
        prompt = data.get('prompt', '')
        context = data.get('context', 'general')
        use_dispatcher = data.get('use_dispatcher', True)  # Dispatcher par défaut
        
        import sys
        sys.stderr.write(f"🧠 [ANALYZE] Prompt: '{prompt}'\n")
        sys.stderr.write(f"🔧 [ANALYZE] use_dispatcher={use_dispatcher}, DISPATCHER_AVAILABLE={DISPATCHER_AVAILABLE}\n")
        sys.stderr.flush()
        
        # 🚀 MODE DISPATCHER - Pattern matching intelligent (PRIORITAIRE)
        if use_dispatcher and DISPATCHER_AVAILABLE:
            sys.stderr.write(f"⚡ [ANALYZE] Mode DISPATCHER activé!\n")
            sys.stderr.flush()
            
            # Utilise dispatch_and_execute qui fait: analyze + execute
            from kibali_dispatcher import dispatch_and_execute
            result = dispatch_and_execute(prompt)
            
            sys.stderr.write(f"✅ [ANALYZE] Dispatcher result: {result}\n")
            sys.stderr.flush()
            
            return jsonify(result)
        
        # MODE AGENT LANGCHAIN - Fallback si dispatcher indisponible
        elif LANGCHAIN_AVAILABLE:
            sys.stderr.write(f"🚀 [ANALYZE] Mode AGENT LangChain (fallback)\n")
            sys.stderr.flush()
            result = execute_agent_task(prompt)
            sys.stderr.write(f"✅ [ANALYZE] Agent result: {result}\n")
            sys.stderr.flush()
            return jsonify(result)
        
        # MODE SIMPLE - Analyse basique sans outils
        else:
            sys.stderr.write(f"⚠️ [ANALYZE] Mode SIMPLE (ni dispatcher ni agent)\n")
            sys.stderr.flush()
            analysis = analyze_with_kibali(prompt, context)
            
            return jsonify({
                'success': True,
                'intent': analysis['intent'],
                'parameters': analysis['parameters'],
                'suggestions': analysis['suggestions']
            })
        
    except Exception as e:
        print(f"❌ [ANALYZE] Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def execute_agent_task(prompt: str) -> dict:
    """Exécute une tâche avec l'agent LangChain"""
    global AGENT_EXECUTOR
    
    try:
        # Initialise l'agent si nécessaire
        if AGENT_EXECUTOR is None and LANGCHAIN_AVAILABLE:
            print("🤖 Initialisation de l'agent LangChain...")
            
            # Crée un LLM HuggingFace
            llm = HuggingFaceEndpoint(
                endpoint_url=f"https://api-inference.huggingface.co/models/{current_model}",
                huggingfacehub_api_token=HF_TOKEN,
                temperature=0.7,
                max_new_tokens=512
            )
            
            # Crée le prompt template
            prompt_template = PromptTemplate(
                template=react_template,
                input_variables=["input", "agent_scratchpad"],
                partial_variables={"tools": "\n".join([f"{t.name}: {t.description}" for t in tools])}
            )
            
            # Crée l'agent
            agent = create_react_agent(llm, tools, prompt_template)
            AGENT_EXECUTOR = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=True,
                max_iterations=5,
                handle_parsing_errors=True
            )
            print("✅ Agent LangChain prêt")
        
        # Exécute l'agent
        if AGENT_EXECUTOR:
            print(f"🚀 Exécution agent pour: '{prompt}'")
            result = AGENT_EXECUTOR.invoke({"input": prompt})
            
            # Parse le résultat
            output = result.get('output', '')
            
            # Extrait les infos de l'exécution
            tools_used = []
            for tool in tools:
                if tool.name in str(result):
                    tools_used.append(tool.name)
            
            return {
                'success': True,
                'intent': 'create',  # TODO: extraire du résultat
                'parameters': {
                    'type': 'character',  # TODO: extraire
                    'description': prompt,
                    'tool': tools_used[0] if tools_used else 'procedural',
                    'tools_used': tools_used
                },
                'agent_output': output,
                'suggestions': [output]
            }
        else:
            raise Exception("Agent non disponible")
            
    except Exception as e:
        import sys, traceback
        sys.stderr.write(f"❌ Agent erreur: {e}\n")
        sys.stderr.write(f"📋 Traceback:\n{traceback.format_exc()}\n")
        sys.stderr.flush()
        # Fallback sur analyse simple
        return analyze_with_kibali(prompt, 'general')

@app.route('/api/agent-execute', methods=['POST'])
def agent_execute():
    """
    Endpoint dédié pour exécuter l'agent avec tous les outils
    
    Body: {
        "task": "Crée un personnage héroïque et ajoute une lumière dramatique",
        "max_iterations": 5
    }
    """
    try:
        data = request.json
        task = data.get('task', '')
        max_iter = data.get('max_iterations', 5)
        
        if not LANGCHAIN_AVAILABLE:
            return jsonify({
                'error': 'LangChain non disponible. Installez: pip install langchain langchain-community'
            }), 503
        
        print(f"🤖 [AGENT] Tâche: {task}")
        result = execute_agent_task(task)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-animation', methods=['POST'])
def generate_animation():
    """
    Génère des keyframes d'animation
    
    Body: {
        "prompt": "marche vers l'avant pendant 3 secondes",
        "object_type": "character",
        "duration_frames": 90
    }
    """
    try:
        data = request.json
        prompt = data.get('prompt', '')
        object_type = data.get('object_type', 'character')
        duration = data.get('duration_frames', 90)
        
        # Génère les keyframes avec Kibali
        keyframes = generate_animation_keyframes(prompt, object_type, duration)
        
        return jsonify({
            'success': True,
            'keyframes': keyframes,
            'duration': duration,
            'fps': 30
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera-control', methods=['POST'])
def camera_control():
    """
    Contrôle de la caméra par prompt
    
    Body: {
        "prompt": "caméra orbite autour du personnage",
        "current_position": {x, y, z}
    }
    """
    try:
        data = request.json
        prompt = data.get('prompt', '')
        current_pos = data.get('current_position', {'x': 5, 'y': 5, 'z': 5})
        
        # Analyse et génère le mouvement de caméra
        camera_path = generate_camera_movement(prompt, current_pos)
        
        return jsonify({
            'success': True,
            'camera_path': camera_path,
            'animation_type': camera_path['type']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/axis-widget', methods=['POST'])
def toggle_axis_widget():
    """Toggle le widget d'orientation des axes"""
    try:
        data = request.json or {}
        action = data.get('action', 'toggle')
        return jsonify({
            'success': True,
            'action': action,
            'message': f'Widget d\'axes {action}',
            'widget_visible': action in ['toggle', 'show']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# ENDPOINTS CAMÉRA EXPERT - 10 CONTRÔLES
# ============================================

@app.route('/api/camera-orbit', methods=['POST'])
def camera_orbit():
    """Orbite 360° autour de la scène"""
    try:
        data = request.json or {}
        duration = data.get('duration', 8000)
        height = data.get('height', 5)
        radius = data.get('radius', 8)
        return jsonify({
            'success': True,
            'command': 'orbit360',
            'params': {'duration': duration, 'height': height, 'radius': radius}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera-move', methods=['POST'])
def camera_move_endpoint():
    """Déplace la caméra dans une direction"""
    try:
        data = request.json or {}
        direction = data.get('direction', 'forward')
        distance = data.get('distance', 2)
        duration = data.get('duration', 1000)
        return jsonify({
            'success': True,
            'command': 'move',
            'params': {'direction': direction, 'distance': distance, 'duration': duration}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera-rotate', methods=['POST'])
def camera_rotate_endpoint():
    """Rotation sur un axe"""
    try:
        data = request.json or {}
        axis = data.get('axis', 'y')
        degrees = data.get('degrees', 90)
        duration = data.get('duration', 1000)
        return jsonify({
            'success': True,
            'command': 'rotate',
            'params': {'axis': axis, 'degrees': degrees, 'duration': duration}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera-flyto', methods=['POST'])
def camera_flyto():
    """Vol cinématique vers position"""
    try:
        data = request.json or {}
        x = data.get('x', 0)
        y = data.get('y', 10)
        z = data.get('z', 5)
        duration = data.get('duration', 2000)
        return jsonify({
            'success': True,
            'command': 'flyto',
            'params': {'x': x, 'y': y, 'z': z, 'duration': duration}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera-lookat', methods=['POST'])
def camera_lookat():
    """Change le point de focus"""
    try:
        data = request.json or {}
        x = data.get('x', 0)
        y = data.get('y', 0)
        z = data.get('z', 0)
        return jsonify({
            'success': True,
            'command': 'lookat',
            'params': {'x': x, 'y': y, 'z': z}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera-zoom', methods=['POST'])
def camera_zoom_endpoint():
    """Zoom in/out"""
    try:
        data = request.json or {}
        factor = data.get('factor', 1.5)
        duration = data.get('duration', 500)
        return jsonify({
            'success': True,
            'command': 'zoom',
            'params': {'factor': factor, 'duration': duration}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera-pan', methods=['POST'])
def camera_pan_endpoint():
    """Pan horizontal/vertical"""
    try:
        data = request.json or {}
        horizontal = data.get('horizontal', 0)
        vertical = data.get('vertical', 0)
        duration = data.get('duration', 1000)
        return jsonify({
            'success': True,
            'command': 'pan',
            'params': {'horizontal': horizontal, 'vertical': vertical, 'duration': duration}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera-shake', methods=['POST'])
def camera_shake_endpoint():
    """Effet shake (explosion, impact)"""
    try:
        data = request.json or {}
        intensity = data.get('intensity', 0.3)
        duration = data.get('duration', 500)
        return jsonify({
            'success': True,
            'command': 'shake',
            'params': {'intensity': intensity, 'duration': duration}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera-preset', methods=['POST'])
def camera_preset_endpoint():
    """Positions préréglées"""
    try:
        data = request.json or {}
        preset = data.get('preset', 'iso')
        return jsonify({
            'success': True,
            'command': 'preset',
            'params': {'preset': preset}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera-stop', methods=['POST'])
def camera_stop_endpoint():
    """Arrête toute animation de caméra"""
    try:
        return jsonify({
            'success': True,
            'command': 'stop'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# FONCTIONS INTERNES
# ============================================

def get_system_prompt(context):
    """Retourne le prompt système selon le contexte"""
    prompts = {
        'creation': """Tu es Kibali, assistant expert en création 3D pour Kibalone Studio.
IMPORTANT: Réponds UNIQUEMENT en français, de manière COURTE (maximum 2-3 phrases).
Tu aides à créer des modèles 3D (personnages, objets, environnements).
Confirme rapidement ce que tu vas créer, sans détails techniques.
Exemple: "Je crée un guerrier héroïque avec armure et épée !"
""",
        
        'animation': """Tu es Kibali, expert en animation 3D.
IMPORTANT: Réponds UNIQUEMENT en français, de manière COURTE (1-2 phrases).
Confirme l'animation que tu vas créer.
Exemple: "J'anime le personnage en marche !"
""",
        
        'camera': """Tu es Kibali, directeur photo virtuel.
IMPORTANT: Réponds UNIQUEMENT en français, de manière COURTE (1-2 phrases).
Confirme le mouvement de caméra.
Exemple: "Caméra en orbite autour de la scène !"
""",
        
        'general': """Tu es Kibali, assistant IA pour la création 3D dans Kibalone Studio.
IMPORTANT: 
- Réponds UNIQUEMENT en français
- Sois TRÈS BREF (maximum 2-3 phrases)
- Confirme rapidement sans explications longues
Tu comprends les demandes de création 3D et réponds de façon concise."""
    }
    
    return prompts.get(context, prompts['general'])

def generate_response(message, system_prompt, history):
    """Génère une réponse avec Kibali - VERSION RAPIDE ET COURTE"""
    global inference_client, current_model
    
    print(f"🤖 [KIBALI] Début génération... (modèle: {current_model})")
    
    # Construction des messages avec instruction de brièveté
    messages = [{"role": "system", "content": system_prompt + "\n\nRAPPEL: Réponds en français, maximum 2-3 phrases courtes."}]
    
    # Ajoute l'historique (RÉDUIT pour vitesse)
    for msg in history[-2:]:  # Seulement 2 derniers messages au lieu de 5
        messages.append(msg)
    
    messages.append({"role": "user", "content": message})
    
    # Génération
    response_text = ""
    try:
        stream = inference_client.chat.completions.create(
            model=current_model,
            messages=messages,
            max_tokens=200,  # RÉDUIT à 200 pour réponses courtes
            temperature=0.7,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
        
        print(f"✅ [KIBALI] Réponse générée: {len(response_text)} chars")
        
        return {
            'text': response_text,
            'analysis': parse_analysis(response_text),
            'suggestions': []
        }
        
    except Exception as e:
        return {
            'text': f"Erreur: {str(e)}",
            'analysis': {},
            'suggestions': []
        }

def analyze_with_kibali(prompt, context):
    """Analyse un prompt avec Kibali"""
    system_prompt = f"""Analyse ce prompt pour la création 3D.
Retourne un JSON avec:
- intent: l'intention (create, animate, camera, light, etc.)
- parameters: {{
    type: le type d'objet (character, environment, object, etc.),
    description: description extraite,
    complexity: niveau de complexité (1-10),
    tool: l'outil à utiliser (meshy, triposr, midas, procedural)
  }}
- suggestions: des suggestions d'amélioration

Prompt: {prompt}
Context: {context}

Choix de l'outil:
- meshy: pour génération 3D réaliste et détaillée (nécessite API key)
- triposr: pour conversion image→3D (actuellement non disponible)
- midas: pour reconstruction 3D multi-vues/photogrammétrie
- procedural: génération procédurale simple (fallback)"""
    
    response = generate_response(prompt, system_prompt, [])
    
    try:
        # Parse le JSON de la réponse
        json_start = response['text'].find('{')
        json_end = response['text'].rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            result = json.loads(response['text'][json_start:json_end])
            # Assure qu'il y a un tool par défaut
            if 'parameters' in result and 'tool' not in result['parameters']:
                result['parameters']['tool'] = 'procedural'
            return result
    except:
        pass
    
    # Fallback simple
    intent = detect_intent(prompt)
    obj_type = 'character' if 'character' in intent or 'personnage' in prompt.lower() else \
               'environment' if 'environment' in intent or 'environnement' in prompt.lower() else \
               'object'
    
    return {
        'intent': intent,
        'parameters': {
            'type': obj_type,
            'description': prompt,
            'complexity': 5,
            'tool': 'procedural'  # Par défaut
        },
        'suggestions': []
    }

def detect_intent(prompt):
    """Détecte l'intention basique du prompt"""
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ['crée', 'créer', 'génère', 'ajoute']):
        if 'personnage' in prompt_lower or 'character' in prompt_lower:
            return 'create_character'
        elif 'environnement' in prompt_lower or 'environment' in prompt_lower:
            return 'create_environment'
        elif 'objet' in prompt_lower or 'object' in prompt_lower:
            return 'create_object'
        return 'create'
    
    elif any(word in prompt_lower for word in ['anime', 'animer', 'mouvement', 'bouge']):
        return 'animate'
    
    elif any(word in prompt_lower for word in ['caméra', 'camera', 'vue', 'plan']):
        return 'camera'
    
    elif any(word in prompt_lower for word in ['lumière', 'light', 'éclairage']):
        return 'light'
    
    return 'general'

def analyze_model_prompt(prompt, model_type):
    """Analyse un prompt de création de modèle"""
    system_prompt = f"""Analyse ce prompt pour créer un modèle 3D de type {model_type}.
Extrais:
- forme de base (humanoid, spherical, cubic, etc.)
- caractéristiques (taille, couleur, style)
- complexité (1-10)
- est_organique (true/false)

Prompt: {prompt}"""
    
    response = generate_response(prompt, system_prompt, [])
    
    return {
        'prompt': prompt,
        'type': model_type,
        'shape': 'humanoid' if 'personnage' in prompt.lower() else 'cubic',
        'scale': 1.0,
        'complexity': 5,
        'organic': model_type == 'character'
    }

def generate_procedural_model(analysis):
    """Génère un modèle procédural simple"""
    # Retourne les données pour générer côté client
    return {
        'type': 'procedural',
        'shape': analysis['shape'],
        'scale': analysis['scale'],
        'vertices': [],  # À générer côté client
        'faces': [],
        'ready': True
    }

def generate_ai_model(analysis):
    """Génère un modèle avec IA (placeholder)"""
    return {
        'type': 'ai_generated',
        'status': 'processing',
        'message': 'Génération IA en cours...',
        'ready': False
    }

def generate_animation_keyframes(prompt, object_type, duration):
    """Génère des keyframes d'animation"""
    # Analyse le prompt
    if 'marche' in prompt.lower() or 'walk' in prompt.lower():
        # Animation de marche
        keyframes = []
        for frame in range(0, duration, 15):
            keyframes.append({
                'frame': frame,
                'transformation': {
                    'translation': {'x': 0, 'y': 0, 'z': frame * 0.05},
                    'rotation': {'x': 0, 'y': 0, 'z': 0},
                    'scale': {'x': 1, 'y': 1, 'z': 1}
                }
            })
        return keyframes
    
    elif 'rotation' in prompt.lower() or 'tourne' in prompt.lower():
        # Animation de rotation
        keyframes = []
        for frame in range(0, duration, 10):
            angle = (frame / duration) * 360
            keyframes.append({
                'frame': frame,
                'transformation': {
                    'translation': {'x': 0, 'y': 0, 'z': 0},
                    'rotation': {'x': 0, 'y': angle, 'z': 0},
                    'scale': {'x': 1, 'y': 1, 'z': 1}
                }
            })
        return keyframes
    
    # Default: simple keyframes
    return [
        {'frame': 0, 'transformation': {'translation': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}},
        {'frame': duration, 'transformation': {'translation': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}}
    ]

def generate_camera_movement(prompt, current_pos):
    """Génère un mouvement de caméra"""
    if 'orbite' in prompt.lower() or 'orbit' in prompt.lower():
        return {
            'type': 'orbit',
            'center': {'x': 0, 'y': 0, 'z': 0},
            'radius': 10,
            'duration': 120,
            'start_angle': 0,
            'end_angle': 360
        }
    
    elif 'zoom' in prompt.lower():
        return {
            'type': 'zoom',
            'start': current_pos,
            'end': {'x': current_pos['x'] * 0.5, 'y': current_pos['y'] * 0.5, 'z': current_pos['z'] * 0.5},
            'duration': 60
        }
    
    else:
        return {
            'type': 'static',
            'position': current_pos
        }

def parse_analysis(text):
    """Parse l'analyse depuis le texte de réponse"""
    # Cherche du JSON dans la réponse
    try:
        json_start = text.find('{')
        json_end = text.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            return json.loads(text[json_start:json_end])
    except:
        pass

# 🧪 ENDPOINT DE DEBUG POUR TESTER LE DISPATCHER
@app.route('/api/dispatcher/test', methods=['POST'])
def test_dispatcher():
    """
    Test le dispatcher avec un prompt
    Retourne le matching de pattern sans exécuter
    
    Body: {
        "prompt": "fait moi un terrain de foot"
    }
    """
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not DISPATCHER_AVAILABLE:
            return jsonify({
                'error': 'Dispatcher non disponible',
                'dispatcher_available': False
            }), 503
        
        # Analyse le prompt
        plan = dispatcher.analyze(prompt)
        
        return jsonify({
            'success': True,
            'prompt': prompt,
            'plan': plan,
            'dispatcher_available': True
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/dispatcher/patterns', methods=['GET'])
def get_dispatcher_patterns():
    """
    Retourne tous les patterns disponibles dans le dispatcher
    Utile pour la documentation
    """
    try:
        if not DISPATCHER_AVAILABLE:
            return jsonify({
                'error': 'Dispatcher non disponible',
                'dispatcher_available': False
            }), 503
        
        # Compte les patterns depuis l'instance
        pattern_count = len(dispatcher.patterns) if dispatcher else 0
        
        return jsonify({
            'success': True,
            'total_patterns': pattern_count,
            'patterns': dispatcher.patterns if dispatcher else [],
            'dispatcher_available': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return {}

# 🎭 ENDPOINTS MOCK pour outils sans implémentation backend
@app.route('/api/mesh/<action>', methods=['POST'])
@app.route('/api/assets/<action>', methods=['POST'])
@app.route('/api/export/<action>', methods=['POST'])
def mock_tool_endpoint(action):
    """
    Endpoint mock qui simule l'exécution des outils
    Pour: mesh operations, assets, export
    """
    try:
        data = request.json or {}
        
        print(f"🔧 [MOCK] Outil: {action}")
        print(f"   Params: {data}")
        
        # Simule un délai de traitement
        import time
        time.sleep(0.5)
        
        return jsonify({
            'success': True,
            'tool': action,
            'message': f'✅ {action} simulé (mock)',
            'params': data,
            'note': 'Implémentation backend à venir'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# DÉMARRAGE
# ============================================

if __name__ == '__main__':
    print("🚀 Démarrage de l'API Kibali-IA pour Kibalone Studio")
    print(f"📁 Kibali path: {KIBALI_PATH}")
    
    if init_kibali():
        print("✅ Kibali-IA prêt")
        
        # Status des systèmes d'orchestration
        print("\n🎛️  Systèmes d'orchestration:")
        if DISPATCHER_AVAILABLE:
            print("  ⚡ DISPATCHER: ✅ ACTIF (150+ patterns)")
        else:
            print("  ⚡ DISPATCHER: ❌ Indisponible")
            
        if LANGCHAIN_AVAILABLE:
            print(f"  🔗 LANGCHAIN: ✅ Disponible ({len(ALL_TOOLS_DEFINITIONS)} outils)")
        else:
            print("  🔗 LANGCHAIN: ❌ Indisponible")
        
        print("\n🌐 API disponible sur: http://localhost:11000")
        print("\nEndpoints disponibles:")
        print("  GET  /api/health")
        print("  POST /api/chat")
        print("  POST /api/generate-model")
        print("  POST /api/text-to-3d")
        print("  POST /api/triposr-generate")
        print("  POST /api/analyze-prompt        ⚡ DISPATCHER")
        print("  POST /api/generate-animation")
        print("  POST /api/camera-control")
        print("  POST /api/dispatcher/test        🧪 DEBUG")
        print("  GET  /api/dispatcher/patterns    📚 DOCS")
        
        port = int(os.environ.get('PORT', 11000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("❌ Impossible de démarrer Kibali-IA")
