#!/usr/bin/env python3
"""
🎬 TEST PIPELINE COMPLET
========================
Teste la création d'un personnage animé avec export
"""

import requests
import json
import time

def test_character_with_animation():
    print("\n" + "="*60)
    print("🎬 TEST: Création personnage qui court et saute")
    print("="*60)
    
    # 1. Créer le personnage
    print("\n[1/3] 🎨 Création du personnage...")
    response = requests.post(
        "http://localhost:11005/api/create-character",
        json={"prompt": "personnage héroïque"}
    )
    
    if not response.ok:
        print(f"❌ Erreur création: {response.status_code}")
        return
    
    character = response.json()
    print(f"✅ Personnage créé: {character['id']}")
    print(f"   Parts: {', '.join(character['parts'])}")
    
    character_id = character['id']
    
    # 2. Créer animation de course
    print("\n[2/3] 🏃 Ajout animation course...")
    response = requests.post(
        "http://localhost:11005/api/create-animation",
        json={"objectId": character_id, "animationType": "run"}
    )
    
    if not response.ok:
        print(f"❌ Erreur animation: {response.status_code}")
        return
    
    anim_run = response.json()
    print(f"✅ Animation course: {anim_run['duration']} frames")
    print(f"   Keyframes: {len(anim_run['keyframes'])}")
    
    # 3. Créer animation saut
    print("\n[3/3] 🦘 Ajout animation saut...")
    response = requests.post(
        "http://localhost:11005/api/create-animation",
        json={"objectId": character_id, "animationType": "jump"}
    )
    
    if not response.ok:
        print(f"❌ Erreur animation: {response.status_code}")
        return
    
    anim_jump = response.json()
    print(f"✅ Animation saut: {anim_jump['duration']} frames")
    print(f"   Keyframes: {len(anim_jump['keyframes'])}")
    
    # 4. Résumé
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLET RÉUSSI!")
    print("="*60)
    print(f"\n📦 RÉSULTATS:")
    print(f"   • ID Personnage: {character_id}")
    print(f"   • Parties: {len(character['parts'])}")
    print(f"   • Animation 1: Course (run) - {anim_run['duration']} frames")
    print(f"   • Animation 2: Saut (jump) - {anim_jump['duration']} frames")
    print(f"\n🎯 Code Three.js pour intégration frontend:")
    print(f"""
    // Utiliser ce code dans kibalone-studio.js
    const characterData = {character};
    const runAnimation = {anim_run};
    const jumpAnimation = {anim_jump};
    """)
    
    return {
        'character': character,
        'animations': {
            'run': anim_run,
            'jump': anim_jump
        }
    }

def test_orchestration():
    """Teste l'orchestration complète"""
    print("\n" + "="*60)
    print("🎯 TEST ORCHESTRATION COMPLÈTE")
    print("="*60)
    
    prompt = "crée un personnage qui court et saute"
    print(f"\n💬 Prompt: '{prompt}'")
    
    print("\n⏳ Envoi à l'orchestrateur...")
    response = requests.post(
        "http://localhost:11000/api/orchestrate",
        json={"prompt": prompt, "execute": True},
        timeout=60
    )
    
    if not response.ok:
        print(f"❌ Erreur orchestration: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    
    print(f"\n✅ Compris: {result.get('understood', 'N/A')}")
    
    if 'plan' in result:
        plan = result['plan']
        print(f"\n📋 Plan:")
        print(f"   • Étapes: {len(plan['steps'])}")
        print(f"   • Complexité: {plan['complexity']}")
        
        for i, step in enumerate(plan['steps'], 1):
            print(f"\n   [{i}] {step['tool']}")
            print(f"       → {step['reason']}")
    
    if 'execution' in result:
        exec_result = result['execution']
        print(f"\n⚡ Exécution:")
        print(f"   • Durée: {exec_result.get('total_duration', 0):.2f}s")
        print(f"   • Succès: {exec_result.get('success', False)}")
        
        if 'steps_results' in exec_result:
            print(f"\n📊 Résultats:")
            for i, step_result in enumerate(exec_result['steps_results'], 1):
                status = "✅" if step_result.get('success') else "❌"
                print(f"   {i}. {status} {step_result.get('tool', 'Unknown')}")

if __name__ == "__main__":
    print("\n" + "🌟"*30)
    print("   TEST PIPELINE KIBALONE COMPLET")
    print("🌟"*30)
    
    # Test backend Three.js direct
    print("\n\n🔷 TEST 1: Backend Three.js Direct")
    test_character_with_animation()
    
    time.sleep(2)
    
    # Test orchestration
    print("\n\n🔷 TEST 2: Orchestration Intelligente")
    test_orchestration()
    
    print("\n\n" + "="*60)
    print("✅ TOUS LES TESTS TERMINÉS")
    print("="*60)
