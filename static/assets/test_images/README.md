# 📸 Dataset de Test - Photogrammétrie Moderne

## 🏰 Source

**Dataset**: Château de Sceaux (OpenMVG)
**Repository**: https://github.com/openMVG/ImageDataset_SceauxCastle

## 📊 Contenu

**Nombre d'images**: 11 photos
**Résolution**: ~3000x2000 pixels
**Format**: JPG
**Poids total**: ~12 MB

## 🎯 Description

Ces images montrent le **Château de Sceaux** photographié sous différents angles. C'est un dataset parfait pour tester la reconstruction 3D multi-vues car :

✅ **Multiple angles** - Photos prises en cercle autour du sujet
✅ **Bon overlap** - ~40-50% de recouvrement entre images adjacentes
✅ **Éclairage constant** - Même conditions d'éclairage
✅ **Haute résolution** - Bonne qualité pour reconstruction précise
✅ **Features riches** - Architecture détaillée (fenêtres, colonnes, textures)

## 🔬 Utilisation pour Tests

### Test Rapide

```bash
cd /home/belikan/Isol/Meshy
python3 test_reconstruction_3d.py
```

### Test dans l'Interface

1. Lancer Kibalone Studio:
   ```bash
   ./start_kibalone_full.sh
   ```

2. Ouvrir `kibalone-studio.html` dans le navigateur

3. Cliquer sur: **📷 Reconstruction 3D → 🔄 Multi-Angles Scan (AI)**

4. Sélectionner toutes les images de `test_images/`

5. Attendre la reconstruction (~2-3 minutes)

## 📈 Résultats Attendus

Avec ces 11 images, vous devriez obtenir :

- **Points totaux**: 80,000 - 150,000 points
- **Taux de réussite**: 80-95%
- **Fitness moyen**: 0.6 - 0.8
- **Temps de traitement**: 2-4 minutes

## 🎨 Visualisation

Après reconstruction, ouvrez les fichiers générés :

```bash
# Avec MeshLab
meshlab reconstruction_*.ply

# Avec CloudCompare
cloudcompare.CloudCompare reconstruction_*.ply
```

## 🔍 Informations Techniques

**Type de scène**: Architecture extérieure
**Distance caméra**: ~10-15 mètres
**Angles de prise de vue**: Circulaire (0° à 330° par pas de 30°)
**Conditions**: Lumière naturelle, ciel couvert (idéal pour la photogrammétrie)

## 📚 Crédit

Dataset original par l'équipe **OpenMVG/openMVS**
Utilisé ici à des fins de test et démonstration
