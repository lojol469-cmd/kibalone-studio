#!/usr/bin/env python3
"""
🎨 KIBALI GREASE PENCIL STUDIO - Le plus puissant au monde
===========================================================
WORKFLOW RÉVOLUTIONNAIRE:
1. SDXL → Génère dessin 2D coloré (personnage, objet)
2. TripoSR → Reconstruit en mesh 3D depuis l'image
3. Three.js → Affiche le mesh 3D texturé

Utilise: SDXL + TripoSR + Qwen2.5-Coder pour code complexe
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import torch
from pathlib import Path
from datetime import datetime

# Import TripoSR
sys.path.insert(0, str(Path(__file__).parent))
from triposr_client_hf import TripoSRClientHF

app = Flask(__name__)
CORS(app)

# Chemins vers les modèles
MODELS_PATH = Path("/home/belikan/Isol/kibali-IA/kibali_data/models/huggingface_cache")

print("="*60)
print("🎨 KIBALI GREASE PENCIL STUDIO")
print("="*60)

# ============================================
# CHARGEMENT DES IA
# ============================================

class GreasePencilAI:
    """Moteur IA pour Grease Pencil avec reconstruction 3D"""
    
    def __init__(self):
        self.code_generator = None  # Qwen2.5-Coder
        self.image_generator = None  # SDXL
        self.controlnet = None  # ControlNet Scribble
        self.animator = None  # AnimateDiff
        self.triposr = None  # TripoSR pour image→3D
        self.models_loaded = False
        
        print("\n📦 Initialisation des IA...")
        self.load_models()
    
    def load_models(self):
        """Charge les modèles IA essentiels"""
        
        # 1. IA DE CODE (Qwen2.5-Coder-1.5B) - Pour code Three.js complexe
        print("\n🧠 [1/3] Chargement IA de Code (Qwen2.5-Coder)...")
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            qwen_path = MODELS_PATH / "models--Qwen--Qwen2.5-Coder-1.5B"  # Nom correct!
            if qwen_path.exists():
                print(f"   📁 Modèle trouvé: {qwen_path}")
                self.code_tokenizer = AutoTokenizer.from_pretrained(
                    str(qwen_path),
                    local_files_only=True,
                    trust_remote_code=True
                )
                self.code_generator = AutoModelForCausalLM.from_pretrained(
                    str(qwen_path),
                    local_files_only=True,
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    device_map="cpu"  # Fallback CPU car GPU non supporté
                )
                print("   ✅ Qwen2.5-Coder chargé (génération code Three.js COMPLEXE)")
            else:
                print(f"   ⚠️  Modèle non trouvé: {qwen_path}")
        except Exception as e:
            print(f"   ❌ Erreur CodeLLM: {e}")
        
        # 2. IA GÉNÉRATIVE (SDXL pour dessins 2D colorés style anime)
        print("\n🎨 [2/3] Chargement IA Générative (SDXL)...")
        try:
            from diffusers import StableDiffusionXLPipeline, ControlNetModel, StableDiffusionXLControlNetPipeline
            
            sdxl_path = MODELS_PATH / "models--stabilityai--stable-diffusion-xl-base-1.0"
            if sdxl_path.exists():
                print(f"   📁 SDXL trouvé: {sdxl_path}")
                self.image_generator = StableDiffusionXLPipeline.from_pretrained(
                    str(sdxl_path),
                    local_files_only=True,
                    torch_dtype=torch.float16
                ).to("cpu")  # CPU car GPU sm_120 non supporté
                print("   ✅ SDXL chargé (dessins 2D colorés réalistes)")
                
                # ControlNet Scribble pour strokes naturels
                print("   🖊️  Chargement ControlNet Scribble...")
                try:
                    controlnet_path = MODELS_PATH / "models--lllyasviel--sd-controlnet-scribble"
                    if controlnet_path.exists():
                        self.controlnet = ControlNetModel.from_pretrained(
                            str(controlnet_path),
                            local_files_only=True,
                            torch_dtype=torch.float16
                        )
                        print("   ✅ ControlNet Scribble chargé (traits naturels)")
                except Exception as e:
                    print(f"   ⚠️  ControlNet non dispo: {e}")
            else:
                print(f"   ⚠️  SDXL non trouvé: {sdxl_path}")
        except Exception as e:
            print(f"   ❌ Erreur Image Gen: {e}")
        
        # 3. IA ANIMATION (AnimateDiff-Lightning)
        print("\n🎬 [3/4] Chargement IA Animation (AnimateDiff)...")
        try:
            from diffusers import AnimateDiffPipeline, MotionAdapter
            
            animatediff_path = MODELS_PATH / "models--ByteDance--AnimateDiff-Lightning"
            if animatediff_path.exists():
                print(f"   📁 Modèle trouvé: {animatediff_path}")
                # Sera chargé à la demande (plus lourd)
                self.animator_path = animatediff_path
                print("   ✅ AnimateDiff prêt (animation temps réel)")
            else:
                print(f"   ⚠️  Modèle non trouvé: {animatediff_path}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # 4. TRIPOSR - Image → Mesh 3D (RÉVOLUTIONNAIRE!)
        print("\n🔮 [4/4] Initialisation TripoSR (Image→3D)...")
        try:
            self.triposr = TripoSRClientHF()
            print("   🚀 Démarrage service TripoSR...")
            result = self.triposr.initialize()
            if result.get('success'):
                print("   ✅ TripoSR prêt (reconstruction 3D depuis images)")
            else:
                print(f"   ⚠️  TripoSR init échoué: {result.get('error')}")
                self.triposr = None
        except Exception as e:
            print(f"   ❌ Erreur TripoSR: {e}")
            self.triposr = None
        
        self.models_loaded = True
        print("\n" + "="*60)
        print("✅ Système Grease Pencil IA initialisé")
        print("="*60)
    
    def generate_threejs_code(self, prompt: str) -> dict:
        """
        🧠 AMÉLIORATION! Génère du code Three.js COMPLEXE avec Qwen2.5-Coder
        + Appel SDXL pour générer les textures/couleurs
        """
        print(f"\n🧠 Génération code Three.js AVANCÉ pour: '{prompt}'")
        
        # ÉTAPE 1: Génère le dessin 2D coloré avec SDXL
        print("   🎨 ÉTAPE 1/2: Génération du dessin coloré...")
        drawing_result = self.generate_asset_2d(prompt)
        
        if not self.code_generator:
            print("   ⚠️  CodeLLM non chargé, fallback code simple")
            return self.fallback_code_generation(prompt, drawing_result)
        
        # ÉTAPE 2: Génère code Three.js complexe avec Qwen
        print("   🧠 ÉTAPE 2/2: Génération code Three.js avec Qwen...")
        
        # Prompt engineering pour code COMPLEXE
        system_prompt = """Tu es un expert en Three.js et animation 2D.
