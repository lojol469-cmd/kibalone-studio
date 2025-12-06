#!/usr/bin/env python3
"""
Intégration Meshy.ai API pour Kibalone Studio
https://docs.meshy.ai/
"""

import os
import requests
import time
import json
from pathlib import Path

class MeshyAIClient:
    """Client pour Meshy.ai API - génération text-to-3D et image-to-3D"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("MESHY_API_KEY")
        self.base_url = "https://api.meshy.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.api_key:
            print("⚠️ MESHY_API_KEY non définie !")
            print("   Obtiens une clé sur: https://www.meshy.ai")
    
    def text_to_3d(self, prompt, style="realistic", negative_prompt="", art_style="realistic"):
        """
        Génère un modèle 3D depuis un prompt texte
        
        Args:
            prompt: Description du modèle ("a futuristic robot")
            style: realistic | cartoon | sculpture | voxel
            negative_prompt: Ce qu'on ne veut PAS
            art_style: realistic | cartoon | anime | etc.
        
        Returns:
            dict: {'task_id': '...', 'status': 'pending'}
        """
        print(f"🎨 [MESHY] Text-to-3D: {prompt}")
        
        if not self.api_key:
            return {'error': 'API key manquante'}
        
        endpoint = f"{self.base_url}/v2/text-to-3d"
        
        payload = {
            "mode": "preview",  # ou "refine" pour haute qualité
            "prompt": prompt,
            "art_style": art_style,
            "negative_prompt": negative_prompt
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ [MESHY] Tâche créée: {result.get('result')}")
            
            return result
            
        except Exception as e:
            print(f"❌ [MESHY] Erreur: {e}")
            return {'error': str(e)}
    
    def image_to_3d(self, image_url, enable_pbr=True):
        """
        Génère un modèle 3D depuis une image
        
        Args:
            image_url: URL publique de l'image
            enable_pbr: Générer textures PBR (materials)
        
        Returns:
            dict: {'task_id': '...', 'status': 'pending'}
        """
        print(f"🖼️ [MESHY] Image-to-3D: {image_url}")
        
        if not self.api_key:
            return {'error': 'API key manquante'}
        
        endpoint = f"{self.base_url}/v2/image-to-3d"
        
        payload = {
            "image_url": image_url,
            "enable_pbr": enable_pbr
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ [MESHY] Tâche créée: {result.get('result')}")
            
            return result
            
        except Exception as e:
            print(f"❌ [MESHY] Erreur: {e}")
            return {'error': str(e)}
    
    def get_task_status(self, task_id):
        """
        Vérifie le statut d'une tâche
        
        Returns:
            dict: {
                'status': 'PENDING' | 'IN_PROGRESS' | 'SUCCEEDED' | 'FAILED',
                'progress': 0-100,
                'model_urls': {...} si terminé
            }
        """
        endpoint = f"{self.base_url}/v2/text-to-3d/{task_id}"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ [MESHY] Erreur statut: {e}")
            return {'error': str(e)}
    
    def wait_for_completion(self, task_id, timeout=300):
        """
        Attend que la génération soit terminée
        
        Args:
            task_id: ID de la tâche
            timeout: Timeout en secondes (défaut 5 min)
        
        Returns:
            dict: Résultat final avec URLs des modèles
        """
        print(f"⏳ [MESHY] Attente génération (task: {task_id})...")
        
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            result = self.get_task_status(task_id)
            
            if 'error' in result:
                return result
            
            status = result.get('status')
            progress = result.get('progress', 0)
            
            print(f"   Status: {status} - Progress: {progress}%")
            
            if status == 'SUCCEEDED':
                print(f"✅ [MESHY] Génération terminée !")
                return result
            
            elif status == 'FAILED':
                print(f"❌ [MESHY] Génération échouée")
                return result
            
            time.sleep(5)  # Vérifie toutes les 5 secondes
        
        print(f"⏱️ [MESHY] Timeout dépassé")
        return {'error': 'Timeout'}
    
    def download_model(self, model_url, output_path):
        """
        Télécharge le modèle 3D
        
        Args:
            model_url: URL du modèle (GLB, FBX, OBJ, etc.)
            output_path: Chemin de sauvegarde local
        """
        print(f"📥 [MESHY] Téléchargement: {output_path}")
        
        try:
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ [MESHY] Téléchargé: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ [MESHY] Erreur téléchargement: {e}")
            return None
    
    def text_to_3d_complete(self, prompt, output_dir="/home/belikan/Isol/Meshy/meshes"):
        """
        Pipeline complet: Prompt → Modèle 3D téléchargé
        
        Returns:
            dict: {
                'success': True,
                'glb_path': '/path/to/model.glb',
                'fbx_path': '/path/to/model.fbx',
                'task_id': '...'
            }
        """
        print(f"\n{'='*60}")
        print(f"🚀 GÉNÉRATION 3D COMPLÈTE: {prompt}")
        print(f"{'='*60}\n")
        
        # 1. Crée la tâche
        task_result = self.text_to_3d(prompt)
        
        if 'error' in task_result:
            return task_result
        
        task_id = task_result.get('result')
        
        # 2. Attend la fin
        final_result = self.wait_for_completion(task_id)
        
        if final_result.get('status') != 'SUCCEEDED':
            return {'success': False, 'error': 'Génération échouée'}
        
        # 3. Télécharge les modèles
        model_urls = final_result.get('model_urls', {})
        
        paths = {}
        
        if 'glb' in model_urls:
            glb_path = f"{output_dir}/meshy_{task_id}.glb"
            self.download_model(model_urls['glb'], glb_path)
            paths['glb_path'] = glb_path
        
        if 'fbx' in model_urls:
            fbx_path = f"{output_dir}/meshy_{task_id}.fbx"
            self.download_model(model_urls['fbx'], fbx_path)
            paths['fbx_path'] = fbx_path
        
        return {
            'success': True,
            'task_id': task_id,
            **paths
        }


# ============================================
# Test
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("🎨 TEST MESHY.AI API")
    print("="*60)
    
    # Check API key
    api_key = os.getenv("MESHY_API_KEY")
    
    if not api_key:
        print("\n⚠️ MESHY_API_KEY non définie !")
        print("\n📝 Pour utiliser Meshy.ai:")
        print("   1. Crée un compte sur: https://www.meshy.ai")
        print("   2. Obtiens une API key")
        print("   3. export MESHY_API_KEY='ta-cle-ici'")
        print("\n💡 Alternative: Utilise le générateur JSON local (gratuit)")
    else:
        client = MeshyAIClient(api_key)
        
        print("\n🧪 Test génération...")
        print("(Note: La génération prend 1-3 minutes)")
        
        # Test simple
        result = client.text_to_3d("a cute robot character")
        print(f"\nRésultat: {json.dumps(result, indent=2)}")
    
    print("\n" + "="*60)
