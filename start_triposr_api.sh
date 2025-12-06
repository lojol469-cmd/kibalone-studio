#!/bin/bash
# Démarre l'API TripoSR pour Kibalone Studio

echo "🚀 Démarrage de l'API TripoSR..."

cd /home/belikan/Isol/Kibalone-Studio

# Active l'environnement conda si nécessaire
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    conda activate base
fi

# Installe les dépendances si nécessaire
echo "📦 Vérification des dépendances..."
pip install flask flask-cors torch torchvision rembg pillow requests -q

# Démarre l'API
echo "✅ Démarrage de l'API sur port 5001..."
python3 triposr_api.py
