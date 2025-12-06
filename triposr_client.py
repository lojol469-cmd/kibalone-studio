#!/usr/bin/env python3
"""
Client TripoSR - Communication avec le service isolé
"""

import subprocess
import json
import sys
from pathlib import Path


class TripoSRClient:
    """Client pour communiquer avec le service TripoSR isolé"""
    
    def __init__(self, service_path="/home/belikan/Isol/Kibalone-Studio/triposr_service.py"):
        self.service_path = service_path
        self.process = None
    
    def start(self):
        """Démarre le service TripoSR"""
        if self.process is not None:
            return True
        
        try:
            print("🚀 Démarrage service TripoSR...")
            self.process = subprocess.Popen(
                ['python3', self.service_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            print("✅ Service TripoSR démarré")
            return True
            
        except Exception as e:
            print(f"❌ Erreur démarrage: {e}")
            return False
    
    def call(self, method, params=None):
        """
        Appelle une méthode sur le service
        
        Args:
            method: Nom de la méthode
            params: Paramètres supplémentaires
        
        Returns:
            dict: Résultat ou erreur
        """
        if self.process is None:
            if not self.start():
                return {'success': False, 'error': 'Service non démarré'}
        
        try:
            # Prépare la requête JSON-RPC
            request = {
                'method': method,
                **(params or {})
            }
            
            # Envoie
            self.process.stdin.write(json.dumps(request) + '\n')
            self.process.stdin.flush()
            
            # Reçoit la réponse
            response_line = self.process.stdout.readline()
            
            if not response_line:
                stderr = self.process.stderr.read()
                return {
                    'success': False,
                    'error': f'Pas de réponse du service. stderr: {stderr}'
                }
            
            response = json.loads(response_line)
            return response
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def initialize(self):
        """Initialise le modèle TripoSR"""
        return self.call('initialize')
    
    def image_to_3d(self, image_path, output_path=None, resolution=256):
        """
        Convertit une image en 3D
        
        Args:
            image_path: Chemin vers l'image
            output_path: Où sauvegarder (défaut: /tmp/output.obj)
            resolution: Résolution du mesh
        
        Returns:
            dict: {'success': bool, 'output_path': str, ...}
        """
        if output_path is None:
            output_path = f"/tmp/triposr_output_{Path(image_path).stem}.obj"
        
        return self.call('image_to_3d', {
            'image_path': image_path,
            'output_path': output_path,
            'resolution': resolution
        })
    
    def stop(self):
        """Arrête le service"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None
            print("🛑 Service TripoSR arrêté")
    
    def __del__(self):
        self.stop()


# Test du client
if __name__ == '__main__':
    print("=== Test TripoSR Client ===\n")
    
    client = TripoSRClient()
    
    # 1. Initialise
    print("1️⃣ Initialisation...")
    result = client.initialize()
    print(f"   Résultat: {result}\n")
    
    if result.get('success'):
        # 2. Test avec une image (si disponible)
        test_image = "/home/belikan/Isol/Kibalone-Studio/test_images/cube.png"
        
        if Path(test_image).exists():
            print(f"2️⃣ Conversion de {test_image}...")
            result = client.image_to_3d(test_image)
            print(f"   Résultat: {result}\n")
        else:
            print(f"⚠️ Image de test non trouvée: {test_image}\n")
    
    client.stop()