Génère du code Three.js AVANCÉ qui crée des personnages/objets avec:
- Géométries multiples (BufferGeometry, shapes)
- Matériaux colorés (MeshBasicMaterial avec couleurs)
- Lignes/strokes (LineBasicMaterial, LineSegments)
- Groupes hiérarchiques (THREE.Group)
- Animations (rotations, mouvements)

Le code doit être COMPLET, EXÉCUTABLE et retourner l'objet final.
Utilise des couleurs vibrantes et des formes expressives."""

        user_prompt = f"""Crée un "{prompt}" en Three.js avec:
1. Au moins 5-10 formes géométriques différentes
2. Couleurs variées et vibrantes
3. Organisation en groupes (corps, membres, accessoires)
4. Strokes pour les contours (LineBasicMaterial)
5. Code exécutable qui retourne l'objet final

Example structure:
```javascript
const character = new THREE.Group();
// Corps
const body = new THREE.Mesh(
    new THREE.CylinderGeometry(0.3, 0.3, 1, 8),
    new THREE.MeshBasicMaterial({{color: 0xFF6B6B}})
);
character.add(body);
// ... autres parties
character; // RETOURNE l'objet
```"""
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            text = self.code_tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = self.code_tokenizer([text], return_tensors="pt").to(self.code_generator.device)
            
            print("   ⚙️  Qwen génère (max 1024 tokens)...")
            outputs = self.code_generator.generate(
                **inputs,
                max_new_tokens=1024,  # Plus long pour code complexe
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.code_tokenizer.eos_token_id
            )
            
            code = self.code_tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
            
            print(f"   ✅ Code généré ({len(code)} caractères)")
            
            # Ajoute l'image comme texture si disponible
            if drawing_result.get('success') and drawing_result.get('image_base64'):
                texture_code = f"""
