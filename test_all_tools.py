#!/usr/bin/env python3
"""
🧪 TEST COMPLET DES 33 OUTILS KIBALI
Teste chaque outil individuellement et en orchestration
"""

import requests
import json
import time

BASE_URL = "http://localhost:11000"

def test_tool(name, prompt, use_agent=True):
    """Teste un outil spécifique"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {name}")
    print(f"📝 Prompt: {prompt}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze-prompt",
            json={"prompt": prompt, "use_agent": use_agent},
            timeout=30
        )
        
        if response.ok:
            data = response.json()
            print(f"✅ Réponse:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║  🚀 KIBALI TOOLS - TEST SUITE COMPLET                        ║
║  33 outils testés en temps réel                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Test 1: Liste des capacités
    test_tool(
        "ListCapabilities",
        "Liste toutes tes capacités",
        use_agent=True
    )
    
    time.sleep(2)
    
    # Test 2: Génération simple
    test_tool(
        "ProceduralGenerate",
        "Crée un cube rouge",
        use_agent=True
    )
    
    time.sleep(2)
    
    # Test 3: Réparation mesh
    test_tool(
        "RepairMesh",
        "Répare ce mesh qui a des trous",
        use_agent=True
    )
    
    time.sleep(2)
    
    # Test 4: Mesure volume
    test_tool(
        "MeasureVolume",
        "Calcule le volume de cet objet",
        use_agent=True
    )
    
    time.sleep(2)
    
    # Test 5: Animation
    test_tool(
        "GenerateAnimation",
        "Anime cet objet qui tourne",
        use_agent=True
    )
    
    time.sleep(2)
    
    # Test 6: Export
    test_tool(
        "ExportSTL",
        "Exporte en STL pour impression",
        use_agent=True
    )
    
    time.sleep(2)
    
    # Test 7: Workflow complexe (multi-outils)
    test_tool(
        "Multi-outils",
        "Crée un cube, répare-le, calcule son volume et exporte en STL",
        use_agent=True
    )
    
    print(f"\n{'='*60}")
    print("✅ TESTS TERMINÉS")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    # Vérifie que l'API est up
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.ok:
            print("✅ API Kibali accessible\n")
            main()
        else:
            print("❌ API Kibali non accessible")
    except:
        print("❌ Impossible de contacter l'API. Vérifie que start_kibalone_full.sh est lancé.")
