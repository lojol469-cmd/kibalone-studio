# 🤖 KibaliAI - Système de Contrôle par IA

## Vue d'ensemble

KibaliAI est un système robuste qui permet à une IA de manipuler **tous les composants de Kibalone Studio via des commandes en langage naturel**. 

## 🎯 Objectif

Remplacer l'interaction utilisateur traditionnelle par un contrôle intelligent via chat, permettant à l'IA de :
- Manipuler la scène 3D
- Contrôler les widgets et outils
- Automatiser les workflows créatifs
- Répondre à des instructions en français naturel

---

## 🏗️ Architecture

```
KibaliAI (Système Central)
    ├── Module AxisWidget (Widget d'axes 3D)
    ├── Module SceneManager (Gestion de scène) [À venir]
    ├── Module ObjectController (Manipulation objets) [À venir]
    └── Module CameraController (Contrôle caméra) [À venir]
```

### Composants Principaux

1. **`kibaliAI.js`** - Système central
   - Enregistrement de modules
   - Parsing de commandes naturelles
   - Exécution robuste avec gestion d'erreurs
   - Historique et statistiques

2. **`axisWidget.js`** (modifié) - Premier module contrôlable
   - API de contrôle exposée
   - 10+ commandes disponibles
   - Intégration avec le système central

3. **`kibaliAI-test.html`** - Interface de test
   - Chat interface élégante
   - Actions rapides prédéfinies
   - Statistiques en temps réel
   - Console visuelle

---

## 📚 Utilisation

### Initialisation

```javascript
// Le système s'initialise automatiquement au chargement
// Les modules s'enregistrent eux-mêmes

// Vérifier que le système est prêt
console.log(KibaliAI.version); // "1.0.0"
```

### Commandes en Langage Naturel

```javascript
// Syntaxe simple
KibaliAI.executeNatural("cache le widget");
KibaliAI.executeNatural("déplace le widget en haut à droite");
KibaliAI.executeNatural("vue z");
KibaliAI.executeNatural("redimensionne le widget à 150");
KibaliAI.executeNatural("opacité du widget 0.5");
```

### Commandes Directes (API)

```javascript
// Pour un contrôle plus précis
KibaliAI.execute('axisWidget', 'hide', {});
KibaliAI.execute('axisWidget', 'setPosition', { corner: 'top-right' });
KibaliAI.execute('axisWidget', 'setSize', { size: 200 });
KibaliAI.execute('axisWidget', 'rotateCameraTo', { axis: 'z', duration: 1000 });
```

---

## 🎮 Commandes AxisWidget Disponibles

| Commande Naturelle | API | Description |
|-------------------|-----|-------------|
| `cache le widget` | `hide` | Masque le widget d'axes |
| `affiche le widget` | `show` | Affiche le widget d'axes |
| `bascule la visibilité` | `toggle` | Inverse la visibilité |
| `déplace le widget en [position]` | `setPosition` | Positions: haut/bas-gauche/droite |
| `redimensionne le widget à [taille]` | `setSize` | Taille en pixels (50-500) |
| `vue [axe]` | `rotateCameraTo` | Axes: x, -x, y, -y, z, -z |
| `réinitialise la caméra` | `resetCamera` | Position par défaut |
| `opacité du widget [valeur]` | `setOpacity` | Valeur: 0.0-1.0 |
| `status du widget` | `getStatus` | Retourne l'état complet |
| `change couleur axe [x/y/z]` | `setAxisColor` | Avec code couleur hex |

---

## 🔧 Exemples Pratiques

### Scénario 1: Workflow de Présentation

```javascript
// Préparer la vue pour une présentation
KibaliAI.executeNatural("vue z");
await sleep(1000);
KibaliAI.executeNatural("cache le widget");
KibaliAI.executeNatural("opacité du widget 0.3");
```

### Scénario 2: Configuration Rapide

```javascript
// Réorganiser l'interface
KibaliAI.executeNatural("déplace le widget en haut à droite");
KibaliAI.executeNatural("redimensionne le widget à 120");
```

### Scénario 3: Navigation Automatique

```javascript
// Tour des axes
const axes = ['x', 'y', 'z', '-x', '-y', '-z'];
for (let axis of axes) {
    KibaliAI.executeNatural(`vue ${axis}`);
    await sleep(2000);
}
```

---

## 📊 Monitoring et Debug

### Statistiques

```javascript
const stats = KibaliAI.getStats();
console.log(stats);
// {
//   modulesCount: 1,
//   totalCommands: 42,
//   totalErrors: 3,
//   successRate: "92.86%",
//   historySize: 42
// }
```

### Historique

