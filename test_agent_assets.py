#!/usr/bin/env python3
"""
Test de l'agent LangChain avec recherche d'assets
Vérifie que l'agent utilise FetchCompleteAsset, SearchTextures, WebSearch
"""

import requests
import json
import time

API_URL = "http://localhost:11000"

def test_prompt(prompt, description):
    """Teste un prompt et affiche le résultat"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {description}")
    print(f"📝 Prompt: \"{prompt}\"")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/api/analyze-prompt",
            json={"prompt": prompt, "use_agent": True},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Réponse API:")
            print(f"   Intent: {data.get('intent', 'N/A')}")
            print(f"   Type: {data.get('type', 'N/A')}")
            
            if data.get('agent_output'):
                print(f"\n🤖 Sortie Agent:")
                print(f"   {data['agent_output'][:300]}...")
            
            if data.get('parameters', {}).get('tools_used'):
                print(f"\n🛠️  Outils utilisés:")
                for tool in data['parameters']['tools_used']:
                    print(f"   ✓ {tool}")
            else:
                print("\n⚠️  AUCUN OUTIL UTILISÉ !")
            
            return data
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║   TEST AGENT LANGCHAIN - RECHERCHE ASSETS DYNAMIQUE      ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # Attendre que l'API soit prête
    print("⏳ Attente démarrage API...")
    time.sleep(2)
    
    tests = [
        ("mets une colonne grecque", "Test FetchCompleteAsset - Colonne"),
        ("crée un terrain de football avec textures", "Test FetchCompleteAsset - Terrain"),
        ("cherche texture bois", "Test SearchTextures"),
        ("trouve modèle 3D de stade", "Test Search3DModels"),
        ("caméra orbite 360", "Test contrôle caméra"),
    ]
    
    results = []
    for prompt, desc in tests:
        result = test_prompt(prompt, desc)
        results.append({
            'prompt': prompt,
            'description': desc,
            'success': result is not None,
            'tools_used': result.get('parameters', {}).get('tools_used', []) if result else []
        })
        time.sleep(1)  # Pause entre tests
    
    # Résumé
    print(f"\n\n{'='*60}")
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    for r in results:
        status = "✅" if r['success'] and r['tools_used'] else "❌"
        tools = ", ".join(r['tools_used']) if r['tools_used'] else "AUCUN"
        print(f"{status} {r['description']}")
        print(f"   Outils: {tools}\n")
    
    # Analyse
    total_tests = len(results)
    tests_with_tools = len([r for r in results if r['tools_used']])
    
    print(f"\n🎯 SCORE: {tests_with_tools}/{total_tests} tests utilisent des outils")
    
    if tests_with_tools == total_tests:
        print("✅ PARFAIT! L'agent utilise les outils correctement!")
    elif tests_with_tools >= total_tests * 0.7:
        print("⚠️  L'agent utilise les outils mais peut être amélioré")
    else:
        print("❌ PROBLÈME! L'agent n'utilise pas les outils!")
        print("   → Vérifier le prompt système")
        print("   → Vérifier que LangChain est bien configuré")

if __name__ == "__main__":
    main()
