#!/usr/bin/env python3
"""
MiDaS Multi-View 3D Reconstruction API pour Kibalone Studio
Reconstruction 3D complète à partir de plusieurs images sous différents angles
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sys
import os
import io
import logging
import numpy as np
import torch
import cv2
from PIL import Image
import uuid
import time

# Ajouter MidasApi au path
sys.path.insert(0, '/home/belikan/Isol/MidasApi')

# Importer les modules de fusion
try:
    from point_cloud_fusion import (
        MultiViewFusion,
        numpy_to_o3d_cloud,
        o3d_cloud_to_numpy
    )
    from depth_enhancement import DepthEnhancer, TemporalDepthSmoothing
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Open3D non disponible: {e}")
    OPEN3D_AVAILABLE = False

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger MiDaS
logger.info("🔧 Chargement du modèle MiDaS...")
try:
    model_type = "MiDaS_small"
    midas = torch.hub.load("intel-isl/MiDaS", model_type, pretrained=True, trust_repo=True)
    midas.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    midas.to(device)
    midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
    transform = midas_transforms.small_transform
    logger.info(f"✅ MiDaS chargé (device: {device})")
except Exception as e:
    logger.error(f"❌ Erreur chargement MiDaS: {e}")
    raise

# Stockage des sessions
sessions = {}
depth_enhancers = {}
temporal_smoothers = {}

def create_ply_content(positions, colors=None):
    """Crée le contenu d'un fichier PLY"""
    vertex_count = len(positions)
    header = [
        "ply",
        "format ascii 1.0",
        f"element vertex {vertex_count}",
        "property float x",
        "property float y",
        "property float z",
    ]
    if colors is not None:
        header.extend([
            "property uchar red",
            "property uchar green",
            "property uchar blue",
        ])
    header.append("end_header")

    lines = header[:]
    for i in range(vertex_count):
        pos = positions[i]
        if colors is not None:
            col = colors[i]
            line = f"{pos[0]} {pos[1]} {pos[2]} {int(col[0] * 255)} {int(col[1] * 255)} {int(col[2] * 255)}"
        else:
            line = f"{pos[0]} {pos[1]} {pos[2]}"
        lines.append(line)
    
    return "\n".join(lines)

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'service': 'midas-multiview-3d',
        'open3d': OPEN3D_AVAILABLE,
        'device': str(device)
    })

