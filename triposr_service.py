#!/usr/bin/env python3
"""
TripoSR Service - Isolé avec framework isol
Génère des modèles 3D depuis images
"""

import sys
import os
from pathlib import Path

# Ajoute isol au path
ISOL_PATH = Path("/home/belikan/Isol")
sys.path.insert(0, str(ISOL_PATH / "isol-framework"))
sys.path.insert(0, str(ISOL_PATH / "triposr_code"))

from base import ServiceBase

class TripoSRService(ServiceBase):
    """Service isolé pour TripoSR - génération image → 3D"""
    
    def __init__(self):
        super().__init__(log_level=20, log_file='/tmp/triposr_service.log')
        self.model = None
        self.device = None
    
    def initialize(self, params):
        """Charge le modèle TripoSR"""
        try:
            import torch
            from tsr.system import TSR
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.log(f"🎨 TripoSR sur: {self.device}")
            
            # Charge le modèle
            self.log("📥 Chargement TripoSR...")
            self.model = TSR.from_pretrained(
                "stabilityai/TripoSR",
                config_name="config.yaml",
                weight_name="model.ckpt",
            )
            self.model.renderer.set_chunk_size(8192)
            self.model.to(self.device)
            
            self.log("✅ TripoSR chargé !")
            
            return {
                'success': True,
                'device': self.device
            }
            
        except Exception as e:
            self.log(f"❌ Erreur init: {e}", level='error')
            return {
                'success': False,
                'error': str(e)
            }
    
    def image_to_3d(self, params):
        """
        Convertit une image en 3D
        
        Params:
            image_path: Chemin vers l'image
            output_path: Où sauvegarder le mesh
            resolution: Résolution du mesh (défaut 256)
        """
        try:
            from PIL import Image
            import torch
            
            image_path = params.get('image_path')
            output_path = params.get('output_path', '/tmp/output.obj')
            resolution = params.get('resolution', 256)
            
            if not self.model:
                return {'success': False, 'error': 'Modèle non initialisé'}
            
            self.log(f"🔄 Conversion: {image_path}")
            
            # Charge l'image
            image = Image.open(image_path)
            
            # Génère le mesh
            with torch.no_grad():
                scene_codes = self.model([image], device=self.device)
                meshes = self.model.extract_mesh(scene_codes, resolution=resolution)
                mesh = meshes[0]
            
            # Sauvegarde
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            mesh.export(output_path)
            
            self.log(f"✅ Mesh sauvegardé: {output_path}")
            
            return {
                'success': True,
                'output_path': output_path,
                'vertices': len(mesh.vertices),
                'faces': len(mesh.faces)
            }
            
        except Exception as e:
            self.log(f"❌ Erreur conversion: {e}", level='error')
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
        else:
            return {'error': f'Méthode inconnue: {method}'}


if __name__ == '__main__':
    service = TripoSRService()
    service.run()
