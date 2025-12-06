"""API Meshy - Génération 3D avancée"""
from flask import Blueprint, jsonify, request
import requests
import logging
from config import Config

meshy_routes = Blueprint('meshy', __name__)
logger = logging.getLogger(__name__)

@meshy_routes.route('/generate', methods=['POST'])
def generate_3d():
    """Génère un modèle 3D photoréaliste"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'Prompt required'}), 400
        
        # Appel API Meshy
        try:
            response = requests.post(
                f'{Config.MESHY_API_URL}/api/text-to-3d-meshy',
                json={'prompt': prompt},
                timeout=120
            )
            
            if response.ok:
                return jsonify(response.json())
            else:
                return jsonify({'error': 'Meshy API error'}), 500
                
        except requests.exceptions.RequestException:
            logger.warning('Meshy offline, mode simulation')
            return jsonify({
                'success': True,
                'model_url': '/static/assets/models/default.glb',
                'message': 'Mode simulation (Meshy offline)'
            })
            
    except Exception as e:
        logger.error(f'Error in Meshy: {e}')
        return jsonify({'error': str(e)}), 500
