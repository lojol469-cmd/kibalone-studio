# 🎬 Kibalone Studio - IA 3D Animation Platform

**Plateforme complète de création 3D pilotée par IA**

## 🚀 Démarrage Rapide

```bash
cd /home/belikan/Isol/Meshy
./start_kibalone_full.sh
```

Puis ouvrez: **http://localhost:8080/kibalone-studio.html**

## 📁 Structure du Projet

```
Kibalone Studio/
├── 🌐 kibalone-studio.html      # Interface principale
├── 🚀 start_kibalone_full.sh    # Lanceur complet
│
├── api/                          # Services Backend IA
│   ├── kibali_api.py            # Chat IA (port 5000)
│   ├── triposr_api.py           # Image → 3D (port 5001)
│   ├── midas_isol_api.py        # Reconstruction 3D (port 5002)
│   └── meshy_api.py             # Génération 3D (port 5003)
│
├── js/                           # Scripts Frontend
│   └── kibalone-studio.js       # Logique interface
│
├── css/                          # Styles
├── img/                          # Assets visuels
├── meshes/                       # Modèles 3D générés
│
├── tests/                        # Tests unitaires
├── docs/                         # Documentation
└── archives/                     # Anciennes versions
```

## 🔧 Services Disponibles

| Service | Port | Description |
|---------|------|-------------|
| **Interface Web** | 8080 | Interface utilisateur principale |
| **Kibali Chat** | 5000 | IA conversationnelle |
| **TripoSR** | 5001 | Génération 3D depuis image |
| **Reconstruction 3D** | 5002 | Multi-vues photogrammétrie (MiDaS) |
| **Meshy** | 5003 | Génération 3D avancée |

## 🎯 Fonctionnalités

- ✅ **Reconstruction 3D Multi-Vues** - Photogrammétrie IA (MiDaS + Isol)
- ✅ **Image → 3D** - Génération depuis photo (TripoSR)
- ✅ **Chat IA** - Assistant intelligent (Kibali)
- ✅ **Génération 3D** - Création avancée (Meshy)

## 📝 Logs

```bash
tail -f /tmp/*_api.log
```

## 🛑 Arrêt

`Ctrl+C` dans le terminal du script, ou:
```bash
pkill -f kibalone
```

## 🔗 Documentation

- [Guide utilisateur](docs/)
- [API Documentation](api/)
- [Tests](tests/)
