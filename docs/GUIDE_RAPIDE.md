# 🎯 GUIDE RAPIDE - Reconstruction 3D avec IA Kibali

## ⚡ Installation en 3 étapes

### 1️⃣ Installer toutes les dépendances

```bash
cd /home/belikan/Isol/Meshy
./install_midas_complete.sh
```

⏱️ Temps: 5-10 minutes

### 2️⃣ Démarrer le système

```bash
cd /home/belikan/Isol/Meshy
./start_kibalone_full.sh
```

Vous devriez voir:
```
✅ API TripoSR prête !
✅ API MiDaS Multi-View prête !
```

### 3️⃣ Tester avec les images d'exemple

**Option A - Script automatique:**
```bash
cd /home/belikan/Isol/Meshy
./run_test_reconstruction.sh
```

**Option B - Interface graphique:**
1. Ouvrir `kibalone-studio.html` dans le navigateur
2. Cliquer sur **📷 Reconstruction 3D → 🔄 Multi-Angles Scan (AI)**
3. Sélectionner les 11 images dans `test_images/`
4. Attendre 2-3 minutes
5. Les fichiers PLY se téléchargent automatiquement

## 📊 Résultats Attendus

Avec les 11 images du Château de Sceaux :

✅ **Points**: 80,000 - 150,000 points  
✅ **Taux réussite**: 85-95%  
✅ **Temps**: 2-4 minutes  
✅ **Fichiers**: `reconstruction_xxx.ply` + `mesh_xxx.ply`

## 🎨 Visualiser

```bash
# Installer MeshLab si nécessaire
sudo apt install meshlab

# Ouvrir les résultats
meshlab reconstruction_*.ply
meshlab mesh_*.ply
```

## 🐛 Dépannage Rapide

### API non disponible
```bash
cd /home/belikan/Isol/Meshy
python3 midas_multiview_api.py
```

### Erreur "Open3D not found"
```bash
pip install open3d>=0.17.0
```

### Logs
```bash
tail -f /tmp/midas_multiview_api.log
tail -f /tmp/triposr_api.log
```

## 📸 Vos Propres Photos

Pour scanner vos objets :

1. **Prendre 8-12 photos** en cercle autour de l'objet
2. Angle entre photos : **30-45°**
3. Distance constante
4. Bon éclairage
5. Overlap 30-50%

Puis utiliser l'interface ou le script Python.

## 🎓 Documentation Complète

Pour plus de détails :
- `/home/belikan/Isol/Meshy/README_RECONSTRUCTION_3D.md`
- `/home/belikan/Isol/MidasApi/README.md`

---

**Version**: 1.0 | **Date**: Dec 2025 | **Système**: IA Kibali
