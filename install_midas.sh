#!/bin/bash
# Installation complète de MiDaS Multi-View pour Kibalone Studio
# Via Isol Framework

set -e  # Arrêter en cas d'erreur

echo "🚀 INSTALLATION MIDAS MULTI-VIEW POUR KIBALONE"
echo "=============================================="
echo ""

cd /home/belikan/Isol/Meshy

# 1. Activer conda
echo "📦 Activation de Conda..."
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    conda activate base
    echo "✅ Conda activé"
else
    echo "❌ Conda non trouvé. Installation requise."
    exit 1
fi

# 2. Installer les dépendances système
echo ""
echo "🔧 Installation des dépendances système..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    build-essential \
    cmake \
    git \
    wget \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglu1-mesa-dev \
    freeglut3-dev \
    mesa-common-dev \
    libeigen3-dev \
    imagemagick

echo "✅ Dépendances système installées"

# 3. Installer les packages Python essentiels
echo ""
echo "🐍 Installation des packages Python..."

# PyTorch (si pas déjà installé)
if ! python3 -c "import torch" 2>/dev/null; then
    echo "   Installing PyTorch..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu -q
fi

# OpenCV
pip install opencv-python opencv-contrib-python -q

# Open3D (crucial pour la reconstruction)
echo "   Installing Open3D (peut prendre quelques minutes)..."
pip install open3d>=0.17.0 -q

# NumPy et SciPy
pip install numpy scipy -q

# Flask pour l'API
pip install flask flask-cors -q

# Pillow pour images
pip install Pillow -q

# Trimesh pour géométrie 3D
pip install trimesh -q

echo "✅ Packages Python installés"

# 4. Télécharger et configurer MiDaS
echo ""
echo "📥 Configuration de MiDaS..."

# Le modèle sera téléchargé automatiquement par torch.hub au premier lancement
python3 -c "
import torch
print('🔄 Téléchargement du modèle MiDaS...')
model = torch.hub.load('intel-isl/MiDaS', 'MiDaS_small', pretrained=True, trust_repo=True)
print('✅ Modèle MiDaS téléchargé')
"

# 5. Vérifier que tout fonctionne
echo ""
echo "🧪 Vérification de l'installation..."

python3 << EOF
import sys

errors = []

# Test imports
try:
    import torch
    print("✅ PyTorch:", torch.__version__)
except Exception as e:
    errors.append(f"PyTorch: {e}")
    print(f"❌ PyTorch: {e}")

try:
    import cv2
    print("✅ OpenCV:", cv2.__version__)
except Exception as e:
    errors.append(f"OpenCV: {e}")
    print(f"❌ OpenCV: {e}")

try:
    import open3d as o3d
    print("✅ Open3D:", o3d.__version__)
except Exception as e:
    errors.append(f"Open3D: {e}")
    print(f"❌ Open3D: {e}")

try:
    import numpy as np
    print("✅ NumPy:", np.__version__)
except Exception as e:
    errors.append(f"NumPy: {e}")
    print(f"❌ NumPy: {e}")

try:
    from flask import Flask
    print("✅ Flask installé")
except Exception as e:
    errors.append(f"Flask: {e}")
    print(f"❌ Flask: {e}")

try:
    from PIL import Image
    print("✅ Pillow installé")
except Exception as e:
    errors.append(f"Pillow: {e}")
    print(f"❌ Pillow: {e}")

try:
    import trimesh
    print("✅ Trimesh installé")
except Exception as e:
    errors.append(f"Trimesh: {e}")
    print(f"❌ Trimesh: {e}")

if errors:
    print("\n❌ Erreurs détectées:")
    for err in errors:
        print(f"   - {err}")
    sys.exit(1)
else:
    print("\n✅ Toutes les vérifications réussies!")
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Installation incomplète. Vérifiez les erreurs ci-dessus."
    exit 1
fi

# 6. Créer le dossier test_images s'il n'existe pas
echo ""
echo "📁 Préparation des dossiers..."
mkdir -p test_images
mkdir -p meshes
mkdir -p outputs

# 7. Test rapide de l'API
echo ""
echo "🧪 Test de l'API MiDaS Multi-View..."

# Lancer l'API en arrière-plan
python3 midas_multiview_api.py > /tmp/midas_install_test.log 2>&1 &
API_PID=$!
echo "   API lancée (PID: $API_PID)"

# Attendre le démarrage
echo "   Attente du démarrage (8 secondes)..."
sleep 8

# Test de santé
if curl -s http://localhost:5002/api/health | grep -q "ok"; then
    echo "✅ API fonctionne correctement!"
    
    # Afficher les infos
    curl -s http://localhost:5002/api/health | python3 -m json.tool
else
    echo "⚠️  API non accessible (peut-être en cours de chargement)"
    echo "   Consultez les logs: tail -f /tmp/midas_install_test.log"
fi

# Arrêter l'API de test
kill $API_PID 2>/dev/null
wait $API_PID 2>/dev/null

echo ""
echo "=============================================="
echo "✅ INSTALLATION TERMINÉE AVEC SUCCÈS!"
echo "=============================================="
echo ""
echo "📚 Prochaines étapes:"
echo ""
echo "1. Lancer Kibalone Studio:"
echo "   cd /home/belikan/Isol/Meshy"
echo "   ./start_kibalone_full.sh"
echo ""
echo "2. Ouvrir l'interface:"
echo "   firefox kibalone-studio.html"
echo ""
echo "3. Tester avec le dataset (11 images):"
echo "   ./run_test_reconstruction.sh"
echo ""
echo "4. Dans l'interface web:"
echo "   Cliquer sur: 📷 Reconstruction 3D → 🔄 Multi-Angles Scan (AI)"
echo "   Sélectionner les images de test_images/"
echo ""
echo "📖 Documentation complète:"
echo "   cat README_RECONSTRUCTION_3D.md"
echo ""
