#!/usr/bin/env python3
"""
Générateur 3D Simplifié pour Kibalone Studio
Utilise Shap-E (plus simple que TripoSR, pas besoin de CUDA 12)
"""

import sys
import os
import torch
import numpy as np
from pathlib import Path
from PIL import Image
import trimesh

# Paths centralisés dans Isol
ISOL_PATH = Path("/home/belikan/Isol")
sys.path.insert(0, str(ISOL_PATH / "kibali-IA"))

class Simple3DGenerator:
    """Génère de vrais modèles 3D avec Shap-E ou Stable Diffusion"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🎨 Générateur 3D Simple sur: {self.device}")
        
        self.sd_pipeline = None
        self.shap_e_model = None
        
    def init_stable_diffusion(self):
        """Initialise Stable Diffusion pour génération d'images"""
        try:
            from diffusers import StableDiffusionPipeline
            
            print("📥 Chargement de Stable Diffusion...")
            self.sd_pipeline = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            ).to(self.device)
            
            print("✅ Stable Diffusion chargé !")
            return True
        except Exception as e:
            print(f"❌ Erreur Stable Diffusion: {e}")
            return False
    
    def init_shap_e(self):
        """Initialise Shap-E pour text-to-3D (alternative à TripoSR)"""
        try:
            from shap_e.diffusion.sample import sample_latents
            from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
            from shap_e.models.download import load_model, load_config
            from shap_e.util.notebooks import decode_latent_mesh
            
            print("📥 Chargement de Shap-E...")
            self.shap_e_model = {
                'model': load_model('transmitter', device=self.device),
                'diffusion': diffusion_from_config(load_config('diffusion')),
            }
            
            print("✅ Shap-E chargé !")
            return True
        except Exception as e:
            print(f"⚠️ Shap-E non disponible: {e}")
            print("💡 Fallback vers génération procédurale avancée")
            return False
    
    def text_to_image(self, prompt, negative_prompt="low quality, blurry"):
        """Génère une image depuis un prompt texte"""
        if not self.sd_pipeline:
            self.init_stable_diffusion()
        
        print(f"🎨 Génération image: {prompt}")
        
        image = self.sd_pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=30,
            guidance_scale=7.5,
            height=512,
            width=512
        ).images[0]
        
        return image
    
    def text_to_3d_procedural(self, prompt):
        """Génération 3D procédurale avancée basée sur le prompt"""
        print(f"🔨 Génération procédurale avancée: {prompt}")
        
        # Analyse du prompt pour déterminer la forme
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['character', 'person', 'hero', 'knight', 'warrior', 'human']):
            mesh = self.create_humanoid_mesh()
        elif any(word in prompt_lower for word in ['cube', 'box', 'building']):
            mesh = self.create_detailed_cube()
        elif any(word in prompt_lower for word in ['sphere', 'ball', 'planet']):
            mesh = self.create_detailed_sphere()
        elif any(word in prompt_lower for word in ['tree', 'plant']):
            mesh = self.create_tree_mesh()
        elif any(word in prompt_lower for word in ['vehicle', 'car', 'ship']):
            mesh = self.create_vehicle_mesh()
        else:
            # Par défaut: forme abstraite
            mesh = self.create_abstract_mesh()
        
        return mesh
    
    def create_humanoid_mesh(self):
        """Crée un humanoïde détaillé"""
        vertices = []
        faces = []
        
        # Corps principal (plus détaillé)
        body = trimesh.creation.box(extents=[0.6, 1.2, 0.3])
        body.apply_translation([0, 1.2, 0])
        
        # Tête
        head = trimesh.creation.icosphere(radius=0.25, subdivisions=2)
        head.apply_translation([0, 2.0, 0])
        
        # Bras
        arm_left = trimesh.creation.box(extents=[0.2, 0.8, 0.2])
        arm_left.apply_translation([-0.5, 1.2, 0])
        
        arm_right = trimesh.creation.box(extents=[0.2, 0.8, 0.2])
        arm_right.apply_translation([0.5, 1.2, 0])
        
        # Jambes
        leg_left = trimesh.creation.box(extents=[0.25, 1.0, 0.25])
        leg_left.apply_translation([-0.2, 0.5, 0])
        
        leg_right = trimesh.creation.box(extents=[0.25, 1.0, 0.25])
        leg_right.apply_translation([0.2, 0.5, 0])
        
        # Combine tout
        mesh = trimesh.util.concatenate([body, head, arm_left, arm_right, leg_left, leg_right])
        
        return mesh
    
    def create_detailed_cube(self):
        """Cube avec détails"""
        mesh = trimesh.creation.box(extents=[1, 1, 1])
        # Ajoute des subdivisions pour plus de détails
        mesh = mesh.subdivide()
        return mesh
    
    def create_detailed_sphere(self):
        """Sphère avec haute résolution"""
        mesh = trimesh.creation.icosphere(radius=0.5, subdivisions=3)
        return mesh
    
    def create_tree_mesh(self):
        """Arbre simple"""
        # Tronc
        trunk = trimesh.creation.cylinder(radius=0.1, height=1.5)
        
        # Feuillage (icosphere)
        leaves = trimesh.creation.icosphere(radius=0.6, subdivisions=2)
        leaves.apply_translation([0, 1.8, 0])
        
        mesh = trimesh.util.concatenate([trunk, leaves])
        return mesh
    
    def create_vehicle_mesh(self):
        """Véhicule simple"""
        # Corps
        body = trimesh.creation.box(extents=[2, 0.8, 1])
        body.apply_translation([0, 0.5, 0])
        
        # Cabine
        cabin = trimesh.creation.box(extents=[1, 0.6, 0.9])
        cabin.apply_translation([0, 1.1, 0])
        
        mesh = trimesh.util.concatenate([body, cabin])
        return mesh
    
    def create_abstract_mesh(self):
        """Forme abstraite intéressante"""
        mesh = trimesh.creation.icosphere(radius=0.5, subdivisions=2)
        # Déforme aléatoirement
        vertices = mesh.vertices
        vertices += np.random.normal(0, 0.05, vertices.shape)
        mesh.vertices = vertices
        return mesh
    
    def text_to_3d(self, prompt, output_path=None):
        """Pipeline complet: Texte → 3D"""
        print(f"\n🚀 Génération 3D depuis: '{prompt}'")
        
        # Génère le mesh (procédural pour l'instant)
        mesh = self.text_to_3d_procedural(prompt)
        
        # Sauvegarde
        if output_path is None:
            output_path = f"/home/belikan/Isol/Kibalone-Studio/meshes/generated_{hash(prompt) % 100000}.obj"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        mesh.export(output_path)
        print(f"✅ Modèle 3D sauvegardé: {output_path}")
        
        return {
            'mesh_path': output_path,
            'success': True
        }
    
    def generate_character(self, description):
        """Génère un personnage"""
        prompt = f"character {description}"
        return self.text_to_3d(prompt, f"/home/belikan/Isol/Kibalone-Studio/meshes/character_{hash(description) % 100000}.obj")
    
    def generate_environment(self, description):
        """Génère un environnement"""
        prompt = f"environment {description}"
        return self.text_to_3d(prompt, f"/home/belikan/Isol/Kibalone-Studio/meshes/environment_{hash(description) % 100000}.obj")
    
    def generate_object(self, description):
        """Génère un objet"""
        prompt = f"object {description}"
        return self.text_to_3d(prompt, f"/home/belikan/Isol/Kibalone-Studio/meshes/object_{hash(description) % 100000}.obj")


# ============================================
# API pour Flask
# ============================================

generator = None

def init_generator():
    """Initialise le générateur"""
    global generator
    if generator is None:
        generator = Simple3DGenerator()
    return generator

def generate_realistic_model(prompt, model_type='character'):
    """Génère un modèle selon le type"""
    gen = init_generator()
    
    try:
        if model_type == 'character':
            return gen.generate_character(prompt)
        elif model_type == 'environment':
            return gen.generate_environment(prompt)
        elif model_type == 'object':
            return gen.generate_object(prompt)
        else:
            return gen.text_to_3d(prompt)
    except Exception as e:
        print(f"❌ Erreur génération: {e}")
        return {
            'success': False,
            'error': str(e)
        }


# ============================================
# Test
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("🎨 TEST GÉNÉRATEUR 3D SIMPLE")
    print("="*60)
    
    gen = Simple3DGenerator()
    
    # Test
    print("\n1️⃣ Test: Personnage héroïque")
    result = gen.generate_character("heroic knight with armor")
    print(f"Résultat: {result}")
    
    print("\n✅ Test terminé !")
