"""
Serveur Flask principal - Kibalone Studio
Architecture propre avec séparation des responsabilités
"""
from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS
import logging
from config import Config

# Initialisation
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.config.from_object(Config)
CORS(app)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{Config.LOGS_DIR}/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialisation
Config.init_app()

# Import des routes API
from api.routes import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    """Page d'accueil - Redirige vers le studio"""
    return send_from_directory('.', 'kibalone-studio.html')

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'kibalone-studio',
        'version': '2.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal error: {error}')
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info('=' * 60)
    logger.info('🚀 Kibalone Studio v2.0')
    logger.info('=' * 60)
    logger.info(f'📡 Serveur: http://{Config.HOST}:{Config.PORT}')
    logger.info(f'📁 Static: {Config.STATIC_DIR}')
    logger.info(f'📝 Logs: {Config.LOGS_DIR}')
    logger.info('=' * 60)
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        threaded=True
    )
