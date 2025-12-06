# 🎓 KIBALONE STUDIO - TUTORIEL COMPLET
## Guide Pas-à-Pas de TOUTES les Fonctionnalités

---

## 📋 TABLE DES MATIÈRES

1. [Démarrage Rapide](#démarrage-rapide)
2. [Interface Utilisateur](#interface-utilisateur)
3. [Commandes Vocales IA](#commandes-vocales-ia)
4. [Outils de Génération (5 outils)](#outils-de-génération)
5. [Outils de Reconstruction (4 outils)](#outils-de-reconstruction)
6. [Outils d'Animation (4 outils)](#outils-danimation)
7. [Outils de Modification (6 outils)](#outils-de-modification)
8. [Outils de Mesure (5 outils)](#outils-de-mesure)
9. [Outils d'Impression 3D (4 outils)](#outils-dimpression-3d)
10. [Outils Import/Export (5 outils)](#outils-importexport)
11. [Tests Avant Production](#tests-avant-production)
12. [Exemples de Workflows](#exemples-de-workflows)
13. [Dépannage](#dépannage)

---

## 🚀 DÉMARRAGE RAPIDE

### 1. Lancer Kibalone Studio

```bash
cd /home/belikan/Isol/Meshy
bash start_kibalone_full.sh
```

**Attendez que tous les services démarrent (environ 10 secondes)**

### 2. Ouvrir l'Interface

Dans votre navigateur: **http://localhost:11080/kibalone-studio.html**

### 3. Vérifier que tout fonctionne

- ✅ Scène 3D visible (grille bleue)
- ✅ Console de logs en bas
- ✅ Chat IA à droite
- ✅ Message "✅ Scene 3D prête"

---

## 🖥️ INTERFACE UTILISATEUR

### Zones de l'Interface

```
┌─────────────────────────────────────────────────────────────┐
│  KIBALONE STUDIO        [Save] [Export] [Render]            │
├───────────────┬─────────────────────────────┬───────────────┤
│               │                             │               │
│  PANNEAU      │     VIEWPORT 3D             │  ASSISTANT IA │
│  CRÉATION     │     (Scene Three.js)        │  KIBALONE     │
│               │                             │               │
│ • Nouveau     │  [Grille] [Axes]           │  💬 Chat      │
│ • Personnage  │  [Caméra] [Contrôles]      │  🤖 Statut    │
│ • Environnemt │                             │  📊 Actions   │
│ • Objet       │  Mode: Position             │               │
│               │  Objet: 1                   │  [Envoyer]    │
│ STYLE         │  Frame: 0                   │               │
│ • Nouveau     │  30 FPS                     │               │
│ • Personnage  │                             │               │
│ CAMÉRA        │                             │               │
│ • Position    │                             │               │
│ • Animation   │                             │               │
│ ANIMATION     │                             │               │
│ • Animer      │                             │               │
│ TIMELINE      │                             │               │
├───────────────┴─────────────────────────────┴───────────────┤
│  📊 LOGS SYSTÈME                              [🗑️ Clear]    │
│  [15:30:12] ✅ Scène 3D prête                               │
│  [15:30:15] 🤖 Assistant IA Kibalone connecté               │
└─────────────────────────────────────────────────────────────┘
```

### Contrôles de Base

- **Rotation caméra**: Clic gauche + déplacer
- **Pan (déplacement)**: Clic droit + déplacer
- **Zoom**: Molette de la souris
- **Sélection objet**: Clic sur un objet
- **Mode déplacement**: Touche "G" + mouvement souris
- **Mode rotation**: Touche "R" + mouvement souris
- **Mode scale**: Touche "S" + mouvement souris

---

## 🎤 COMMANDES VOCALES IA

### Comment Parler à Kibali

1. **Cliquez dans le champ de chat** en bas à droite
2. **Tapez votre commande** en langage naturel
3. **Appuyez sur Entrée** ou cliquez "Envoyer"
4. **Kibali analyse** et exécute automatiquement

### Exemples de Commandes

```
✅ "Crée un personnage héroïque"
✅ "Génère un cube rouge de 2 mètres"
✅ "Répare ce mesh qui a des trous"
✅ "Anime cet objet qui tourne"
✅ "Exporte en STL pour impression"
✅ "Calcule le volume de cet objet"
✅ "Que peux-tu faire?"
```

### Niveau de Détail

**Simple:** "Crée un personnage"
**Détaillé:** "Crée un guerrier cyberpunk avec armure néon bleue et cape flottante"
**Workflow:** "Crée un cube, répare-le, optimise à 10k faces et exporte en GLTF"

---

## 🎨 OUTILS DE GÉNÉRATION (5 outils)

### 1. ProceduralGenerate - Génération Rapide

**Usage:** Formes géométriques simples instantanées

**Commandes:**
```
"Crée un cube rouge"
"Ajoute une sphère dorée"
"Génère 5 cylindres aléatoires"
"Fais un torus vert"
```

**Paramètres:**
- Forme: cube, sphere, cylinder, cone, torus, plane
- Couleur: rouge, bleu, vert, doré, etc.
- Taille: "de 2 mètres", "petit", "grand"
- Position: "au centre", "à gauche", "en haut"

**Test:**
```bash
curl -X POST http://localhost:11000/api/analyze-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Crée un cube rouge de 2m", "use_agent": true}'
```

**Temps d'exécution:** < 1 seconde  
**Format de sortie:** Three.js Mesh

---

### 2. MeshyGenerate - Photoréaliste IA

**Usage:** Modèles ultra-réalistes avec textures HD

**Commandes:**
```
"Génère un dragon photoréaliste"
"Crée une voiture de sport rouge brillante"
"Fais un personnage cyberpunk détaillé"
"Génère un vaisseau spatial futuriste"
```

**Paramètres:**
- Art Style: realistic, cartoon, low-poly, voxel
- Détails: "très détaillé", "texture HD", "photoréaliste"
- Matériaux: métal, cuir, tissu, pierre, bois

**Test:**
```bash
curl -X POST http://localhost:11003/api/text-to-3d-meshy \
  -H "Content-Type: application/json" \
  -d '{"prompt": "heroic knight", "art_style": "realistic"}'
```

**Temps d'exécution:** 2-5 minutes  
**Format de sortie:** GLTF/GLB avec textures PBR  
**⚠️ Nécessite:** Clé API Meshy (configurée dans .env)

---

### 3. AdvancedGenerate - Anatomie Complexe

**Usage:** Personnages avec squelette, muscles, rigging

**Commandes:**
```
"Crée un humain avec squelette complet"
"Génère un personnage avec anatomie détaillée"
"Fais un alien avec système musculaire"
```

**Paramètres:**
- Method: grease-pencil, blender-style, anatomical
- Details: skeleton, muscles, skin, rigging
- Style: realistic, stylized, cartoon

**Test:**
```bash
curl -X POST http://localhost:11000/api/generate-advanced \
  -H "Content-Type: application/json" \
  -d '{"prompt": "human character", "method": "grease-pencil"}'
```

**Temps d'exécution:** 30-90 secondes  
**Format de sortie:** GLB avec rigging

---

### 4. RealisticGenerate - Ultra-Réalisme

**Usage:** Combine IA + photogrammétrie

**Commandes:**
```
"Crée un visage humain photoréaliste"
"Génère un environnement forestier dense"
"Fais un bâtiment architectural réaliste"
```

**Paramètres:**
- Type: character, object, environment
- Quality: low, medium, high, ultra
- Details: skin pores, wrinkles, imperfections

**Test:**
```bash
curl -X POST http://localhost:11000/api/generate-realistic \
  -H "Content-Type: application/json" \
  -d '{"prompt": "realistic face", "type": "character"}'
```

**Temps d'exécution:** 3-10 minutes  
**Format de sortie:** GLTF avec textures 4K

---

### 5. TextureGenerate - Textures PBR IA

**Usage:** Génère textures (albedo, normal, roughness, metallic)

**Commandes:**
```
"Applique une texture bois vieilli"
"Génère une texture métal rouillé"
"Crée une texture pierre antique"
"Fais une texture tissu velours"
```

**Paramètres:**
- Style: wood, metal, stone, fabric, skin, sci-fi
- Resolution: 1K, 2K, 4K
- Variation: aged, clean, damaged, worn

**Test:**
```bash
curl -X POST http://localhost:11000/api/generate-texture \
  -H "Content-Type: application/json" \
  -d '{"style": "metal", "resolution": "2K"}'
```

**Temps d'exécution:** 10-30 secondes  
**Format de sortie:** PNG (albedo, normal, roughness, AO)

---

## 🔬 OUTILS DE RECONSTRUCTION (4 outils)

### 6. MiDaSCreateSession - Init Photogrammétrie

**Usage:** Démarre une session de scan 3D multi-vues

**Commandes:**
```
"Commence une reconstruction 3D"
"Initialise un scan photogrammétrie"
"Crée une session de reconstruction"
```

**Test:**
```bash
curl -X POST http://localhost:11002/api/create-session \
  -H "Content-Type: application/json" \
  -d '{"name": "mon_objet"}'
```

**Retour:** `{"session_id": "abc123", "status": "ready"}`

---

### 7. MiDaSUploadImage - Upload Photos

**Usage:** Ajoute des photos à la session

**Commandes:**
```
"Ajoute cette photo à la session"
"Upload 10 images pour le scan"
"Charge ces vues de l'objet"
```

**Minimum:** 3 images  
**Optimal:** 8-20 images  
**Maximum:** 50 images

**Test:**
```bash
curl -X POST http://localhost:11002/api/upload-image \
  -F "session_id=abc123" \
  -F "image=@/path/to/photo.jpg"
```

**Format:** JPG, PNG (max 10MB par image)

---

### 8. MiDaSGenerateMesh - Génère Mesh 3D

**Usage:** Calcule le modèle 3D final

**Commandes:**
```
"Génère le mesh depuis les photos"
"Calcule la reconstruction 3D"
"Crée le modèle final en haute qualité"
```

**Paramètres:**
- Quality: low (rapide), medium (équilibré), high (détails max)

**Test:**
```bash
curl -X POST http://localhost:11002/api/generate-mesh \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123", "quality": "high"}'
```

**Temps d'exécution:** 
- Low: 30s-1min
- Medium: 1-3min
- High: 3-10min

**Format de sortie:** OBJ + textures

---

### 9. TripoSRImageTo3D - Image Unique → 3D

**Usage:** Transforme UNE photo en 3D complet

**Commandes:**
```
"Transforme cette image en 3D"
"Crée un modèle depuis cette photo"
"Convertis ce dessin en 3D"
```

**Test:**
```bash
curl -X POST http://localhost:11001/api/text-to-3d-triposr \
  -H "Content-Type: application/json" \
  -d '{"image_path": "/path/to/image.jpg"}'
```

**Temps d'exécution:** 30-60 secondes  
**Format de sortie:** GLB  
**⚠️ Note:** Module torchmcubes manquant actuellement

---

## 🎬 OUTILS D'ANIMATION (4 outils)

### 10. GenerateAnimation - Animation Procédurale

**Usage:** Anime les objets automatiquement

**Commandes:**
```
"Fais tourner ce cube sur lui-même"
"Anime le personnage qui marche"
"Fais flotter cet objet de haut en bas"
"Crée une rotation de 360° en 5 secondes"
```

**Paramètres:**
- Type: rotate, translate, scale, bounce, float
- Duration: en secondes (1-60s)
- Axis: x, y, z, all
- Easing: linear, ease-in, ease-out, bounce

**Test:**
```bash
curl -X POST http://localhost:11000/api/generate-animation \
  -H "Content-Type: application/json" \
  -d '{"object": "selected", "type": "rotate", "duration": 5}'
```

**Format de sortie:** Keyframes Three.js

---

### 11. CameraAnimation - Caméra Cinématique

**Usage:** Mouvements de caméra fluides

**Commandes:**
```
"Orbite autour du personnage"
"Zoom sur le visage dramatiquement"
"Travelling latéral gauche vers droite"
"Shake la caméra violemment"
"Suis ce personnage en mouvement"
```

**Types d'animations:**
- **Orbit:** Rotation autour d'un point/objet
- **Dolly:** Zoom avant/arrière
- **Pan:** Panoramique horizontal/vertical
- **Shake:** Tremblement (intensité réglable)
- **Follow:** Suit un objet (tracking)

**Test:**
```bash
curl -X POST http://localhost:11000/api/camera-control \
  -H "Content-Type: application/json" \
  -d '{"action": "orbit", "target": "character", "duration": 10}'
```

**Paramètres:**
- Duration: 1-60 secondes
- Speed: slow, normal, fast
- Radius (orbit): distance en mètres
- Intensity (shake): 0.1-1.0

---

### 12. KeyframesCreate - Keyframes Manuels

**Usage:** Contrôle précis des animations

**Commandes:**
```
"Crée un keyframe à 0s position (0,0,0)"
"Ajoute 10 keyframes de rotation sur 5 secondes"
"Keyframe à 0s: (0,0,0), à 5s: (10,0,0)"
```

**Format:**
```
"Temps: Action"
"0s: position(0,0,0), 2s: position(5,0,0), 5s: position(10,5,0)"
```

**Test:**
```bash
curl -X POST http://localhost:11000/api/create-keyframes \
  -H "Content-Type: application/json" \
  -d '{"object": "cube", "keyframes": "0s:(0,0,0), 5s:(10,0,0)"}'
```

---

### 13. OrganicMovement - Mocap IA

**Usage:** Animations réalistes générées par IA

**Commandes:**
```
"Fais marcher ce personnage naturellement"
"Anime ce dragon qui vole"
"Crée une course réaliste"
"Fais sauter le personnage"
```

**Types:**
- **Walk:** Marche naturelle
- **Run:** Course
- **Jump:** Saut avec physique
- **Fly:** Vol organique
- **Swim:** Nage
- **Idle:** Repos avec micro-mouvements

**Test:**
```bash
curl -X POST http://localhost:11000/api/organic-movement \
  -H "Content-Type: application/json" \
  -d '{"character": "hero", "movement": "walk"}'
```

**Temps d'exécution:** 5-15 secondes  
**Format de sortie:** Animation clips (BVH/FBX compatible)

---

## 🔧 OUTILS DE MODIFICATION (6 outils)

### 14. RepairMesh - Réparation Automatique

**Usage:** Corrige géométrie cassée

**Commandes:**
```
"Répare les trous de ce mesh"
"Corrige la géométrie cassée"
"Unifie les vertices dupliqués"
"Ferme les ouvertures"
```

**Corrections automatiques:**
- ✅ Bouche les trous
- ✅ Corrige faces inversées
- ✅ Unifie vertices dupliqués
- ✅ Supprime faces dégénérées
- ✅ Recalcule normales

**Test:**
```bash
curl -X POST http://localhost:11000/api/repair-mesh \
  -H "Content-Type: application/json" \
  -d '{"mesh_id": "selected"}'
```

**Temps d'exécution:** 1-5 secondes  
**Algorithme:** Advancing Front Mesh (AFM)

---

### 15. OptimizeMesh - Optimisation Topologie

**Usage:** Réduit polygones, simplifie géométrie

**Commandes:**
```
"Réduis à 10k triangles"
"Optimise pour mobile (5k polys)"
"Simplifie en gardant les détails"
"Décime à 50% des faces"
```

**Niveaux recommandés:**
- **Mobile:** 5k-10k faces
- **Desktop:** 50k-100k faces
- **VR:** 20k-30k faces
- **Cinématique:** 500k+ faces

**Test:**
```bash
curl -X POST http://localhost:11000/api/optimize-mesh \
  -H "Content-Type: application/json" \
  -d '{"mesh_id": "selected", "target_faces": 10000}'
```

**Options:**
- Preserve edges: oui/non
- Preserve UVs: oui/non
- Quality: 0.1-1.0 (1.0 = détails max)

---

### 16. SubdivideMesh - Subdivision Surface

**Usage:** Augmente résolution/lissage

**Commandes:**
```
"Subdivise 2 fois"
"Lisse ce mesh"
"Augmente la résolution"
```

**Formule:** 1 iteration = 4× triangles

**Test:**
```bash
curl -X POST http://localhost:11000/api/subdivide-mesh \
  -H "Content-Type: application/json" \
  -d '{"mesh_id": "selected", "iterations": 2}'
```

**⚠️ Attention:** 3+ iterations = très lourd!

---

### 17. TransformMesh - Transformations Géométriques

**Usage:** Déplace, tourne, scale les objets

**Commandes:**
```
"Déplace de 5 mètres sur X"
"Tourne de 90° sur Y"
"Scale 2x sur tous axes"
"Déplace à la position (5, 2, 3)"
```

**Opérations:**
- **Translate:** `translate x:5` ou `translate (5,0,0)`
- **Rotate:** `rotate y:90` (degrés)
- **Scale:** `scale 2` ou `scale (2,1,1)`

**Test:**
```bash
curl -X POST http://localhost:11000/api/transform-mesh \
  -H "Content-Type: application/json" \
  -d '{"operation": "translate", "value": "x:5"}'
```

---

### 18. MergeMeshes - Fusion Multiple Objets

**Usage:** Combine plusieurs meshes en un

**Commandes:**
```
"Fusionne tous les objets sélectionnés"
"Combine les pièces du personnage"
"Merge ces 5 cubes en un"
```

**Test:**
```bash
curl -X POST http://localhost:11000/api/merge-meshes \
  -H "Content-Type: application/json" \
  -d '{"mesh_ids": ["cube1", "cube2", "cube3"]}'
```

**Avantages:**
- ✅ 1 seul draw call (performance)
- ✅ Export simplifié
- ✅ Moins de gestion d'objets

---

### 19. BooleanOperation - Opérations Booléennes CSG

**Usage:** Union, soustraction, intersection

**Commandes:**
```
"Soustrais cette sphère du cube"
"Fais l'intersection de ces 2 objets"
"Union de tous les objets"
```

**Opérations:**
- **Union (∪):** Combine 2 meshes
- **Subtract (−):** Soustrait B de A
- **Intersect (∩):** Garde seulement l'intersection

**Test:**
```bash
curl -X POST http://localhost:11000/api/boolean-operation \
  -H "Content-Type: application/json" \
  -d '{"operation": "subtract", "mesh_a": "cube", "mesh_b": "sphere"}'
```

---

## 📐 OUTILS DE MESURE (5 outils)

### 20. MeasureDistance - Distance 2 Points

**Usage:** Calcule distance entre 2 points/objets

**Commandes:**
```
"Mesure distance entre cube et sphère"
"Quelle est la hauteur du personnage?"
"Distance du point A au point B"
```

**Test:**
```bash
curl -X POST http://localhost:11000/api/measure-distance \
  -H "Content-Type: application/json" \
  -d '{"point_a": "cube", "point_b": "sphere"}'
```

**Retour:** Distance en mètres

---

### 21. MeasureVolume - Volume/Surface/Masse

**Usage:** Calculs physiques du mesh

**Commandes:**
```
"Calcule le volume de cet objet"
"Quelle est la surface totale?"
"Où est le centre de masse?"
```

**Test:**
```bash
curl -X POST http://localhost:11000/api/measure-volume \
  -H "Content-Type: application/json" \
  -d '{"mesh_id": "selected"}'
```

**Retour:**
- Volume (m³)
- Surface (m²)
- Centre de masse (x,y,z)
- Densité (si matériau défini)

---

### 22. CalculateBounds - Bounding Box

**Usage:** Dimensions min/max de l'objet

**Commandes:**
```
"Quelle est la taille de la bounding box?"
"Calcule les dimensions XYZ"
"Donne-moi les limites de l'objet"
```

**Test:**
```bash
curl -X POST http://localhost:11000/api/calculate-bounds \
  -H "Content-Type: application/json" \
  -d '{"mesh_id": "selected"}'
```

**Retour:**
```json
{
  "min": [-1.2, -1.5, -0.9],
  "max": [1.3, 1.5, 0.9],
  "size": [2.5, 3.0, 1.8]
}
```

---

### 23. DetectCollisions - Détection Intersections

**Usage:** Vérifie collisions entre objets

**Commandes:**
```
"Est-ce que ces objets se touchent?"
"Détecte toutes les collisions dans la scène"
"Y a-t-il des intersections?"
```

**Test:**
```bash
curl -X POST http://localhost:11000/api/detect-collisions \
  -H "Content-Type: application/json" \
  -d '{"mesh_ids": "all"}'
```

**Retour:** Liste des paires en collision

---

### 24. AnalyzeScene - État Complet Scène

**Usage:** Inventaire et statistiques

**Commandes:**
```
"Analyse la scène complète"
"Combien d'objets y a-t-il?"
"Donne-moi les stats de la scène"
```

**Test:**
```bash
curl -X POST http://localhost:11000/api/analyze-scene \
  -H "Content-Type: application/json" \
  -d '{"query": "état"}'
```

**Retour:**
- Nombre d'objets
- Total de triangles
- Positions caméras
- Lumières actives
- FPS actuel
- Mémoire utilisée

---

## 🏗️ OUTILS D'IMPRESSION 3D (4 outils)

### 25. SliceMesh - Découpage Layers (G-code)

**Usage:** Prépare pour impression 3D

**Commandes:**
```
"Slice ce modèle pour impression"
"Prépare avec support 0.2mm layer"
"Génère le G-code"
```

**Paramètres:**
- **Layer height:** 0.1-0.3mm (0.2 standard)
- **Infill:** 10-100% (20% standard)
- **Support:** auto/manuel
- **Shells:** 2-4 (nombre de contours)

**Test:**
```bash
curl -X POST http://localhost:11000/api/slice-mesh \
  -H "Content-Type: application/json" \
  -d '{"layer_height": 0.2, "infill": 20}'
```

**Temps d'exécution:** 10s-2min selon complexité  
**Format de sortie:** G-code (compatible Cura/PrusaSlicer)

---

### 26. GenerateSupports - Supports Automatiques

**Usage:** Crée structures de support

**Commandes:**
```
"Ajoute des supports pour les overhangs"
"Génère supports angle > 45°"
"Crée supports avec densité 30%"
```

**Paramètres:**
- **Angle:** 30-60° (défaut 45°)
- **Density:** 0.1-0.5 (défaut 0.3)
- **Type:** tree, linear, grid

**Test:**
```bash
curl -X POST http://localhost:11000/api/generate-supports \
  -H "Content-Type: application/json" \
  -d '{"angle": 45, "density": 0.3}'
```

**Algorithme:** Clever Support (Vanek et al. 2014)

---

### 27. OrientForPrint - Orientation Optimale

**Usage:** Oriente pour minimiser supports

**Commandes:**
```
"Oriente ce modèle pour impression optimale"
"Trouve la meilleure orientation"
"Minimise les supports"
```

**Modes:**
- **auto:** Calcul automatique
- **minimal_support:** Moins de supports
- **strength:** Solidité max
- **speed:** Impression rapide

**Test:**
```bash
curl -X POST http://localhost:11000/api/orient-for-print \
  -H "Content-Type: application/json" \
  -d '{"optimization": "minimal_support"}'
```

**Résultat:** Rotation optimale (x,y,z degrés)

---

### 28. CheckPrintability - Vérification Imprimabilité

**Usage:** Détecte problèmes avant impression

**Commandes:**
```
"Est-ce imprimable?"
"Vérifie si c'est prêt pour FDM"
"Détecte les problèmes d'impression"
```

**Vérifications:**
- ✅ Parois trop fines (< 0.4mm)
- ✅ Îlots flottants (non connectés)
- ✅ Overhangs extrêmes (> 70°)
- ✅ Taille plateau dépassée
- ✅ Précision imprimante

**Types d'imprimantes:**
- **FDM:** Filament (Prusa, Ender, etc.)
- **SLA:** Résine (Form3, Elegoo)
- **SLS:** Poudre (industriel)

**Test:**
```bash
curl -X POST http://localhost:11000/api/check-printability \
  -H "Content-Type: application/json" \
  -d '{"printer_type": "FDM"}'
```

---

## 💾 OUTILS IMPORT/EXPORT (5 outils)

### 29. ExportGLTF - Format Web Standard

**Usage:** Export optimisé pour web (Three.js, BabylonJS)

**Commandes:**
```
"Exporte en GLB"
"Sauvegarde pour web"
"Export GLTF avec animations"
```

**Test:**
```bash
curl -X POST http://localhost:11000/api/export-gltf \
  -H "Content-Type: application/json" \
  -d '{"filename": "model.glb"}'
```

**Formats:**
- **.gltf:** JSON + fichiers séparés
- **.glb:** Binaire (tout-en-un)

**Inclus:** Géométrie, textures, matériaux, animations

---

### 30. ExportOBJ - Format Universel

**Usage:** Compatible tous logiciels 3D

**Commandes:**
```
"Exporte en OBJ"
"Sauvegarde pour Blender"
"Export OBJ + MTL"
```

**Test:**
```bash
curl -X POST http://localhost:11000/api/export-obj \
  -H "Content-Type: application/json" \
  -d '{"filename": "model.obj"}'
```

**Fichiers générés:**
- `model.obj` (géométrie)
- `model.mtl` (matériaux)
- `textures/` (images)

**Compatible:** Blender, Maya, 3DS Max, ZBrush, Cinema 4D

---

### 31. ExportSTL - Format Impression 3D

**Usage:** Standard pour slicers

**Commandes:**
```
"Exporte en STL"
"Sauvegarde pour impression"
"Export STL binaire"
```

**Test:**
```bash
curl -X POST http://localhost:11000/api/export-stl \
  -H "Content-Type: application/json" \
  -d '{"filename": "model.stl"}'
```

**Types:**
- **Binary:** Plus petit, plus rapide
- **ASCII:** Lisible humainement

**Compatible:** Cura, PrusaSlicer, Simplify3D

---

### 32. ExportFBX - Format Game Engines

**Usage:** Pour Unity, Unreal, Godot

**Commandes:**
```
"Exporte en FBX"
"Sauvegarde pour Unity"
"Export FBX avec rigging"
```

**Test:**
```bash
curl -X POST http://localhost:11000/api/export-fbx \
  -H "Content-Type: application/json" \
  -d '{"filename": "model.fbx"}'
```

**Inclus:** Animations, rigging, matériaux, colliders

---

### 33. ImportMesh - Import Multiple Formats

**Usage:** Charge fichiers externes

**Commandes:**
```
"Charge ce fichier OBJ"
"Importe le personnage FBX"
"Load model.gltf"
```

**Formats supportés:**
- OBJ (+ MTL)
- STL
- GLTF/GLB
- FBX
- PLY
- DAE (Collada)

**Test:**
```bash
curl -X POST http://localhost:11000/api/import-mesh \
  -H "Content-Type: application/json" \
  -d '{"filepath": "/path/to/model.obj"}'
```

---

## 🧪 TESTS AVANT PRODUCTION

### Test Unitaire de Chaque Outil

```bash
# Lance la suite de tests complète
cd /home/belikan/Isol/Meshy
python3 test_tools_direct.py
```

### Tests Individuels par Catégorie

```bash
# Test génération
curl -X POST http://localhost:11000/api/analyze-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Crée un cube rouge", "use_agent": true}'

# Test réparation
curl -X POST http://localhost:11000/api/analyze-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Répare ce mesh", "use_agent": true}'

# Test animation
curl -X POST http://localhost:11000/api/analyze-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Anime cet objet", "use_agent": true}'

# Test mesure
curl -X POST http://localhost:11000/api/analyze-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Calcule le volume", "use_agent": true}'

# Test export
curl -X POST http://localhost:11000/api/analyze-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Exporte en STL", "use_agent": true}'
```

### Vérification des Services

```bash
# Vérifie que tous les services sont actifs
curl http://localhost:11000/api/health  # Kibali
curl http://localhost:11002/api/health  # MiDaS
curl http://localhost:11003/api/health  # Meshy
```

### Tests de Performance

```bash
# Compte le nombre d'outils chargés
curl -s http://localhost:11000/api/analyze-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "que peux-tu faire?", "use_agent": true}' | jq
```

---

## 🔥 EXEMPLES DE WORKFLOWS COMPLETS

### Workflow 1: Création Simple

```
User: "Crée un personnage héroïque"

Kibali exécute automatiquement:
1. MeshyGenerate("heroic character, armor, cape")
2. AnalyzeScene() → Vérifie que c'est chargé
3. ✅ Affiche: "Personnage créé à la position (0,0,0)"
```

### Workflow 2: Modélisation + Export

```
User: "Crée un cube, répare-le, optimise à 10k faces et exporte en STL"

Kibali exécute:
1. ProceduralGenerate("cube", size=2)
2. RepairMesh() → Corrige géométrie
3. OptimizeMesh(target_faces=10000)
4. ExportSTL("cube_optimized.stl")
5. ✅ "Fichier prêt: cube_optimized.stl"
```

### Workflow 3: Photogrammétrie Complète

```
User: "Scanne cet objet depuis ces 8 photos dans le dossier /images"

Kibali exécute:
1. MiDaSCreateSession() → ID session
2. MiDaSUploadImage(photo1.jpg) × 8
3. MiDaSGenerateMesh(quality="high")
4. RepairMesh() → Nettoie le résultat
5. OptimizeMesh(target_faces=50000)
6. ✅ Affiche le mesh reconstruit
```

### Workflow 4: Animation Cinématique

```
User: "Crée un dragon, fais-le voler et orbite la caméra autour"

Kibali exécute:
1. RealisticGenerate("dragon with wings")
2. OrganicMovement(object="dragon", movement="fly", duration=10)
3. CameraAnimation(type="orbit", target="dragon", duration=10, radius=15)
4. ✅ Lance l'animation preview
```

### Workflow 5: Préparation Impression 3D

```
User: "Prépare ce modèle pour impression FDM avec supports"

Kibali exécute:
1. AnalyzeScene() → Détecte le mesh sélectionné
2. CheckPrintability(printer="FDM") → Vérifie
3. RepairMesh() → Bouche les trous
4. OrientForPrint(optimization="minimal_support")
5. GenerateSupports(angle=50, density=0.3)
6. SliceMesh(layer_height=0.2, infill=20)
7. ExportSTL("ready_to_print.stl")
8. ✅ "Modèle prêt! G-code: output/sliced.gcode"
```

### Workflow 6: Test A/B Textures

```
User: "Génère 3 variations de texture métal pour cet objet"

Kibali exécute:
1. TextureGenerate(style="metal", variation="clean") → Version 1
2. TextureGenerate(style="metal", variation="rusted") → Version 2
3. TextureGenerate(style="metal", variation="scratched") → Version 3
4. ✅ Affiche les 3 versions en preview
```

---

## 🛠️ DÉPANNAGE

### L'agent ne répond pas

**Symptômes:** Interface affiche "❌ Erreur API: Failed to fetch"

**Solutions:**
```bash
# 1. Vérifie que les services sont lancés
lsof -i :11000 -i :11002 -i :11003 | grep LISTEN

# 2. Relance les APIs
pkill -9 python3
cd /home/belikan/Isol/Meshy
bash start_kibalone_full.sh

# 3. Vérifie les logs
tail -f /tmp/kibali_api.log
```

---

### Token HuggingFace invalide

**Symptômes:** "401 Unauthorized" dans les logs

**Solution:**
```bash
# Vérifie le token dans .env
cat /home/belikan/Isol/kibali-IA/.env

# Remplace par ton token
echo "HF_TOKEN=hf_YOUR_TOKEN_HERE" > /home/belikan/Isol/kibali-IA/.env

# Redémarre
pkill -9 -f kibali_api && sleep 2
cd /home/belikan/Isol/Meshy && python3 kibali_api.py &
```

---

### Outil ne s'exécute pas

**Symptômes:** L'agent analyse mais ne fait rien

**Diagnostic:**
```bash
# Regarde les logs détaillés
tail -50 /tmp/kibali_api.log | grep "Agent"

# Vérifie le nombre d'outils chargés
grep "outils chargés" /tmp/kibali_api.log
# Devrait afficher: "✅ 34 outils chargés"
```

**Solution:** Si < 34 outils, vérifie `kibali_tools_registry.py`

---

### Port déjà utilisé

**Symptômes:** "Address already in use"

**Solution:**
```bash
# Tue les processus sur les ports
lsof -ti:11000 | xargs kill -9
lsof -ti:11002 | xargs kill -9
lsof -ti:11003 | xargs kill -9
lsof -ti:11080 | xargs kill -9

# Relance
bash start_kibalone_full.sh
```

---

### Performance lente

**Symptômes:** FPS bas, lags

**Solutions:**
1. **Réduis les polygones:** "Optimise ce mesh à 10k faces"
2. **Désactive ombres:** Dans les paramètres Three.js
3. **LOD (Level of Detail):** Utilise plusieurs versions du mesh
4. **Culling:** Active frustum culling

---

### Mémoire insuffisante

**Symptômes:** Crash après génération

**Solution:**
```bash
# Vérifie la RAM disponible
free -h

# Nettoie les meshes non utilisés
# Dans l'interface: "Supprime tous les objets invisibles"

# Redémarre les services
bash start_kibalone_full.sh
```

---

## 📊 RÉSUMÉ DES COMMANDES UTILES

```bash
# === DÉMARRAGE ===
cd /home/belikan/Isol/Meshy
bash start_kibalone_full.sh

# === ARRÊT ===
pkill -9 -f "kibali_api|meshy_api|midas|triposr|http.server"

# === LOGS ===
tail -f /tmp/kibali_api.log      # Logs Kibali
tail -f /tmp/meshy_api.log       # Logs Meshy
tail -f /tmp/midas_api.log       # Logs MiDaS

# === TESTS ===
python3 test_tools_direct.py     # Tests outils
python3 test_all_tools.py        # Suite complète

# === DEBUG ===
curl http://localhost:11000/api/health    # Vérifie Kibali
lsof -i :11000                            # Vérifie port
ps aux | grep python3                     # Processus Python
```

---

## 🎯 CHECKLIST AVANT PRODUCTION

### Phase 1: Installation
- [ ] Tous les services démarrent sans erreur
- [ ] Interface accessible sur http://localhost:11080
- [ ] 34 outils chargés (vérifie logs)
- [ ] Tokens configurés (.env)

### Phase 2: Tests Unitaires
- [ ] ProceduralGenerate fonctionne
- [ ] MeshyGenerate répond (si clé API)
- [ ] RepairMesh corrige géométrie
- [ ] Animation fonctionne
- [ ] Export STL/OBJ/GLTF réussi

### Phase 3: Tests Workflows
- [ ] Workflow simple (1 outil)
- [ ] Workflow moyen (2-3 outils)
- [ ] Workflow complexe (5+ outils)
- [ ] Photogrammétrie complète
- [ ] Préparation impression 3D

### Phase 4: Performance
- [ ] FPS > 30 avec 10 objets
- [ ] Réponse API < 2 secondes
- [ ] Pas de memory leak après 1h
- [ ] Génération < 5 min (photoréaliste)

### Phase 5: Documentation
- [ ] Tous les outils documentés
- [ ] Exemples testés
- [ ] Vidéos de démo créées
- [ ] FAQ complétée

---

## 🚀 MISE EN PRODUCTION

### 1. Configuration Serveur

```bash
# Installe dependencies
pip install -r requirements.txt

# Configure ports externes
# Dans start_kibalone_full.sh, remplace localhost par 0.0.0.0
```

### 2. Optimisations

```bash
# Active compression GZIP
# Dans kibali_api.py, ajoute Flask-Compress

# Cache des modèles
# Configure Redis pour cache LLM

# Load balancing
# Utilise Nginx pour distribuer requêtes
```

### 3. Monitoring

```bash
# Installe Prometheus + Grafana
docker run -d -p 9090:9090 prom/prometheus

# Dashboard en temps réel
# Métriques: FPS, temps réponse API, RAM, CPU
```

---

## 📞 SUPPORT

### Documentation
- Guide complet: `/home/belikan/Isol/Meshy/KIBALI_TOOLS_COMPLETE_GUIDE.md`
- Ce tutoriel: `/home/belikan/Isol/Meshy/TUTORIAL_COMPLET.md`
- API docs: `/home/belikan/Isol/Meshy/API_DOCUMENTATION.md`

### Logs
- Kibali: `/tmp/kibali_api.log`
- Meshy: `/tmp/meshy_api.log`
- MiDaS: `/tmp/midas_api.log`
- TripoSR: `/tmp/triposr_api.log`

### Commandes Aide
```bash
# Liste des outils disponibles
curl -X POST http://localhost:11000/api/analyze-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "que peux-tu faire?", "use_agent": true}'

# Version et status
curl http://localhost:11000/api/health
```

---

## 🎉 CONCLUSION

Vous maîtrisez maintenant **LES 33 OUTILS** de Kibalone Studio!

**Prochaines étapes:**
1. ✅ Teste chaque outil individuellement
2. ✅ Crée tes propres workflows
3. ✅ Partage tes créations
4. ✅ Contribue au projet

**Bienvenue dans le futur de la création 3D! 🚀**

---

*Dernière mise à jour: 6 décembre 2025*  
*Version: 1.0*  
*Kibalone Studio by Kibali-IA*
