#!/usr/bin/env python3
"""
Générateur 3D Avancé - Multiple méthodes
1. Code IA procédural (rapide, formes simples)
2. TripoSR (réaliste, depuis image ou texte)
3. Grease Pencil IA (dessin 2D → 3D)
4. Modélisation avancée (comme Blender, via code)
"""

import sys
import os
from pathlib import Path

ISOL_PATH = Path("/home/belikan/Isol")
sys.path.insert(0, str(ISOL_PATH / "kibali-IA"))

from huggingface_hub import InferenceClient
import json


class Advanced3DGenerator:
    """Générateur 3D avec méthodes multiples"""
    
    def __init__(self):
        self.client = InferenceClient(token=os.getenv("HF_TOKEN"))
        self.model = "mistralai/Mistral-7B-Instruct-v0.2"
        print("🎨 Générateur 3D Avancé initialisé")
    
    def generate_advanced_character(self, prompt):
        """Génère un personnage détaillé avec anatomie"""
        
        system_prompt = """Tu es un expert en modélisation 3D humanoïde avec Three.js.
Génère un personnage DÉTAILLÉ avec :
- Tête (sphère + détails visage)
- Torse (box avec forme)
- Bras gauche/droit (cylindres articulés)
- Mains (petites sphères)
- Jambes gauche/droite (cylindres)
- Pieds (boxes)

Code JavaScript pur, utilisable directement.
Retourne UNIQUEMENT le code, pas d'explication."""

        user_prompt = f"""Crée ce personnage en Three.js: {prompt}

Structure attendue:
```javascript
const character = new THREE.Group();

// Tête
const head = new THREE.Mesh(
    new THREE.SphereGeometry(0.3, 32, 32),
    new THREE.MeshStandardMaterial({{color: 0xFFCC88}})
);
head.position.set(0, 2.2, 0);
character.add(head);

// Yeux
const eyeLeft = new THREE.Mesh(
    new THREE.SphereGeometry(0.05, 16, 16),
    new THREE.MeshStandardMaterial({{color: 0x000000}})
);
eyeLeft.position.set(-0.1, 2.25, 0.25);
character.add(eyeLeft);

// Torse
const torso = new THREE.Mesh(
    new THREE.BoxGeometry(0.8, 1.2, 0.4),
    new THREE.MeshStandardMaterial({{color: 0x4488FF}})
);
torso.position.set(0, 1.2, 0);
character.add(torso);

// Bras (avec articulations)
const armLeft = new THREE.Group();
const upperArmL = new THREE.Mesh(
    new THREE.CylinderGeometry(0.08, 0.08, 0.6, 16),
    new THREE.MeshStandardMaterial({{color: 0xFFCC88}})
);
upperArmL.position.set(0, -0.3, 0);
armLeft.add(upperArmL);
armLeft.position.set(-0.5, 1.6, 0);
character.add(armLeft);

// Continue avec tous les membres...
return character;
```

Adapte les couleurs et formes selon: {prompt}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            code = response.choices[0].message.content.strip()
            
            # Nettoie le code
            if "```javascript" in code:
                code = code.split("```javascript")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()
            
            return {'success': True, 'code': code, 'method': 'advanced-procedural'}
            
        except Exception as e:
            print(f"❌ Erreur génération avancée: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_grease_pencil(self, prompt):
        """Génère du code pour dessiner en 2D/3D comme Grease Pencil"""
        
        system_prompt = """Tu es un expert en dessin vectoriel 3D avec Three.js.
Tu crées des dessins style "Grease Pencil" (Blender) en utilisant:
- THREE.Line pour les traits
- THREE.BufferGeometry pour les formes
- Points pour dessiner des courbes
- Couleurs et épaisseurs variables

Code JavaScript pur, exécutable directement."""

        user_prompt = f"""Dessine ceci en style Grease Pencil: {prompt}

