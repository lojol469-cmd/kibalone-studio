# 🤖 IA Kibali - Reconstruction 3D Multi-Vues

## 📋 Description

L'IA Kibali intègre maintenant un système de **reconstruction 3D complète** à partir de plusieurs photos prises sous différents angles. Cette fonctionnalité utilise **MiDaS** pour l'estimation de profondeur et **Open3D** pour la fusion multi-vues avancée.

## 🚀 Démarrage

### 1. Lancer tous les services

```bash
cd /home/belikan/Isol/Meshy
./start_kibalone_full.sh
```

Cela démarre:
- **API TripoSR** (port 5001) - Génération 3D depuis texte/image
- **API MiDaS Multi-View** (port 5002) - Reconstruction 3D multi-angles

### 2. Ouvrir l'interface

Ouvrez dans votre navigateur:
```
file:///home/belikan/Isol/Meshy/kibalone-studio.html
```

## 📸 Utilisation - Reconstruction Multi-Angles

### Étape 1: Prendre des Photos

**Recommandations**:
- **Nombre**: 8-12 photos minimum
- **Angles**: 30-45° entre chaque photo
- **Distance**: Gardez la même distance de l'objet
- **Overlap**: 30-50% de recouvrement entre photos adjacentes
- **Éclairage**: Constant, éviter les ombres fortes
- **Fond**: Uniforme ou neutre si possible

**Exemple de séquence**:
```
Photos à: 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°
```

### Étape 2: Lancer la Reconstruction

1. Dans Kibalone Studio, cliquez sur:
   ```
   📷 Reconstruction 3D → 🔄 Multi-Angles Scan (AI)
   ```

2. Sélectionnez vos 8-12 photos

3. L'IA Kibali va automatiquement:
   - ✅ Créer une session de reconstruction
   - ✅ Estimer la profondeur de chaque image (MiDaS)
   - ✅ Améliorer les depth maps (filtrage avancé)
   - ✅ Aligner les scans (RANSAC + ICP)
   - ✅ Fusionner les nuages de points (TSDF volumétrique)
   - ✅ Générer le nuage fusionné
   - ✅ Créer un mesh 3D (Poisson)

### Étape 3: Récupérer les Résultats

Deux fichiers sont automatiquement téléchargés:
- `reconstruction_xxxxx.ply` - Nuage de points fusionné
- `mesh_xxxxx.ply` - Mesh triangulaire

## 📊 Suivi en Temps Réel

L'interface affiche:
```
⏳ Progression: 75% (6/8 images - 125,432 points)
```

Et les statistiques finales:
```
✅ Reconstruction terminée!
📊 Points totaux: 125,432
📷 Scans fusionnés: 8
✨ Taux de réussite: 87.5%
```

## 🎨 Visualisation des Résultats

### Option 1: MeshLab (Recommandé)

```bash
# Installer
sudo apt install meshlab

# Visualiser
meshlab reconstruction_xxxxx.ply
meshlab mesh_xxxxx.ply
```

### Option 2: Blender

1. Ouvrir Blender
2. File → Import → Stanford PLY
3. Sélectionner le fichier

### Option 3: CloudCompare

```bash
sudo snap install cloudcompare
cloudcompare.CloudCompare reconstruction_xxxxx.ply
```

## 🔧 Paramètres Avancés

Les paramètres par défaut sont optimisés pour des objets moyens. Pour personnaliser:

### Objet Petit (bijou, pièce)

Modifier dans `midas_multiview_api.py`:
```json
{
  "voxel_size": 0.002,
  "max_correspondence": 0.02
}
```

### Grande Scène / Room Scan

```json
{
  "voxel_size": 0.01,
  "max_correspondence": 0.10
}
```

## 📈 Qualité de Reconstruction

Le **fitness score** (0-1) indique la qualité de l'alignement:

- `> 0.8`: ✅ **Excellent** - Alignement parfait
- `0.5-0.8`: 🟨 **Acceptable** - Bon résultat
- `< 0.5`: ❌ **Mauvais** - Ajouter plus de photos

