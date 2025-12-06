# 📡 KIBALONE STUDIO - Documentation des APIs

## 🌐 Architecture

```
Frontend (11080)
    ↓
┌─────────────────────────────────────────────────┐
│  JavaScript (kibalone-studio.js)                 │
│  • Appelle les APIs via fetch()                  │
│  • Traite les réponses JSON                      │
└─────────────────────────────────────────────────┘
    ↓↓↓
    ↓ http://localhost:11000/api/*
    ↓ http://localhost:11002/api/*
    ↓ http://localhost:11003/api/*
    ↓↓↓
┌─────────────────────────────────────────────────┐
│  Backend APIs (Python Flask)                     │
└─────────────────────────────────────────────────┘
```

---

## 🔵 API KIBALI-IA (Port 11000)

**Service principal** pour l'intelligence artificielle et l'analyse de prompts.

### Endpoints disponibles

#### 1. Health Check
```bash
GET /api/health
```
**Réponse:**
```json
{
  "status": "ok",
  "service": "Kibali-IA API",
  "version": "1.0",
  "model": "mistralai/Mistral-7B-Instruct-v0.2"
}
```

#### 2. Analyse de Prompt ⭐ (Utilisé par le frontend)
```bash
POST /api/analyze-prompt
Content-Type: application/json

{
  "prompt": "Crée un personnage héroïque avec une cape",
  "context": "general"
}
```

**Réponse:**
```json
{
  "success": true,
  "intent": "create",
  "parameters": {
    "type": "character",
    "description": "héroïque avec cape"
  },
  "suggestions": [
    "Définir caractéristiques physiques...",
    "Ajouter détails vestimentaires..."
  ]
}
```

**Types détectés:**
- `character` - Personnages
- `environment` - Environnements/décors
- `object` - Objets 3D
- `camera` - Contrôle caméra
- `animation` - Animations
- `light` - Éclairages

#### 3. Chat
```bash
POST /api/chat

{
  "message": "Comment créer un personnage ?"
}
```

#### 4. Génération de Modèle 3D
```bash
POST /api/generate-model

{
  "prompt": "un robot futuriste",
  "complexity": 7
}
```

#### 5. Génération d'Animation
```bash
POST /api/generate-animation

{
  "prompt": "marcher lentement",
  "duration": 120,
  "fps": 30
}
```

#### 6. Contrôle Caméra
```bash
POST /api/camera-control

{
  "action": "orbit",
  "parameters": {"speed": 0.5}
}
```

---

## 🔵 API MIDAS ISOL (Port 11002)

**Reconstruction 3D** à partir de multiple vues d'images.

### Endpoints disponibles

#### 1. Health Check
```bash
GET /health
```

#### 2. Créer une Session
```bash
POST /api/create_session

{
  "name": "Mon projet château",
  "description": "Reconstruction d'un château"
}
```

**Réponse:**
```json
{
  "success": true,
  "session_id": "uuid-1234-5678",
  "message": "Session créée"
}
```

#### 3. Upload Image
```bash
POST /api/upload_scan

{
  "session_id": "uuid-1234-5678",
  "image": "base64_encoded_image_data"
}
```

#### 4. Générer Mesh 3D
```bash
POST /api/generate_mesh

{
  "session_id": "uuid-1234-5678",
  "quality": "high"
}
```

#### 5. Télécharger Mesh
```bash
GET /api/download_mesh/<session_id>
```
Retourne un fichier `.obj` ou `.ply`

#### 6. Test Reconstruction
```bash
GET /api/test_reconstruction
```
Génère un mesh de test (château) pour démo

---

## 🔵 API MESHY.AI (Port 11003)

**Génération 3D photoréaliste** via service cloud Meshy.ai

### Endpoints disponibles

#### 1. Health Check
```bash
GET /api/health
```

**Réponse:**
```json
{
  "status": "ok",
  "service": "meshy-ai-integration",
  "meshy_configured": false,
  "hf_configured": false
}
```

#### 2. Génération 3D ⭐ (Utilisé par le frontend)
```bash
POST /api/text-to-3d-meshy

{
  "prompt": "un dragon médiéval détaillé",
  "art_style": "realistic",
  "negative_prompt": "low quality, blurry"
}
```

**Réponse (si clé API configurée):**
```json
{
  "success": true,
  "task_id": "meshy_task_123",
  "model_path": "/path/to/model.obj",
  "preview_url": "https://..."
}
```

**Réponse (sans clé API):**
```json
{
  "success": false,
  "error": "MESHY_API_KEY required",
  "message": "Configure MESHY_API_KEY pour utiliser la génération photoréaliste",
  "fallback": "use_procedural"
}
```

**Configuration requise:**
```bash
export MESHY_API_KEY=your_api_key_here
```
Obtenir une clé: https://www.meshy.ai/

---

## 🔴 API TRIPOSR (Port 11001) - ⚠️ NON DISPONIBLE

**Image → 3D** conversion

**Statut:** Module `torchmcubes` manquant

**Installation requise:**
```bash
pip install torchmcubes
```

---

## 📊 Mapping Frontend → Backend

### Depuis `kibalone-studio.js`

```javascript
// 1. Analyse du prompt utilisateur
fetch('http://localhost:11000/api/analyze-prompt', {
  method: 'POST',
  body: JSON.stringify({ prompt: userInput })
})

// 2. Si type='character' détecté → génération via Meshy
fetch('http://localhost:11003/api/text-to-3d-meshy', {
  method: 'POST',
  body: JSON.stringify({ 
    prompt: userInput,
    art_style: 'realistic' 
  })
})
```

### Flux de traitement

1. **Utilisateur tape** : "Crée un personnage héroïque"
2. **Frontend appelle** : `POST /api/analyze-prompt`
3. **Kibali répond** : `{parameters: {type: "character"}}`
4. **Frontend détecte** : `commandType = "character"`
5. **Frontend appelle** : `POST /api/text-to-3d-meshy`
6. **Meshy génère** : Modèle 3D (si clé API disponible)
7. **Frontend crée** : Cube coloré en fallback si erreur

---

## 🧪 Tests manuels

### Test complet du flux

```bash
# 1. Vérifier que les APIs sont actives
curl http://localhost:11000/api/health
curl http://localhost:11002/health
curl http://localhost:11003/api/health

# 2. Tester l'analyse de prompt
curl -X POST http://localhost:11000/api/analyze-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Crée un cube rouge"}'

# 3. Tester la génération Meshy (nécessite API key)
curl -X POST http://localhost:11003/api/text-to-3d-meshy \
  -H "Content-Type: application/json" \
  -d '{"prompt":"a red cube", "art_style":"realistic"}'
```

---

## 🐛 Debugging

### Logs Console JavaScript

Ouvrir la console navigateur (F12) pour voir :
```
📝 Commande détectée: character
📊 Analyse complète: {...}
🎯 Action: character - "Crée un personnage"
```

### Logs Backend

```bash
# Kibali
tail -f /tmp/kibali_api.log

# MiDaS
tail -f /tmp/midas_isol_api.log

# Meshy
tail -f /tmp/meshy_api.log
```

---

## ⚙️ Configuration

### Variables d'environnement

```bash
# API Meshy (optionnel)
export MESHY_API_KEY=your_key

# HuggingFace Token (optionnel)
export HUGGINGFACE_TOKEN=your_token

# Ports personnalisés
export PORT=11000  # Pour chaque API
```

### Lancement

```bash
cd /home/belikan/Isol/Meshy
bash start_kibalone_full.sh
```

Accès: http://localhost:11080/kibalone-studio.html

---

**Dernière mise à jour:** 6 décembre 2025
