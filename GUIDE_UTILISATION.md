# 🎮 Kibalone Studio - Guide d'Utilisation

## 🚀 Démarrage

```bash
cd /home/belikan/Isol/Meshy
./start_kibalone_full.sh
```

Ouvrez votre navigateur : **http://localhost:8080/kibalone-studio.html**

---

## 🧪 Test Rapide - Reconstruction 3D

### Option 1 : Bouton Direct
Cliquez sur **"🤖 🎬 Test Reconstruction AI"** dans le panneau gauche.
→ Lance automatiquement une reconstruction avec les images de test.

### Option 2 : Prompt Kibali (Chat IA)
Tapez dans le chat :
- `"Lance une reconstruction 3D test"`
- `"Fais un scan du château"`
- `"Reconstruction multi-angles"`

→ Kibali détecte et lance le processus automatiquement !

---

## 🎨 Fonctionnalités Principales

### 1️⃣ Reconstruction 3D Multi-Vues
- **Bouton** : "🔄 Multi-Angles Scan (AI)"
- **Action** : Upload 5-10 photos d'un objet sous différents angles
- **Résultat** : Modèle 3D fusionné dans la scène

### 2️⃣ Charger un Modèle PLY
- **Bouton** : "📂 Charger PLY/Nuage"
- **Format** : Fichiers .ply (nuages de points ou meshes)
- **Source** : MeshLab, CloudCompare, etc.

### 3️⃣ Sélection et Suppression
- **Clic sur objet** : Sélectionner (surbrillance verte)
- **Panneau Sélection** : Affiche nom, type, nombre de vertices
- **🗑️ Bouton Supprimer** : Efface l'objet sélectionné

### 4️⃣ Chat Kibali IA
Exemples de commandes :
```
"Crée un personnage cyberpunk"
"Ajoute une lumière bleue"
"Anime la caméra"
"Lance une reconstruction 3D test"
```

---

## 🖱️ Contrôles de la Scène 3D

| Action | Commande |
|--------|----------|
| **Orbiter** | Clic gauche + Glisser |
| **Zoomer** | Molette souris |
| **Sélectionner** | Clic sur objet |
| **Supprimer** | Bouton 🗑️ après sélection |

---

## 📂 Structure des Fichiers

```
Isol/Meshy/
├── kibalone-studio.html          # Interface principale
├── js/kibalone-studio.js         # Logique frontend
├── test_images/                  # Images de test (château)
│   ├── image_01.jpg ... image_11.jpg
│   └── README.md
├── midas_isol_api.py            # API Reconstruction 3D
├── kibali_api.py                # API Chat IA
├── meshy_api.py                 # API Génération 3D
└── start_kibalone_full.sh       # Script de lancement
```

---

## 🔧 APIs Backend

| Service | Port | Description |
|---------|------|-------------|
| **Interface Web** | 8080 | Interface Kibalone Studio |
| **Kibali Chat** | 5000 | IA conversationnelle |
| **TripoSR** | 5001 | Image → Modèle 3D |
| **Reconstruction 3D** | 5002 | Multi-vues MiDaS |
| **Meshy** | 5003 | Génération 3D avancée |

---

## 📊 Workflow de Reconstruction

1. **Upload Images** → API crée une session
2. **Traitement** → MiDaS calcule la profondeur
3. **Fusion** → RANSAC + ICP alignent les nuages
4. **Génération** → Poisson reconstruction crée le mesh
5. **Affichage** → Three.js charge le PLY dans la scène

---

## 💡 Astuces

### Pour une Bonne Reconstruction
✅ Prenez 5-10 photos autour de l'objet
✅ Angle entre photos : 30-45°
✅ Éclairage constant
✅ Évitez les surfaces réfléchissantes
✅ Gardez l'objet au centre

### Prompts Kibali Utiles
```
"Reconstruction 3D test"          → Lance test auto
"Crée un personnage ninja"        → Génère modèle 3D
"Ajoute lumière rouge"            → Éclairage scène
"Anime la caméra en rotation"    → Animation
```

---

## 🐛 Dépannage

**Services ne démarrent pas**
```bash
# Vérifier les ports
lsof -i :5000,5002,8080

# Tuer les processus
pkill -f midas_isol_api
pkill -f http.server

# Redémarrer
./start_kibalone_full.sh
```

**Reconstruction échoue**
```bash
# Vérifier les logs
tail -f /tmp/midas_isol_api.log

# Tester l'API
curl http://localhost:5002/health
```

**Modèle n'apparaît pas**
- F12 → Console navigateur (erreurs JS)
- Vérifier que PLYLoader.js est chargé
- Essayer de zoomer/dézoomer

---

## 📞 Support

- **Logs** : `/tmp/*.log`
- **Test images** : `test_images/`
- **Documentation** : Ce fichier + README dans test_images/

---

## 🎯 Checklist Premier Lancement

- [ ] Services démarrés (`./start_kibalone_full.sh`)
- [ ] Interface ouverte (http://localhost:8080/kibalone-studio.html)
- [ ] Cliquer sur "🤖 🎬 Test Reconstruction AI"
- [ ] Attendre 30-60s
- [ ] Modèle du château apparaît dans la scène
- [ ] Tester sélection (clic sur modèle)
- [ ] Tester suppression (bouton 🗑️)
- [ ] Tester prompt Kibali : "Reconstruction 3D test"

---

**🎉 Profitez de Kibalone Studio !**
