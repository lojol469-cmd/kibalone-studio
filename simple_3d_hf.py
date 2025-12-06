#!/usr/bin/env python3
"""
Générateur 3D simple via HuggingFace
Utilise les API HF directement, sans subprocess
"""

import os
import requests
from pathlib import Path
from PIL import Image
import io


class Simple3DGenerator:
    """Générateur 3D via HuggingFace API - simple et direct"""
    
    def __init__(self):
        self.token = None
        self._load_token()
    
    def _load_token(self):
        """Charge le token HF depuis .env"""
        env_path = Path("/home/belikan/kibali-IA/.env")
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith('HF_TOKEN='):
                        self.token = line.split('=', 1)[1].strip().strip('"')
                        break
    
    def text_to_3d_shap_e(self, prompt, output_path=None):
        """
        Génération text-to-3D avec Shap-E (OpenAI)
        
        Args:
            prompt: Description du modèle 3D
            output_path: Où sauvegarder (.ply)
        
        Returns:
            dict: {'success': bool, 'output_path': str, ...}
        """
        if not self.token:
            return {'success': False, 'error': 'HF_TOKEN non trouvé'}
        
        if output_path is None:
            safe_name = "".join(c if c.isalnum() else "_" for c in prompt[:30])
            output_path = f"/tmp/shap_e_{safe_name}.ply"
        
        try:
            print(f"🔄 Génération Shap-E: {prompt}")
            
            # API HuggingFace pour Shap-E (nouvelle URL)
            url = "https://router.huggingface.co/models/openai/shap-e"
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            payload = {"inputs": prompt}
            
            print("📡 Appel API HuggingFace...")
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 503:
                # Modèle en cours de chargement
                return {
                    'success': False,
                    'error': 'Modèle en chargement, réessayez dans 20 secondes',
                    'status': 'loading'
                }
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code} - {response.text[:200]}"
                }
            
            # Sauvegarde
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Mesh sauvegardé: {output_path}")
            
            return {
                'success': True,
                'output_path': output_path,
                'model': 'shap-e',
                'size': len(response.content)
            }
            
        except requests.Timeout:
            return {
                'success': False,
                'error': 'Timeout de l\'API (> 120s)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def image_to_3d_triposr(self, image_path, output_path=None):
        """
        Conversion image → 3D avec TripoSR
        
        Note: L'API HF de TripoSR peut ne pas être disponible
        """
        if not self.token:
            return {'success': False, 'error': 'HF_TOKEN non trouvé'}
        
        if output_path is None:
            output_path = f"/tmp/triposr_{Path(image_path).stem}.obj"
        
        try:
            print(f"🔄 Conversion TripoSR: {image_path}")
            
            # Charge l'image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            url = "https://router.huggingface.co/models/stabilityai/TripoSR"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            print("📡 Appel API TripoSR...")
            response = requests.post(url, headers=headers, data=image_data, timeout=120)
            
            if response.status_code == 503:
                return {
                    'success': False,
                    'error': 'Modèle TripoSR en chargement',
                    'status': 'loading'
                }
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"TripoSR Error: {response.status_code} - {response.text[:200]}"
                }
            
            # Sauvegarde
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Mesh TripoSR sauvegardé: {output_path}")
            
            return {
                'success': True,
                'output_path': output_path,
                'model': 'triposr',
                'size': len(response.content)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Test
if __name__ == '__main__':
    print("=== Test Simple 3D Generator ===\n")
    
    gen = Simple3DGenerator()
    
    if not gen.token:
        print("❌ Token HF non trouvé")
    else:
        print("✅ Token HF chargé\n")
        
        # Test text-to-3D
        print("1️⃣ Test Shap-E (text-to-3D)...")
        result = gen.text_to_3d_shap_e("a red cube")
        print(f"   Résultat: {result}\n")
