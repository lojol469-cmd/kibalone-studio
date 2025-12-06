#!/usr/bin/env python3
"""
TripoSR Service - Version HuggingFace (sans dépendances locales)
Utilise l'API HuggingFace pour éviter les conflits de dépendances
"""

import sys
import os
from pathlib import Path

# Ajoute isol au path
ISOL_PATH = Path("/home/belikan/Isol")
sys.path.insert(0, str(ISOL_PATH / "isol-framework"))

from base import ServiceBase
import requests
from PIL import Image
import io
import base64


class TripoSRServiceHF(ServiceBase):
    """Service TripoSR via API HuggingFace - pas de dépendances CUDA !"""
    
    def __init__(self):
        super().__init__(log_level=20, log_file='/tmp/triposr_hf_service.log')
        self.api_url = "https://api-inference.huggingface.co/models/stabilityai/TripoSR"
        self.token = None
    
    def initialize(self, params):
        """Initialise avec le token HF"""
        try:
            # Charge le token depuis .env (de l'original kibali-IA)
            env_path = Path("/home/belikan/kibali-IA/.env")
            if env_path.exists():
                with open(env_path) as f:
                    for line in f:
                        if line.startswith('HF_TOKEN='):
                            self.token = line.split('=', 1)[1].strip().strip('"')
                            break
            
            if not self.token:
                return {
                    'success': False,
                    'error': 'HF_TOKEN non trouvé dans .env'
                }
            
            self.logger.info("✅ TripoSR HF initialisé")
            
            return {
                'success': True,
                'mode': 'huggingface-api'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur init: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def image_to_3d(self, params):
        """
        Convertit une image en 3D via API HF
        
        Note: L'API HF de TripoSR peut ne pas supporter tous les formats.
        Alternative: utiliser des modèles text-to-3D comme Shap-E
        """
        try:
            image_path = params.get('image_path')
            output_path = params.get('output_path', '/tmp/output.obj')
            
            if not self.token:
                return {'success': False, 'error': 'Non initialisé'}
            
            self.logger.info(f"🔄 Conversion: {image_path}")
            
            # Charge l'image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Appel API HF
            headers = {"Authorization": f"Bearer {self.token}"}
            
            self.logger.info("📡 Appel API HuggingFace...")
            response = requests.post(
                self.api_url,
                headers=headers,
                data=image_data,
                timeout=60
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code} - {response.text}"
                }
            
            # Sauvegarde le résultat
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"✅ Mesh sauvegardé: {output_path}")
            
            return {
                'success': True,
                'output_path': output_path,
                'size': len(response.content)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur conversion: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def text_to_3d_shap_e(self, params):
        """
        Alternative: Génération text-to-3D avec Shap-E
        Plus stable que TripoSR image-to-3D sur HF
        """
        try:
            prompt = params.get('prompt')
            output_path = params.get('output_path', '/tmp/output.ply')
            
            if not self.token:
                return {'success': False, 'error': 'Non initialisé'}
            
            self.logger.info(f"🔄 Génération text-to-3D: {prompt}")
            
            # Utilise Shap-E (OpenAI, supporté sur HF)
            shap_e_url = "https://api-inference.huggingface.co/models/openai/shap-e"
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt
            }
            
            self.logger.info("📡 Appel Shap-E API...")
            response = requests.post(
                shap_e_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"Shap-E Error: {response.status_code} - {response.text}"
                }
            
            # Sauvegarde
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"✅ Mesh Shap-E sauvegardé: {output_path}")
            
            return {
                'success': True,
                'output_path': output_path,
                'model': 'shap-e',
                'size': len(response.content)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur Shap-E: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process(self, params):
        """Point d'entrée principal"""
        method = params.get('method')
        
        if method == 'initialize':
            return self.initialize(params)
        elif method == 'image_to_3d':
            return self.image_to_3d(params)
        elif method == 'text_to_3d':
            return self.text_to_3d_shap_e(params)
        else:
            return {'error': f'Méthode inconnue: {method}'}


if __name__ == '__main__':
    service = TripoSRServiceHF()
    service.run()
