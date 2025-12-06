#!/usr/bin/env python3
"""
Générateur 3D JSON - Double IA
Kibali analyse → Mistral code → JSON → Three.js
"""

import sys
import os
import json
from pathlib import Path

ISOL_PATH = Path("/home/belikan/Isol")
sys.path.insert(0, str(ISOL_PATH / "kibali-IA"))

from huggingface_hub import InferenceClient

class DualAI3DGenerator:
    """Double IA pour génération 3D"""
    
    def __init__(self):
        self.client = InferenceClient(token=os.getenv("HF_TOKEN"))
        self.kibali_model = "mistralai/Mistral-7B-Instruct-v0.2"
        self.coder_model = "mistralai/Mistral-7B-Instruct-v0.2"
        print(f"🤖 Double IA 3D Generator ready!")
    
    def analyze_with_kibali(self, prompt):
        """Kibali analyse le prompt et décrit le modèle"""
        
        system_prompt = """Tu es Kibali, expert en modélisation 3D.
Analyse le prompt et décris PRÉCISÉMENT le modèle 3D à créer.

Format de réponse (JSON strict):
{
  "type": "character/object/environment",
  "parts": [
    {"name": "body", "shape": "box/sphere/cylinder", "size": [w,h,d], "position": [x,y,z], "color": "0xFF0000", "material": "standard/basic"},
    {"name": "head", "shape": "sphere", "size": [r], "position": [x,y,z], "color": "0xFFCC88"}
  ],
  "style": "realistic/cartoon/robot/fantasy",
  "scale": 1.0
}

IMPORTANT: Réponds UNIQUEMENT avec le JSON, rien d'autre."""
        
        print(f"🧠 [KIBALI] Analyse: {prompt}")
        
        try:
            response = ""
            stream = self.client.chat.completions.create(
                model=self.kibali_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Décris le modèle 3D pour: {prompt}"}
                ],
                max_tokens=600,
                temperature=0.7,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    response += chunk.choices[0].delta.content
            
            # Extrait le JSON
            json_data = self.extract_json(response)
            print(f"✅ [KIBALI] Analyse complète")
            
            return json_data
            
        except Exception as e:
            print(f"❌ [KIBALI] Erreur: {e}")
            return self.get_fallback_structure(prompt)
    
    def extract_json(self, text):
        """Extrait le JSON du texte"""
        try:
            # Cherche entre { }
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
            else:
                return None
        except:
            return None
    
    def get_fallback_structure(self, prompt):
        """Structure par défaut si Kibali échoue"""
        prompt_lower = prompt.lower()
        
        if 'robot' in prompt_lower:
            return {
                "type": "character",
                "parts": [
                    {"name": "body", "shape": "box", "size": [0.8, 1.2, 0.6], "position": [0, 1.5, 0], "color": "0x888888", "material": "standard"},
                    {"name": "head", "shape": "box", "size": [0.6, 0.6, 0.6], "position": [0, 2.5, 0], "color": "0xAAAAAA", "material": "standard"},
                    {"name": "eye1", "shape": "sphere", "size": [0.1], "position": [-0.2, 2.5, 0.35], "color": "0x00FFFF", "material": "basic"},
                    {"name": "eye2", "shape": "sphere", "size": [0.1], "position": [0.2, 2.5, 0.35], "color": "0x00FFFF", "material": "basic"}
                ],
                "style": "robot",
                "scale": 1.0
            }
        elif any(word in prompt_lower for word in ['guerrier', 'knight', 'hero', 'héros']):
            return {
                "type": "character",
                "parts": [
                    {"name": "body", "shape": "box", "size": [0.7, 1.3, 0.4], "position": [0, 1.5, 0], "color": "0x8B4513", "material": "standard"},
                    {"name": "armor", "shape": "box", "size": [0.75, 0.8, 0.45], "position": [0, 1.7, 0], "color": "0xC0C0C0", "material": "standard"},
                    {"name": "head", "shape": "sphere", "size": [0.3], "position": [0, 2.4, 0], "color": "0xFFDBAC", "material": "standard"},
                    {"name": "helmet", "shape": "sphere", "size": [0.35], "position": [0, 2.5, 0], "color": "0xFFD700", "material": "standard"},
                    {"name": "cape", "shape": "box", "size": [0.9, 1.2, 0.1], "position": [0, 1.5, -0.3], "color": "0xFF0000", "material": "standard"}
                ],
                "style": "fantasy",
                "scale": 1.0
            }
        else:
            return {
                "type": "character",
                "parts": [
                    {"name": "body", "shape": "box", "size": [0.6, 1.2, 0.3], "position": [0, 1.2, 0], "color": "0x4488FF", "material": "standard"},
                    {"name": "head", "shape": "sphere", "size": [0.25], "position": [0, 2.0, 0], "color": "0xFFCC88", "material": "standard"}
                ],
                "style": "simple",
                "scale": 1.0
            }
    
    def json_to_threejs_code(self, json_structure, name="object"):
        """Convertit le JSON en code Three.js"""
        
        print(f"🎨 [BUILDER] Génération code Three.js...")
        
        code = f"const {name} = new THREE.Group();\n\n"
        
        for part in json_structure.get('parts', []):
            part_name = part['name']
            shape = part['shape']
            size = part['size']
            pos = part['position']
            color = part['color']
            material_type = part.get('material', 'standard')
            
            # Géométrie
            if shape == 'box':
                geometry = f"new THREE.BoxGeometry({size[0]}, {size[1]}, {size[2]})"
            elif shape == 'sphere':
                radius = size[0]
                geometry = f"new THREE.SphereGeometry({radius}, 16, 16)"
            elif shape == 'cylinder':
                radius = size[0] if len(size) > 0 else 0.1
                height = size[1] if len(size) > 1 else 1.0
                geometry = f"new THREE.CylinderGeometry({radius}, {radius}, {height})"
            else:
                geometry = "new THREE.BoxGeometry(1, 1, 1)"
            
            # Matériau
            if material_type == 'basic':
                material = f"new THREE.MeshBasicMaterial({{color: {color}}})"
            else:
                material = f"new THREE.MeshStandardMaterial({{color: {color}, metalness: 0.3, roughness: 0.7}})"
            
            # Mesh
            code += f"const {part_name} = new THREE.Mesh(\n"
            code += f"    {geometry},\n"
            code += f"    {material}\n"
            code += f");\n"
            code += f"{part_name}.position.set({pos[0]}, {pos[1]}, {pos[2]});\n"
            code += f"{part_name}.castShadow = true;\n"
            code += f"{part_name}.receiveShadow = true;\n"
            code += f"{name}.add({part_name});\n\n"
        
        # Ajoute bras et jambes si c'est un personnage
        if json_structure.get('type') == 'character':
            code += self.add_limbs_code(name)
        
        code += f"return {name};"
        
        print(f"✅ [BUILDER] Code généré: {len(code)} chars")
        
        return code
    
    def add_limbs_code(self, name):
        """Ajoute bras et jambes automatiquement"""
        code = "// Bras\n"
        code += "const armLeft = new THREE.Mesh(\n"
        code += "    new THREE.CylinderGeometry(0.1, 0.1, 0.8),\n"
        code += "    new THREE.MeshStandardMaterial({color: 0x4488FF})\n"
        code += ");\n"
        code += "armLeft.position.set(-0.5, 1.4, 0);\n"
        code += "armLeft.rotation.z = 0.3;\n"
        code += f"{name}.add(armLeft);\n\n"
        
        code += "const armRight = armLeft.clone();\n"
        code += "armRight.position.set(0.5, 1.4, 0);\n"
        code += "armRight.rotation.z = -0.3;\n"
        code += f"{name}.add(armRight);\n\n"
        
        code += "// Jambes\n"
        code += "const legLeft = new THREE.Mesh(\n"
        code += "    new THREE.CylinderGeometry(0.12, 0.12, 1.0),\n"
        code += "    new THREE.MeshStandardMaterial({color: 0x333366})\n"
        code += ");\n"
        code += "legLeft.position.set(-0.2, 0.5, 0);\n"
        code += f"{name}.add(legLeft);\n\n"
        
        code += "const legRight = legLeft.clone();\n"
        code += "legRight.position.set(0.2, 0.5, 0);\n"
        code += f"{name}.add(legRight);\n\n"
        
        return code
    
    def generate_3d_model(self, prompt):
        """Pipeline complet: Prompt → JSON → Code Three.js"""
        
        print(f"\n{'='*60}")
        print(f"🚀 GÉNÉRATION 3D COMPLÈTE: {prompt}")
        print(f"{'='*60}\n")
        
        # 1. Kibali analyse
        json_structure = self.analyze_with_kibali(prompt)
        
        if not json_structure:
            json_structure = self.get_fallback_structure(prompt)
        
        # 2. Génère le code Three.js
        code = self.json_to_threejs_code(json_structure, "character")
        
        return {
            'success': True,
            'json_structure': json_structure,
            'code': code,
            'prompt': prompt
        }


# ============================================
# API
# ============================================

generator = None

def init_dual_ai_generator():
    global generator
    if generator is None:
        generator = DualAI3DGenerator()
    return generator

def generate_with_dual_ai(prompt):
    gen = init_dual_ai_generator()
    return gen.generate_3d_model(prompt)


# ============================================
# Test
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("🤖 TEST DOUBLE IA 3D GENERATOR")
    print("="*60)
    
    gen = DualAI3DGenerator()
    
    # Test
    result = gen.generate_3d_model("un robot spatial avec laser")
    
    if result['success']:
        print("\n✅ SUCCÈS !")
        print(f"\n📋 JSON Structure:")
        print(json.dumps(result['json_structure'], indent=2))
        print(f"\n💻 Code Three.js:")
        print(result['code'][:300] + "...")
    
    print("\n" + "="*60)
    print("✅ Test terminé !")
    print("="*60)
