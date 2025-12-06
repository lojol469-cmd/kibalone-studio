#!/usr/bin/env python3
"""
Générateur 3D Réaliste pour Kibalone Studio
Intègre TripoSR, LGM, Stable Diffusion pour génération de vrais modèles 3D
"""

import sys
import os
import torch
import numpy as np
from pathlib import Path
from PIL import Image
import trimesh

# Paths - TOUT CENTRALISÉ dans /home/belikan/Isol
ISOL_PATH = Path("/home/belikan/Isol")
TRIPOSR_PATH = ISOL_PATH / "triposr_code"
KIBALI_IA_PATH = ISOL_PATH / "kibali-IA"
MODELS_PATH = ISOL_PATH / "models"

sys.path.insert(0, str(TRIPOSR_PATH))
sys.path.insert(0, str(KIBALI_IA_PATH))

class RealisticModelGenerator:
    """Génère de vrais modèles 3D réalistes"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🎨 Générateur 3D sur: {self.device}")
        
        self.triposr_model = None
        self.sd_pipeline = None
        self.lgm_model = None
        
    def init_triposr(self):
        """Initialise TripoSR pour Text/Image-to-3D"""
        try:
            from tsr.system import TSR
            
            print("📥 Chargement de TripoSR...")
            self.triposr_model = TSR.from_pretrained(
                "stabilityai/TripoSR",
                config_name="config.yaml",
                weight_name="model.ckpt",
            )
            self.triposr_model.renderer.set_chunk_size(8192)
            self.triposr_model.to(self.device)
            
            print("✅ TripoSR chargé !")
            return True
        except Exception as e:
            print(f"❌ Erreur TripoSR: {e}")
            return False
    
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
    
    def image_to_3d(self, image_path_or_pil):
        """Convertit une image en modèle 3D avec TripoSR"""
        if not self.triposr_model:
            self.init_triposr()
        
        print(f"🔄 Conversion image → 3D...")
        
        # Charge l'image
        if isinstance(image_path_or_pil, str):
            image = Image.open(image_path_or_pil)
        else:
            image = image_path_or_pil
        
        # Convertit en 3D
        with torch.no_grad():
            scene_codes = self.triposr_model([image], device=self.device)
            meshes = self.triposr_model.extract_mesh(scene_codes, resolution=256)
            mesh = meshes[0]
        
        print("✅ Modèle 3D généré !")
        return mesh
    
    def text_to_3d(self, prompt, output_path=None):
        """Pipeline complet: Texte → Image → 3D"""
        print(f"\n🚀 Génération 3D complète depuis: '{prompt}'")
        
        # 1. Génère l'image
        image = self.text_to_image(prompt)
        
        # Sauvegarde l'image temporaire
        temp_image_path = "/tmp/kibalone_temp_gen.png"
        image.save(temp_image_path)
        print(f"✅ Image générée: {temp_image_path}")
        
        # 2. Convertit en 3D
        mesh = self.image_to_3d(image)
        
        # 3. Sauvegarde le mesh
        if output_path is None:
            output_path = "/home/belikan/Isol/Meshy/meshes/generated_model.obj"
        
        mesh.export(output_path)
        print(f"✅ Modèle 3D sauvegardé: {output_path}")
        
        return {
            'mesh_path': output_path,
            'image_path': temp_image_path,
            'success': True
        }
    
    def generate_character(self, description):
        """Génère un personnage réaliste"""
        prompt = f"3D render of {description}, high quality, detailed, professional 3d model, clean background"
        return self.text_to_3d(prompt, f"/home/belikan/Isol/Meshy/meshes/character_{hash(description)}.obj")
    
    def generate_environment(self, description):
        """Génère un environnement"""
        prompt = f"3D environment scene of {description}, high quality, detailed architecture, professional 3d rendering"
        return self.text_to_3d(prompt, f"/home/belikan/Isol/Meshy/meshes/environment_{hash(description)}.obj")
    
    def generate_object(self, description):
        """Génère un objet"""
        prompt = f"3D model of {description}, high quality, detailed object, product photography style"
        return self.text_to_3d(prompt, f"/home/belikan/Isol/Meshy/meshes/object_{hash(description)}.obj")


# ============================================
# API pour Flask
# ============================================

generator = None

def init_generator():
    """Initialise le générateur (appelé au démarrage)"""
    global generator
    if generator is None:
        generator = RealisticModelGenerator()
    return generator

def generate_realistic_model(prompt, model_type='character'):
    """Génère un modèle réaliste selon le type"""
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
    print("🎨 TEST GÉNÉRATEUR 3D RÉALISTE")
    print("="*60)
    
    gen = RealisticModelGenerator()
    
    # Test 1: Personnage
    print("\n1️⃣ Test: Génération d'un personnage héroïque")
    result = gen.generate_character("a heroic knight with armor and sword")
    print(f"Résultat: {result}")
    
    # Test 2: Objet
    print("\n2️⃣ Test: Génération d'un objet")
    result = gen.generate_object("a magical staff with glowing crystals")
    print(f"Résultat: {result}")
    
    print("\n✅ Tests terminés !")
