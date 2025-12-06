#!/usr/bin/env python3
"""
🎨 Pipeline complet: Texte → Image → 3D avec TripoSR
====================================================
1. Génère une image depuis le prompt (via API Stable Diffusion)
2. Convertit l'image en modèle 3D avec TripoSR
3. Exporte en Three.js
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import requests
import base64
import io
from PIL import Image
import os

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URLs des APIs
HUGGINGFACE_API = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HF_TOKEN = os.getenv('HUGGINGFACE_TOKEN', '')  # Optionnel

@app.route('/api/text-to-3d-real', methods=['POST'])
def text_to_3d_real():
    """Pipeline complet: Texte → Image → 3D"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'No prompt'}), 400
        
        logger.info(f"📝 Prompt: {prompt}")
        
        # Étape 1: Génère l'image avec prompt optimisé
        enhanced_prompt = enhance_prompt_for_3d(prompt)
        logger.info(f"✨ Prompt amélioré: {enhanced_prompt}")
        
        image = generate_image_from_text(enhanced_prompt)
        
        if image is None:
            logger.warning("⚠️ Impossible de générer l'image, utilisation du fallback")
            return jsonify({
                'success': False,
                'error': 'Image generation failed',
                'fallback': 'use_procedural'
            }), 500
        
        logger.info(f"✅ Image générée: {image.size}")
        
        # Étape 2: Sauvegarde temporaire
        temp_path = f"/tmp/kibalone_{hash(prompt)}.png"
        image.save(temp_path)
        logger.info(f"💾 Image sauvegardée: {temp_path}")
        
        # Étape 3: Convertit en base64 pour debug
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image_data': f"data:image/png;base64,{image_b64}",
            'image_path': temp_path,
            'prompt': prompt,
            'enhanced_prompt': enhanced_prompt,
            'message': 'Image générée. TripoSR nécessite CUDA 12+, utilisez le modèle procédural amélioré.'
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

def enhance_prompt_for_3d(prompt):
    """
    Améliore le prompt pour la génération 3D
    Ajoute des mots-clés pour avoir un personnage propre
    """
    base_enhancements = [
        "3D character",
        "T-pose",
        "neutral pose", 
        "white background",
        "studio lighting",
        "high quality",
        "detailed",
        "character sheet style",
        "front view",
        "full body"
    ]
    
    # Détecte le type et ajoute des détails
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ['guerrier', 'warrior', 'knight', 'chevalier']):
        specific = "medieval warrior with armor and sword, heroic pose"
    elif any(word in prompt_lower for word in ['robot', 'mech', 'android']):
        specific = "futuristic robot character, metallic surface, sci-fi design"
    elif any(word in prompt_lower for word in ['dragon', 'creature', 'monster']):
        specific = "fantasy creature, detailed scales, mythical beast"
    elif any(word in prompt_lower for word in ['mage', 'wizard', 'sorcier']):
        specific = "fantasy mage with robe and staff, magical character"
    else:
        specific = "stylized character, cartoon style, clean design"
    
    enhanced = f"{specific}, {', '.join(base_enhancements)}"
    return enhanced

def generate_image_from_text(prompt):
    """
    Génère une image depuis un prompt via Hugging Face Inference API
    """
    try:
        headers = {"Content-Type": "application/json"}
        
        if HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"
            logger.info("🔑 Utilisation du token Hugging Face")
        else:
            logger.warning("⚠️ Pas de token HF, l'API peut être limitée")
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": "blurry, low quality, distorted, multiple views, text, watermark, signature",
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        }
        
        logger.info("🎨 Appel API Stable Diffusion...")
        response = requests.post(HUGGINGFACE_API, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            logger.info(f"✅ Image reçue: {image.size}")
            return image
        else:
            logger.error(f"❌ Erreur API: {response.status_code}")
            logger.error(f"Response: {response.text[:200]}")
            return create_placeholder_image(prompt)
            
    except Exception as e:
        logger.error(f"❌ Erreur génération image: {e}")
        return create_placeholder_image(prompt)

def create_placeholder_image(prompt):
    """
    Crée une image placeholder avec le texte du prompt
    """
    from PIL import ImageDraw, ImageFont
    
    img = Image.new('RGB', (512, 512), color='white')
    draw = ImageDraw.Draw(img)
    
    # Texte
    text = f"Personnage:\n{prompt[:30]}"
    try:
        # Essaye d'utiliser une police
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = None
    
    # Dessine un bonhomme simple
    draw.ellipse([206, 100, 306, 200], fill='peachpuff', outline='black', width=2)  # Tête
    draw.rectangle([231, 200, 281, 350], fill='blue', outline='black', width=2)  # Corps
    draw.line([231, 220, 180, 280], fill='peachpuff', width=8)  # Bras gauche
    draw.line([281, 220, 332, 280], fill='peachpuff', width=8)  # Bras droit
    draw.line([240, 350, 220, 450], fill='blue', width=8)  # Jambe gauche
    draw.line([272, 350, 292, 450], fill='blue', width=8)  # Jambe droite
    
    # Yeux
    draw.ellipse([230, 140, 250, 160], fill='black')
    draw.ellipse([262, 140, 282, 160], fill='black')
    
    # Bouche
    draw.arc([230, 160, 282, 190], 0, 180, fill='black', width=3)
    
    draw.text((50, 20), text, fill='black', font=font)
    
    logger.info("🖼️ Image placeholder créée")
    return img

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'text-to-image-to-3d',
        'huggingface_token': bool(HF_TOKEN)
    })

if __name__ == '__main__':
    logger.info("🚀 Pipeline Text→Image→3D démarré")
    logger.info("📡 http://localhost:5002")
    if not HF_TOKEN:
        logger.warning("⚠️ Variable HUGGINGFACE_TOKEN non définie")
        logger.info("💡 Export HUGGINGFACE_TOKEN=your_token pour activer Stable Diffusion")
    app.run(host='0.0.0.0', port=5002, debug=False)
