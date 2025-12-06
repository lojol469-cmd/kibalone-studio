"""
Configuration centralisée pour Kibalone Studio
"""
import os

class Config:
    # Serveur
    HOST = '0.0.0.0'
    PORT = 8080
    DEBUG = False
    
    # Chemins
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    UPLOAD_FOLDER = '/tmp/kibalone_uploads'
    
    # APIs Services
    KIBALI_API_URL = 'http://localhost:5000'
    TRIPOSR_API_URL = 'http://localhost:5001'
    MIDAS_API_URL = 'http://localhost:5002'
    MESHY_API_URL = 'http://localhost:5003'
    
    # Isol Framework
    ISOL_MIDAS_SERVICE = '/home/belikan/Isol/isol-framework/midas_service.py'
    MIDAS_ISOL_PYTHON = '/home/belikan/miniconda3/envs/midas_isol/bin/python'
    
    # Limites
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    MAX_IMAGES_PER_RECONSTRUCTION = 20
    
    # CORS
    CORS_ORIGINS = '*'
    
    @staticmethod
    def init_app():
        """Initialise les dossiers nécessaires"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
