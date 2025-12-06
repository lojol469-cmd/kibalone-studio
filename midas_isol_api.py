#!/usr/bin/env python3
"""
MiDaS Isol API pour Kibalone Studio
Utilise le service MiDaS isolé via l'architecture Isol
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sys
import os
import logging
import time
import tempfile
from pathlib import Path

# Ajouter isol-framework au path
sys.path.insert(0, '/home/belikan/Isol/isol-framework')
from midas_client import MiDaSClient

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Client MiDaS
midas_client = MiDaSClient()

# Stockage des sessions actives
sessions = {}

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "midas-isol-api"})

@app.route('/api/create_session', methods=['POST'])
def create_session():
    """
    Créer une nouvelle session de reconstruction multi-vues
    
    Body (JSON):
        preset: str - Nom du preset (photogrammetry, small, medium, large, room, building)
    
    Returns:
        session_id: str - Identifiant unique de la session
    """
    try:
        data = request.get_json() or {}
        preset = data.get('preset', 'photogrammetry')
        
        logger.info(f"📸 Création session avec preset: {preset}")
        
        # Créer session via le service isolé
        result = midas_client.create_session(preset=preset)
        
        if 'error' in result:
            return jsonify({"error": result['error']}), 500
        
        session_id = result['session_id']
        
        # Stocker localement les métadonnées
        sessions[session_id] = {
            'created_at': time.time(),
            'preset': preset,
            'images': [],
            'total_scans': 0
        }
        
        logger.info(f"✅ Session créée: {session_id}")
        
        return jsonify({
            "session_id": session_id,
            "preset": preset,
            "status": "created"
        })
    
    except Exception as e:
        logger.error(f"Erreur create_session: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload_scan', methods=['POST'])
def upload_scan():
    """
    Upload une image et l'ajoute à la session de reconstruction
    
    Form Data:
        file: Image file
        session_id: str - ID de la session
    
    Returns:
        total_points: int - Nombre total de points dans le nuage fusionné
        fitness: float - Score de confiance de l'alignement
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400
        
        file = request.files['file']
        session_id = request.form.get('session_id')
        
        if not session_id or session_id not in sessions:
            return jsonify({"error": "Session invalide"}), 400
        
        # Sauvegarder temporairement l'image
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        logger.info(f"📸 Ajout scan à {session_id}: {file.filename}")
        
        # Ajouter le scan via le service isolé
        result = midas_client.add_scan(session_id, temp_path)
        
        # Nettoyer
        os.remove(temp_path)
        os.rmdir(temp_dir)
        
        if 'error' in result:
            return jsonify({"error": result['error']}), 500
        
        # Mettre à jour les métadonnées locales
        sessions[session_id]['images'].append(file.filename)
        sessions[session_id]['total_scans'] = result.get('total_scans', 0)
        
        logger.info(f"✅ Scan ajouté: {result.get('total_points', 0)} points, fitness={result.get('fitness', 0):.3f}")
        
        return jsonify({
            "session_id": session_id,
            "total_points": result.get('total_points', 0),
            "total_scans": result.get('total_scans', 0),
            "fitness": result.get('fitness', 1.0),
            "processing_time": result.get('processing_time', 0),
            "status": "scan_added"
        })
    
    except Exception as e:
        logger.error(f"Erreur upload_scan: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate_mesh', methods=['POST'])
def generate_mesh():
    """
    Génère le mesh 3D final à partir de la session
    
    Body (JSON):
        session_id: str - ID de la session
        output_path: str (optional) - Chemin de sortie personnalisé
    
    Returns:
        mesh_path: str - Chemin du fichier PLY généré
    """
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        
        if not session_id or session_id not in sessions:
            return jsonify({"error": "Session invalide"}), 400
        
        output_path = data.get('output_path', f'/tmp/mesh_{session_id}.ply')
        
        logger.info(f"🎨 Génération du mesh pour {session_id}")
        
        # Générer le mesh via le service isolé
        result = midas_client.generate_mesh(session_id, output_path)
        
        if 'error' in result:
            return jsonify({"error": result['error']}), 500
        
        mesh_path = result.get('mesh_path', output_path)
        
        logger.info(f"✅ Mesh généré: {mesh_path}")
        
        return jsonify({
            "session_id": session_id,
            "mesh_path": mesh_path,
            "vertices": result.get('vertices', 0),
            "faces": result.get('faces', 0),
            "status": "mesh_generated"
        })
    
    except Exception as e:
        logger.error(f"Erreur generate_mesh: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/download_mesh/<session_id>', methods=['GET'])
def download_mesh(session_id):
    """
    Télécharge le mesh PLY généré
    """
    try:
        if session_id not in sessions:
            return jsonify({"error": "Session invalide"}), 404
        
        mesh_path = f'/tmp/mesh_{session_id}.ply'
        
        if not os.path.exists(mesh_path):
            return jsonify({"error": "Mesh non généré"}), 404
        
        return send_file(
            mesh_path,
            as_attachment=True,
            download_name=f'reconstruction_{session_id}.ply',
            mimetype='application/octet-stream'
        )
    
    except Exception as e:
        logger.error(f"Erreur download_mesh: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete_session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    Supprime une session de reconstruction
    """
    try:
        if session_id in sessions:
            del sessions[session_id]
            logger.info(f"🗑️ Session supprimée: {session_id}")
        
        # Nettoyer le mesh temporaire
        mesh_path = f'/tmp/mesh_{session_id}.ply'
        if os.path.exists(mesh_path):
            os.remove(mesh_path)
        
        return jsonify({"status": "deleted"})
    
    except Exception as e:
        logger.error(f"Erreur delete_session: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """
    Liste toutes les sessions actives
    """
    return jsonify({
        "sessions": [
            {
                "session_id": sid,
                "preset": meta['preset'],
                "total_scans": meta['total_scans'],
                "images": len(meta['images']),
                "created_at": meta['created_at']
            }
            for sid, meta in sessions.items()
        ]
    })

@app.route('/api/test_reconstruction', methods=['GET'])
def serve_test_reconstruction():
    """
    Sert le fichier de reconstruction test
    """
    try:
        test_file = Path('/tmp/chateau_direct.ply')
        
        if not test_file.exists():
            return jsonify({"error": "Test reconstruction not found"}), 404
        
        return send_file(
            test_file,
            mimetype='application/octet-stream',
            as_attachment=False,
            download_name='chateau_test.ply'
        )
    
    except Exception as e:
        logger.error(f"Erreur serve_test_reconstruction: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 MiDaS Isol API - Kibalone Studio")
    logger.info("=" * 60)
    logger.info("📡 API disponible sur: http://localhost:11002")
    logger.info("🔗 Endpoints:")
    logger.info("   POST /api/create_session - Créer une session")
    logger.info("   POST /api/upload_scan - Ajouter une image")
    logger.info("   POST /api/generate_mesh - Générer le mesh 3D")
    logger.info("   GET  /api/download_mesh/<id> - Télécharger le mesh")
    logger.info("   DEL  /api/delete_session/<id> - Supprimer une session")
    logger.info("   GET  /api/test_reconstruction - Fichier test château")
    logger.info("=" * 60)
    
    port = int(os.environ.get('PORT', 11002))
    app.run(host='0.0.0.0', port=port, debug=False)

