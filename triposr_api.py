#!/usr/bin/env python3
"""
TripoSR API pour Kibalone Studio
Génère des modèles 3D réalistes via Isol Framework
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging
import requests
import json
import base64
import io
from PIL import Image

# Ajoute Isol Framework au path
sys.path.insert(0, '/home/belikan/Isol/isol-framework')
from client import ServiceClient

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Client du service TripoSR via Isol Framework
triposr_client = ServiceClient('/home/belikan/Isol/isol-framework/triposr_service.py')

# Initialise le service au démarrage
logger.info("🚀 Initialisation du service TripoSR...")
init_result = triposr_client.call({'action': 'initialize'})
if init_result.get('success'):
    logger.info(f"✅ Service TripoSR prêt (device: {init_result.get('device')})")
else:
    logger.error(f"❌ Erreur init: {init_result.get('error')}")

# Stable Diffusion API pour générer des images depuis du texte
STABILITY_API_KEY = os.getenv('STABILITY_API_KEY', '')

def text_to_image(prompt):
    """
    Génère une image depuis un prompt texte via Stable Diffusion
    """
    try:
        # Utilise l'API locale si disponible, sinon utilise Hugging Face
        hf_api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        
        headers = {}
        hf_token = os.getenv('HUGGINGFACE_TOKEN', '')
        if hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"
        
        payload = {
            "inputs": f"{prompt}, 3D render, white background, centered, professional product photo",
            "parameters": {
                "negative_prompt": "blur, low quality, distorted",
                "num_inference_steps": 30,
            }
        }
        
        response = requests.post(hf_api_url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            return image
        else:
            logger.error(f"Error from Hugging Face API: {response.status_code}")
            # Fallback: créer une image simple
            return create_simple_image(prompt)
            
    except Exception as e:
        logger.error(f"Error in text_to_image: {e}")
        return create_simple_image(prompt)

def create_simple_image(prompt):
    """
    Crée une image simple pour les tests
    """
    # Crée une image blanche avec du texte
    img = Image.new('RGB', (512, 512), color='white')
    return img

@app.route('/api/health', methods=['GET'])
def health():
    """Check API health"""
    return jsonify({
        'status': 'ok',
        'service': 'triposr via isol-framework',
        'framework': 'isol'
    })
def text_to_3d_triposr():
    """
    Endpoint principal: Texte -> Image -> Modèle 3D
    """
    try:
        data = request.json
        prompt = data.get('prompt', '')
        resolution = data.get('resolution', 256)
        
        if not prompt:
            return jsonify({'success': False, 'error': 'No prompt provided'}), 400
        
        logger.info(f"📝 Prompt reçu: {prompt}")
        
        # Étape 1: Génère une image depuis le prompt
        logger.info("🎨 Génération de l'image...")
        image = text_to_image(prompt)
        
        if image is None:
            return jsonify({'success': False, 'error': 'Failed to generate image'}), 500
        
        # Convertit l'image en base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Étape 2: Envoie au service TripoSR via Isol Framework
        logger.info("🎯 Appel du service TripoSR...")
        result = triposr_client.call({
            'action': 'generate',
            'image': image_b64,
            'resolution': resolution
        })
        
        if result.get('success'):
            logger.info(f"✅ Modèle 3D généré: {result.get('vertices_count')} vertices")
            return jsonify(result)
        else:
            logger.error(f"❌ Erreur: {result.get('error')}")
            return jsonify(result), 500
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_threejs_code(vertices, faces, prompt):
    """
    Génère du code Three.js pour afficher le mesh
    """
    # Limite le nombre de vertices pour la performance
    max_vertices = 5000
    if len(vertices) > max_vertices:
        # Simplifie le mesh
        step = len(vertices) // max_vertices
        vertices = vertices[::step]
    
    # Convertit en listes Python
    vertices_list = vertices.tolist()
    faces_list = faces.tolist()
    
    code = f"""
(function() {{
    const geometry = new THREE.BufferGeometry();
    
    // Vertices
    const vertices = new Float32Array({json.dumps(vertices_list).replace(' ', '')});
    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    
    // Faces (indices)
    const indices = new Uint32Array({json.dumps(faces_list).replace(' ', '')});
    geometry.setIndex(new THREE.BufferAttribute(indices, 1));
    
    // Compute normals
    geometry.computeVertexNormals();
    
    // Material
    const material = new THREE.MeshStandardMaterial({{
        color: 0x{np.random.randint(0, 0xFFFFFF):06x},
        metalness: 0.3,
        roughness: 0.6,
        flatShading: false
    }});
    
    // Create mesh
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.userData.type = 'character';
    mesh.userData.prompt = '{prompt}';
    mesh.userData.method = 'triposr';
    
    // Create group
    const group = new THREE.Group();
    group.add(mesh);
    group.position.set(0, 0, 0);
    group.scale.set(1, 1, 1);
    
    return group;
}})()
"""
    return code

@app.route('/api/health', methods=['GET'])
def health():
    """Check API health"""
    return jsonify({
        'status': 'ok',
        'service': 'triposr via isol-framework',
        'framework': 'isol'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 11001))
    print(f"🚀 TripoSR API démarrée sur http://localhost:{port}")
    print("📡 Endpoints:")
    print("   POST /api/text-to-3d-triposr - Génère un modèle 3D depuis un prompt")
    print("   GET  /api/health - Vérifie l'état de l'API")
    app.run(host='0.0.0.0', port=port, debug=True)
