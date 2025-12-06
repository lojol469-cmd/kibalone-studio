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
    
    def analyze_with_mistral(self, prompt):
        """PHASE 1: Mistral analyse et décompose la requête"""
        analysis_prompt = f"""Analyse cette requête 3D et fournis une structure JSON:

REQUÊTE: "{prompt}"

Détermine:
- object_type: character/environment/object/effect
- style: realistic/cartoon/low-poly/cyberpunk/fantasy
- complexity: simple/medium/complex
- key_features: liste des caractéristiques principales
- geometry_hints: formes Three.js à utiliser (BoxGeometry, SphereGeometry, etc.)
- color_palette: couleurs hexadécimales suggérées

Réponds UNIQUEMENT en JSON valide."""

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
                    'geometry_hints': ['BoxGeometry', 'SphereGeometry'],
                    'color_palette': ['0x888888']
                }
        except Exception as e:
            print(f"⚠️  Mistral analysis error: {e}")
            return {
                'object_type': 'object',
                'style': 'realistic',
                'complexity': 'medium',
                'key_features': [prompt],
                'geometry_hints': ['BoxGeometry'],
                'color_palette': ['0x888888']
            }
    
    def generate_code_with_codellama(self, prompt, analysis):
        """PHASE 2: Génère le code Three.js avec Mistral API ou CodeLlama local"""
        
        # PRIORITÉ: Utilise Mistral API pour générer du vrai code créatif
        print(f"   💻 Génération code avec Mistral API...")
        
        code_prompt = f"""Tu es un expert Three.js. Génère du code JavaScript créatif et détaillé pour: "{prompt}"

ANALYSE:
- Type: {analysis.get('object_type', 'object')}
- Style: {analysis.get('style', 'realistic')}
- Complexité: {analysis.get('complexity', 'medium')}
- Features: {', '.join(analysis.get('key_features', []))}
- Couleurs suggérées: {', '.join(analysis.get('color_palette', ['0x888888']))}

EXIGENCES CRÉATIVES:
1. Crée un groupe principal: const group = new THREE.Group();
2. Pour un personnage: ajoute torse, tête, bras, jambes avec formes variées (CylinderGeometry, SphereGeometry, BoxGeometry)
3. Pour environnement: multiple objets (arbres, rochers, sol) avec positions espacées
4. Pour objet: détails complexes, plusieurs parties assemblées
5. Utilise MeshStandardMaterial avec couleurs contextuelles (metalness: 0.3, roughness: 0.7)
6. Positionne chaque élément avec .position.set(x, y, z) et rotation si nécessaire
7. Ajoute le groupe: studio.scene.add(group);
8. Log final: addLog('✅ {prompt} créé avec [nombre] éléments');

GÉNÈRE 30-50 LIGNES DE CODE MINIMUM, CRÉATIF ET DÉTAILLÉ. CODE UNIQUEMENT, PAS DE MARKDOWN NI ```javascript:"""

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
            
            # 2. Retire les commentaires multi-lignes qui peuvent casser
            import re
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
            
            # 3. Retire les lignes de commentaires simples
            lines = []
            for line in code.split('\n'):
                stripped = line.strip()
                # Garde seulement si pas un commentaire pur
                if not stripped.startswith('//') or 'http' in stripped:
                    lines.append(line)
            code = '\n'.join(lines)
            
            # 4. Fixe les parenthèses/accolades mal fermées (basique)
            open_parens = code.count('(')
            close_parens = code.count(')')
            if open_parens > close_parens:
                code += ')' * (open_parens - close_parens)
            
            # 5. Ajoute addLog si manquant
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
    
    def generate(self, prompt, object_type='object'):
        """Pipeline complet: Mistral analyse → CodeLlama génère"""
        print(f"🧠 [Mistral] Analyse de: {prompt}")
        analysis = self.analyze_with_mistral(prompt)
        print(f"   → Type: {analysis.get('object_type')}, Style: {analysis.get('style')}")
        
        print(f"💻 [CodeLlama] Génération du code...")
        code = self.generate_code_with_codellama(prompt, analysis)
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
        
        fix_prompt = f"""Tu es un expert JavaScript/Three.js. Corrige ce code qui génère une erreur.

ERREUR JAVASCRIPT:
{error_message}

CODE PROBLÉMATIQUE:
{broken_code}

CONTEXTE: Le code devait créer "{original_prompt}" en Three.js

INSTRUCTIONS:
1. Identifie l'erreur (syntaxe, parenthèses, virgules, etc.)
2. Corrige le code COMPLÈTEMENT
3. Retourne UNIQUEMENT le code corrigé, sans explications
4. Le code doit utiliser THREE.js et studio.scene
5. PAS de markdown, PAS de commentaires explicatifs

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
            
            # Nettoyage
            import re
            fixed_code = re.sub(r'```[a-z]*\n?', '', fixed_code)
            fixed_code = re.sub(r'/\*.*?\*/', '', fixed_code, flags=re.DOTALL)
            
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

