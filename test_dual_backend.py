#!/usr/bin/env python3
"""
🧪 TEST ARCHITECTURE DOUBLE BACKEND
====================================
Teste l'orchestration avec Blender + Three.js
"""

import requests
import json
import time

def print_header(text):
    print("\n" + "="*60)
    print(f"🎯 {text}")
    print("="*60)

def test_backend(name, url, color):
    """Teste un backend"""
    print(f"\n{color}[TEST] {name}...\033[0m")
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"  \033[92m✅ {name} OK\033[0m")
            return True
        else:
            print(f"  \033[91m❌ {name} ERROR (status {response.status_code})\033[0m")
            return False
    except Exception as e:
        print(f"  \033[91m❌ {name} DOWN: {e}\033[0m")
        return False

def test_orchestration(prompt):
    """Teste l'orchestration complète"""
    print_header(f"Test: {prompt}")
    
    try:
        # Appel orchestration
        response = requests.post(
            "http://localhost:11000/api/orchestrate",
            json={"prompt": prompt, "execute": True},
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        
        # Affiche le plan
        if result.get('understood'):
            print(f"\n✅ Prompt compris: {result['understood']}")
        
        if 'plan' in result:
            plan = result['plan']
            print(f"\n📋 Plan créé:")
            print(f"   • Étapes: {len(plan['steps'])}")
            print(f"   • Complexité: {plan['complexity']}")
            print(f"   • Temps estimé: {plan['estimated_time']}")
            
            print(f"\n🔧 Outils utilisés:")
            for i, step in enumerate(plan['steps'], 1):
                print(f"   {i}. {step['tool']} - {step['reason']}")
        
        # Affiche les résultats d'exécution
        if 'execution' in result:
            exec_result = result['execution']
            print(f"\n⚡ Exécution:")
            print(f"   • Durée totale: {exec_result.get('total_duration', 0):.2f}s")
            print(f"   • Succès: {exec_result.get('success', False)}")
            
            if 'steps_results' in exec_result:
                print(f"\n📊 Résultats par étape:")
                for i, step_result in enumerate(exec_result['steps_results'], 1):
                    status = "✅" if step_result.get('success') else "❌"
                    duration = step_result.get('duration', 0)
                    print(f"   {i}. {status} {step_result.get('tool', 'Unknown')} ({duration:.2f}s)")
                    
                    # Affiche le backend utilisé
                    if 'result' in step_result and 'model_url' in step_result['result']:
                        print(f"      → Blender Backend: {step_result['result']['model_url']}")
                    elif 'result' in step_result and 'id' in step_result['result']:
                        print(f"      → Three.js Backend: {step_result['result']['id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "🌟"*30)
    print("   TEST ARCHITECTURE DOUBLE BACKEND")
    print("🌟"*30)
    
    # Teste les backends
    print_header("Vérification des backends")
    
    backends = [
        ("Kibali Orchestrator", "http://localhost:11000/api/health", "\033[95m"),
        ("Blender Backend", "http://localhost:11004/api/health", "\033[96m"),
        ("Three.js Backend", "http://localhost:11005/api/health", "\033[93m"),
    ]
    
    all_ok = True
    for name, url, color in backends:
        if not test_backend(name, url, color):
            all_ok = False
    
    if not all_ok:
        print("\n❌ Certains backends sont DOWN - lancez start_kibalone_full.sh")
        return
    
    print("\n\033[92m✅ Tous les backends sont UP!\033[0m")
    
    # Tests d'orchestration
    tests = [
        "crée un personnage qui court et saute",
        "crée une sphère rouge",
        "génère un cube bleu qui tourne"
    ]
    
    for prompt in tests:
        test_orchestration(prompt)
        time.sleep(1)
    
    print("\n" + "="*60)
    print("✅ Tests terminés!")
    print("="*60)

if __name__ == "__main__":
    main()
