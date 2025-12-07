#!/usr/bin/env python3
"""
Générateur IA Hybride - MISTRAL (raisonnement) + CODELLAMA (code)
Architecture 2-passes:
1. Mistral analyse et décompose la requête
2. CodeLlama génère le code Three.js complexe
"""

import sys
import os
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import InferenceClient

ISOL_PATH = Path("/home/belikan/Isol")
sys.path.insert(0, str(ISOL_PATH / "kibali-IA"))

class HybridAIGenerator:
    """Système hybride: Mistral (pensée) + CodeLlama (exécution)"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🧠 Initialisation Générateur Hybride IA...")
        print(f"   Device: {self.device}")
        
        # 1️⃣ MISTRAL - Raisonnement et analyse
        self.mistral_client = InferenceClient(token=os.getenv("HF_TOKEN"))
        self.mistral_model = "mistralai/Mistral-7B-Instruct-v0.2"
        print(f"✅ Mistral chargé (API HF) - Raisonnement")
        
        # 2️⃣ CODELLAMA - Génération de code
        self.codellama = None
        self.codellama_tokenizer = None
        self._load_codellama()
    
    def _load_codellama(self):
        """Charge CodeLlama localement"""
        try:
            codellama_path = Path("/home/belikan/Isol/kibali-IA/kibali_data/models/huggingface_cache/models--codellama--CodeLlama-7b-hf/snapshots/6c284d1468fe6c413cf56183e69b194dcfa27fe6")
            
            if not codellama_path.exists():
                print("⚠️  CodeLlama: fallback vers API HF")
                return
            
            print(f"📦 Chargement CodeLlama-7b...")
            
            self.codellama_tokenizer = AutoTokenizer.from_pretrained(
                str(codellama_path),
                trust_remote_code=True,
                local_files_only=True
            )
            
            self.codellama = AutoModelForCausalLM.from_pretrained(
                str(codellama_path),
                trust_remote_code=True,
                local_files_only=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            if self.device == "cpu":
                self.codellama = self.codellama.to(self.device)
            
            self.codellama.eval()
            print(f"✅ CodeLlama chargé sur {self.device} - Génération code")
            
        except Exception as e:
            print(f"⚠️  CodeLlama fallback API: {e}")
            self.codellama = None
    
    def analyze_with_mistral(self, prompt, scene_context=None):
        """PHASE 1: Mistral analyse et décompose la requête avec contexte scène"""
        
        # 🔥 NOUVEAU: Construit un prompt enrichi avec le contexte
        context_info = ""
        if scene_context and scene_context.get('total_objects', 0) > 0:
            context_info = f"""

CONTEXTE DE LA SCÈNE ACTUELLE:
- Nombre d'objets existants: {scene_context['total_objects']}
- Objets présents: {', '.join([obj['name'] for obj in scene_context.get('objects', [])[:5]])}
- Personnage présent: {'OUI' if scene_context.get('has_character') else 'NON'}
- Véhicule présent: {'OUI' if scene_context.get('has_vehicle') else 'NON'}
- Eau présente: {'OUI' if scene_context.get('has_water') else 'NON'}
- Environnement présent: {'OUI' if scene_context.get('has_environment') else 'NON'}

IMPORTANT: Tiens compte du contexte pour adapter ta génération!
- Si un bateau existe et l'utilisateur demande "ajoute de l'eau", positionne l'eau SOUS le bateau
- Si un personnage existe et l'utilisateur demande "ajoute un sol", crée le sol SOUS le personnage
- Adapte la position, l'échelle et l'orientation selon les objets existants
- Si demande de "mettre X sur Y", utilise les positions des objets existants pour calculer la nouvelle position"""
        
        analysis_prompt = f"""Analyse cette requête 3D et fournis une analyse technique détaillée en JSON:{context_info}

REQUÊTE: "{prompt}"

