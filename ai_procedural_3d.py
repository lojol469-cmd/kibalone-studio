#!/usr/bin/env python3
"""
Générateur 3D par CODE IA - Multi-Model Edition
L'IA génère du CODE JavaScript Three.js avec CodeLlama-7B OU Qwen2.5-Coder
Choisit automatiquement le meilleur modèle disponible
"""

import sys
import os
from pathlib import Path
import torch

# Paths centralisés
ISOL_PATH = Path("/home/belikan/Isol")
sys.path.insert(0, str(ISOL_PATH / "kibali-IA"))

from transformers import AutoModelForCausalLM, AutoTokenizer

class AIProceduralGenerator:
    """L'IA génère du CODE avec CodeLlama-7B ou Qwen2.5-Coder"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Liste des modèles disponibles (par ordre de préférence)
        self.available_models = [
            {
                'name': 'CodeLlama-7b',
                'path': '/home/belikan/Isol/kibali-IA/kibali_data/models/huggingface_cache/models--codellama--CodeLlama-7b-hf/snapshots/6c284d1468fe6c413cf56183e69b194dcfa27fe6',
                'priority': 1  # Préféré: plus gros, meilleur pour code
            }
        ]
        
        print(f"🚀 Initialisation Générateur Code IA...")
        print(f"   Device: {self.device}")
        
        # Charge le premier modèle disponible
        self.model = None
        self.tokenizer = None
        self.model_name = None
        
        for model_info in self.available_models:
            if self._try_load_model(model_info):
                break
        
        if self.model is None:
            print("⚠️  Aucun modèle local disponible, fallback vers API HuggingFace")
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(token=os.getenv("HF_TOKEN"))
            self.fallback_model = "mistralai/Mistral-7B-Instruct-v0.2"
        
        print(f"🎨 Générateur Procédural IA actif")
    
    def _try_load_model(self, model_info):
        """Essaie de charger un modèle"""
        try:
            model_path = Path(model_info['path'])
            
            # Vérifie si le modèle existe
            if not model_path.exists():
                print(f"⚠️  {model_info['name']}: modèle introuvable à {model_path}")
                return False
            
            print(f"📦 Chargement de {model_info['name']}...")
            
            # Charge le tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(model_path),
                trust_remote_code=True,
                local_files_only=True
            )
            
            # Charge le modèle avec optimisations
            self.model = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                trust_remote_code=True,
                local_files_only=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            self.model.eval()
            self.model_name = model_info['name']
            
            print(f"✅ {model_info['name']} chargé sur {self.device}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur chargement {model_info['name']}: {e}")
            return False
    
    def generate_3d_code(self, prompt, object_type='character'):
        """Génère du CODE JavaScript Three.js avec le modèle chargé"""
        
        system_prompt = f"""You are a Three.js expert. Generate ONLY executable JavaScript code.

CRITICAL RULES:
1. Return PURE JavaScript, NO markdown, NO explanations
2. Use THREE.Group() as container
3. Code MUST work with eval() in browser context
4. Use ONLY: BoxGeometry, SphereGeometry, CylinderGeometry, PlaneGeometry, ConeGeometry
5. Apply MeshStandardMaterial with colors (0xRRGGBB hex format)
6. Use position.set(x,y,z), rotation.set(), scale.set()
7. END with variable name WITHOUT 'return': just write 'obj;' NOT 'return obj;'
8. NO texture loading, NO fetch(), NO external files
9. NO console.log, NO comments
10. Variable names: obj, tree, character, env (common names)

CORRECT EXAMPLE:
const tree = new THREE.Group();
const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.3,0.4,3), new THREE.MeshStandardMaterial({{color: 0x8B4513}}));
trunk.position.y = 1.5;
tree.add(trunk);
const leaves = new THREE.Mesh(new THREE.SphereGeometry(1.5), new THREE.MeshStandardMaterial({{color: 0x228B22}}));
leaves.position.y = 3.5;
tree.add(leaves);
tree;

