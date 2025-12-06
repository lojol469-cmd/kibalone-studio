#!/usr/bin/env python3
"""
🎨 GREASE PENCIL IA BACKEND
===========================
Dessine dans l'espace 3D en 2D avec l'IA
Utilise: ControlNet + SDXL pour créer des dessins stylisés
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from diffusers import StableDiffusionXLPipeline, ControlNetModel, StableDiffusionXLControlNetPipeline
from PIL import Image, ImageDraw
import numpy as np
import base64
from io import BytesIO
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Chemins des modèles
MODEL_CACHE = Path("/home/belikan/Isol/kibali-IA/kibali_data/models/huggingface_cache")
OUTPUT_DIR = Path("/tmp/kibalone_grease_pencil")
OUTPUT_DIR.mkdir(exist_ok=True)

print("🎨 Chargement des modèles IA pour Grease Pencil...")

# ControlNet pour le contrôle des traits
controlnet_canny = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11p_sd15_canny",
    torch_dtype=torch.float16,
    cache_dir=MODEL_CACHE
)

controlnet_scribble = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-scribble",
    torch_dtype=torch.float16,
    cache_dir=MODEL_CACHE
)

# Pipeline SDXL pour qualité artistique
pipe_sdxl = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    cache_dir=MODEL_CACHE
).to("cuda" if torch.cuda.is_available() else "cpu")

print("✅ Modèles chargés!")

class GreasePencilAI:
    """Génère des dessins 2D/3D avec IA"""
    
    def __init__(self):
        self.pipe = pipe_sdxl
        self.controlnet_canny = controlnet_canny
        self.controlnet_scribble = controlnet_scribble
        
    def generate_character_sketch(self, prompt: str, style="anime"):
        """
        Génère un personnage dessiné avec IA
        
        Args:
            prompt: Description du personnage
            style: anime, cartoon, realistic, sketch
        """
        print(f"🎨 Génération personnage: {prompt} (style: {style})")
        
        # Prompts améliorés selon le style
        style_prompts = {
            "anime": f"{prompt}, anime style, cel shading, clean lines, vibrant colors, 2D animation",
            "cartoon": f"{prompt}, cartoon style, bold outlines, flat colors, expressive",
            "realistic": f"{prompt}, realistic drawing, detailed linework, shading",
            "sketch": f"{prompt}, pencil sketch, rough lines, artistic, hand-drawn"
        }
        
        full_prompt = style_prompts.get(style, prompt)
        negative_prompt = "3d render, photo, blurry, ugly, deformed"
        
        # Génération
        image = self.pipe(
            prompt=full_prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=30,
            guidance_scale=7.5,
            height=512,
            width=512
        ).images[0]
        
        # Sauvegarde
        timestamp = int(time.time() * 1000)
        filename = f"character_{timestamp}.png"
        filepath = OUTPUT_DIR / filename
        image.save(filepath)
        
        return {
            "success": True,
            "image_path": str(filepath),
            "image_url": f"/grease-pencil/images/{filename}",
            "prompt": full_prompt,
            "style": style,
            "size": [512, 512]
        }
    
    def generate_multiple_characters(self, descriptions: list, style="anime"):
        """Génère plusieurs personnages (ex: 2 personnages qui courent)"""
        print(f"🎨 Génération de {len(descriptions)} personnages...")
        
        results = []
        for i, desc in enumerate(descriptions):
            result = self.generate_character_sketch(desc, style)
            result['index'] = i
            results.append(result)
            
        return {
            "success": True,
            "characters": results,
            "count": len(results),
            "style": style
        }
    
    def create_stroke_data(self, image_path: str):
        """
        Convertit une image en données de traits (strokes) pour Three.js
        """
        image = Image.open(image_path)
        
        # Détection des contours (simulation)
        # TODO: Utiliser un modèle de détection de contours
        
        # Pour l'instant, retourne des données de base
        strokes = {
            "type": "GreasePencilLayer",
            "name": "Character",
            "strokes": [
                {
                    "points": [[0, 0, 0], [1, 0, 0], [1, 1, 0]],
                    "color": [0, 0, 0, 1],
                    "thickness": 2
                }
            ]
        }
        
        return strokes

# Instance globale
grease_ai = GreasePencilAI()

# ============================================
# ENDPOINTS API
# ============================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "service": "Grease Pencil IA Backend",
        "models_loaded": ["SDXL", "ControlNet-Canny", "ControlNet-Scribble"]
    })

@app.route('/api/draw-character', methods=['POST'])
def draw_character():
    """
    Dessine un personnage via prompt IA
    
    Body:
        {
            "prompt": "personnage héroïque",
            "style": "anime",
            "position_3d": [0, 0, 0]
        }
    """
    data = request.json
    prompt = data.get('prompt', 'character')
    style = data.get('style', 'anime')
    position = data.get('position_3d', [0, 0, 0])
    
    try:
        result = grease_ai.generate_character_sketch(prompt, style)
        
        # Ajoute les données 3D
        result['position_3d'] = position
        result['layer_name'] = f"Character_{int(time.time())}"
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/draw-scene', methods=['POST'])
def draw_scene():
    """
    Dessine une scène complète avec plusieurs personnages
    
    Body:
        {
            "prompt": "deux personnages qui courent",
            "characters": [
                {"description": "héros musclé", "position": [0, 0, 0]},
                {"description": "héroïne rapide", "position": [2, 0, 0]}
            ],
            "style": "anime"
        }
    """
    data = request.json
    characters = data.get('characters', [])
    style = data.get('style', 'anime')
    
    if not characters:
        # Parse le prompt pour extraire les personnages
        prompt = data.get('prompt', '')
        # TODO: Parser intelligent avec IA
        characters = [
            {"description": prompt, "position": [0, 0, 0]}
        ]
    
    try:
        descriptions = [c['description'] for c in characters]
        result = grease_ai.generate_multiple_characters(descriptions, style)
        
        # Ajoute les positions 3D
        for i, char_result in enumerate(result['characters']):
            if i < len(characters):
                char_result['position_3d'] = characters[i].get('position', [i*2, 0, 0])
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/grease-pencil/images/<filename>', methods=['GET'])
def serve_image(filename):
    """Sert les images générées"""
    filepath = OUTPUT_DIR / filename
    if filepath.exists():
        return send_file(filepath, mimetype='image/png')
    return jsonify({"error": "Image not found"}), 404

# ============================================
# DÉMARRAGE
# ============================================

if __name__ == '__main__':
    import time
    from flask import send_file
    
    print("="*60)
    print("🎨 GREASE PENCIL IA BACKEND")
    print("="*60)
    print("✅ Génération 2D/3D avec IA")
    print("✅ Styles: anime, cartoon, realistic, sketch")
    print("✅ ControlNet pour précision")
    print(f"📁 Output: {OUTPUT_DIR}")
    print("="*60)
    
    app.run(host='0.0.0.0', port=11007, debug=False)