Exemple de structure:
```javascript
const drawing = new THREE.Group();

// Trait principal
const points = [];
points.push(new THREE.Vector3(0, 0, 0));
points.push(new THREE.Vector3(1, 1, 0));
points.push(new THREE.Vector3(2, 0.5, 0));

const geometry = new THREE.BufferGeometry().setFromPoints(points);
const material = new THREE.LineBasicMaterial({{
    color: 0xFF0000,
    linewidth: 3
}});
const line = new THREE.Line(geometry, material);
drawing.add(line);

// Ajoute plus de traits pour former le dessin
return drawing;
```

Adapte pour dessiner: {prompt}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1200,
                temperature=0.8
            )
            
            code = response.choices[0].message.content.strip()
            
            if "```javascript" in code:
                code = code.split("```javascript")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()
            
            return {'success': True, 'code': code, 'method': 'grease-pencil'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_blender_style(self, prompt):
        """Modélisation avancée style Blender avec opérations booléennes, etc."""
        
        system_prompt = """Tu es un expert Blender/Three.js. Tu crées des modèles 3D complexes avec:
- Opérations booléennes (union, soustraction)
- Modificateurs (bevel, subdivision)
- Formes paramétriques
- Assemblages complexes

Code JavaScript Three.js pur et exécutable."""

        user_prompt = f"""Modélise en style Blender: {prompt}

Utilise des techniques avancées:
```javascript
const model = new THREE.Group();

// Forme de base
const base = new THREE.Mesh(
    new THREE.BoxGeometry(2, 0.5, 2),
    new THREE.MeshStandardMaterial({{
        color: 0x888888,
        metalness: 0.5,
        roughness: 0.3
    }})
);

// Ajoute détails avec d'autres formes
// Simule des booléens en positionnant intelligemment
// Utilise scale/rotation pour formes complexes

return model;
```

Crée: {prompt}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            code = response.choices[0].message.content.strip()
            
            if "```javascript" in code:
                code = code.split("```javascript")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()
            
            return {'success': True, 'code': code, 'method': 'blender-style'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Instance globale
_generator = None

def init_advanced_generator():
    """Initialise le générateur avancé"""
    global _generator
    if _generator is None:
        _generator = Advanced3DGenerator()
    return _generator

def generate_advanced_3d(prompt, method='auto'):
    """
    Génère un modèle 3D avec la méthode choisie
    
    Args:
        prompt: Description du modèle
        method: 'advanced', 'grease-pencil', 'blender-style', 'auto'
    """
    generator = init_advanced_generator()
    
    # Détection auto de la méthode
    if method == 'auto':
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ['dessine', 'trait', 'ligne', 'sketch']):
            method = 'grease-pencil'
        elif any(word in prompt_lower for word in ['complexe', 'détaillé', 'realistic', 'avancé']):
            method = 'blender-style'
        else:
            method = 'advanced'
    
    # Génère selon la méthode
    if method == 'grease-pencil':
        return generator.generate_grease_pencil(prompt)
    elif method == 'blender-style':
        return generator.generate_blender_style(prompt)
    else:  # advanced
        return generator.generate_advanced_character(prompt)


if __name__ == '__main__':
    # Test
    print("=== Test Générateur Avancé ===\n")
    
    # Test personnage avancé
    result = generate_advanced_3d("un guerrier avec armure", "advanced")
    if result['success']:
        print("✅ Personnage avancé généré")
        print(f"Code: {result['code'][:200]}...\n")
    
    # Test Grease Pencil
    result = generate_advanced_3d("dessine un dragon", "grease-pencil")
    if result['success']:
        print("✅ Grease Pencil généré")
        print(f"Code: {result['code'][:200]}...\n")
    
    # Test Blender style
    result = generate_advanced_3d("un vaisseau spatial complexe", "blender-style")
    if result['success']:
        print("✅ Blender style généré")
        print(f"Code: {result['code'][:200]}...\n")
