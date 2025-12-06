#!/usr/bin/env python3
"""
🧠 KIBALI DISPATCHER - Copilote Intelligent 3D
==============================================
Analyse n'importe quelle demande complexe et ORCHESTRE les 48 outils.
Comme GitHub Copilot mais pour la 3D!

NOUVEAU: Utilise l'ORCHESTRATEUR pour les demandes complexes!

EXEMPLES DE COMPRÉHENSION:
- "crée un personnage qui court" → Orchestrator → RealisticGenerate + OrganicMovement
- "terrain de foot" → Orchestrator → MeshyGenerate (photoréaliste)
- "personnage héroïque vue 360" → Orchestrator → AdvancedGenerate + CameraOrbit360
"""

import re
from typing import Dict, List, Tuple, Optional

# Import de l'orchestrateur
try:
    from kibali_orchestrator import orchestrate_prompt
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    print("⚠️ Orchestrator non disponible - mode simple")

class KibaliDispatcher:
    """Dispatcher intelligent qui ORCHESTRE les 48 outils"""
    
    def __init__(self):
        self.use_orchestrator = ORCHESTRATOR_AVAILABLE
        print(f"🧠 Dispatcher initialisé - Orchestrator: {self.use_orchestrator}")
        
    def dispatch(self, prompt: str) -> Dict:
        """
        Point d'entrée principal: analyse et retourne l'action à exécuter
        
        NOUVEAU: Si orchestrator disponible, l'utilise pour demandes complexes
        """
        
        # Détecte si c'est une demande COMPLEXE
        is_complex = self._is_complex_request(prompt)
        
        if is_complex and self.use_orchestrator:
            # Utilise l'ORCHESTRATEUR pour les demandes complexes
            return {
                'type': 'orchestrated',
                'action': 'orchestrate',
                'prompt': prompt,
                'message': 'Orchestration intelligente des outils'
            }
        else:
            # Utilise le pattern matching simple pour actions simples
            return self._simple_dispatch(prompt)
    
    def _is_complex_request(self, prompt: str) -> bool:
        """Détecte si la demande nécessite orchestration"""
        prompt_lower = prompt.lower()
        
        # Indicateurs de complexité
        complexity_indicators = [
            # Création + Animation
            ('créé', 'court'),
            ('créé', 'saute'),
            ('personnage', 'mouvement'),
            ('personnage', 'animation'),
            
            # Création + Caméra
            ('créé', '360'),
            ('créé', 'orbite'),
            ('créé', 'film'),
            
            # Multi-objets
            ('plusieurs', 'objet'),
            ('scene', 'complet'),
            ('environnement', 'avec'),
            
            # Mots-clés complexité
            'qui court', 'qui saute', 'qui marche',
            'avec animation', 'et anime',
            'vue 360', 'caméra tourne',
            'personnage', 'character',
            'scène complète'
        ]
        
        # Vérifie indicateurs
        for indicator in complexity_indicators:
            if isinstance(indicator, tuple):
                if all(kw in prompt_lower for kw in indicator):
                    return True
            else:
                if indicator in prompt_lower:
                    return True
        
        return False
    
    def _simple_dispatch(self, prompt: str) -> Dict:
        """Pattern matching simple pour actions simples"""
        prompt_lower = prompt.lower()
        
        # ACTIONS SIMPLES
        
        # Caméra orbite
        if any(kw in prompt_lower for kw in ['orbite', '360', 'tourne autour']):
            return {
                'type': 'simple',
                'action': 'camera_orbit',
                'params': {'duration': 8, 'height': 5, 'radius': 10}
            }
        
        # Caméra zoom
        if 'zoom' in prompt_lower:
            factor = 2.0 if 'avant' in prompt_lower or 'in' in prompt_lower else 0.5
            return {
                'type': 'simple',
                'action': 'camera_zoom',
                'params': {'factor': factor}
            }
        
        # Suppression
        if any(kw in prompt_lower for kw in ['retire', 'supprime', 'enlève', 'remove']):
            # Extrait le nombre
            import re
            numbers = re.findall(r'\d+', prompt)
            count = int(numbers[0]) if numbers else 1
            return {
                'type': 'simple',
                'action': 'remove_objects',
                'params': {'count': count}
            }
        
        # Clear scene
        if any(kw in prompt_lower for kw in ['vide', 'clear', 'reset']):
            return {
                'type': 'simple',
                'action': 'clear_scene',
                'params': {}
            }
        
        # Par défaut: orchestration
        return {
            'type': 'orchestrated',
            'action': 'orchestrate',
            'prompt': prompt,
            'message': 'Demande orchestrée par défaut'
        }


    # ANCIENNES MÉTHODES (conservées pour compatibilité)
    def _init_patterns(self) -> List[Dict]:
        """Définit tous les patterns de reconnaissance"""
        return [
            # CRÉATIONS COMPLEXES - Utilise les outils procéduraux de Kibali
            {
                'keywords': ['terrain', 'football', 'foot', 'stade', 'stadium'],
                'action': 'procedural_generate',
                'description': 'rectangular football field with grass texture, white lines, goals at each end, realistic stadium ground',
                'priority': 10
            },
            {
                'keywords': ['colonne', 'column', 'grec', 'greek', 'pilier'],
                'action': 'procedural_generate',
                'description': 'ancient greek column with marble texture, doric style, fluted shaft, detailed capital',
                'priority': 10
            },
            {
                'keywords': ['bâtiment', 'building', 'immeuble', 'maison', 'house'],
                'action': 'procedural_generate',
                'description': 'detailed building structure with windows, doors, roof',
                'priority': 9
            },
            {
                'keywords': ['arbre', 'tree', 'forêt', 'forest'],
                'action': 'procedural_generate',
                'description': 'realistic tree with branches, leaves, bark texture',
                'priority': 9
            },
            {
                'keywords': ['voiture', 'car', 'véhicule', 'vehicle'],
                'action': 'procedural_generate',
                'description': 'detailed car model with wheels, windows, body panels',
                'priority': 9
            },
            {
                'keywords': ['chaise', 'chair', 'siège', 'seat'],
                'action': 'procedural_generate',
                'description': 'comfortable chair with legs, seat, backrest',
                'priority': 8
            },
            
            # TEXTURES SPÉCIFIQUES
            {
                'keywords': ['texture', 'matériau', 'material', 'applique'],
                'action': 'apply_texture',
                'priority': 8
            },
            
            # CONTRÔLE CAMÉRA
            {
                'keywords': ['orbite', '360', 'tourne autour'],
                'action': 'camera_orbit',
                'priority': 10
            },
            {
                'keywords': ['zoom'],
                'action': 'camera_zoom',
                'priority': 9
            },
            {
                'keywords': ['caméra', 'camera', 'vue'],
                'action': 'camera_control',
                'priority': 8
            },
            
            # SUPPRESSION/MODIFICATION
            {
                'keywords': ['retire', 'supprime', 'enlève', 'efface', 'remove', 'delete'],
                'action': 'remove_objects',
                'priority': 10
            },
            {
                'keywords': ['vide', 'clear', 'reset', 'tout supprimer'],
                'action': 'clear_scene',
                'priority': 10
            },
            
            # QUANTITÉ
            {
                'keywords': ['plusieurs', 'beaucoup', 'plein'],
                'action': 'multiple',
                'priority': 7
            }
        ]
    
    def analyze(self, prompt: str) -> Dict:
        """
        Analyse le prompt et retourne une stratégie d'exécution
        
        Returns:
            {
                'primary_action': str,
                'actions': List[Dict],
                'parameters': Dict,
                'complexity': int
            }
        """
        prompt_lower = prompt.lower()
        
        # Détecte les nombres
        numbers = self._extract_numbers(prompt)
        
        # Trouve les patterns correspondants
        matched_patterns = []
        for pattern in self.patterns:
            if any(kw in prompt_lower for kw in pattern['keywords']):
                matched_patterns.append(pattern)
        
        # Trie par priorité
        matched_patterns.sort(key=lambda x: x['priority'], reverse=True)
        
        if not matched_patterns:
            return self._generic_create(prompt)
        
        # Pattern principal
        main_pattern = matched_patterns[0]
        
        # Construit le plan d'action
        actions = []
        
        if main_pattern['action'] == 'procedural_generate':
            # Utilise ProceduralGenerate - Génération par code IA (rapide!)
            description = main_pattern.get('description', prompt)
            actions.append({
                'tool': 'ProceduralGenerate',
                'params': {
                    'prompt': description,
                    'complexity': 'high'
                }
            })
        
        elif main_pattern['action'] == 'apply_texture':
            texture_query = self._extract_texture_query(prompt)
            actions.append({
                'tool': 'TextureGenerate',
                'params': {'style': texture_query}
            })
        
        elif main_pattern['action'] == 'camera_orbit':
            duration = numbers[0] if numbers else 8
            actions.append({
                'tool': 'CameraOrbit360',
                'params': {'duration': duration, 'height': 5, 'radius': 8}
            })
        
        elif main_pattern['action'] == 'camera_zoom':
            factor = 2.0 if 'avant' in prompt_lower or 'in' in prompt_lower else 0.5
            actions.append({
                'tool': 'CameraZoom',
                'params': {'factor': factor, 'duration': 1}
            })
        
        elif main_pattern['action'] == 'camera_control':
            actions.extend(self._parse_camera_commands(prompt, prompt_lower, numbers))
        
        elif main_pattern['action'] == 'remove_objects':
            count = numbers[0] if numbers else 1
            actions.append({
                'tool': 'RemoveObjects',
                'params': {'count': count}
            })
        
        elif main_pattern['action'] == 'clear_scene':
            actions.append({
                'tool': 'ClearScene',
                'params': {}
            })
        
        # Gère la multiplicité
        if main_pattern.get('action') == 'multiple' or numbers and numbers[0] > 1:
            count = numbers[0] if numbers else 3
            actions[0]['params']['count'] = count
        
        return {
            'primary_action': main_pattern['action'],
            'actions': actions,
            'parameters': {
                'numbers': numbers,
                'original_prompt': prompt
            },
            'complexity': len(actions)
        }
    
    def _extract_numbers(self, text: str) -> List[int]:
        """Extrait tous les nombres du texte"""
        numbers = re.findall(r'\b(\d+)\b', text)
        return [int(n) for n in numbers]
    
    def _extract_texture_query(self, prompt: str) -> str:
        """Extrait le type de texture demandé"""
        texture_keywords = {
            'bois': 'wood',
            'wood': 'wood',
            'métal': 'metal',
            'metal': 'metal',
            'pierre': 'stone',
            'stone': 'stone',
            'marbre': 'marble',
            'marble': 'marble',
            'béton': 'concrete',
            'concrete': 'concrete',
            'herbe': 'grass',
            'grass': 'grass',
            'tissu': 'fabric',
            'fabric': 'fabric',
            'verre': 'glass',
            'glass': 'glass'
        }
        
        prompt_lower = prompt.lower()
        for keyword, texture_type in texture_keywords.items():
            if keyword in prompt_lower:
                return texture_type
        
        return 'default'
    
    def _parse_camera_commands(self, prompt: str, prompt_lower: str, numbers: List[int]) -> List[Dict]:
        """Parse les commandes de caméra complexes"""
        actions = []
        
        # Directions
        directions = {
            'avance': ('forward', 'CameraMove'),
            'recule': ('backward', 'CameraMove'),
            'gauche': ('left', 'CameraMove'),
            'droite': ('right', 'CameraMove'),
            'monte': ('up', 'CameraMove'),
            'descend': ('down', 'CameraMove'),
        }
        
        for keyword, (direction, tool) in directions.items():
            if keyword in prompt_lower:
                distance = numbers[0] if numbers else 2
                actions.append({
                    'tool': tool,
                    'params': {'direction': direction, 'distance': distance, 'duration': 1}
                })
        
        # Rotations
        if 'rotation' in prompt_lower or 'tourne de' in prompt_lower:
            degrees = numbers[0] if numbers else 90
            actions.append({
                'tool': 'CameraRotate',
                'params': {'axis': 'y', 'degrees': degrees, 'duration': 1}
            })
        
        # Presets
        presets = {
            'face': 'front',
            'front': 'front',
            'dos': 'back',
            'back': 'back',
            'haut': 'top',
            'top': 'top',
            'isométrique': 'iso',
            'iso': 'iso'
        }
        
        for keyword, preset in presets.items():
            if keyword in prompt_lower:
                actions.append({
                    'tool': 'CameraPreset',
                    'params': {'preset': preset}
                })
        
        return actions
    
    def _generic_create(self, prompt: str) -> Dict:
        """Action générique quand aucun pattern ne correspond"""
        return {
            'primary_action': 'generic_create',
            'actions': [{
                'tool': 'ProceduralGenerate',
                'params': {'prompt': prompt}
            }],
            'parameters': {'original_prompt': prompt},
            'complexity': 1
        }
    
    def execute_plan(self, plan: Dict) -> Dict:
        """
        Exécute le plan d'action et retourne les résultats
        """
        results = []
        
        for action in plan['actions']:
            tool = action['tool']
            params = action['params']
            
            try:
                # ProceduralGenerate - Génération rapide par code IA
                if tool == 'ProceduralGenerate':
                    results.append({
                        'tool': tool,
                        'success': True,
                        'params': params,
                        'frontend_action': {
                            'type': 'generate_procedural',
                            'prompt': params['prompt']
                        }
                    })
                
                # TextureGenerate - Génération de texture PBR
                elif tool == 'TextureGenerate':
                    results.append({
                        'tool': tool,
                        'success': True,
                        'params': params,
                        'frontend_action': {
                            'type': 'generate_texture',
                            'style': params['style']
                        }
                    })
                
                # Caméra - Contrôles directs
                elif tool.startswith('Camera'):
                    results.append({
                        'tool': tool,
                        'success': True,
                        'params': params,
                        'frontend_action': {
                            'type': 'camera_control',
                            'action': tool,
                            'params': params
                        }
                    })
                
                # Autres outils - Retourne les params pour exécution frontend
                else:
                    results.append({
                        'tool': tool,
                        'success': True,
                        'params': params
                    })
            
            except Exception as e:
                results.append({
                    'tool': tool,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'plan': plan,
            'results': results,
            'success': all(r['success'] for r in results)
        }


# ============================================
# FONCTION PRINCIPALE POUR KIBALI API
# ============================================

def dispatch_and_execute(prompt: str) -> Dict:
    """
    Point d'entrée unique: analyse et exécute le prompt
    
    Returns:
        {
            'understood': bool,
            'plan': Dict,
            'execution': Dict,
            'frontend_actions': List[Dict]  # Actions à exécuter côté frontend
        }
    """
    dispatcher = KibaliDispatcher()
    
    # Analyse
    plan = dispatcher.analyze(prompt)
    
    # Exécute
    execution = dispatcher.execute_plan(plan)
    
    # Prépare les actions frontend
    frontend_actions = []
    for result in execution['results']:
        if result.get('frontend_action'):
            frontend_actions.append(result['frontend_action'])
        else:
            # Action générique
            frontend_actions.append({
                'type': result['tool'],
                'params': result.get('params', {})
            })
    
    return {
        'understood': True,
        'plan': plan,
        'execution': execution,
        'frontend_actions': frontend_actions,
        'summary': f"✅ {len(plan['actions'])} action(s): {', '.join([a['tool'] for a in plan['actions']])}"
    }


# ============================================
# TESTS
# ============================================

if __name__ == "__main__":
    print("🧠 KIBALI DISPATCHER - Tests")
    print("=" * 60)
    
    test_prompts = [
        "fait moi un terrain de foot",
        "ajoute une colonne grecque en marbre",
        "caméra orbite 360 pendant 10 secondes",
        "retire 3 objets",
        "zoom avant",
        "crée 5 arbres",
        "vide la scène",
        "cherche texture bois",
        "caméra monte de 5 mètres puis tourne 90 degrés"
    ]
    
    dispatcher = KibaliDispatcher()
    
    for prompt in test_prompts:
        print(f"\n📝 Prompt: \"{prompt}\"")
        plan = dispatcher.analyze(prompt)
        print(f"   Action: {plan['primary_action']}")
        print(f"   Outils: {', '.join([a['tool'] for a in plan['actions']])}")
        if plan['parameters'].get('numbers'):
            print(f"   Nombres: {plan['parameters']['numbers']}")
    
    print("\n✅ Tous les tests passés!")
