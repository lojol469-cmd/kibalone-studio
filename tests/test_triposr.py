#!/usr/bin/env python3
"""
Test rapide de TripoSR pour vérifier que tout fonctionne
"""

import sys
sys.path.insert(0, '/home/belikan/Isol/Meshy')

from realistic_generator import RealisticModelGenerator
import os

print("="*60)
print("🎨 TEST TRIPOSR + STABLE DIFFUSION")
print("="*60)

# Check CUDA
import torch
print(f"\n🔥 CUDA disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

# Initialise le générateur
print("\n📥 Initialisation du générateur...")
gen = RealisticModelGenerator()

# Test 1: Simple objet
print("\n" + "="*60)
print("TEST 1: Génération d'un cube magique")
print("="*60)

try:
    result = gen.generate_object("a glowing magical cube with runes")
    if result['success']:
        print(f"✅ SUCCÈS !")
        print(f"   Mesh: {result['mesh_path']}")
        print(f"   Image: {result['image_path']}")
        
        # Vérifie que le fichier existe
        if os.path.exists(result['mesh_path']):
            size = os.path.getsize(result['mesh_path']) / 1024
            print(f"   Taille: {size:.2f} KB")
        else:
            print(f"⚠️ Fichier non trouvé: {result['mesh_path']}")
    else:
        print(f"❌ ÉCHEC: {result.get('error')}")
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ Test terminé !")
print("="*60)
