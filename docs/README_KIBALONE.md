# 🎬 Kibalone Studio - Génération 3D avec TripoSR

Interface d'animation 3D pilotée par IA avec génération réaliste via **TripoSR**.

## 🚀 Démarrage Rapide

```bash
cd /home/belikan/Isol/Meshy
./start_kibalone_full.sh
```

Puis ouvrez `kibalone-studio.html` dans votre navigateur.

## 🎯 Architecture

### Backend - API TripoSR (Port 5001)
- **Texte → Image** : Utilise Stable Diffusion ou Hugging Face
- **Image → 3D** : TripoSR génère un mesh réaliste
- **Export** : Convertit en code Three.js pour le navigateur

### Frontend - Kibalone Studio
- **Interface 3D** : Three.js pour le rendu en temps réel
- **Assistant IA** : Analyse les prompts et choisit la méthode optimale
- **Fallbacks** : Si TripoSR n'est pas disponible, génération procédurale

## 🎨 Utilisation

### Exemples de prompts :

**Personnages réalistes (TripoSR)** :
- "Crée un guerrier médiéval avec armure"
- "Personnage robot futuriste"
- "Créature fantastique dragon"

**Environnements** :
- "Environnement forêt magique"
- "Décor de ville cyberpunk"

**Animation** :
- "Anime le personnage en marche"
- "Rotation de caméra cinématique"

## 🔧 Configuration

### Variables d'environnement (optionnel)

```bash
export HUGGINGFACE_TOKEN="your_token"  # Pour Stable Diffusion
export STABILITY_API_KEY="your_key"    # Pour Stability AI
```

### Dépendances Python

```bash
pip install flask flask-cors torch torchvision rembg pillow requests
```

## 📊 Méthodes de Génération

1. **TripoSR** (Priorité 1) : Modèles 3D réalistes haute qualité
2. **Advanced 3D** : Génération procédurale complexe
3. **Grease Pencil** : Dessins 2D/3D stylisés
4. **Simple** : Formes géométriques basiques (fallback)

## 🐛 Dépannage

### L'API TripoSR ne démarre pas
```bash
# Vérifier les logs
tail -f /tmp/triposr_api.log

# Vérifier CUDA
python3 -c "import torch; print(torch.cuda.is_available())"
```

### Modèles trop simples
- Vérifiez que l'API TripoSR est bien démarrée (`curl http://localhost:5001/api/health`)
- Regardez la console du navigateur pour les messages de fallback

### Performance lente
- Réduisez la résolution dans `triposr_api.py` (ligne avec `resolution=256`)
- Utilisez `chunk_size` plus petit si problème de mémoire GPU

## 📁 Structure des Fichiers

```
Meshy/
├── kibalone-studio.html      # Interface principale
├── js/
│   └── kibalone-studio.js    # Logique frontend
├── triposr_api.py            # API TripoSR (backend)
├── start_kibalone_full.sh    # Script de démarrage
└── README_KIBALONE.md        # Ce fichier
```

## 🎓 Notes Techniques

### Optimisations
- Les meshes sont simplifiés à 5000 vertices max pour la performance
- Le background est automatiquement retiré des images
- Les normales sont recalculées pour un rendu optimal

### Formats supportés
- **Export** : OBJ, GLB (via code Three.js)
- **Import images** : PNG, JPG, WEBP

## 🔮 Roadmap

- [ ] Support des animations squelettiques
- [ ] Export vers Blender
- [ ] Galerie de modèles pré-générés
- [ ] Support multi-vues pour TripoSR
- [ ] Textures procédurales avancées

## 📝 Licence

Voir LICENSE
