"""
Routes API centralisées
"""
from flask import Blueprint, jsonify, request
import logging

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Import des modules API
from .kibali_chat import chat_routes
from .midas_reconstruction import midas_routes
from .triposr_3d import triposr_routes
from .meshy_generation import meshy_routes

# Enregistrement des sous-routes
api_bp.register_blueprint(chat_routes, url_prefix='/chat')
api_bp.register_blueprint(midas_routes, url_prefix='/midas')
api_bp.register_blueprint(triposr_routes, url_prefix='/triposr')
api_bp.register_blueprint(meshy_routes, url_prefix='/meshy')

@api_bp.route('/health')
def api_health():
    """Health check de l'API"""
    return jsonify({
        'status': 'healthy',
        'apis': {
            'chat': '/api/chat',
            'midas': '/api/midas',
            'triposr': '/api/triposr',
            'meshy': '/api/meshy'
        }
    })