```javascript
const history = KibaliAI.getHistory(10); // 10 dernières commandes
history.forEach(entry => {
    console.log(`${entry.timestamp}: [${entry.module}] ${entry.command}`);
});
```

### Liste des Modules

```javascript
const modules = KibaliAI.listModules();
console.log(modules);
// [
//   {
//     name: "axisWidget",
//     commandCount: 42,
//     errorCount: 3,
//     commands: [...]
//   }
// ]
```

---

## 🚀 Extension du Système

### Ajouter un Nouveau Module

```javascript
// 1. Créer votre module avec une interface AI
MyModule.prototype.initAIControl = function() {
    var _this = this;
    this.aiControl = {
        commands: {
            'doSomething': (params) => _this.doSomething(params),
            'reset': () => _this.reset()
        },
        execute: function(commandName, params) {
            // Logique d'exécution
        },
        listCommands: function() {
            // Liste des commandes
        }
    };
    
    // 2. Enregistrer dans KibaliAI
    KibaliAI.registerModule('myModule', this.aiControl);
}
```

### Ajouter des Patterns de Langage Naturel

Dans `kibaliAI.js`, ajoutez vos patterns dans `parseNaturalCommand()`:

```javascript
{
    regex: /mon pattern ([a-z]+)/i,
    module: 'monModule',
    command: 'maCommande',
    getParams: function(match) {
        return { param: match[1] };
    }
}
```

---

## 🎨 Interface de Test

Ouvrez `kibaliAI-test.html` dans un navigateur pour :
- Tester les commandes visuellement
- Voir les statistiques en temps réel
- Utiliser les actions rapides prédéfinies
- Debug avec la console visuelle

---

## 📝 Format des Réponses

Toutes les commandes retournent un objet standardisé :

```javascript
// Succès
{
    success: true,
    result: { ... },  // Données spécifiques au module
    command: "hide",
    module: "axisWidget"
}

// Erreur
{
    success: false,
    error: "Message d'erreur",
    command: "invalid",
    module: "axisWidget",
    suggestion: "Suggestion pour corriger" // optionnel
}
```

---

## 🔐 Sécurité et Validation

- Validation des paramètres (ranges, types)
- Gestion robuste des erreurs
- Logs détaillés pour debugging
- Isolation des modules
- Historique limité (100 entrées max)

---

## 🛠️ Modules à Venir

1. **SceneManager** - Gestion complète de la scène
   - Ajout/suppression d'objets
   - Manipulation de groupes
   - Import/export

2. **ObjectController** - Contrôle d'objets 3D
   - Position, rotation, échelle
   - Matériaux et textures
   - Animations

3. **CameraController** - Contrôle caméra avancé
   - Trajectoires
   - Points de vue prédéfinis
   - Animations de caméra

4. **LightController** - Gestion de l'éclairage
   - Types de lumières
   - Intensité, couleurs
   - Ombres

5. **MaterialEditor** - Édition de matériaux
   - Propriétés physiques
   - Shaders personnalisés
   - Textures procédurales

---

## 💡 Tips et Bonnes Pratiques

1. **Commandes en Chaîne**: Utilisez des promesses pour séquencer
2. **Feedback Visuel**: Vérifiez toujours `result.success`
3. **Historique**: Consultez l'historique pour débugger
4. **Stats**: Surveillez le taux de succès
5. **Help**: `KibaliAI.help()` pour aide rapide

---

## 🐛 Troubleshooting

### Le système ne répond pas
```javascript
// Vérifier l'initialisation
console.log(typeof KibaliAI); // doit être "object"
console.log(KibaliAI.getStats());
```

### Commande non reconnue
```javascript
// Lister les commandes disponibles
KibaliAI.listCommands();
```

### Erreurs répétées
```javascript
// Vérifier l'historique
const history = KibaliAI.getHistory();
console.log(history.filter(h => !h.success));
```

---

## 📞 Support

Pour toute question ou contribution :
- Consultez l'historique: `KibaliAI.getHistory()`
- Listez les commandes: `KibaliAI.listCommands()`
- Aide: `KibaliAI.help()`

---

## 🎯 Roadmap

- [x] Architecture de base
- [x] Module AxisWidget
- [x] Parsing en langage naturel
- [x] Interface de test
- [ ] Module SceneManager
- [ ] Module ObjectController
- [ ] Module CameraController
- [ ] Intégration backend API
- [ ] Support multi-langues
- [ ] Commandes vocales
- [ ] Machine Learning pour comprendre intentions

---

**Version**: 1.0.0  
**Date**: Décembre 2025  
**Projet**: Kibalone Studio - KibaliAI
