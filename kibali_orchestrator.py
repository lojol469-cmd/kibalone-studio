#!/usr/bin/env python3
"""
🎭 KIBALI ORCHESTRATOR - Chef d'orchestre IA
==============================================
Kibali analyse le prompt et ORCHESTRE les 48 outils en séquence
Comme un réalisateur de film qui coordonne tous les départements
"""

import re
from typing import List, Dict, Optional
from kibali_tools_registry import ALL_TOOLS_DEFINITIONS

class KibaliOrchestrator:
    """Orchestrateur intelligent qui utilise les 48 outils"""
    
    def __init__(self):
        self.tools = {tool['name']: tool for tool in ALL_TOOLS_DEFINITIONS}
        print(f"🎭 Orchestrateur initialisé avec {len(self.tools)} outils")
    
    def analyze_and_orchestrate(self, prompt: str) -> Dict:
        """
        Analyse le prompt et crée un PLAN D'EXÉCUTION avec les outils
        
        Returns:
            {
                'understood': bool,
                'plan': {
                    'steps': [
                        {'step': 1, 'tool': 'MeshyGenerate', 'params': {...}, 'reason': '...'},
                        {'step': 2, 'tool': 'OrganicMovement', 'params': {...}, 'reason': '...'}
                    ],
                    'estimated_time': 30,
                    'complexity': 'high'
                },
                'execution_log': []  # Rempli en temps réel
            }
        """
        prompt_lower = prompt.lower()
        
        # Détecte l'intention principale
        plan = {
            'steps': [],
            'estimated_time': 0,
            'complexity': 'medium'
        }
        
        # CRÉATION DE PERSONNAGE
        if any(kw in prompt_lower for kw in ['personnage', 'character', 'humain', 'héros']):
            plan['steps'].append({
                'step': len(plan['steps']) + 1,
                'tool': 'RealisticGenerate',
                'params': {
                    'prompt': prompt,
                    'type': 'character',
                    'quality': 'high'
                },
                'reason': 'Génération du personnage avec anatomie réaliste',
                'estimated_time': 10
            })
            plan['estimated_time'] += 10
        
        # ENVIRONNEMENT
        if any(kw in prompt_lower for kw in ['terrain', 'environnement', 'scène', 'forêt', 'ville']):
            plan['steps'].append({
                'step': len(plan['steps']) + 1,
                'tool': 'RealisticGenerate',
                'params': {
                    'prompt': prompt,
                    'type': 'environment',
                    'quality': 'medium'
                },
                'reason': 'Création de l\'environnement',
                'estimated_time': 8
            })
            plan['estimated_time'] += 8
        
        # ANIMATION - MARCHE
        if any(kw in prompt_lower for kw in ['marche', 'walk', 'court', 'run', 'bouge']):
            plan['steps'].append({
                'step': len(plan['steps']) + 1,
                'tool': 'OrganicMovement',
                'params': {
                    'animation_type': 'run' if 'court' in prompt_lower else 'walk',
                    'duration': 5,
                    'speed': 1.5 if 'court' in prompt_lower else 1.0
                },
                'reason': 'Animation de déplacement réaliste',
                'estimated_time': 3
            })
            plan['estimated_time'] += 3
        
        # ANIMATION - SAUT
        if any(kw in prompt_lower for kw in ['saut', 'saute', 'jump']):
            plan['steps'].append({
                'step': len(plan['steps']) + 1,
                'tool': 'GenerateAnimation',
                'params': {
                    'movement': 'jump',
                    'duration': 2,
                    'height': 2.0
                },
                'reason': 'Animation de saut',
                'estimated_time': 3
            })
            plan['estimated_time'] += 3
        
        # RIGGING (si nécessaire pour animation)
        if len([s for s in plan['steps'] if 'Animation' in s['tool'] or 'Movement' in s['tool']]) > 0:
            # Insère le rigging AVANT les animations
            rigging_step = {
                'step': 0,  # Sera réordonné
                'tool': 'AdvancedGenerate',
                'params': {
                    'method': 'grease-pencil',  # Méthode qui fait le rigging
                    'prompt': prompt,
                    'include_rigging': True
                },
                'reason': 'Rigging du squelette pour animations',
                'estimated_time': 5
            }
            # Insère avant les animations
            anim_index = next((i for i, s in enumerate(plan['steps']) if 'Animation' in s['tool'] or 'Movement' in s['tool']), None)
            if anim_index:
                plan['steps'].insert(anim_index, rigging_step)
                plan['estimated_time'] += 5
        
        # CAMÉRA - Orbite
        if any(kw in prompt_lower for kw in ['orbite', '360', 'tourne autour', 'film']):
            plan['steps'].append({
                'step': len(plan['steps']) + 1,
                'tool': 'CameraOrbit360',
                'params': {
                    'duration': 8,
                    'height': 5,
                    'radius': 10
                },
                'reason': 'Caméra orbite 360° pour filmer',
                'estimated_time': 1
            })
            plan['estimated_time'] += 1
        
        # CAMÉRA - Vue spécifique
        if any(kw in prompt_lower for kw in ['vue de face', 'vue de haut', 'isométrique']):
            preset = 'iso' if 'iso' in prompt_lower else ('top' if 'haut' in prompt_lower else 'front')
            plan['steps'].append({
                'step': len(plan['steps']) + 1,
                'tool': 'CameraPreset',
                'params': {'preset': preset},
                'reason': f'Positionnement caméra vue {preset}',
                'estimated_time': 1
            })
            plan['estimated_time'] += 1
        
        # OPTIMISATION
        if any(kw in prompt_lower for kw in ['optimise', 'optimize', 'allège']):
            plan['steps'].append({
                'step': len(plan['steps']) + 1,
                'tool': 'OptimizeMesh',
                'params': {
                    'target_polygons': 5000,
                    'preserve_uvs': True
                },
                'reason': 'Optimisation du mesh (réduction polygones)',
                'estimated_time': 2
            })
            plan['estimated_time'] += 2
        
        # EXPORT
        if any(kw in prompt_lower for kw in ['export', 'sauvegarde', 'save']):
            format_type = 'gltf' if 'gltf' in prompt_lower or 'glb' in prompt_lower else 'obj'
            plan['steps'].append({
                'step': len(plan['steps']) + 1,
                'tool': 'ExportGLTF' if format_type == 'gltf' else 'ExportOBJ',
                'params': {
                    'output_path': f'/tmp/kibalone_export.{format_type}'
                },
                'reason': f'Export en format {format_type.upper()}',
                'estimated_time': 2
            })
            plan['estimated_time'] += 2
        
        # Réordonne les steps
        for i, step in enumerate(plan['steps']):
            step['step'] = i + 1
        
        # Détermine complexité
        if len(plan['steps']) > 5:
            plan['complexity'] = 'high'
        elif len(plan['steps']) > 2:
            plan['complexity'] = 'medium'
        else:
            plan['complexity'] = 'low'
        
        return {
            'understood': len(plan['steps']) > 0,
            'prompt': prompt,
            'plan': plan,
            'execution_log': []
        }
    
    def get_tool_description(self, tool_name: str) -> str:
        """Retourne la description d'un outil"""
        tool = self.tools.get(tool_name)
        return tool['description'] if tool else 'Outil inconnu'