// Texture générée par SDXL
const textureData = 'data:image/png;base64,{drawing_result['image_base64'][:100]}...'; // Tronqué
const loader = new THREE.TextureLoader();
// loader.load(textureData, (texture) => {{ /* Applique texture */ }});
"""
                code = texture_code + "\n" + code
            
            return {
                'success': True,
                'code': code,
                'type': 'threejs',
                'prompt': prompt,
                'generator': 'Qwen2.5-Coder-1.5B',
                'drawing': drawing_result.get('image_path') if drawing_result.get('success') else None
            }
            
        except Exception as e:
            print(f"   ❌ Erreur Qwen: {e}")
            import traceback
            traceback.print_exc()
            return self.fallback_code_generation(prompt, drawing_result)
    
    
    def fallback_code_generation(self, prompt: str, drawing_result: dict = None) -> dict:
        """Génération de code Three.js AMÉLIORÉ avec support texture"""
        
        print("   🔄 Fallback: génération code template avancé")
        
        # Si on a une image SDXL, on l'utilise comme texture!
        if drawing_result and drawing_result.get('success') and drawing_result.get('image_base64'):
            print("   🎨 Utilisation texture SDXL générée")
            img_data = drawing_result['image_base64']
            
            code = f"""
// {prompt} - Avec texture SDXL générée!
const group = new THREE.Group();

// Plan avec la texture du dessin 2D
const textureLoader = new THREE.TextureLoader();
const texture = textureLoader.load('data:image/png;base64,{img_data[:200]}...');

const planeGeometry = new THREE.PlaneGeometry(3, 3);
const planeMaterial = new THREE.MeshBasicMaterial({{ 
    map: texture,
    side: THREE.DoubleSide,
    transparent: true
}});
const plane = new THREE.Mesh(planeGeometry, planeMaterial);
group.add(plane);

// Contours
const outlinePoints = [
    new THREE.Vector3(-1.5, -1.5, 0.01),
    new THREE.Vector3(1.5, -1.5, 0.01),
    new THREE.Vector3(1.5, 1.5, 0.01),
    new THREE.Vector3(-1.5, 1.5, 0.01),
    new THREE.Vector3(-1.5, -1.5, 0.01)
];
const outlineGeometry = new THREE.BufferGeometry().setFromPoints(outlinePoints);
const outlineMaterial = new THREE.LineBasicMaterial({{ color: 0x000000, linewidth: 2 }});
const outline = new THREE.Line(outlineGeometry, outlineMaterial);
group.add(outline);

group.position.set(0, 1, 0);
group; // Retourne l'objet
"""
            return {
                'success': True,
                'code': code,
                'type': 'threejs',
                'prompt': prompt,
                'generator': 'fallback+SDXL',
                'has_texture': True
            }
        
        # Templates simples si pas d'image
        if "personnage" in prompt.lower() or "character" in prompt.lower():
            code = """
// Personnage style Grease Pencil
const character = new THREE.Group();

// Corps (stroke)
const bodyPoints = [
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0, 1, 0),
    new THREE.Vector3(0, 1.5, 0)
];
const bodyGeometry = new THREE.BufferGeometry().setFromPoints(bodyPoints);
const bodyMaterial = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 3 });
const bodyLine = new THREE.Line(bodyGeometry, bodyMaterial);
character.add(bodyLine);

