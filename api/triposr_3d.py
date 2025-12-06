"""API TripoSR - Image vers 3D"""
from flask import Blueprint, jsonify, request
import requests
import logging
from config import Config

triposr_routes = Blueprint('triposr', __name__)
logger = logging.getLogger(__name__)

@triposr_routes.route('/generate', methods=['POST'])
def generate_3d():
    """Génère un modèle 3D depuis une image"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'Prompt required'}), 400
        
        # Appel API TripoSR
        try:
            response = requests.post(
                f'{Config.TRIPOSR_API_URL}/api/generate',
                json={'prompt': prompt},
                timeout=60
            )
            
            if response.ok:
                return jsonify(response.json())
            else:
                return jsonify({'error': 'TripoSR API error'}), 500
                
        except requests.exceptions.RequestException:
            logger.warning('TripoSR offline, mode simulation')
            return jsonify({
                'success': True,
                'model_url': '/static/assets/models/default.obj',
                'message': 'Mode simulation (TripoSR offline)'
            })
            
    except Exception as e:
        logger.error(f'Error in TripoSR: {e}')
        return jsonify({'error': str(e)}), 500