WRONG (DO NOT USE return):
return tree; // ILLEGAL IN EVAL!
"""
        
        user_prompt = f"Create: {prompt} (type: {object_type}). Return code WITHOUT 'return' keyword."
        
        print(f"🤖 [{self.model_name or 'API'}] Génération: {prompt}")
        
        try:
            # Si modèle local disponible
            if self.model is not None:
                # Format prompt selon le modèle
                if 'CodeLlama' in self.model_name:
                    # CodeLlama préfère un format simple
                    text = f"{system_prompt}\n\n{user_prompt}\n\n"
                else:
                    # Qwen2.5-Coder utilise chat template
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                    text = self.tokenizer.apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=True
                    )
                
                inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
                
                # Génère avec paramètres optimisés
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=1024,
                        temperature=0.2,  # Très bas pour code précis
                        top_p=0.9,
                        do_sample=True,
                        pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id
                    )
                
                response = self.tokenizer.decode(
                    outputs[0][inputs['input_ids'].shape[1]:], 
                    skip_special_tokens=True
                )
                
                print(f"   Réponse brute: {len(response)} chars")
                
            else:
                # Fallback API HuggingFace
                print("⚠️  Fallback API HuggingFace")
                response = ""
                stream = self.client.chat.completions.create(
                    model=self.fallback_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        response += chunk.choices[0].delta.content
            
            # Nettoie et extrait le code
            code = self.extract_javascript_code(response)
            
            # Valide le code
            if not self.validate_code(code):
                print(f"⚠️  Code invalide, utilisation fallback")
                code = self.get_fallback_code(object_type)
            
            print(f"✅ Code généré: {len(code)} chars")
            
            return {
                'success': True,
                'code': code,
                'raw_response': response
            }
            
        except Exception as e:
            print(f"❌ Erreur génération: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'code': self.get_fallback_code(object_type)
            }
    
    def validate_code(self, code):
        """Valide que le code contient les éléments essentiels"""
        required = ['THREE.', 'new THREE.', 'Group', 'Mesh']
        return any(req in code for req in required) and len(code) > 50
    
    def extract_javascript_code(self, text):
        """Extrait le code JavaScript du texte"""
        # Enlève les balises markdown
        if '```javascript' in text:
            code = text.split('```javascript')[1].split('```')[0].strip()
        elif '```js' in text:
            code = text.split('```js')[1].split('```')[0].strip()
        elif '```' in text:
            code = text.split('```')[1].split('```')[0].strip()
        else:
            # Prend tout si pas de markdown
            code = text.strip()
        
        return code
    
    def get_fallback_code(self, object_type):
        """Code de fallback si l'IA échoue"""
        fallback = {
            'character': """
const character = new THREE.Group();
const body = new THREE.Mesh(
    new THREE.BoxGeometry(0.6, 1.2, 0.3),
    new THREE.MeshStandardMaterial({color: 0x4488ff})
);
body.position.y = 1.2;
character.add(body);
const head = new THREE.Mesh(
    new THREE.SphereGeometry(0.25, 16, 16),
    new THREE.MeshStandardMaterial({color: 0xffcc88})
);
head.position.y = 2.0;
character.add(head);
character;
""",
            'object': """
const obj = new THREE.Mesh(
    new THREE.BoxGeometry(1, 1, 1),
    new THREE.MeshStandardMaterial({color: 0xff5533})
);
obj;
""",
            'environment': """
const env = new THREE.Group();
const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(10, 10),
    new THREE.MeshStandardMaterial({color: 0x33aa33})
);
ground.rotation.x = -Math.PI / 2;
env.add(ground);
env;
"""
        }
        return fallback.get(object_type, fallback['object'])
    
    def generate_animation_code(self, prompt, object_name='object'):
        """Génère du code d'animation"""
        
        system_prompt = """Tu es expert en animation Three.js. Génère du CODE pour animer un objet.

RÈGLES:
1. Code JavaScript pur uniquement
2. Utilise la variable 'frame' (0 à frameCount)
3. Modifie position, rotation, scale de l'objet
4. Utilise Math.sin, Math.cos pour animations fluides
5. Return l'objet modifié

EXEMPLE:
```javascript
object.position.y = Math.sin(frame * 0.1) * 0.5;
object.rotation.y = frame * 0.02;
object;
```"""
        
        user_prompt = f"""Animation: {prompt}
Objet: {object_name}

CODE JAVASCRIPT:"""
        
        print(f"🎬 [IA] Génération animation: {prompt}")
        
        try:
            response = ""
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=400,
                temperature=0.7,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    response += chunk.choices[0].delta.content
            
            code = self.extract_javascript_code(response)
            print(f"✅ [IA] Animation générée")
            
            return {
                'success': True,
                'code': code
            }
            
        except Exception as e:
            print(f"❌ [IA] Erreur animation: {e}")
            return {
                'success': False,
                'code': f"{object_name}.rotation.y += 0.01; {object_name};"
            }
    
    def generate_camera_code(self, prompt):
        """Génère du code pour mouvement caméra"""
        
        system_prompt = """Tu es expert en cinématographie 3D. Génère du CODE pour mouvement de caméra.

RÈGLES:
1. Code JavaScript uniquement
2. Utilise la variable 'frame' pour progression
3. Modifie camera.position et camera.lookAt()
4. Mouvements fluides avec Math.sin/cos

EXEMPLE:
```javascript
const angle = frame * 0.02;
camera.position.x = Math.cos(angle) * 5;
camera.position.z = Math.sin(angle) * 5;
camera.lookAt(0, 1, 0);
```"""
        
        user_prompt = f"""Mouvement caméra: {prompt}

CODE JAVASCRIPT:"""
        
        print(f"🎥 [IA] Génération caméra: {prompt}")
        
        try:
            response = ""
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=400,
                temperature=0.7,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    response += chunk.choices[0].delta.content
            
            code = self.extract_javascript_code(response)
            print(f"✅ [IA] Caméra générée")
            
            return {
                'success': True,
                'code': code
            }
            
        except Exception as e:
            print(f"❌ [IA] Erreur caméra: {e}")
            return {
                'success': False,
                'code': "camera.position.z = 5;"
            }


