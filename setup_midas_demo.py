#!/usr/bin/env python3
"""
Script de démo MiDaS - Utilise les 11 images du Château de Sceaux
Reconstruction 3D par photogrammétrie multi-vues
"""

import os
from pathlib import Path
import time
import sys

# Répertoire des images de test (Château de Sceaux)
TEST_IMAGES_DIR = Path("/home/belikan/Isol/Meshy/static/assets/test_images")

def get_test_photos():
    """Récupère les 11 photos du château"""
    print("\n📸 Récupération des photos du Château de Sceaux...")
    
    photo_paths = sorted(TEST_IMAGES_DIR.glob("image_*.jpg"))
    
    if not photo_paths:
        print("   ❌ Aucune image trouvée!")
        return []
    
    print(f"   ✅ {len(photo_paths)} photos trouvées")
    for i, path in enumerate(photo_paths, 1):
        size_mb = path.stat().st_size / (1024*1024)
        print(f"      [{i:2d}] {path.name} ({size_mb:.1f} MB)")
    
    return [str(p) for p in photo_paths]

def save_default_mesh_path(mesh_path):
    """Sauvegarde le chemin du mesh pour le frontend"""
    config_file = Path("/home/belikan/Isol/Meshy/demo_config.json")
    
    import json
    config = {
        "default_mesh": mesh_path,
        "demo_mode": True,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    config_file.write_text(json.dumps(config, indent=2))
    print(f"\n💾 Configuration sauvegardée: {config_file}")

def main():
    print("="*60)
    print("🎬 DÉMO MIDAS - CHÂTEAU DE SCEAUX (11 PHOTOS)")
    print("="*60)
    print("📚 Dataset: OpenMVG Sceaux Castle")
    print("🏰 Sujet: Architecture (Château)")
    print("📸 Angles: Multi-vues circulaires")
    print("="*60)
    
    # 1. Récupère les photos du château
    photo_paths = get_test_photos()
    
    if not photo_paths:
        print("\n❌ Aucune photo disponible")
        print("   Vérifiez: /home/belikan/Isol/Meshy/static/assets/test_images/")
        return
    
    # 2. Reconstruction batch directe
    print("\n🔮 Reconstruction 3D en mode batch...")
    mesh_path = reconstruct_batch_direct(photo_paths)
    
    if mesh_path:
        # 3. Sauvegarde pour le frontend
        save_default_mesh_path(mesh_path)
        
        print("\n" + "="*60)
        print("✅ DÉMO CHÂTEAU PRÊTE!")
        print("="*60)
        print(f"📦 Mesh 3D: {mesh_path}")
        print(f"🏰 Sujet: Château de Sceaux (architecture)")
        print(f"📸 Source: {len(photo_paths)} photos multi-vues")
        print("")
        print("🌐 Ouvrez: http://localhost:11080/kibalone-studio.html")
        print("   Le château 3D sera chargé automatiquement!")
        print("="*60)
    else:
        print("\n❌ Échec de la génération du mesh")

def reconstruct_batch_direct(photo_paths):
    """Reconstruction batch directe via MiDaS client"""
    print(f"   📸 {len(photo_paths)} photos → Mesh 3D...")
    
    output_path = "/home/belikan/Isol/Meshy/outputs/midas_demo.obj"
    
    try:
        # Import du client MiDaS
        import sys
        sys.path.insert(0, '/home/belikan/Isol/isol-framework')
        from midas_client import MiDaSClient
        
        client = MiDaSClient()
        
        # Init
        print("   ⚙️  Initialisation MiDaS...")
        result = client.initialize()
        if not result.get('success'):
            print(f"   ❌ Init failed: {result}")
            return None
        
        # Reconstruction batch
        print("   🔄 Reconstruction en cours...")
        result = client.reconstruct_batch(
            image_paths=photo_paths,
            preset="photogrammetry",
            output_path=output_path
        )
        
        if result.get('success'):
            mesh_path = result.get('output_path', output_path)
            print(f"   ✅ Mesh généré: {mesh_path}")
            print(f"   📊 Vertices: {result.get('vertices', 0)}")
            print(f"   📊 Faces: {result.get('triangles', 0)}")
            return mesh_path
        else:
            print(f"   ❌ Erreur: {result.get('error', 'Unknown')}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
