# KIBALONE STUDIO - Système 3D IA

## 🎯 Objectif
Studio 3D contrôlé par IA pour créer des animations, modèles 3D et scènes interactives par prompts.

## 📁 Architecture

```
/home/belikan/Isol/Meshy/
├── kibalone-studio.html          # Interface web principale
├── js/kibalone-studio.js          # Logique Three.js + IA
├── server.js                      # Serveur Node (port 3000)
├── kibali_api.py                  # API Flask (port 5000)
└── Générateurs 3D:
    ├── ai_procedural_3d.py       # Génération par code IA (ACTIF)
    ├── dual_ai_3d_generator.py   # Dual AI (Kibali + Mistral)
    ├── simple_3d_hf.py           # API HuggingFace (expérimental)
    ├── triposr_service_hf.py     # Service TripoSR isolé
    └── triposr_client_hf.py      # Client pour TripoSR
```

## ✅ Ce qui fonctionne

### 1. Interface Kibalone Studio
- **UI complète** avec timeline, viewport 3D, chat AI
- **Three.js** configuré avec OrbitControls
- **Design cyberpunk** avec gradients et effets
- **Sections**: Création, Caméra, Animation, Éclairage

### 2. API Flask (port 5000)
```bash
Endpoints opérationnels:
- GET  /api/health              # Status API
- POST /api/chat                # Chat avec Kibali-IA
- POST /api/generate-model      # Génère code 3D par IA
- POST /api/text-to-3d          # Génération 3D (expérimental)
- POST /api/analyze-prompt      # Analyse intentions
- POST /api/generate-animation  # Génère keyframes
- POST /api/camera-control      # Contrôle caméra
```

### 3. Génération 3D par Code IA (RECOMMANDÉ)
**Fichier**: `ai_procedural_3d.py`

**Principe**:
1. Kibali-IA analyse le prompt
2. Génère du code JavaScript Three.js
3. Frontend exécute le code → objet 3D

**Avantages**:
- ✅ Rapide (4-5 secondes)
- ✅ Pas de dépendances lourdes
- ✅ Flexible et personnalisable
- ✅ Fonctionne immédiatement

**Test**:
```bash
curl -X POST http://localhost:5000/api/generate-model \
  -H "Content-Type: application/json" \
  -d '{"prompt": "un robot avec des bras", "type": "character"}'
```

### 4. JSON-based Generation
**Fichiers**: `js/kibalone-studio.js`

**Méthodes**:
- `generateJSONFromPrompt(prompt)` → Structure JSON
- `buildFromJSON(jsonStructure)` → Three.js objects
- Inspiré du pattern `animation.git`

### 5. Kibali-IA Integration
- **Modèle**: Mistral-7B-Instruct-v0.2 (rapide)
- **Token HF**: Chargé depuis `/home/belikan/kibali-IA/.env`
- **Réponses**: 4-5 secondes
- **Max tokens**: 500 (optimisé pour vitesse)

## ⚠️ Problèmes connus

### 1. Frontend ne rend pas les modèles
**Status**: Backend OK, frontend cassé
**Symptômes**:
- API répond correctement (testé avec curl)
- Aucun modèle n'apparaît dans le viewport
- Console JavaScript pas vérifiée

**TODO**:
- [ ] Ouvrir console navigateur
- [ ] Vérifier `buildFromJSON()` est appelé
- [ ] Tester avec un cube simple d'abord

### 2. TripoSR bloqué par CUDA
**Problème**: Nécessite CUDA 12.0+, système a 11.5
**Composant**: `torchmcubes` compilation échoue

**Solutions tentées**:
- ❌ Installation locale (CUDA mismatch)
- ⏳ API HuggingFace (modèle non disponible)
- ⏳ Service isolé avec isol framework (WIP)

### 3. API HuggingFace 3D
**Status**: Expérimental
**Problèmes**:
- Shap-E: 404 Not Found
- TripoSR: API status inconnu
- Nouveau router HF: `router.huggingface.co`

## 🚀 Démarrage rapide

### 1. Lancer l'écosystème
```bash
cd /home/belikan/Isol/Meshy
bash start_kibalone.sh
```

Cela démarre:
- Node server (port 3000)
- Flask API (port 5000)

### 2. Accès
```
Interface: http://localhost:3000/studio
API Health: http://localhost:5000/api/health
```

### 3. Test génération 3D
```bash
# Via API
curl -X POST http://localhost:5000/api/generate-model \
  -H "Content-Type: application/json" \
  -d '{"prompt": "un guerrier", "type": "character"}'

# Devrait retourner du code JavaScript Three.js
```

## 📋 Prochaines étapes

### Priorité HAUTE
1. **Fix frontend rendering**
   - Debug console JavaScript
   - Vérifier buildFromJSON()
   - Test avec cube simple

2. **Tester pipeline complet**
   - Prompt → JSON → Three.js → Rendu
   - Vérifier que les modèles apparaissent

### Priorité MOYENNE
3. **Système d'animation**
   - Implémenter timeline fonctionnelle
   - Keyframes generation working

4. **Contrôle caméra**
   - Orbite, zoom, pan via prompts
   - Smooth transitions

### Priorité BASSE
5. **Export vidéo**
   - Rendering to MP4
   - Screenshot system

6. **TripoSR réel**
   - Résoudre CUDA 12 ou utiliser API
   - Pour des meshes de meilleure qualité

## 🛠️ Technologies

- **Frontend**: Three.js r128, OrbitControls
- **Backend**: Flask 2.0+, CORS enabled
- **IA**: Mistral-7B-Instruct-v0.2 via HuggingFace
- **3D Generation**: Procédural code génération
- **Serveur**: Node.js + Express
- **GPU**: NVIDIA RTX 5090 (25GB), CUDA 11.5

## 📝 Notes techniques

### Génération par code IA
Le générateur analyse le prompt et produit du code comme:
```javascript
const group = new THREE.Group();
const head = new THREE.Mesh(
  new THREE.SphereGeometry(0.5),
  new THREE.MeshStandardMaterial({color: 0xff0000})
);
head.position.set(0, 1.5, 0);
group.add(head);
// ... arms, legs, etc
return group;
```

Ce code est évalué côté client pour créer l'objet 3D.

### Framework isol
Permet d'isoler des services Python avec dépendances conflictuelles.
**Pattern**: Process isolation + JSON-RPC over stdio

**Usage prévu**:
```python
from base import ServiceBase

class MyService(ServiceBase):
    def process(self, params):
        # Traitement isolé
        return {'result': 'ok'}
```

Communication via stdin/stdout JSON.

## 🔗 Liens utiles

- Kibali-IA: `/home/belikan/kibali-IA`
- Animation reference: `/home/belikan/Isol/animation`
- TripoSR code: `/home/belikan/Isol/triposr_code`
- Isol framework: `/home/belikan/Isol/isol-framework`

## 📧 Workflow de développement

1. **Modification API**: Redémarrer Flask
   ```bash
   pkill -f kibali_api.py
   python3 kibali_api.py &
   ```

2. **Modification frontend**: Refresh navigateur (Ctrl+R)

3. **Test backend seul**:
   ```bash
   curl -X POST http://localhost:5000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "créé un cube"}'
   ```

4. **Logs**:
   ```bash
   tail -f /tmp/kibali_api.log    # API logs
   # Frontend: console navigateur (F12)
   ```

---

**Dernière mise à jour**: 2024-12-05  
**Status**: Backend fonctionnel ✅ | Frontend à débugger ⚠️
