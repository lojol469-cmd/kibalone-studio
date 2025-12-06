#!/usr/bin/env python3
"""Test direct des outils Kibali via API"""
import requests
import json

def test_tool(prompt, description):
    print(f"\n{'='*70}")
    print(f"🧪 TEST: {description}")
    print(f"📝 Prompt: {prompt}")
    print(f"{'='*70}")
    
    response = requests.post(
        'http://localhost:11000/api/analyze-prompt',
        json={'prompt': prompt, 'use_agent': True},
        timeout=30
    )
    
    if response.ok:
        data = response.json()
        print("✅ Réponse:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return data
    else:
        print(f"❌ Erreur: {response.status_code}")
        return None

# Tests des différents outils
print("""
╔══════════════════════════════════════════════════════════════════╗
║           🚀 TEST OUTILS KIBALI EN TEMPS RÉEL                    ║
╚══════════════════════════════════════════════════════════════════╝
""")

# Test 1: Génération
test_tool("Crée un cube rouge de 2 mètres", "ProceduralGenerate")

# Test 2: Réparation
test_tool("Répare ce mesh cassé", "RepairMesh")

# Test 3: Mesure
test_tool("Calcule le volume de cet objet", "MeasureVolume")

# Test 4: Animation
test_tool("Fais tourner cet objet sur lui-même", "GenerateAnimation")

# Test 5: Export
test_tool("Exporte en format STL", "ExportSTL")

# Test 6: Liste capacités
test_tool("Que peux-tu faire?", "ListCapabilities")

print(f"\n{'='*70}")
print("✅ TESTS TERMINÉS")
print(f"{'='*70}\n")