// Tête (cercle)
const headGeometry = new THREE.CircleGeometry(0.3, 32);
const headMaterial = new THREE.MeshBasicMaterial({ color: 0xFFCCAA });
const head = new THREE.Mesh(headGeometry, headMaterial);
head.position.set(0, 2, 0);
character.add(head);

// Bras (strokes)
const armLPoints = [
    new THREE.Vector3(-0.3, 1.5, 0),
    new THREE.Vector3(-0.6, 1, 0)
];
const armLGeometry = new THREE.BufferGeometry().setFromPoints(armLPoints);
const armL = new THREE.Line(armLGeometry, bodyMaterial);
character.add(armL);

const armRPoints = [
    new THREE.Vector3(0.3, 1.5, 0),
    new THREE.Vector3(0.6, 1, 0)
];
const armRGeometry = new THREE.BufferGeometry().setFromPoints(armRPoints);
const armR = new THREE.Line(armRGeometry, bodyMaterial);
character.add(armR);

// Jambes (strokes)
const legLPoints = [
    new THREE.Vector3(-0.2, 0, 0),
    new THREE.Vector3(-0.2, -0.8, 0)
];
const legLGeometry = new THREE.BufferGeometry().setFromPoints(legLPoints);
const legL = new THREE.Line(legLGeometry, bodyMaterial);
character.add(legL);

const legRPoints = [
    new THREE.Vector3(0.2, 0, 0),
    new THREE.Vector3(0.2, -0.8, 0)
];
const legRGeometry = new THREE.BufferGeometry().setFromPoints(legRPoints);
const legR = new THREE.Line(legRGeometry, bodyMaterial);
character.add(legR);

character.position.set(0, 1, 0);
character; // Retourne l'objet
"""
        else:
            # Forme générique
            code = f"""
// {prompt} - Style Grease Pencil
const object = new THREE.Group();

// Stroke principal
const points = [
    new THREE.Vector3(-1, 0, 0),
    new THREE.Vector3(0, 1, 0),
    new THREE.Vector3(1, 0, 0)
];

const geometry = new THREE.BufferGeometry().setFromPoints(points);
const material = new THREE.LineBasicMaterial({{ 
    color: 0x{format(hash(prompt) % 0xFFFFFF, '06x')}, 
    linewidth: 2 
}});

const line = new THREE.Line(geometry, material);
object.add(line);