@app.route('/api/create_session', methods=['POST'])
def create_session():
    """Crée une nouvelle session de reconstruction 3D"""
    try:
        if not OPEN3D_AVAILABLE:
            return jsonify({
                'error': 'Open3D non disponible. Installez avec: pip install open3d>=0.17.0'
            }), 500
        
        data = request.json or {}
        session_id = str(uuid.uuid4())
        
        voxel_size = data.get('voxel_size', 0.005)
        use_tsdf = data.get('use_tsdf', True)
        max_correspondence = data.get('max_correspondence', 0.05)
        
        # Créer le système de fusion
        sessions[session_id] = MultiViewFusion(
            voxel_size=voxel_size,
            max_correspondence_distance=max_correspondence,
            use_tsdf=use_tsdf
        )
        
        depth_enhancers[session_id] = DepthEnhancer(
            bilateral_d=9,
            bilateral_sigma_color=75,
            bilateral_sigma_space=75
        )
        
        temporal_smoothers[session_id] = TemporalDepthSmoothing(
            window_size=5,
            alpha=0.3
        )
        
        logger.info(f"✅ Session créée: {session_id}")
        
        return jsonify({
            'session_id': session_id,
            'config': {
                'voxel_size': voxel_size,
                'use_tsdf': use_tsdf,
                'max_correspondence': max_correspondence
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur create_session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload_scan', methods=['POST'])
def upload_scan():
    """Upload une image et fusionne dans la session"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier'}), 400
        
        session_id = request.form.get('session_id')
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Session invalide'}), 400
        
        file = request.files['file']
        image = Image.open(file).convert('RGB')
        image = image.resize((320, 240), Image.LANCZOS)
        image_np = np.array(image)
        
        # Estimation de profondeur avec MiDaS
        img_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        input_batch = transform(img_bgr).to(device)
        
        with torch.no_grad():
            prediction = midas(input_batch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=(240, 320),
                mode="bicubic",
                align_corners=False,
            ).squeeze().cpu().numpy()
        
        depth = prediction
        
        # Enhancement de profondeur
        enhancer = depth_enhancers[session_id]
        smoother = temporal_smoothers[session_id]
        
        depth = smoother.add_frame(depth)
        depth, confidence_map = enhancer.enhance_depth(depth, rgb_image=image_np)
        
        # Conversion en nuage de points
        positions, colors = enhancer.depth_to_points_3d(
            depth,
            rgb_image=image_np,
            focal_length=525.0,
            scale_factor=1.0
        )
        
        # Fusion multi-vues
        fusion = sessions[session_id]
        cloud = numpy_to_o3d_cloud(positions, colors)
        stats = fusion.add_scan(cloud, frame_id=f"scan_{fusion.total_scans}")
        
        # Récupérer le nuage fusionné
        fused_cloud = fusion.get_fused_cloud(remove_outliers=True, compute_normals=False)
        fused_positions, fused_colors = o3d_cloud_to_numpy(fused_cloud)
        
        logger.info(
            f"Scan ajouté: session={session_id}, "
            f"points={len(fused_positions)}, "
            f"fitness={stats['fitness']:.3f}, "
            f"scans={stats['total_scans']}"
        )
        
        return jsonify({
            'success': True,
            'total_points': len(fused_positions),
            'total_scans': stats['total_scans'],
            'fitness': stats['fitness'],
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Erreur upload_scan: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_fused_cloud/<session_id>', methods=['GET'])
def get_fused_cloud(session_id):
    """Récupère le nuage fusionné"""
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Session non trouvée'}), 404
        
        fusion = sessions[session_id]
        cloud = fusion.get_fused_cloud(remove_outliers=True, compute_normals=False)
        positions, colors = o3d_cloud_to_numpy(cloud)
        
        # Créer le PLY
        ply_content = create_ply_content(positions, colors)
        ply_bytes = io.BytesIO(ply_content.encode('ascii'))
        
        return send_file(
            ply_bytes,
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=f'fused_cloud_{session_id[:8]}.ply'
        )
        
    except Exception as e:
        logger.error(f"Erreur get_fused_cloud: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_mesh/<session_id>', methods=['POST'])
def get_mesh(session_id):
    """Génère un mesh 3D"""
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Session non trouvée'}), 404
        
        data = request.json or {}
        method = data.get('method', 'poisson')
        poisson_depth = data.get('poisson_depth', 9)
        
        fusion = sessions[session_id]
        
        logger.info(f"Génération mesh ({method}, depth={poisson_depth})...")
        mesh = fusion.get_mesh(method=method, poisson_depth=poisson_depth)
        
        # Sauvegarder temporairement
        temp_path = f'/tmp/mesh_{session_id}.ply'
        o3d.io.write_triangle_mesh(temp_path, mesh)
        
        logger.info(f"Mesh généré: {len(mesh.vertices)} vertices, {len(mesh.triangles)} triangles")
        
        return send_file(
            temp_path,
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=f'mesh_{session_id[:8]}.ply'
        )
        
    except Exception as e:
        logger.error(f"Erreur get_mesh: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session_stats/<session_id>', methods=['GET'])
def session_stats(session_id):
    """Statistiques de session"""
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Session non trouvée'}), 404
        
        fusion = sessions[session_id]
        
        return jsonify({
            'session_id': session_id,
            'total_scans': fusion.total_scans,
            'successful_registrations': fusion.successful_registrations,
            'success_rate': fusion.successful_registrations / fusion.total_scans if fusion.total_scans > 0 else 0,
            'total_points': len(fusion.global_cloud.points),
            'voxel_size': fusion.voxel_size,
            'use_tsdf': fusion.use_tsdf
        })
        
    except Exception as e:
        logger.error(f"Erreur session_stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Supprime une session"""
    try:
        if session_id in sessions:
            del sessions[session_id]
            del depth_enhancers[session_id]
            del temporal_smoothers[session_id]
            logger.info(f"Session supprimée: {session_id}")
            return jsonify({'success': True})
        return jsonify({'error': 'Session non trouvée'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    logger.info(f"🚀 Démarrage MiDaS Multi-View API sur port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
