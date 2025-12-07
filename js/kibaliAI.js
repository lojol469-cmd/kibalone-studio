/**
 * KibaliAI - Système centralisé de contrôle par IA via chat
 * Permet à l'IA de manipuler tous les composants de Kibalone Studio
 * 
 * Architecture:
 * - Enregistrement de modules (axisWidget, sceneManager, etc.)
 * - Parsing de commandes en langage naturel
 * - Exécution robuste avec validation et logs
 * - Historique des commandes
 */

var KibaliAI = (function() {
  'use strict';
  
  var modules = {};
  var commandHistory = [];
  var maxHistorySize = 100;
  
  return {
    version: '1.0.0',
    
    /**
     * Enregistre un nouveau module contrôlable par l'IA
     * @param {string} moduleName - Nom du module
     * @param {object} moduleInterface - Interface du module avec commandes
     */
    registerModule: function(moduleName, moduleInterface) {
      if (modules[moduleName]) {
        console.warn(`[KibaliAI] Module "${moduleName}" déjà enregistré, écrasement...`);
      }
      
      modules[moduleName] = {
        interface: moduleInterface,
        registeredAt: new Date(),
        commandCount: 0,
        errorCount: 0
      };
      
      console.log(`[KibaliAI] Module "${moduleName}" enregistré avec succès`);
      return true;
    },
    
    /**
     * Exécute une commande sur un module
     * @param {string} moduleName - Nom du module
     * @param {string} commandName - Nom de la commande
     * @param {object} params - Paramètres de la commande
     */
    execute: function(moduleName, commandName, params) {
      var timestamp = new Date();
      
      try {
        // Validation du module
        if (!modules[moduleName]) {
          throw new Error(`Module "${moduleName}" non trouvé. Modules disponibles: ${Object.keys(modules).join(', ')}`);
        }
        
        var module = modules[moduleName];
        
        // Exécution de la commande
        var result = module.interface.execute(commandName, params);
        
        // Mise à jour des statistiques
        module.commandCount++;
        if (!result.success) {
          module.errorCount++;
        }
        
        // Ajout à l'historique
        this.addToHistory({
          timestamp: timestamp,
          module: moduleName,
          command: commandName,
          params: params,
          result: result,
          success: result.success
        });
        
        return result;
        
      } catch (error) {
        console.error('[KibaliAI] Erreur d\'exécution:', error);
        
        var errorResult = {
          success: false,
          error: error.message,
          module: moduleName,
          command: commandName
        };
        
        this.addToHistory({
          timestamp: timestamp,
          module: moduleName,
          command: commandName,
          params: params,
          result: errorResult,
          success: false
        });
        
        if (modules[moduleName]) {
          modules[moduleName].errorCount++;
        }
        
        return errorResult;
      }
    },
    
    /**
     * Parse et exécute une commande en langage naturel
     * @param {string} naturalCommand - Commande en langage naturel
     */
    executeNatural: function(naturalCommand) {
      console.log(`[KibaliAI] Parsing: "${naturalCommand}"`);
      
      var parsed = this.parseNaturalCommand(naturalCommand);
      
      if (!parsed) {
        return {
          success: false,
          error: 'Impossible de comprendre la commande',
          suggestion: 'Utilisez listCommands() pour voir les commandes disponibles'
        };
      }
      
      console.log('[KibaliAI] Commande parsée:', parsed);
      return this.execute(parsed.module, parsed.command, parsed.params);
    },
    
    /**
     * Parse une commande en langage naturel vers une commande structurée
     * @param {string} text - Texte de la commande
     * @returns {object|null} Commande structurée ou null
     */
    parseNaturalCommand: function(text) {
      text = text.toLowerCase().trim();
      
      // Patterns de commandes pour AxisWidget
      var patterns = [
        {
          regex: /cache (le widget|les axes|l'axe|axiswidget)/i,
          module: 'axisWidget',
          command: 'hide',
          params: {}
        },
        {
          regex: /affiche (le widget|les axes|l'axe|axiswidget)/i,
          module: 'axisWidget',
          command: 'show',
          params: {}
        },
        {
          regex: /masque (le widget|les axes)/i,
          module: 'axisWidget',
          command: 'hide',
          params: {}
        },
        {
          regex: /montre (le widget|les axes)/i,
          module: 'axisWidget',
          command: 'show',
          params: {}
        },
        {
          regex: /bascule (le widget|les axes|la visibilité)/i,
          module: 'axisWidget',
          command: 'toggle',
          params: {}
        },
        {
          regex: /d[ée]place.*widget.*en (haut|bas)[\s-]*(gauche|droite)/i,
          module: 'axisWidget',
          command: 'setPosition',
          getParams: function(match) {
            var vertical = match[1];
            var horizontal = match[2];
            var corner = `${vertical === 'haut' ? 'top' : 'bottom'}-${horizontal === 'gauche' ? 'left' : 'right'}`;
            return { corner: corner };
          }
        },
        {
          regex: /(?:redimensionne|agrandit|r[ée]duit).*widget.*?(\d+)/i,
          module: 'axisWidget',
          command: 'setSize',
          getParams: function(match) {
            return { size: parseInt(match[1]) };
          }
        },
        {
          regex: /change.*couleur.*axe\s+(x|y|z).*(?:#([0-9a-f]{6})|(0x[0-9a-f]{6}))/i,
          module: 'axisWidget',
          command: 'setAxisColor',
          getParams: function(match) {
            var color = match[2] ? parseInt(match[2], 16) : parseInt(match[3]);
            return { axis: match[1], color: color };
          }
        },
        {
          regex: /oriente.*cam[ée]ra.*vers.*axe\s+([-]?[xyz])/i,
          module: 'axisWidget',
          command: 'rotateCameraTo',
          getParams: function(match) {
            return { axis: match[1], duration: 1000 };
          }
        },
        {
          regex: /vue\s+([-]?[xyz])/i,
          module: 'axisWidget',
          command: 'rotateCameraTo',
          getParams: function(match) {
            return { axis: match[1], duration: 800 };
          }
        },
        {
          regex: /r[ée]initialise.*cam[ée]ra/i,
          module: 'axisWidget',
          command: 'resetCamera',
          params: {}
        },
        {
          regex: /opacit[ée].*widget.*?(0?\.\d+|1\.?0?)/i,
          module: 'axisWidget',
          command: 'setOpacity',
          getParams: function(match) {
            return { opacity: parseFloat(match[1]) };
          }
        },
        {
          regex: /(?:status|[ée]tat).*widget/i,
          module: 'axisWidget',
          command: 'getStatus',
          params: {}
        },
        
        // ========== COMMANDES CAMÉRA ==========
        {
          regex: /(?:fais\s+)?tourne(?:r)?.*cam[ée]ra.*360.*?(\d+)?\s*(?:seconde|sec|s)?/i,
          module: 'camera',
          command: 'rotate360',
          getParams: function(match) {
            var seconds = match[1] ? parseInt(match[1]) : 5;
            return { duration: seconds * 1000, axis: 'y' };
          }
        },
        {
          regex: /(?:fais\s+)?tourne(?:r)?.*cam[ée]ra/i,
          module: 'camera',
          command: 'rotate360',
          params: { duration: 5000, axis: 'y' }
        },
        {
          regex: /orbite.*autour.*?(\d+)\s*(?:degr[ée]|°)?.*?(\d+)?\s*(?:seconde|sec|s)?/i,
          module: 'camera',
          command: 'orbitAround',
          getParams: function(match) {
            var angle = parseInt(match[1]);
            var seconds = match[2] ? parseInt(match[2]) : 3;
            return { target: {x:0, y:0, z:0}, angle: angle, duration: seconds * 1000 };
          }
        },
        {
          regex: /zoom.*?(avant|arri[èe]re|in|out)/i,
          module: 'camera',
          command: 'zoom',
          getParams: function(match) {
            var direction = match[1].toLowerCase();
            var factor = (direction === 'avant' || direction === 'in') ? 0.7 : 1.3;
            return { factor: factor, duration: 500 };
          }
        },
        {
          regex: /zoom.*?(\d+\.?\d*)x?/i,
          module: 'camera',
          command: 'zoom',
          getParams: function(match) {
            return { factor: parseFloat(match[1]), duration: 500 };
          }
        },
        {
          regex: /(?:effet\s+)?(?:tremble|shake)/i,
          module: 'camera',
          command: 'shake',
          params: { intensity: 0.5, duration: 500 }
        },
        {
          regex: /r[ée]initialise.*cam[ée]ra|reset.*cam/i,
          module: 'camera',
          command: 'reset',
          params: {}
        },
        {
          regex: /arr[êe]te.*animation.*cam[ée]ra|stop.*cam/i,
          module: 'camera',
          command: 'stopAnimation',
          params: {}
        },
        {
          regex: /position.*cam[ée]ra|o[ùu]\s+est.*cam[ée]ra/i,
          module: 'camera',
          command: 'getPosition',
          params: {}
        },
        {
          regex: /(?:change|modifie).*fov.*?(\d+)/i,
          module: 'camera',
          command: 'setFOV',
          getParams: function(match) {
            return { fov: parseInt(match[1]), duration: 500 };
          }
        },
        {
          regex: /(?:effet\s+)?(?:vertigo|dolly|hitchcock)/i,
          module: 'camera',
          command: 'dollyZoom',
          params: { duration: 2000 }
        },
        {
          regex: /d[ée]place.*cam[ée]ra.*?(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)/i,
          module: 'camera',
          command: 'moveTo',
          getParams: function(match) {
            return {
              x: parseFloat(match[1]),
              y: parseFloat(match[2]),
              z: parseFloat(match[3]),
              duration: 1000
            };
          }
        },
        {
          regex: /regarde.*?(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)/i,
          module: 'camera',
          command: 'lookAt',
          getParams: function(match) {
            return {
              x: parseFloat(match[1]),
              y: parseFloat(match[2]),
              z: parseFloat(match[3])
            };
          }
        }
      ];
      
      // Recherche du pattern correspondant
      for (var i = 0; i < patterns.length; i++) {
        var pattern = patterns[i];
        var match = text.match(pattern.regex);
        
        if (match) {
          return {
            module: pattern.module,
            command: pattern.command,
            params: pattern.getParams ? pattern.getParams(match) : pattern.params
          };
        }
      }
      
      // Si aucun pattern ne matche, essayer avec l'IA
      return this.parseWithAI(text);
    },
    
    /**
     * Parse une commande avec l'IA (fallback intelligent)
     * Utilise des heuristiques + analyse sémantique
     */
    parseWithAI: function(text) {
      console.log('[KibaliAI] Analyse sémantique:', text);
      
      // Mots-clés par module
      var keywords = {
        axisWidget: ['widget', 'axes', 'axe', 'repère', 'repere'],
        camera: ['caméra', 'camera', 'vue', 'tourne', 'rotation', 'zoom', 'orbite', 
                 'regard', 'déplace', 'deplace', 'bouge', 'anime'],
        viewport: ['viewport', 'fenêtre', 'fenetre', 'mini', 'preview', 'aperçu', 'apercu']
      };
      
      // Détection du module
      var detectedModule = null;
      var maxScore = 0;
      
      for (var module in keywords) {
        var score = 0;
        keywords[module].forEach(function(keyword) {
          if (text.includes(keyword)) score++;
        });
        if (score > maxScore) {
          maxScore = score;
          detectedModule = module;
        }
      }
      
      if (!detectedModule) {
        return null;
      }
      
      // Détection de la commande selon le module
      if (detectedModule === 'axisWidget') {
        return this.parseAxisWidgetCommand(text);
      } else if (detectedModule === 'camera') {
        return this.parseCameraCommand(text);
      } else if (detectedModule === 'viewport') {
        return this.parseViewportCommand(text);
      }
      
      return null;
    },
    
    /**
     * Parse les commandes du viewport
     */
    parseViewportCommand: function(text) {
      // Cache/Affiche
      if (text.match(/(?:cache|masque)/)) {
        return { module: 'viewport', command: 'hide', params: {} };
      }
      if (text.match(/(?:affiche|montre)/)) {
        return { module: 'viewport', command: 'show', params: {} };
      }
      
      // Position
      if (text.match(/(?:déplace|deplace|met|place|positionne)/)) {
        var position = null;
        
        if (text.match(/haut.*droite|droite.*haut/)) position = 'top-right';
        else if (text.match(/haut.*gauche|gauche.*haut/)) position = 'top-left';
        else if (text.match(/bas.*droite|droite.*bas/)) position = 'bottom-right';
        else if (text.match(/bas.*gauche|gauche.*bas/)) position = 'bottom-left';
        
        if (position) {
          return { module: 'viewport', command: 'setPosition', params: { position: position } };
        }
      }
      
      // Taille
      if (text.match(/(?:grand|agrand|large)/)) {
        return { module: 'viewport', command: 'resize', params: { large: true } };
      }
      if (text.match(/(?:petit|r[ée]duit)/)) {
        return { module: 'viewport', command: 'resize', params: { large: false } };
      }
      
      return null;
    },
    
    /**
     * Parse les commandes du widget d'axes
     */
    parseAxisWidgetCommand: function(text) {
      // Cache/Masque/Invisible
      if (text.match(/(?:cache|masque|invisible|disparait)/)) {
        return { module: 'axisWidget', command: 'hide', params: {} };
      }
      
      // Affiche/Montre/Visible
      if (text.match(/(?:affiche|montre|visible|apparait)/)) {
        return { module: 'axisWidget', command: 'show', params: {} };
      }
      
      // Déplacement
      if (text.match(/(?:déplace|deplace|met|place|positionne)/)) {
        var corner = null;
        
        if (text.match(/haut.*droite|droite.*haut/)) corner = 'top-right';
        else if (text.match(/haut.*gauche|gauche.*haut/)) corner = 'top-left';
        else if (text.match(/bas.*droite|droite.*bas/)) corner = 'bottom-right';
        else if (text.match(/bas.*gauche|gauche.*bas/)) corner = 'bottom-left';
        else if (text.match(/haut/)) corner = 'top-left';
        else if (text.match(/bas/)) corner = 'bottom-left';
        else if (text.match(/droite/)) corner = 'bottom-right';
        else if (text.match(/gauche/)) corner = 'bottom-left';
        
        if (corner) {
          return { module: 'axisWidget', command: 'setPosition', params: { corner: corner } };
        }
      }
      
      // Taille
      var sizeMatch = text.match(/(\d+)\s*(?:px|pixel)?/);
      if (sizeMatch && text.match(/(?:taille|grand|petit|dimension)/)) {
        return { module: 'axisWidget', command: 'setSize', params: { size: parseInt(sizeMatch[1]) } };
      }
      
      // Opacité
      var opacityMatch = text.match(/(0?\.\d+|1\.?0?)/);
      if (opacityMatch && text.match(/opacit[ée]/)) {
        return { module: 'axisWidget', command: 'setOpacity', params: { opacity: parseFloat(opacityMatch[1]) } };
      }
      
      return null;
    },
    
    /**
     * Parse les commandes de caméra
     */
    parseCameraCommand: function(text) {
      // Déplacement de position (mettre la caméra quelque part)
      if (text.match(/(?:met|mets|place|positionne).*(?:cam[ée]ra|vue)/)) {
        // Position spécifique avec coordonnées
        var coordMatch = text.match(/(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)/);
        if (coordMatch) {
          return { 
            module: 'camera', 
            command: 'moveTo', 
            params: { 
              x: parseFloat(coordMatch[1]), 
              y: parseFloat(coordMatch[2]), 
              z: parseFloat(coordMatch[3]),
              duration: 1000 
            } 
          };
        }
        
        // Position relative (gauche, droite, haut, bas)
        var distance = 50;
        if (text.match(/gauche/)) {
          return { module: 'camera', command: 'moveTo', params: { x: -distance, y: 0, z: 0, duration: 1000 } };
        }
        if (text.match(/droite/)) {
          return { module: 'camera', command: 'moveTo', params: { x: distance, y: 0, z: 0, duration: 1000 } };
        }
        if (text.match(/haut/)) {
          return { module: 'camera', command: 'moveTo', params: { x: 0, y: distance, z: 0, duration: 1000 } };
        }
        if (text.match(/bas/)) {
          return { module: 'camera', command: 'moveTo', params: { x: 0, y: -distance, z: 0, duration: 1000 } };
        }
      }
      
      // Rotation 360
      if (text.match(/(?:tourne|rotation|360|tour)/)) {
        var durationMatch = text.match(/(\d+)\s*(?:seconde|sec|s)/);
        var duration = durationMatch ? parseInt(durationMatch[1]) * 1000 : 5000;
        
        return { module: 'camera', command: 'rotate360', params: { duration: duration, axis: 'y' } };
      }
      
      // Zoom
      if (text.match(/zoom/)) {
        var factor = 1.5;
        if (text.match(/avant|in|plus/)) factor = 0.7;
        if (text.match(/arrière|arri[eè]re|out|moins/)) factor = 1.3;
        
        return { module: 'camera', command: 'zoom', params: { factor: factor, duration: 500 } };
      }
      
      // Reset
      if (text.match(/(?:réinitialise|reinitialise|reset|origine|initial)/)) {
        return { module: 'camera', command: 'reset', params: {} };
      }
      
      // Orbite
      if (text.match(/orbit/)) {
        return { module: 'camera', command: 'orbitAround', params: { target: {x:0,y:0,z:0}, angle: 360, duration: 3000 } };
      }
      
      // Shake/Tremble
      if (text.match(/(?:tremble|shake|secoue)/)) {
        return { module: 'camera', command: 'shake', params: { intensity: 0.5, duration: 500 } };
      }
      
      // Stop animation
      if (text.match(/(?:arrête|arrete|stop)/)) {
        return { module: 'camera', command: 'stopAnimation', params: {} };
      }
      
      // Position
      if (text.match(/(?:position|où|ou)/)) {
        return { module: 'camera', command: 'getPosition', params: {} };
      }
      
      // Vue (axes)
      var axisMatch = text.match(/vue\s+([-]?[xyz])/);
      if (axisMatch) {
        return { module: 'axisWidget', command: 'rotateCameraTo', params: { axis: axisMatch[1], duration: 800 } };
      }
      
      return null;
    },
    
    /**
     * Liste tous les modules enregistrés
     */
    listModules: function() {
      return Object.keys(modules).map(name => ({
        name: name,
        commandCount: modules[name].commandCount,
        errorCount: modules[name].errorCount,
        registeredAt: modules[name].registeredAt,
        commands: modules[name].interface.listCommands()
      }));
    },
    
    /**
     * Liste toutes les commandes disponibles pour un module
     * @param {string} moduleName - Nom du module (optionnel)
     */
    listCommands: function(moduleName) {
      if (moduleName) {
        if (!modules[moduleName]) {
          return { error: `Module "${moduleName}" non trouvé` };
        }
        return {
          module: moduleName,
          commands: modules[moduleName].interface.listCommands()
        };
      }
      
      // Liste toutes les commandes de tous les modules
      var allCommands = {};
      Object.keys(modules).forEach(name => {
        allCommands[name] = modules[name].interface.listCommands();
      });
      return allCommands;
    },
    
    /**
     * Récupère l'historique des commandes
     * @param {number} limit - Nombre maximum de commandes à retourner
     */
    getHistory: function(limit) {
      limit = limit || 20;
      return commandHistory.slice(-limit);
    },
    
    /**
     * Ajoute une entrée à l'historique
     * @private
     */
    addToHistory: function(entry) {
      commandHistory.push(entry);
      
      // Limite la taille de l'historique
      if (commandHistory.length > maxHistorySize) {
        commandHistory.shift();
      }
    },
    
    /**
     * Efface l'historique
     */
    clearHistory: function() {
      commandHistory = [];
      console.log('[KibaliAI] Historique effacé');
    },
    
    /**
     * Récupère les statistiques globales
     */
    getStats: function() {
      var totalCommands = 0;
      var totalErrors = 0;
      
      Object.keys(modules).forEach(name => {
        totalCommands += modules[name].commandCount;
        totalErrors += modules[name].errorCount;
      });
      
      return {
        modulesCount: Object.keys(modules).length,
        totalCommands: totalCommands,
        totalErrors: totalErrors,
        successRate: totalCommands > 0 ? ((totalCommands - totalErrors) / totalCommands * 100).toFixed(2) + '%' : 'N/A',
        historySize: commandHistory.length
      };
    },
    
    /**
     * Mode d'aide - affiche comment utiliser le système
     */
    help: function() {
      console.log(`
╔════════════════════════════════════════════════════════════════╗
║                    KibaliAI v${this.version}                         ║
║            Système de contrôle par IA pour Kibalone Studio     ║
╚════════════════════════════════════════════════════════════════╝

UTILISATION:

1. Commandes en langage naturel:
   KibaliAI.executeNatural("cache le widget")
   KibaliAI.executeNatural("déplace le widget en haut à droite")
   KibaliAI.executeNatural("vue -z")
   KibaliAI.executeNatural("redimensionne le widget à 150")

2. Commandes directes:
   KibaliAI.execute('axisWidget', 'hide', {})
   KibaliAI.execute('axisWidget', 'setPosition', { corner: 'top-right' })

3. Informations:
   KibaliAI.listModules()       - Liste tous les modules
   KibaliAI.listCommands()      - Liste toutes les commandes
   KibaliAI.getHistory()        - Historique des commandes
   KibaliAI.getStats()          - Statistiques d'utilisation
   KibaliAI.help()              - Affiche cette aide

EXEMPLES DE COMMANDES:
- "cache le widget"
- "affiche les axes"
- "déplace le widget en bas à droite"
- "oriente la caméra vers l'axe z"
- "vue -y"
- "redimensionne le widget à 200"
- "opacité du widget 0.5"
- "réinitialise la caméra"
- "status du widget"

      `);
    }
  };
})();

// Exposition globale
window.KibaliAI = KibaliAI;

// Message de bienvenue
console.log(`
%c╔════════════════════════════════════════════════════════════════╗
║                 🤖 KibaliAI Initialisé v${KibaliAI.version}              ║
║     Tapez KibaliAI.help() pour voir les commandes disponibles ║
╚════════════════════════════════════════════════════════════════╝`,
'color: #00ff00; font-weight: bold;'
);
