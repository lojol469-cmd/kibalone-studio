#!/usr/bin/env python3
"""
TripoSR Simplifié pour Kibalone Studio
Génère des modèles 3D depuis des images 2D
"""

import sys
import os
import torch
import numpy as np
from pathlib import Path
from PIL import Image
import trimesh

ISOL_PATH = Path("/home/belikan/Isol")
TRIPOSR_PATH = ISOL_PATH / "triposr_code"
sys.path.insert(0, str(TRIPOSR_PATH))

class TripoSRSimple:
    """Version simplifiée de TripoSR pour Kibalone"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        print(f"🎨 TripoSR Simple sur: {self.device}")
    
    def load_model(self):
        """Charge le modèle TripoSR"""
        try:
            from tsr.system import TSR
            
            print("📥 Chargement TripoSR...")
            self.model = TSR.from_pretrained(
                "stabilityai/TripoSR",
                config_name="config.yaml",
                weight_name="model.ckpt",
            )
            self.model.to(self.device)
            print("✅ TripoSR chargé !")
            return True
            
        except Exception as e:
            print(f"❌ Erreur chargement TripoSR: {e}")
            print("💡 Fallback vers génération procédurale")
            return False
    
    def image_to_3d_procedural(self, image_path, output_path=None):
        """
        Fallback: Génère un modèle 3D procédural inspiré de l'image
        (en attendant que TripoSR se charge correctement)
        """
        print(f"🎨 Génération procédurale depuis: {image_path}")
        
        # Charge l'image
        img = Image.open(image_path).convert('RGB')
        img = img.resize((128, 128))
        
        # Analyse des couleurs dominantes
        pixels = np.array(img)
        avg_color = pixels.mean(axis=(0, 1))
        
        # Crée un modèle basique avec la couleur dominante
        mesh = self.create_character_mesh(avg_color)
        
        if output_path is None:
            output_path = f"/home/belikan/Isol/Meshy/meshes/triposr_{hash(image_path) % 100000}.obj"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        mesh.export(output_path)
        
        print(f"✅ Modèle généré: {output_path}")
        
        return {
            'success': True,
            'mesh_path': output_path,
            'method': 'procedural'
        }
    
    def create_character_mesh(self, color):
        """Crée un personnage procédural avec la couleur donnée"""
        
        # Convertit RGB [0-255] en hex
        hex_color = '#%02x%02x%02x' % tuple(color.astype(int))
        
        # Corps
        body = trimesh.creation.box(extents=[0.6, 1.2, 0.3])
        body.apply_translation([0, 1.2, 0])
        
        # Tête
        head = trimesh.creation.icosphere(radius=0.25, subdivisions=2)
        head.apply_translation([0, 2.0, 0])
        
        # Bras
        arm_left = trimesh.creation.cylinder(radius=0.1, height=0.8)
        arm_left.apply_translation([-0.5, 1.2, 0])
        
        arm_right = trimesh.creation.cylinder(radius=0.1, height=0.8)
        arm_right.apply_translation([0.5, 1.2, 0])
        
        # Jambes
        leg_left = trimesh.creation.cylinder(radius=0.12, height=1.0)
        leg_left.apply_translation([-0.2, 0.5, 0])
        
        leg_right = trimesh.creation.cylinder(radius=0.12, height=1.0)
        leg_right.apply_translation([0.2, 0.5, 0])
        
        # Combine
        mesh = trimesh.util.concatenate([
            body, head, arm_left, arm_right, leg_left, leg_right
        ])
        
        # Applique la couleur (metadata)
        mesh.visual.face_colors = color
        
        return mesh
    
    def text_to_image_simple(self, prompt):
        """Crée une image simple depuis un prompt (pour tester)"""
        print(f"🎨 Génération image: {prompt}")
        
        # Crée une image de couleur unie pour le test
        color_map = {
            'robot': (128, 128, 128),
            'knight': (192, 192, 192),
            'hero': (255, 215, 0),
            'blue': (68, 136, 255),
            'red': (255, 68, 68),
            'green': (68, 255, 136)
        }
        
        prompt_lower = prompt.lower()
        color = (68, 136, 255)  # Bleu par défaut
        
        for key, value in color_map.items():
            if key in prompt_lower:
                color = value
                break
        
        # Crée l'image
        img = Image.new('RGB', (512, 512), color)
        
        # Sauvegarde
        img_path = f"/tmp/kibalone_prompt_{hash(prompt) % 100000}.png"
        img.save(img_path)
        
        print(f"✅ Image générée: {img_path}")
        return img_path
    
    def text_to_3d(self, prompt, output_path=None):
        """Pipeline complet: Texte → Image → 3D"""
        print(f"\n🚀 Génération 3D depuis: '{prompt}'")
        
        # 1. Génère une image depuis le prompt
        image_path = self.text_to_image_simple(prompt)
        
        # 2. Convertit l'image en 3D
        result = self.image_to_3d_procedural(image_path, output_path)
        
        result['prompt'] = prompt
        result['image_path'] = image_path
        
        return result
    
    def generate_from_prompt(self, prompt, model_type='character'):
        """Interface compatible avec le reste du système"""
        output_path = f"/home/belikan/Isol/Meshy/meshes/triposr_{model_type}_{hash(prompt) % 100000}.obj"
        return self.text_to_3d(prompt, output_path)


# ============================================
# API
# ============================================

generator = None

def init_triposr_generator():
    global generator
    if generator is None:
        generator = TripoSRSimple()
    return generator

def generate_with_triposr(prompt, model_type='character'):
    gen = init_triposr_generator()
    return gen.generate_from_prompt(prompt, model_type)


# ============================================
# Test
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("🎨 TEST TRIPOSR SIMPLE")
    print("="*60)
    
    gen = TripoSRSimple()
    
    # Test
    print("\n1️⃣ Test: Génération d'un robot")
    result = gen.generate_from_prompt("a futuristic robot", "character")
    
    if result['success']:
        print(f"\n✅ SUCCÈS !")
        print(f"   Mesh: {result['mesh_path']}")
        print(f"   Image: {result.get('image_path')}")
        print(f"   Méthode: {result.get('method')}")
    
    print("\n" + "="*60)
