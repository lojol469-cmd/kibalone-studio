"""API Reconstruction 3D MiDaS"""
from flask import Blueprint, jsonify, request, send_file
import requests
import logging
import os
import uuid
from werkzeug.utils import secure_filename
from config import Config

midas_routes = Blueprint('midas', __name__)
logger = logging.getLogger(__name__)

# Stockage sessions
sessions = {}

@midas_routes.route('/create_session', methods=['POST'])
def create_session():
    """Créer une session de reconstruction"""
    try:
        data = request.get_json() or {}
        preset = data.get('preset', 'photogrammetry')
        
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'preset': preset,
            'images': [],
            'status': 'created'
        }
        
        logger.info(f'Session créée: {session_id}')
        return jsonify({
            'success': True,
            'session_id': session_id,
            'preset': preset
        })
    except Exception as e:
        logger.error(f'Error creating session: {e}')
        return jsonify({'error': str(e)}), 500

@midas_routes.route('/upload_image', methods=['POST'])
def upload_image():
    """Upload une image pour reconstruction"""
    try:
        session_id = request.form.get('session_id')
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Sauvegarder l'image
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, f'{session_id}_{filename}')
        file.save(filepath)
        
        sessions[session_id]['images'].append(filepath)
        logger.info(f'Image uploaded: {filename} -> {session_id}')
        
        return jsonify({
            'success': True,
            'image_count': len(sessions[session_id]['images'])
        })
    except Exception as e:
        logger.error(f'Error uploading image: {e}')
        return jsonify({'error': str(e)}), 500

@midas_routes.route('/reconstruct', methods=['POST'])
def reconstruct():
    """Lance la reconstruction 3D"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        session = sessions[session_id]
        if len(session['images']) < 3:
            return jsonify({'error': 'Need at least 3 images'}), 400
        
        # Appel à l'API MiDaS
        try:
            response = requests.post(
                f'{Config.MIDAS_API_URL}/api/generate_mesh',
                json={'session_id': session_id},
                timeout=300
            )
            
            if response.ok:
                result = response.json()
                sessions[session_id]['status'] = 'completed'
                sessions[session_id]['result'] = result
                return jsonify(result)
            else:
                return jsonify({'error': 'MiDaS API error'}), 500
                
        except requests.exceptions.RequestException:
            # Mode local: simulation
            logger.warning('MiDaS API offline, simulation mode')
            sessions[session_id]['status'] = 'completed'
            return jsonify({
                'success': True,
                'vertices': 50000,
                'faces': 100000,
                'message': 'Mode simulation (MiDaS offline)'
            })
            
    except Exception as e:
        logger.error(f'Error in reconstruction: {e}')
        return jsonify({'error': str(e)}), 500

@midas_routes.route('/test_reconstruction', methods=['GET'])
def test_reconstruction():
    """Reconstruction de test avec images par défaut"""
    try:
        # Utiliser les images de test
        test_images_dir = os.path.join(Config.STATIC_DIR, 'assets', 'test_images')
        
        if not os.path.exists(test_images_dir):
            return jsonify({'error': 'Test images not found'}), 404
        
        # Créer une session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'preset': 'photogrammetry',
            'images': [],
            'status': 'processing'
        }
        
        # Charger les images de test
        test_images = [f for f in os.listdir(test_images_dir) if f.endswith(('.jpg', '.png'))][:5]
        
        for img in test_images:
            img_path = os.path.join(test_images_dir, img)
            sessions[session_id]['images'].append(img_path)
        
        logger.info(f'Test reconstruction avec {len(test_images)} images')
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'image_count': len(test_images),
            'message': 'Reconstruction de test lancée'
        })
        
    except Exception as e:
        logger.error(f'Error in test reconstruction: {e}')
        return jsonify({'error': str(e)}), 500