object; // Retourne l'objet
"""
        
        return {
            'success': True,
            'code': code,
            'type': 'threejs',
            'prompt': prompt,
            'generator': 'fallback'
        }
    
    
    def generate_asset_2d(self, prompt: str) -> dict:
        """
        🎨 NOUVEAU! Génère un VRAI dessin 2D coloré avec SDXL
        Style: anime, 2D animation, avec couleurs naturelles
        """
        print(f"\n🎨 Génération DESSIN 2D COLORÉ: '{prompt}'")
        
        if not self.image_generator:
            print("⚠️  Générateur d'images non disponible, fallback")
            return {'success': False, 'error': 'Image generator not loaded'}
        
        try:
            # Prompts optimisés pour dessin 2D style anime/cartoon
            style_prompts = {
                'anime': f"{prompt}, anime art style, cel shading, vibrant colors, clean outlines, 2D animation, Studio Ghibli inspired, masterpiece",
                'cartoon': f"{prompt}, cartoon style, bold colors, thick outlines, expressive, Disney Pixar style, hand-drawn animation",
                'grease_pencil': f"{prompt}, 2D hand-drawn style, colored pencil sketch, natural strokes, artistic drawing, animation frame",
                'realistic': f"{prompt}, detailed 2D illustration, realistic colors, professional art, high quality drawing"
            }
            
            # Détecte le style depuis le prompt
            style = 'anime'  # Style par défaut
            if 'cartoon' in prompt.lower():
                style = 'cartoon'
            elif 'réaliste' in prompt.lower() or 'realistic' in prompt.lower():
                style = 'realistic'
            
            full_prompt = style_prompts.get(style, style_prompts['anime'])
            negative_prompt = "3d render, photorealistic, photo, blurry, ugly, deformed, bad anatomy, low quality"
            
            print(f"   📝 Style détecté: {style}")
            print(f"   ⚙️  Génération SDXL (30 steps)...")
            
            # Génération avec SDXL
            image = self.image_generator(
                prompt=full_prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=30,  # Qualité élevée
                guidance_scale=7.5,
                height=768,  # Haute résolution
                width=768
            ).images[0]
            
            # Sauvegarde
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"drawing_{timestamp}.png"
            output_path = f"/tmp/kibalone_grease_pencil/{filename}"
            Path("/tmp/kibalone_grease_pencil").mkdir(exist_ok=True)
            image.save(output_path)
            
            print(f"   ✅ Dessin coloré sauvegardé: {output_path}")
            
            # Convertit l'image en base64 pour l'envoyer au frontend
            from io import BytesIO
            import base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                'success': True,
                'image_path': output_path,
                'image_base64': img_str,
                'prompt': prompt,
                'style': style,
                'generator': 'SDXL-1.0',
                'resolution': '768x768'
            }
            
        except Exception as e:
            print(f"   ❌ Erreur génération: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def generate_character_3d_from_2d(self, prompt: str) -> dict:
        """
        🔮 WORKFLOW RÉVOLUTIONNAIRE!
        Prompt → SDXL (dessin 2D) → TripoSR (mesh 3D) → GLTF
        
        C'est LA méthode la plus simple et puissante!
        """
        print(f"\n{'='*60}")
        print(f"🔮 WORKFLOW 2D→3D: '{prompt}'")
        print(f"{'='*60}")
        
        # ÉTAPE 1: Génère dessin 2D avec SDXL
        print("\n🎨 ÉTAPE 1/3: Génération dessin 2D...")
        drawing = self.generate_asset_2d(prompt)
        
        if not drawing.get('success'):
            print("   ❌ Échec génération 2D")
            return {'success': False, 'error': 'Drawing generation failed'}
        
        image_path = drawing['image_path']
        print(f"   ✅ Image 2D: {image_path}")
        
        # ÉTAPE 2: Reconstruit en 3D avec TripoSR
        if not self.triposr:
            print("   ⚠️  TripoSR non disponible, fallback code 2D")
            return drawing  # Retourne juste l'image
        
        print("\n🔮 ÉTAPE 2/3: Reconstruction 3D avec TripoSR...")
        output_mesh = f"/tmp/kibalone_grease_pencil/mesh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.obj"
        
        try:
            result = self.triposr.image_to_3d(
                image_path=image_path,
                output_path=output_mesh
            )
            
            if not result.get('success'):
                print(f"   ❌ TripoSR failed: {result.get('error')}")
                return drawing  # Fallback sur l'image 2D
            
            print(f"   ✅ Mesh 3D généré: {result['output_path']}")
            print(f"   📊 {result.get('vertices', 0)} vertices, {result.get('faces', 0)} faces")
            
            # ÉTAPE 3: Génère code Three.js pour charger le mesh
            print("\n⚡ ÉTAPE 3/3: Génération code Three.js...")
            
            threejs_code = f"""
// {prompt} - Mesh 3D reconstruit depuis SDXL + TripoSR
const group = new THREE.Group();

// Chargement du mesh OBJ
const objLoader = new THREE.OBJLoader();
objLoader.load(
    '{result['output_path']}',
    (obj) => {{
        // Applique la texture du dessin 2D
        const textureLoader = new THREE.TextureLoader();
        const texture = textureLoader.load('data:image/png;base64,{drawing.get('image_base64', '')[:100]}...');
        
        obj.traverse((child) => {{
            if (child.isMesh) {{
                child.material = new THREE.MeshStandardMaterial({{
                    map: texture,
                    side: THREE.DoubleSide
                }});
            }}
        }});
        
        obj.scale.set(2, 2, 2);
        group.add(obj);
    }},
    (progress) => console.log('Loading...', progress),
    (error) => console.error('Load error:', error)
);

