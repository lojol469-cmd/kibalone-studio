#!/bin/bash
# Installation complète de MiDaS Multi-View avec Isol Framework
# Guide d'installation automatique

set -e  # Arrêt en cas d'erreur

echo "🚀 INSTALLATION MIDAS MULTI-VIEW + ISOL FRAMEWORK"
echo "=================================================="
echo ""

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction d'affichage
log_info() { echo -e "${GREEN}✅ $1${NC}"; }
log_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

# Vérifier conda
if ! command -v conda &> /dev/null; then
    log_error "Conda non trouvé. Installez Miniconda d'abord."
fi

log_info "Conda trouvé: $(conda --version)"

# Activer l'environnement base
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate base

log_info "Environnement conda activé"

# 1. Installer les dépendances système
echo ""
echo "📦 Installation des dépendances système..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    python3-dev \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

log_info "Dépendances système installées"

# 2. Installer PyTorch avec CUDA si disponible
echo ""
echo "🔥 Installation de PyTorch..."

if command -v nvidia-smi &> /dev/null; then
    log_info "GPU NVIDIA détecté, installation PyTorch avec CUDA"
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 -q
else
    log_warn "Pas de GPU NVIDIA, installation PyTorch CPU"
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu -q
fi

log_info "PyTorch installé"

# 3. Installer Open3D (critique pour la fusion)
echo ""
echo "🎨 Installation Open3D..."
pip install open3d>=0.17.0 -q

log_info "Open3D installé"

# 4. Installer les dépendances de vision/3D
echo ""
echo "👁️  Installation dépendances vision/3D..."
pip install -q \
    opencv-python-headless \
    opencv-contrib-python \
    numpy \
    scipy \
    scikit-image \
    Pillow \
    trimesh \
    pymeshlab \
    vtk

log_info "Dépendances vision/3D installées"

# 5. Installer Flask pour l'API
echo ""
echo "🌐 Installation Flask..."
pip install -q \
    flask \
    flask-cors \
    gunicorn

log_info "Flask installé"

# 6. Installer les utilitaires
echo ""
echo "🔧 Installation utilitaires..."
pip install -q \
    timm \
    ultralytics

log_info "Utilitaires installés"

# 7. Vérifier MiDaS (téléchargement des modèles)
echo ""
echo "🎯 Vérification MiDaS..."
python3 -c "
import torch
print('PyTorch:', torch.__version__)
print('CUDA disponible:', torch.cuda.is_available())

# Télécharger le modèle MiDaS
print('Téléchargement du modèle MiDaS...')
model = torch.hub.load('intel-isl/MiDaS', 'MiDaS_small', pretrained=True, trust_repo=True)
print('✅ Modèle MiDaS téléchargé')
"

log_info "MiDaS vérifié et modèle téléchargé"

# 8. Vérifier Open3D
echo ""
echo "🔍 Vérification Open3D..."
python3 -c "
import open3d as o3d
print('Open3D version:', o3d.__version__)
print('✅ Open3D fonctionne')
"

log_info "Open3D vérifié"

# 9. Créer les liens symboliques pour Isol
echo ""
echo "🔗 Configuration Isol Framework..."

# Copier les modules vers Meshy si pas déjà fait
if [ ! -f "/home/belikan/Isol/Kibalone-Studio/point_cloud_fusion.py" ]; then
    cp /home/belikan/Isol/MidasApi/point_cloud_fusion.py /home/belikan/Isol/Kibalone-Studio/
    log_info "point_cloud_fusion.py copié"
fi

if [ ! -f "/home/belikan/Isol/Kibalone-Studio/depth_enhancement.py" ]; then
    cp /home/belikan/Isol/MidasApi/depth_enhancement.py /home/belikan/Isol/Kibalone-Studio/
    log_info "depth_enhancement.py copié"
fi

# 10. Test de l'API
echo ""
echo "🧪 Test de l'API MiDaS Multi-View..."

cd /home/belikan/Isol/Kibalone-Studio

# Tester l'import des modules
python3 -c "
import sys
sys.path.insert(0, '/home/belikan/Isol/MidasApi')
from point_cloud_fusion import MultiViewFusion, numpy_to_o3d_cloud
from depth_enhancement import DepthEnhancer
import open3d as o3d
print('✅ Tous les modules importés avec succès')
"

log_info "Modules testés avec succès"

# 11. Créer le dossier de logs
mkdir -p /tmp
touch /tmp/midas_multiview_api.log

# 12. Résumé final
echo ""
echo "=================================================="
echo "✅ INSTALLATION TERMINÉE AVEC SUCCÈS !"
echo "=================================================="
echo ""
echo "📋 Résumé de l'installation:"
echo "   • PyTorch: $(python3 -c 'import torch; print(torch.__version__)')"
echo "   • Open3D: $(python3 -c 'import open3d; print(open3d.__version__)')"
echo "   • OpenCV: $(python3 -c 'import cv2; print(cv2.__version__)')"
echo "   • Flask: $(python3 -c 'import flask; print(flask.__version__)')"
echo ""
echo "🚀 Pour démarrer le système:"
echo "   cd /home/belikan/Isol/Kibalone-Studio"
echo "   ./start_kibalone_full.sh"
echo ""
echo "🧪 Pour tester la reconstruction 3D:"
echo "   cd /home/belikan/Isol/Kibalone-Studio"
echo "   ./run_test_reconstruction.sh"
echo ""
echo "📚 Documentation:"
echo "   /home/belikan/Isol/Kibalone-Studio/README_RECONSTRUCTION_3D.md"
echo ""
