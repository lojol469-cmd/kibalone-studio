#!/usr/bin/env python3
"""
🎨 API Réaliste avec Meshy.ai
==============================
Utilise l'API Meshy pour générer des modèles 3D photoréalistes
sans avoir besoin de TripoSR local
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import time
import os

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Keys (à configurer)
MESHY_API_KEY = os.getenv('MESHY_API_KEY', '')
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN', '')

@app.route('/api/text-to-3d-meshy', methods=['POST'])
def text_to_3d_meshy():
    """Génère un modèle 3D via Meshy.ai"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'No prompt'}), 400
        
        if not MESHY_API_KEY:
            logger.warning("⚠️ MESHY_API_KEY non configurée")
            return jsonify({
                'success': False,
                'error': 'MESHY_API_KEY required',
                'message': 'Configure MESHY_API_KEY pour utiliser la génération photoréaliste',
                'fallback': 'use_procedural'
            }), 503
        
        logger.info(f"📝 Génération Meshy: {prompt}")
        
        # Appel API Meshy
        response = requests.post(
            'https://api.meshy.ai/v2/text-to-3d',
            headers={
                'Authorization': f'Bearer {MESHY_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'prompt': prompt,
                'art_style': 'realistic',
                'negative_prompt': 'low quality, blurry, distorted'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get('result')
            
            logger.info(f"✅ Tâche créée: {task_id}")
            
            # Poll jusqu'à completion
            model_url = wait_for_meshy_completion(task_id)
            
            if model_url:
                return jsonify({
                    'success': True,
                    'model_url': model_url,
                    'task_id': task_id,
                    'method': 'meshy-ai'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Timeout waiting for model'
                }), 500
        else:
            logger.error(f"❌ Erreur Meshy: {response.status_code}")
            return jsonify({
                'success': False,
                'error': f'Meshy API error: {response.status_code}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def wait_for_meshy_completion(task_id, max_wait=300):
    """Attend la completion du modèle Meshy"""
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(
                f'https://api.meshy.ai/v2/text-to-3d/{task_id}',
                headers={'Authorization': f'Bearer {MESHY_API_KEY}'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                
                logger.info(f"📊 Status: {status}")
                
                if status == 'SUCCEEDED':
                    return result.get('model_urls', {}).get('glb')
                elif status == 'FAILED':
                    logger.error("❌ Génération échouée")
                    return None
                
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"❌ Erreur polling: {e}")
            time.sleep(5)
    
    logger.warning("⏱️ Timeout")
    return None

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'meshy-ai-integration',
        'meshy_configured': bool(MESHY_API_KEY),
        'hf_configured': bool(HUGGINGFACE_TOKEN)
    })

if __name__ == '__main__':
    logger.info("🚀 API Meshy.ai démarrée")
    logger.info("📡 http://localhost:11003")
    
    if not MESHY_API_KEY:
        logger.warning("⚠️ MESHY_API_KEY non configurée")
        logger.info("💡 Obtenez une clé sur https://www.meshy.ai/")
        logger.info("💡 export MESHY_API_KEY=your_key")
    
    port = int(os.environ.get('PORT', 11003))
    app.run(host='0.0.0.0', port=port, debug=False)