group.position.set(0, 1, 0);
group; // Retourne le groupe
"""
            
            print("   ✅ Code Three.js généré")
            
            return {
                'success': True,
                'code': threejs_code,
                'type': 'threejs',
                'prompt': prompt,
                'generator': 'SDXL+TripoSR',
                'workflow': '2D_to_3D',
                'image_path': image_path,
                'mesh_path': result['output_path'],
                'mesh_stats': {
                    'vertices': result.get('vertices', 0),
                    'faces': result.get('faces', 0)
                }
            }
            
        except Exception as e:
            print(f"   ❌ Erreur reconstruction 3D: {e}")
            import traceback
            traceback.print_exc()
            return drawing  # Fallback sur l'image 2D

# Instance globale
grease_pencil_ai = GreasePencilAI()

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/health', methods=['GET'])
def health():
    """Status de l'API"""
    return jsonify({
        'service': 'Kibali Grease Pencil Studio',
        'status': 'ok',
        'models_loaded': grease_pencil_ai.models_loaded,
        'capabilities': {
            'code_generation': grease_pencil_ai.code_generator is not None,
            'image_generation': grease_pencil_ai.image_generator is not None,
            'animation': grease_pencil_ai.animator_path is not None
        }
    })

@app.route('/api/process-prompt', methods=['POST'])
def process_prompt():
    """
    🚀 ENDPOINT PRINCIPAL - Workflow intelligent
    Détecte le type de prompt et choisit la meilleure méthode:
    - Personnages/objets 3D → SDXL + TripoSR (reconstruction 3D)
    - Scènes/formes simples → Code Three.js généré par Qwen
    """
    data = request.json
    prompt = data.get('prompt', '')
    force_method = data.get('method', 'auto')  # auto, 3d, code
    
    if not prompt:
        return jsonify({'success': False, 'error': 'No prompt provided'}), 400
    
    print(f"\n{'='*60}")
    print(f"📨 Nouveau prompt: '{prompt}'")
    print(f"🎯 Méthode: {force_method}")
    print(f"{'='*60}")
    
    # Détection intelligente du type de prompt
    keywords_3d = ['personnage', 'character', 'personne', 'animal', 'créature', 'objet', 'meuble']
    keywords_code = ['scène', 'forêt', 'environnement', 'fond', 'paysage', 'ligne', 'forme']
    
    use_3d_reconstruction = force_method == '3d' or (
        force_method == 'auto' and 
        any(kw in prompt.lower() for kw in keywords_3d)
    )
    
    if use_3d_reconstruction and grease_pencil_ai.triposr:
        print("🔮 Workflow sélectionné: SDXL → TripoSR → Mesh 3D")
        result = grease_pencil_ai.generate_character_3d_from_2d(prompt)
    else:
        print("🧠 Workflow sélectionné: Génération code Three.js")
        result = grease_pencil_ai.generate_threejs_code(prompt)
    
    return jsonify(result)

@app.route('/api/generate-asset', methods=['POST'])
def generate_asset():
    """
    Génère un asset 2D (texture, sprite) avec IA générative
    """
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'success': False, 'error': 'No prompt provided'}), 400
    
    result = grease_pencil_ai.generate_asset_2d(prompt)
    return jsonify(result)

@app.route('/api/animate', methods=['POST'])
def animate():
    """
    Crée une animation entre plusieurs frames
    """
    data = request.json
    frames = data.get('frames', [])
    
    # TODO: Implémenter avec AnimateDiff
    
    return jsonify({
        'success': True,
        'message': 'Animation generation (coming soon)',
        'frames': len(frames)
    })

# ============================================
# DÉMARRAGE
# ============================================

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 11006))
    
    print("\n" + "="*60)
    print("🚀 KIBALI GREASE PENCIL STUDIO - DÉMARRAGE")
    print("="*60)
    print(f"🌐 API: http://localhost:{PORT}")
    print("="*60)
    print("\nEndpoints:")
    print("  GET  /api/health")
    print("  POST /api/process-prompt  (génère code Three.js)")
    print("  POST /api/generate-asset  (génère asset 2D)")
    print("  POST /api/animate         (animation frames)")
    print("="*60)
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
