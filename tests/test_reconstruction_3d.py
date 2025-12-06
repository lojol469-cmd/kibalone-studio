#!/usr/bin/env python3
"""
Script de test pour la reconstruction 3D multi-vues dans Kibalone Studio
"""
import requests
import time
from pathlib import Path
import sys

BASE_URL = "http://localhost:5002"

def check_api_health():
    """Vérifie que l'API est accessible"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.ok:
            data = response.json()
            print(f"✅ API MiDaS Multi-View: {data['status']}")
            print(f"   Device: {data['device']}")
            print(f"   Open3D: {data['open3d']}")
            return True
    except Exception as e:
        print(f"❌ API non disponible: {e}")
        print("\nLancez l'API avec:")
        print("   cd /home/belikan/Isol/Kibalone-Studio")
        print("   ./start_kibalone_full.sh")
        return False

def test_reconstruction(image_dir):
    """Test de reconstruction avec des images"""
    image_path = Path(image_dir)
    
    if not image_path.exists():
        print(f"❌ Dossier non trouvé: {image_dir}")
        return False
    
    images = list(image_path.glob("*.jpg")) + list(image_path.glob("*.png"))
    
    if len(images) < 3:
        print(f"❌ Pas assez d'images dans {image_dir}")
        print("   Minimum: 3 images, Recommandé: 8-12 images")
        return False
    
    print(f"\n📸 Trouvé {len(images)} images:")
    for img in images:
        print(f"   • {img.name}")
    
    try:
        # 1. Créer session
        print("\n🔧 Création de la session...")
        response = requests.post(f"{BASE_URL}/api/create_session", json={
            "voxel_size": 0.005,
            "use_tsdf": True,
            "max_correspondence": 0.05
        })
        
        session_data = response.json()
        session_id = session_data['session_id']
        print(f"✅ Session: {session_id[:8]}...")
        
        # 2. Upload images
        print("\n📤 Upload et fusion des images...")
        for i, image_file in enumerate(images, 1):
            print(f"\n📸 Image {i}/{len(images)}: {image_file.name}")
            
            with open(image_file, 'rb') as f:
                files = {'file': f}
                data = {'session_id': session_id}
                
                response = requests.post(
                    f"{BASE_URL}/api/upload_scan",
                    files=files,
                    data=data
                )
                
                if response.ok:
                    result = response.json()
                    print(f"   ✅ Points: {result['total_points']:,}")
                    print(f"   📊 Fitness: {result['fitness']:.3f}")
                    print(f"   🔢 Scans: {result['total_scans']}")
                else:
                    print(f"   ❌ Erreur: {response.text}")
            
            time.sleep(0.5)
        
        # 3. Statistiques
        print("\n📊 Statistiques finales...")
        response = requests.get(f"{BASE_URL}/api/session_stats/{session_id}")
        stats = response.json()
        
        print(f"   Total points: {stats['total_points']:,}")
        print(f"   Scans réussis: {stats['successful_registrations']}/{stats['total_scans']}")
        print(f"   Taux de réussite: {stats['success_rate']*100:.1f}%")
        print(f"   Voxel size: {stats['voxel_size']}")
        
        # 4. Export nuage
        print("\n💾 Export du nuage de points...")
        response = requests.get(f"{BASE_URL}/api/get_fused_cloud/{session_id}")
        
        if response.ok:
            output_file = f"test_reconstruction_{int(time.time())}.ply"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"✅ Sauvegardé: {output_file}")
        
        # 5. Générer mesh
        print("\n🎨 Génération du mesh...")
        response = requests.post(
            f"{BASE_URL}/api/get_mesh/{session_id}",
            json={"method": "poisson", "poisson_depth": 9}
        )
        
        if response.ok:
            mesh_file = f"test_mesh_{int(time.time())}.ply"
            with open(mesh_file, 'wb') as f:
                f.write(response.content)
            print(f"✅ Sauvegardé: {mesh_file}")
        
        # 6. Nettoyage
        print("\n🗑️ Nettoyage...")
        requests.delete(f"{BASE_URL}/api/delete_session/{session_id}")
        
        print("\n🎉 Test terminé avec succès!")
        print("\nVisualisez les résultats avec:")
        print(f"   meshlab {output_file}")
        print(f"   meshlab {mesh_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 TEST RECONSTRUCTION 3D MULTI-VUES")
    print("=" * 60)
    
    # Vérifier l'API
    if not check_api_health():
        sys.exit(1)
    
    # Dossier de test
    test_dir = Path("/home/belikan/Isol/Kibalone-Studio/test_images")
    
    if test_dir.exists():
        print(f"\n📂 Utilisation du dossier: {test_dir}")
        test_reconstruction(test_dir)
    else:
        print(f"\n📂 Créez le dossier: {test_dir}")
        print("   Et ajoutez 8-12 photos de votre objet sous différents angles")
        test_dir.mkdir(exist_ok=True)
        print(f"✅ Dossier créé: {test_dir}")

if __name__ == "__main__":
    main()