# ============================================
# FONCTION PRINCIPALE POUR API
# ============================================

def orchestrate_prompt(prompt: str) -> Dict:
    """Point d'entrée: analyse et crée le plan d'orchestration"""
    orchestrator = KibaliOrchestrator()
    result = orchestrator.analyze_and_orchestrate(prompt)
    
    # Ajoute les descriptions des outils
    for step in result['plan']['steps']:
        step['tool_description'] = orchestrator.get_tool_description(step['tool'])
    
    return result


# ============================================
# TESTS
# ============================================

if __name__ == "__main__":
    print("🎭 KIBALI ORCHESTRATOR - Tests\n" + "="*60)
    
    test_prompts = [
        "crée un personnage qui court et saute",
        "terrain de foot avec caméra qui tourne autour",
        "personnage héroïque vue isométrique",
        "environnement forêt magique avec animation"
    ]
    
    orchestrator = KibaliOrchestrator()
    
    for prompt in test_prompts:
        print(f"\n📝 Prompt: \"{prompt}\"")
        result = orchestrator.analyze_and_orchestrate(prompt)
        
        if result['understood']:
            print(f"✅ Plan: {len(result['plan']['steps'])} étapes")
            print(f"⏱️  Temps estimé: {result['plan']['estimated_time']}s")
            print(f"🎯 Complexité: {result['plan']['complexity']}")
            print("\n📋 Étapes:")
            for step in result['plan']['steps']:
                print(f"   {step['step']}. {step['tool']}: {step['reason']}")
        else:
            print("❌ Prompt non compris")
    
    print("\n" + "="*60)
