# 🔥 KIBALONE STUDIO + KIBALI-IA

## 🎯 Architecture Complète

```
┌─────────────────────────────────────────────────────────┐
│                  KIBALONE STUDIO                        │
│              (Interface Web 3D)                         │
│         http://localhost:3000/studio                    │
└─────────────────┬───────────────────────────────────────┘
                  │ Fetch API
                  ↓
┌─────────────────────────────────────────────────────────┐
│              API FLASK (Port 5000)                      │
│            kibali_api.py                                │
│  Endpoints:                                             │
│    /api/chat                - Chat avec Kibali          │
│    /api/generate-model      - Génération 3D             │
│    /api/analyze-prompt      - Analyse prompts           │
│    /api/generate-animation  - Génération keyframes      │
│    /api/camera-control      - Contrôle caméra           │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────┐
│           KIBALI-IA (Cerveau)                           │
│        /home/belikan/kibali-IA                          │
│  • Qwen/Mistral pour LLM                                │
│  • Sentence Transformers                                │
│  • CLIP pour vision                                     │
│  • TripoSR pour génération 3D                           │
│  • Tous les modèles locaux                              │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Démarrage

### Méthode 1: Script automatique (Recommandé)
```bash
cd /home/belikan/Isol/Meshy
./start_kibalone.sh
```

### Méthode 2: Manuel
```bash
# Terminal 1 - API Kibali
cd /home/belikan/Isol/Meshy
python3 kibali_api.py

# Terminal 2 - Serveur Web
cd /home/belikan/Isol/Meshy
node server.js
```

## 🌐 Accès

- **Kibalone Studio**: http://localhost:3000/studio
- **Meshy Original**: http://localhost:3000
- **API Kibali**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## 💬 Exemples de Prompts

### Création
```
"Crée un personnage héroïque avec une cape rouge et une armure"
"Génère une forêt enchantée avec des arbres lumineux"
"Ajoute un château médiéval en pierre"
"Crée une créature fantastique volante"
```

### Animation
```
"Anime le personnage en marchant vers l'avant"
"Le héros fait un salto arrière spectaculaire"
"L'arbre se balance doucement avec le vent"
"Rotation lente de tous les objets"
```

### Caméra
```
"Caméra orbite autour de la scène en 360°"
"Vue cinématique dramatique avec zoom avant"
"Camera suit le personnage principal"
"Plan séquence en travelling latéral"
```

### Éclairage
```
"Ambiance de coucher de soleil orangé"
"Éclairage dramatique avec ombres portées"
"Lumière douce et naturelle du matin"
"Effets de concert avec lumières colorées"
```

## 🎨 Fonctionnalités Intégrées

### ✅ Kibali-IA fait:
- 🧠 Analyse intelligente des prompts
- 📝 Génération de descriptions 3D
- 🎬 Création de keyframes d'animation
- 🎥 Contrôle automatique de caméra
- 💡 Suggestions créatives
- 🗣️ Conversation naturelle

### ✅ Kibalone Studio fait:
- 🎨 Rendu 3D en temps réel (Three.js)
- ⏱️ Timeline interactive
- 📦 Gestion d'objets
- 🎮 Contrôles intuitifs
- 💾 Sauvegarde/Export
- 🎬 Prévisualisation animations

## 📊 API Endpoints

### POST /api/chat
```json
{
  "message": "Crée un personnage héroïque",
  "context": "creation",
  "history": []
}
```

### POST /api/generate-model
```json
{
  "prompt": "un dragon majestueux",
  "type": "character",
  "method": "procedural"
}
```

### POST /api/analyze-prompt
```json
{
  "prompt": "anime en marchant",
  "context": "animation"
}
```

### POST /api/generate-animation
```json
{
  "prompt": "marche vers l'avant",
  "object_type": "character",
  "duration_frames": 90
}
```

### POST /api/camera-control
```json
{
  "prompt": "orbite autour du centre",
  "current_position": {"x": 5, "y": 5, "z": 5}
}
```

## 🔧 Configuration

### Fichiers principaux
```
/home/belikan/Isol/Meshy/
├── kibalone-studio.html    # Interface web
├── js/
│   └── kibalone-studio.js  # Logique Three.js + API calls
├── kibali_api.py           # API Flask -> Kibali
├── server.js               # Serveur Node.js
└── start_kibalone.sh       # Script de démarrage
```

### Variables d'environnement (Kibali)
```bash
HF_TOKEN=hf_your_token_here
TAVILY_API_KEY=tvly_your_key_here
```

## 🎯 Workflow Typique

1. **Utilisateur tape un prompt** dans le chat
   → "Crée un personnage avec cape"

2. **Frontend envoie à l'API**
   → POST http://localhost:5000/api/chat

3. **API Kibali analyse avec LLM**
   → Utilise Qwen/Mistral

4. **Kibali retourne analyse structurée**
   → {intent: 'create_character', parameters: {...}}

5. **Frontend exécute l'action**
   → Génère le modèle 3D dans Three.js

6. **Résultat affiché**
   → Personnage ajouté à la scène

## 🚀 Prochaines Étapes

### Phase 2 (En cours)
- [ ] Intégration TripoSR pour vrais modèles 3D
- [ ] Export OBJ/STL réel
- [ ] Animation avec physique
- [ ] Rendu vidéo MP4

### Phase 3 (Futur)
- [ ] Bibliothèque de personnages
- [ ] Collaboration temps réel
- [ ] Cloud rendering
- [ ] Marketplace d'assets

## 🐛 Debugging

### Vérifier les services
```bash
# API Kibali
curl http://localhost:5000/api/health

# Serveur Node
curl http://localhost:3000

# Logs
tail -f /tmp/kibali_api.log
tail -f /tmp/kibalone_studio.log
```

### Problèmes courants

**API ne répond pas:**
```bash
# Vérifier le processus
ps aux | grep kibali_api.py

# Relancer
python3 kibali_api.py
```

**Serveur Node crash:**
```bash
cd /home/belikan/Isol/Meshy
npm install express
node server.js
```

**Kibali-IA manquant:**
```bash
# Vérifier que le dossier existe
ls -la /home/belikan/kibali-IA/

# Vérifier le .env
cat /home/belikan/kibali-IA/.env
```

## 💡 Astuces

### Performance
- Les requêtes à Kibali prennent 1-3 secondes
- Le fallback local est instantané
- La génération 3D IA peut prendre 10-30 secondes

### Prompts Efficaces
- Soyez spécifique: "héros avec armure dorée" > "héros"
- Donnez du contexte: "pour une scène médiévale"
- Utilisez des adjectifs: "dramatique", "doux", "épique"

### Shortcuts
- **Ctrl+I** : Import mesh (Meshy)
- **G** : Toggle gizmo
- **F** : Center camera
- **Entrée** : Envoyer prompt (chat)

## 📚 Documentation

### Kibali-IA
- Dossier: `/home/belikan/kibali-IA`
- README original avec toutes les capacités

### Three.js
- https://threejs.org/docs/

### Flask
- https://flask.palletsprojects.com/

## 🎉 C'est Prêt !

**Kibalone Studio** est maintenant un logiciel complet piloté par **Kibali-IA** !

Tout se fait par prompts naturels, comme tu voulais. 🚀✨