## 🐛 Troubleshooting

### "API MiDaS Multi-View non disponible"

```bash
# Vérifier que l'API est lancée
curl http://localhost:5002/api/health

# Relancer si nécessaire
cd /home/belikan/Isol/Meshy
python3 midas_multiview_api.py
```

### "Erreur: Open3D non disponible"

```bash
pip install open3d>=0.17.0
```

### Mesh avec trous / qualité faible

**Solutions**:
- Prendre plus de photos (12-16 au lieu de 8)
- Scanner aussi le dessus/dessous de l'objet
- Réduire l'angle entre photos (20-30° au lieu de 45°)
- Améliorer l'éclairage (plus uniforme)

### Alignement échoue (fitness < 0.5)

**Solutions**:
- Angles trop grands entre photos → ajouter photos intermédiaires
- Objet trop uniforme → ajouter des marqueurs/texture
- Overlap insuffisant → prendre photos plus rapprochées

## 🎯 Exemples de Cas d'Usage

### 1. Scanner un Produit (E-commerce)

```
📸 8 photos à 45° d'intervalle
⏱️ Temps: ~2-3 minutes
📦 Résultat: Modèle 3D pour visualisation web
```

### 2. Numérisation d'Objet Culturel

```
📸 12-16 photos (haute qualité)
⏱️ Temps: ~5 minutes
🎨 Résultat: Modèle haute-fidélité pour archivage
```

### 3. Scan d'Espace / Pièce

```
📸 20-30 photos (panoramique)
⏱️ Temps: ~10 minutes
🏠 Résultat: Modèle 3D de l'environnement
```

## 🔍 Architecture Technique

```
┌─────────────────────────────────────────────────────┐
│           Kibalone Studio (Interface)                │
│                kibalone-studio.html                  │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         midas_multiview_api.py (Port 5002)          │
│  • Gestion des sessions                             │
│  • Coordination du pipeline                         │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌─────────────┐ ┌─────────────┐ ┌──────────────────┐
│   MiDaS     │ │   Open3D    │ │ Depth Enhancer   │
│   Depth     │ │   Fusion    │ │   Filtrage       │
└─────────────┘ └─────────────┘ └──────────────────┘
        │            │                    │
        └────────────┴────────────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  Fichiers PLY   │
            │  • Points       │
            │  • Mesh         │
            └─────────────────┘
```

## 📚 Références

- **MiDaS**: https://github.com/isl-org/MiDaS
- **Open3D**: https://www.open3d.org/
- **ICP Algorithm**: Iterative Closest Point
- **TSDF**: Truncated Signed Distance Function
- **Poisson Reconstruction**: Surface reconstruction algorithm

## 📝 Logs et Débogage

Les logs sont disponibles dans:
```
/tmp/midas_multiview_api.log
```

Pour suivre en temps réel:
```bash
tail -f /tmp/midas_multiview_api.log
```

## 🎓 Pour Aller Plus Loin

### Améliorer la Qualité

1. **Multi-pass scanning**: Scanner à différentes hauteurs
2. **HDR photos**: Utiliser des photos haute dynamique
3. **Marqueurs**: Ajouter des points de référence sur l'objet
4. **Post-processing**: Utiliser MeshLab pour nettoyer le mesh

### Automatisation

Créer un script Python pour automatiser la capture:

```python
import requests
from pathlib import Path

# Créer session
session = requests.post('http://localhost:5002/api/create_session').json()
session_id = session['session_id']

# Scanner automatiquement
for angle in range(0, 360, 30):
    # Votre code pour tourner le plateau
    rotate_platform(angle)
    
    # Capturer photo
    photo = capture_photo()
    
    # Upload
    files = {'file': open(photo, 'rb')}
    data = {'session_id': session_id}
    requests.post('http://localhost:5002/api/upload_scan', 
                  files=files, data=data)

# Exporter
requests.get(f'http://localhost:5002/api/get_fused_cloud/{session_id}')
```

---

**Développé par**: IA Kibali System  
**Version**: 1.0  
**Date**: Décembre 2025
