#!/usr/bin/env python3
"""
Client TripoSR HF - Version sans dépendances CUDA
"""

import subprocess
import json
from pathlib import Path


class TripoSRClientHF:
    """Client pour le service TripoSR via HuggingFace API"""
    
    def __init__(self, service_path="/home/belikan/Isol/Meshy/triposr_service_hf.py"):
        self.service_path = service_path
        self.process = None
    
    def start(self):
        """Démarre le service TripoSR HF"""
        if self.process is not None:
            return True
        
        try:
            print("🚀 Démarrage service TripoSR HF...")
            self.process = subprocess.Popen(
                ['python3', self.service_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            print("✅ Service TripoSR HF démarré")
            return True
            
        except Exception as e:
            print(f"❌ Erreur démarrage: {e}")
            return False
    
    def call(self, method, params=None):
        """Appelle une méthode sur le service"""
        if self.process is None:
            if not self.start():
                return {'success': False, 'error': 'Service non démarré'}
        
        try:
            # Prépare la requête
            request = {
                'method': method,
                **(params or {})
            }
            
            # Envoie
            self.process.stdin.write(json.dumps(request) + '\n')
            self.process.stdin.flush()
            
            # Reçoit
            response_line = self.process.stdout.readline()
            
            if not response_line:
                stderr = self.process.stderr.read()
                return {
                    'success': False,
                    'error': f'Pas de réponse. stderr: {stderr}'
                }
            
            response = json.loads(response_line)
            return response
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def initialize(self):
        """Initialise le service"""
        return self.call('initialize')
    
    def image_to_3d(self, image_path, output_path=None):
        """Convertit une image en 3D"""
        if output_path is None:
            output_path = f"/tmp/triposr_hf_{Path(image_path).stem}.obj"
        
        return self.call('image_to_3d', {
            'image_path': image_path,
            'output_path': output_path
        })
    
    def text_to_3d(self, prompt, output_path=None):
        """Génère un 3D depuis un prompt (Shap-E)"""
        if output_path is None:
            # Génère un nom de fichier depuis le prompt
            safe_name = "".join(c if c.isalnum() else "_" for c in prompt[:30])
            output_path = f"/tmp/shap_e_{safe_name}.ply"
        
        return self.call('text_to_3d', {
            'prompt': prompt,
            'output_path': output_path
        })
    
    def stop(self):
        """Arrête le service"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None
            print("🛑 Service TripoSR HF arrêté")
    
    def __del__(self):
        self.stop()


# Test du client
if __name__ == '__main__':
    print("=== Test TripoSR HF Client ===\n")
    
    client = TripoSRClientHF()
    
    # 1. Initialise
    print("1️⃣ Initialisation...")
    result = client.initialize()
    print(f"   Résultat: {result}\n")
    
    if result.get('success'):
        # 2. Test text-to-3D (Shap-E)
        print("2️⃣ Test text-to-3D avec Shap-E...")
        result = client.text_to_3d("a red cube")
        print(f"   Résultat: {result}\n")
        
        if result.get('success'):
            print(f"   ✅ Fichier: {result.get('output_path')}")
    
    client.stop()