Analyse technique professionnelle:
- object_type: character/vehicle/building/furniture/animal/plant/environment/props/mechanical/water/terrain
- style: realistic/stylized/cartoon/anime/cyberpunk/fantasy/medieval/modern/abstract/minimalist
- complexity: simple/medium/complex/very_complex (basé sur nombre de parties et détails)
- key_features: liste détaillée des caractéristiques techniques (dimensions, matériaux, fonctionnalités)
- geometry_hints: géométries Three.js optimales (BoxGeometry, CylinderGeometry, SphereGeometry, ConeGeometry, TorusGeometry, PlaneGeometry, etc.)
- color_palette: couleurs hexadécimales réalistes pour matériaux PBR
- material_properties: {{"metalness": float, "roughness": float, "transmission": float, "transparent": bool}} par partie
- scale_reference: échelle réaliste en mètres (ex: character=1.8, vehicle=4.5, water_plane=100)
- position_hint: position suggérée basée sur le contexte (ex: {{"y": -0.5}} pour eau sous bateau)
- animation_potential: parties animables (joints, portes, roues, vagues, etc.)
- lighting_requirements: besoins en éclairage spécifiques
- contextual_adaptation: comment s'intégrer dans la scène existante

Réponds UNIQUEMENT en JSON valide et détaillé."""

        try:
            # Utilise chat_completion au lieu de text_generation
            messages = [
                {
                    "role": "system",
                    "content": "Tu es un expert en analyse de prompts 3D. Réponds uniquement en JSON valide."
                },
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ]
            
            response = self.mistral_client.chat_completion(
                messages=messages,
                model=self.mistral_model,
                max_tokens=256,
                temperature=0.3
            )
            
            # Extrait le contenu de la réponse
            response_text = response.choices[0].message.content.strip()
            
            # Parse la réponse JSON
            import json
            # Extrait le JSON de la réponse
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                analysis = json.loads(response_text[json_start:json_end])
                return analysis
            else:
                # Fallback si pas de JSON
                return {
                    'object_type': 'object',
                    'style': 'realistic',
                    'complexity': 'medium',
                    'key_features': [prompt],
                    'geometry_hints': ['BoxGeometry', 'CylinderGeometry', 'SphereGeometry'],
                    'color_palette': ['0x888888', '0x444444', '0xcccccc'],
                    'material_properties': {'metalness': 0.3, 'roughness': 0.7, 'transmission': 0.0},
                    'scale_reference': 1.0,
                    'animation_potential': [],
                    'lighting_requirements': 'standard'
                }
        except Exception as e:
            print(f"⚠️  Mistral analysis error: {e}")
            return {
                'object_type': 'object',
                'style': 'realistic',
                'complexity': 'medium',
                'key_features': [prompt],
                'geometry_hints': ['BoxGeometry', 'CylinderGeometry'],
                'color_palette': ['0x888888', '0x666666'],
                'material_properties': {'metalness': 0.2, 'roughness': 0.8, 'transmission': 0.0},
                'scale_reference': 1.0,
                'animation_potential': [],
                'lighting_requirements': 'standard'
            }
    
    def _get_example_for_type(self, object_type, scene_context=None):
        """Retourne un exemple de code selon le type d'objet"""
        
        # Position adaptative selon contexte
        position_y = 0
        if scene_context and scene_context.get('has_vehicle'):
            position_y = -1  # Sous le véhicule pour eau/sol
        
        examples = {
            'water': f"""
const waterGroup = new THREE.Group();
const waterGeo = new THREE.PlaneGeometry(50, 50, 32, 32);
const waterMat = new THREE.MeshStandardMaterial({{
    color: 0x1e90ff,
    metalness: 0.8,
    roughness: 0.2,
    transparent: true,
    opacity: 0.7
}});
const waterMesh = new THREE.Mesh(waterGeo, waterMat);
waterMesh.rotation.x = -Math.PI / 2;
waterMesh.position.y = {position_y};
waterGroup.add(waterMesh);
studio.scene.add(waterGroup);
""",
            'vehicle': """
const boatGroup = new THREE.Group();
const hullGeo = new THREE.BoxGeometry(4, 1, 2);
const hullMat = new THREE.MeshStandardMaterial({{ color: 0x8b4513, roughness: 0.7 }});
const hull = new THREE.Mesh(hullGeo, hullMat);
boatGroup.add(hull);
const deckGeo = new THREE.BoxGeometry(3.5, 0.2, 1.8);
const deck = new THREE.Mesh(deckGeo, hullMat);
deck.position.y = 0.6;
boatGroup.add(deck);
studio.scene.add(boatGroup);
""",
            'character': """
const characterGroup = new THREE.Group();
const bodyGeo = new THREE.CylinderGeometry(0.3, 0.3, 1.2, 16);
const bodyMat = new THREE.MeshStandardMaterial({{ color: 0xffdbac }});
const body = new THREE.Mesh(bodyGeo, bodyMat);
characterGroup.add(body);
const headGeo = new THREE.SphereGeometry(0.25, 16, 16);
const head = new THREE.Mesh(headGeo, bodyMat);
head.position.y = 0.85;
characterGroup.add(head);
studio.scene.add(characterGroup);
""",
            'environment': f"""
const groundGroup = new THREE.Group();
const groundGeo = new THREE.PlaneGeometry(100, 100);
const groundMat = new THREE.MeshStandardMaterial({{ color: 0x228b22, roughness: 0.9 }});
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.position.y = {position_y};
groundGroup.add(ground);
studio.scene.add(groundGroup);
"""
        }
        
        return examples.get(object_type, examples['vehicle'])
    
    def generate_code_with_codellama(self, prompt, analysis, scene_context=None):
        """PHASE 2: Génère le code Three.js avec Mistral API ou CodeLlama local + contexte scène"""
        
        # 🔥 NOUVEAU: Construit les instructions contextuelles
        context_instructions = ""
        if scene_context and scene_context.get('total_objects', 0) > 0:
            existing_objects = ', '.join([f"{obj['name']} (type: {obj['type']}, pos: {obj['position']})" 
                                         for obj in scene_context.get('objects', [])[:3]])
            
            context_instructions = f"""

CONTEXTE DE LA SCÈNE EXISTANTE - TRÈS IMPORTANT:
- {scene_context['total_objects']} objet(s) déjà dans la scène
- Objets existants: {existing_objects}
- Bounds scène: min({scene_context['bounds']['min']['x']:.1f}, {scene_context['bounds']['min']['y']:.1f}, {scene_context['bounds']['min']['z']:.1f}), max({scene_context['bounds']['max']['x']:.1f}, {scene_context['bounds']['max']['y']:.1f}, {scene_context['bounds']['max']['z']:.1f})

RÈGLES DE POSITIONNEMENT CONTEXTUEL:
1. Si demande "ajouter eau" et véhicule existe → positionne eau SOUS le véhicule (y négatif)
2. Si demande "ajouter sol/terrain" → positionne sous tous les objets existants
3. Si demande "mettre X sur Y" → calcule position relative basée sur les objets existants
4. Utilise les bounds pour ne pas créer d'objets en collision
5. Adapte l'échelle en fonction des objets existants

Position hint: {analysis.get('position_hint', 'auto')}
Adaptation contextuelle: {analysis.get('contextual_adaptation', 'intégration intelligente')}"""
        
        # PRIORITÉ: Utilise Mistral API pour générer du vrai code créatif
        print(f"   💻 Génération code contextuel avec Mistral API...")
        
        # 🔥 EXEMPLE CONCRET selon le type d'objet
        example_code = self._get_example_for_type(analysis.get('object_type', 'object'), scene_context)
        
        # Position adaptée au contexte
        position_hint = "0"
        if scene_context and scene_context.get('total_objects', 0) > 0:
            if 'water' in prompt.lower() or 'sea' in prompt.lower() or 'mer' in prompt.lower():
                position_hint = "-1"  # Sous les objets existants
            elif 'ground' in prompt.lower() or 'sol' in prompt.lower() or 'floor' in prompt.lower():
                position_hint = "-0.5"  # Sous les objets
        
        code_prompt = f"""Create Three.js code for: {prompt}

Type: {analysis.get('object_type')}
Colors: {', '.join(analysis.get('color_palette', ['0x888888'])[:2])}
Scale: {analysis.get('scale_reference', 1.0)}m
Position Y: {position_hint}

RULES:
- NO import/require/export
- Use THREE (global)
- Use studio.scene.add()
- ASCII characters only

EXAMPLE CODE:
{example_code}

NOW CREATE CODE FOR: {prompt}

CODE:"""

        try:
            # Utilise chat_completion au lieu de text_generation pour Mistral
            from huggingface_hub import InferenceClient
            
            messages = [
                {
                    "role": "user",
                    "content": code_prompt
                }
            ]
            
            response = self.mistral_client.chat_completion(
                messages=messages,
                model=self.mistral_model,
                max_tokens=2000,  # Augmenté pour code plus long
                temperature=0.9,  # Plus créatif
                top_p=0.95
            )
            
            # Extrait le contenu de la réponse
            code = response.choices[0].message.content.strip()
            
            # Nettoyage agressif du code généré
            # 1. Enlève les balises markdown
            if '```' in code:
                parts = code.split('```')
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Code entre ```
                        if part.startswith('javascript\n') or part.startswith('js\n'):
                            code = part.split('\n', 1)[1]
                        else:
                            code = part
                        break
            
            # 2. 🔥 Nettoie caractères non-ASCII
            cleaned_chars = []
            for char in code:
                if ord(char) < 128 or char in ['\n', '\r', '\t']:  # ASCII seulement
                    cleaned_chars.append(char)
                else:
                    print(f"   🚫 Caractère non-ASCII supprimé: {repr(char)}")
            code = ''.join(cleaned_chars)
            
            # 3. 🔥 Retire TOUTES les lignes avec import/require/export
            import re
            lines = []
            for line in code.split('\n'):
                stripped = line.strip()
                # Élimine les imports/requires/exports
                if any(keyword in stripped for keyword in ['import ', 'require(', 'export ', 'module.exports']):
                    print(f"   🚫 Ligne supprimée: {stripped[:50]}")
                    continue
                lines.append(line)
            code = '\n'.join(lines)
            
            # 4. Retire les commentaires multi-lignes qui peuvent casser
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
            
            # 5. Retire les lignes de commentaires simples (sauf URLs)
            lines = []
            for line in code.split('\n'):
                stripped = line.strip()
                # Garde seulement si pas un commentaire pur (sauf si contient http)
                if not stripped.startswith('//') or 'http' in stripped:
                    lines.append(line)
            code = '\n'.join(lines)
            
            # 6. Fixe les parenthèses/accolades mal fermées (basique)
            open_parens = code.count('(')
            close_parens = code.count(')')
            if open_parens > close_parens:
                code += ')' * (open_parens - close_parens)
            
            # 6. Ajoute addLog si manquant
            if 'addLog' not in code:
                code += f"\naddLog('✅ {prompt} créé');"
            
            # Vérifie que le code contient du Three.js
            if 'THREE.' in code or 'Group' in code:
                return code
            else:
                print(f"⚠️  Code généré invalide, fallback")
                return self._generate_fallback_code(prompt, analysis)
            
        except Exception as e:
            print(f"⚠️  Mistral API error: {e}")
            # Essaie CodeLlama local si disponible
            if self.codellama is not None:
                return self._generate_with_local_codellama(prompt, analysis)
            return self._generate_fallback_code(prompt, analysis)
    
    def _generate_with_local_codellama(self, prompt, analysis):
        """Utilise CodeLlama local"""
        
        # Construit un prompt enrichi avec l'analyse
        code_prompt = f"""// Three.js Expert Code Generator
// Task: Create {analysis.get('object_type', 'object')}
// Style: {analysis.get('style', 'realistic')}
// Complexity: {analysis.get('complexity', 'medium')}
// Features: {', '.join(analysis.get('key_features', []))}

// Generate THREE.js code for: {prompt}
// Use geometries: {', '.join(analysis.get('geometry_hints', []))}
// Color palette: {', '.join(str(c) for c in analysis.get('color_palette', []))}

const createModel = () => {{
    const group = new THREE.Group();
    
    // Materials
    const materials = {{
        main: new THREE.MeshStandardMaterial({{
            color: {analysis.get('color_palette', ['0x888888'])[0]},
            roughness: 0.7,
            metalness: 0.2
        }})
    }};
    
    // Geometry
"""
        
        if self.codellama is not None:
            # Utilise CodeLlama local
            try:
                inputs = self.codellama_tokenizer(code_prompt, return_tensors="pt").to(self.device)
                
                with torch.no_grad():
                    outputs = self.codellama.generate(
                        **inputs,
                        max_new_tokens=1024,  # Code long et complexe
                        temperature=0.4,
                        do_sample=True,
                        top_p=0.95,
                        repetition_penalty=1.1
                    )
                
                generated = self.codellama_tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Extrait seulement le code généré (après le prompt)
                code = generated[len(code_prompt):].strip()
                
                # Complète le code s'il manque la fin
                if not code.endswith('};'):
                    code += "\n    return group;\n};\n\nconst model = createModel();\nstudio.scene.add(model);"
                
                return code
                
            except Exception as e:
                print(f"⚠️  CodeLlama generation error: {e}")
        
        # Fallback: génération simple
        return self._generate_fallback_code(prompt, analysis)
    
    def _generate_fallback_code(self, prompt, analysis):
        """Code simple si CodeLlama échoue"""
        obj_type = analysis.get('object_type', 'object')
        color = analysis.get('color_palette', ['0x888888'])[0]
        
        return f"""
const group = new THREE.Group();

// Create {obj_type}
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({{
    color: {color},
    roughness: 0.7,
    metalness: 0.2
}});
const mesh = new THREE.Mesh(geometry, material);
mesh.castShadow = true;
mesh.receiveShadow = true;

group.add(mesh);
studio.scene.add(group);

// Log
addLog('✅ {prompt} créé');
"""
    
    def generate(self, prompt, object_type='object', scene_context=None):
        """Pipeline complet: Mistral analyse → CodeLlama génère avec contexte"""
        print(f"🧠 [Mistral] Analyse de: {prompt}")
        
        # 🔥 NOUVEAU: Enrichit l'analyse avec le contexte de la scène
        if scene_context and scene_context.get('total_objects', 0) > 0:
            print(f"📊 Contexte scène: {scene_context['total_objects']} objet(s)")
            print(f"   • Personnage: {scene_context.get('has_character', False)}")
            print(f"   • Véhicule: {scene_context.get('has_vehicle', False)}")
            print(f"   • Eau: {scene_context.get('has_water', False)}")
            print(f"   • Environnement: {scene_context.get('has_environment', False)}")
        
        analysis = self.analyze_with_mistral(prompt, scene_context)
        print(f"   → Type: {analysis.get('object_type')}, Style: {analysis.get('style')}")
        
        print(f"💻 [CodeLlama] Génération du code contextuel...")
        code = self.generate_code_with_codellama(prompt, analysis, scene_context)
        print(f"   → {len(code)} caractères générés")
        
        return {
            'success': True,
            'code': code,
            'type': 'javascript',
            'analysis': analysis
        }
    
    def fix_code_with_mistral(self, broken_code, error_message, original_prompt):
        """AUTO-CORRECTION: Mistral corrige le code cassé"""
        print(f"🔧 [Mistral] Auto-correction du code...")
        print(f"   Erreur: {error_message}")
        
        # 🔥 NOUVEAU: Détection d'erreur spécifique import/require
        if 'import' in error_message.lower() or 'require' in error_message.lower() or 'module' in error_message.lower():
            print("   🚫 Détection erreur import/require - Nettoyage automatique")
            # Nettoie directement sans appeler Mistral
            import re
            lines = []
            for line in broken_code.split('\n'):
                stripped = line.strip()
                if not any(keyword in stripped for keyword in ['import ', 'require(', 'export ', 'module.exports']):
                    lines.append(line)
            cleaned_code = '\n'.join(lines)
            
            # Vérifie que le code restant est valide
            if 'THREE.' in cleaned_code and len(cleaned_code) > 50:
                print("   ✅ Code nettoyé automatiquement")
                return cleaned_code
        
        fix_prompt = f"""Tu es un expert JavaScript/Three.js. Corrige ce code qui génère une erreur.

⚠️ RÈGLES CRITIQUES:
- ❌ INTERDICTION: import, require, export, module.exports
- ✅ CODE NAVIGATEUR UNIQUEMENT (THREE déjà disponible)
- ✅ Utilise studio.scene pour ajouter les objets

ERREUR JAVASCRIPT:
{error_message}

CODE PROBLÉMATIQUE:
{broken_code[:500]}...

CONTEXTE: Le code devait créer "{original_prompt}" en Three.js

INSTRUCTIONS:
1. Retire TOUS les import/require/export si présents
2. Utilise uniquement THREE.* (déjà disponible globalement)
3. Corrige les erreurs de syntaxe (parenthèses, virgules, etc.)
4. Retourne UNIQUEMENT le code corrigé complet et fonctionnel
5. Le code doit utiliser THREE.js et studio.scene
6. PAS de markdown, PAS de commentaires explicatifs

CODE CORRIGÉ:"""

        try:
            messages = [
                {
                    "role": "system",
                    "content": "Tu es un expert en débogage JavaScript. Réponds uniquement avec du code corrigé."
                },
                {
                    "role": "user",
                    "content": fix_prompt
                }
            ]
            
            response = self.mistral_client.chat_completion(
                messages=messages,
                model=self.mistral_model,
                max_tokens=2000,
                temperature=0.3  # Moins créatif, plus précis
            )
            
            fixed_code = response.choices[0].message.content.strip()
            
            # 🔥 Nettoyage renforcé du code corrigé
            import re
            # Retire markdown
            fixed_code = re.sub(r'```[a-z]*\n?', '', fixed_code)
            fixed_code = re.sub(r'/\*.*?\*/', '', fixed_code, flags=re.DOTALL)
            
            # Retire TOUS les imports/requires/exports
            lines = []
            for line in fixed_code.split('\n'):
                stripped = line.strip()
                if not any(keyword in stripped for keyword in ['import ', 'require(', 'export ', 'module.exports']):
                    lines.append(line)
                else:
                    print(f"   🚫 Ligne supprimée (correction): {stripped[:50]}")
            fixed_code = '\n'.join(lines)
            
            print(f"   ✅ Code corrigé: {len(fixed_code)} caractères")
            return fixed_code
            
        except Exception as e:
            print(f"   ❌ Correction échouée: {e}")
            return None


# Instance globale
_generator = None

def init_hybrid_generator():
    """Initialise le générateur hybride"""
    global _generator
    if _generator is None:
        _generator = HybridAIGenerator()
    return _generator

def generate_hybrid_3d(prompt, object_type='object'):
    """Point d'entrée principal"""
    generator = init_hybrid_generator()
    return generator.generate(prompt, object_type)

def fix_broken_code(code, error, prompt):
    """Point d'entrée pour auto-correction"""
    generator = init_hybrid_generator()
    fixed = generator.fix_code_with_mistral(code, error, prompt)
    if fixed:
        return {'success': True, 'fixed_code': fixed}
    else:
        return {'success': False, 'error': 'Auto-correction impossible'}

