#!/usr/bin/env python3
"""
⚡ KIBALI EXECUTOR - Exécution en temps réel avec logs
======================================================
Execute le plan d'orchestration en appelant les vrais outils
Affiche les logs en temps réel pour voir le processus
"""

import time
import asyncio
import requests
from typing import Dict, List
from datetime import datetime
from kibali_orchestrator import orchestrate_prompt

class KibaliExecutor:
    """Exécute le plan d'orchestration en temps réel"""
    
    def __init__(self, api_base_url: str = "http://localhost:11000"):
        self.api_base = api_base_url
        self.execution_logs = []
    
    def log(self, message: str, level: str = "INFO"):
        """Ajoute un log avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.execution_logs.append(log_entry)
        
        # Couleurs pour terminal
        colors = {
            'INFO': '\033[94m',    # Bleu
            'SUCCESS': '\033[92m', # Vert
            'WARNING': '\033[93m', # Jaune
            'ERROR': '\033[91m',   # Rouge
            'TOOL': '\033[95m'     # Magenta
        }
        reset = '\033[0m'
        color = colors.get(level, '')
        
        print(f"{color}[{timestamp}] {level}: {message}{reset}")
    
    async def execute_tool_step(self, step: Dict) -> Dict:
        """Exécute une étape (appel d'un outil)"""
        tool_name = step['tool']
        params = step['params']
        
        self.log(f"🔧 Outil sélectionné: {tool_name}", "TOOL")
        self.log(f"📋 Raison: {step['reason']}", "INFO")
        self.log(f"⚙️  Paramètres: {params}", "INFO")
        
        start_time = time.time()
        
        try:
            # Mapping des outils vers les endpoints API
            endpoint_map = {
                # GÉNÉRATION - Backend Blender (port 11004) pour réalisme
                'MeshyGenerate': 'http://localhost:11003/api/text-to-3d-meshy',
                'RealisticGenerate': 'http://localhost:11004/api/realistic-generate',
                'AdvancedGenerate': 'http://localhost:11004/api/advanced-generate',
                
                # GÉNÉRATION - Backend Three.js (port 11005) pour vitesse
                'ProceduralGenerate': 'http://localhost:11005/api/create-object',
                'TextureGenerate': '/api/generate-texture',
                
                # ANIMATION - Blender Backend pour animations réalistes
                'GenerateAnimation': 'http://localhost:11004/api/generate-animation',
                'OrganicMovement': 'http://localhost:11004/api/organic-movement',
                'KeyframesCreate': 'http://localhost:11004/api/generate-animation',
                'CameraAnimation': '/api/camera-control',
                
                # CAMÉRA - Sur kibali_api
                'CameraOrbit360': '/api/camera-control',
                'CameraMove': '/api/camera-control',
                'CameraRotate': '/api/camera-control',
                'CameraFlyTo': '/api/camera-control',
                'CameraLookAt': '/api/camera-control',
                'CameraZoom': '/api/camera-control',
                'CameraPan': '/api/camera-control',
                'CameraShake': '/api/camera-control',
                'CameraPreset': '/api/camera-control',
                'CameraStop': '/api/camera-control',
                
                # MODIFICATION MESH - Three.js Backend pour rapidité
                'RepairMesh': '/api/mesh/repair',
                'OptimizeMesh': '/api/mesh/optimize',
                'SubdivideMesh': '/api/mesh/subdivide',
                'TransformMesh': 'http://localhost:11005/api/transform-mesh',
                'MergeMeshes': '/api/mesh/merge',
                'BooleanOperation': '/api/mesh/boolean',
                
                # RECONSTRUCTION
                'MiDaSReconstruct': 'http://localhost:11002/api/create_session',
                'TripoSRReconstruct': 'http://localhost:11001/api/generate',
                
                # ASSETS - Mock
                'Search3DModels': '/api/assets/search',
                'SearchTextures': '/api/assets/search',
                'FetchCompleteAsset': '/api/assets/fetch',
                
                # EXPORT - Mock
                'ExportGLTF': '/api/export/gltf',
                'ExportOBJ': '/api/export/obj'
            }
            
            endpoint = endpoint_map.get(tool_name)
            if not endpoint:
                self.log(f"❌ Endpoint non trouvé pour {tool_name}", "ERROR")
                return {
                    'success': False,
                    'error': f'Endpoint non mappé: {tool_name}',
                    'duration': 0
                }
            
            # Détermine l'URL complète
            if endpoint.startswith('http'):
                url = endpoint  # URL complète (autre service)
            else:
                url = f"{self.api_base}{endpoint}"  # Endpoint relatif sur kibali_api
            
            self.log(f"📡 Appel API: POST {endpoint}", "INFO")
            
            response = requests.post(url, json=params, timeout=60)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"✅ {tool_name} terminé en {duration:.2f}s", "SUCCESS")
                
                return {
                    'success': True,
                    'tool': tool_name,
                    'result': result,
                    'duration': duration
                }
            else:
                self.log(f"⚠️ Erreur API: {response.status_code}", "WARNING")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'duration': duration
                }
        
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            self.log(f"⏱️  Timeout après {duration:.2f}s", "ERROR")
            return {'success': False, 'error': 'Timeout', 'duration': duration}
        
        except Exception as e:
            duration = time.time() - start_time
            self.log(f"❌ Erreur: {str(e)}", "ERROR")
            return {'success': False, 'error': str(e), 'duration': duration}
    
    async def execute_plan(self, plan: Dict) -> Dict:
        """Exécute le plan complet étape par étape"""
        self.log("="*60, "INFO")
        self.log(f"🎬 DÉBUT DE L'EXÉCUTION", "INFO")
        self.log(f"📊 {len(plan['steps'])} étapes à exécuter", "INFO")
        self.log(f"⏱️  Temps estimé: {plan['estimated_time']}s", "INFO")
        self.log("="*60, "INFO")
        
        results = []
        total_duration = 0
        
        for step in plan['steps']:
            self.log(f"\n{'='*60}", "INFO")
            self.log(f"📍 ÉTAPE {step['step']}/{len(plan['steps'])}", "INFO")
            self.log(f"{'='*60}", "INFO")
            
            result = await self.execute_tool_step(step)
            results.append(result)
            total_duration += result['duration']
            
            # Pause entre les étapes
            if step['step'] < len(plan['steps']):
                self.log("⏸️  Pause 1s avant prochaine étape...", "INFO")
                await asyncio.sleep(1)
        
        # Résumé final
        self.log("\n" + "="*60, "INFO")
        self.log("🏁 EXÉCUTION TERMINÉE", "SUCCESS")
        self.log("="*60, "INFO")
        
        success_count = sum(1 for r in results if r['success'])
        self.log(f"✅ Réussis: {success_count}/{len(results)}", "SUCCESS")
        self.log(f"⏱️  Durée totale: {total_duration:.2f}s (estimé: {plan['estimated_time']}s)", "INFO")
        
        return {
            'success': success_count == len(results),
            'results': results,
            'duration': total_duration,
            'logs': self.execution_logs
        }