# ============================================
# API
# ============================================

generator = None

def init_ai_generator():
    """Initialise le générateur IA"""
    global generator
    if generator is None:
        generator = AIProceduralGenerator()
    return generator

def generate_3d_by_ai(prompt, object_type='character'):
    """Génère la 3D via code IA"""
    gen = init_ai_generator()
    return gen.generate_3d_code(prompt, object_type)

def generate_animation_by_ai(prompt, object_name='object'):
    """Génère l'animation via code IA"""
    gen = init_ai_generator()
    return gen.generate_animation_code(prompt, object_name)

def generate_camera_by_ai(prompt):
    """Génère le mouvement caméra via code IA"""
    gen = init_ai_generator()
    return gen.generate_camera_code(prompt)


# ============================================
# Test
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("🎨 TEST GÉNÉRATEUR PROCÉDURAL IA")
    print("="*60)
    
    gen = AIProceduralGenerator()
    
    # Test 1: Génération personnage
    print("\n1️⃣ Test: Personnage robot")
    result = gen.generate_3d_code("un robot futuriste avec antennes", "character")
    if result['success']:
        print(f"✅ Code généré:\n{result['code'][:200]}...")
    else:
        print(f"❌ Échec")
    
    # Test 2: Animation
    print("\n2️⃣ Test: Animation marche")
    result = gen.generate_animation_code("marche sur place", "character")
    if result['success']:
        print(f"✅ Animation:\n{result['code'][:150]}...")
    
    print("\n✅ Tests terminés !")