# ============================================
# FONCTION PRINCIPALE POUR API
# ============================================

async def process_prompt_full(prompt: str) -> Dict:
    """
    Point d'entrée complet:
    1. Orchestration (création du plan)
    2. Exécution (appels API en temps réel)
    """
    
    # Phase 1: Orchestration
    print("\n🎭 PHASE 1: ORCHESTRATION")
    print("="*60)
    orchestration = orchestrate_prompt(prompt)
    
    if not orchestration['understood']:
        return {
            'success': False,
            'error': 'Prompt non compris',
            'orchestration': orchestration
        }
    
    # Phase 2: Exécution
    print("\n⚡ PHASE 2: EXÉCUTION")
    print("="*60)
    executor = KibaliExecutor()
    execution = await executor.execute_plan(orchestration['plan'])
    
    return {
        'success': execution['success'],
        'orchestration': orchestration,
        'execution': execution
    }


# ============================================
# TESTS
# ============================================

if __name__ == "__main__":
    import sys
    
    # Test avec un prompt
    prompt = sys.argv[1] if len(sys.argv) > 1 else "crée un personnage qui court et saute"
    
    print(f"\n{'='*60}")
    print(f"🎯 PROMPT: {prompt}")
    print(f"{'='*60}\n")
    
    result = asyncio.run(process_prompt_full(prompt))
    
    if result['success']:
        print("\n🎉 Succès complet!")
    else:
        print("\n⚠️ Échec ou erreurs")
