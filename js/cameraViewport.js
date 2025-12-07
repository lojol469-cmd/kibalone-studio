/**
 * CameraViewport - Mini fenêtre affichant la vue caméra (comme Blender)
 * Permet de visualiser ce que voit la caméra en temps réel
 */

CameraViewport = function(mainCamera, scene) {
  this.mainCamera = mainCamera;
  this.scene = scene;
  this.visible = true;
  
  // Créer le container
  this.container = document.createElement('div');
  document.body.appendChild(this.container);
  this.container.id = 'camera-viewport';
  this.styleContainer();
  
  // Créer le renderer dédié
  this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  this.renderer.setSize(320, 180); // 16:9 ratio
  this.renderer.setClearColor(0x1a1a2e);
  this.container.appendChild(this.renderer.domElement);
  
  // Créer une caméra qui clone la position de la caméra principale
  this.viewCamera = this.mainCamera.clone();
  
  // Ajouter un titre
  this.title = document.createElement('div');
  this.title.style.position = 'absolute';
  this.title.style.top = '5px';
  this.title.style.left = '5px';
  this.title.style.color = '#00d4ff';
  this.title.style.fontSize = '11px';
  this.title.style.fontWeight = 'bold';
  this.title.style.textShadow = '0 0 5px rgba(0,212,255,0.5)';
  this.title.style.pointerEvents = 'none';
  this.title.innerHTML = '📹 CAMERA VIEW';
  this.container.appendChild(this.title);
  
  // Ajouter les infos
  this.info = document.createElement('div');
  this.info.style.position = 'absolute';
  this.info.style.bottom = '5px';
  this.info.style.left = '5px';
  this.info.style.color = '#fff';
  this.info.style.fontSize = '9px';
  this.info.style.fontFamily = 'monospace';
  this.info.style.textShadow = '0 0 3px rgba(0,0,0,0.8)';
  this.info.style.pointerEvents = 'none';
  this.container.appendChild(this.info);
  
  // Boutons de contrôle
  this.createControls();
  
  // Initialiser l'API AI
  this.initAIControl();
  
  console.log('📹 CameraViewport initialisé');
}

CameraViewport.prototype.initAIControl = function() {
  var _this = this;
  this.aiControl = {
    commands: {
      'hide': () => { _this.visible = false; _this.container.style.display = 'none'; return { status: 'Viewport caché' }; },
      'show': () => { _this.visible = true; _this.container.style.display = 'block'; return { status: 'Viewport affiché' }; },
      'toggle': () => { _this.toggleVisibility(); return { status: 'Visibilité basculée' }; },
      'setPosition': (params) => { _this.setPosition(params.position); return { status: 'Position changée', position: params.position }; },
      'resize': (params) => { 
        var size = params.large ? { w: 640, h: 360 } : { w: 320, h: 180 };
        _this.container.style.width = size.w + 'px';
        _this.container.style.height = size.h + 'px';
        _this.renderer.setSize(size.w, size.h);
        return { status: 'Taille changée', size: size };
      },
      'setBorderColor': (params) => { _this.setBorderColor(params.color); return { status: 'Couleur changée' }; }
    },
    
    execute: function(commandName, params) {
      try {
        if (!this.commands[commandName]) {
          throw new Error(`Commande inconnue: ${commandName}`);
        }
        var result = this.commands[commandName](params);
        console.log(`[CameraViewport AI] Commande "${commandName}" exécutée`);
        return { success: true, result: result, command: commandName };
      } catch (error) {
        console.error(`[CameraViewport AI] Erreur "${commandName}":`, error);
        return { success: false, error: error.message, command: commandName };
      }
    },
    
    listCommands: function() {
      return Object.keys(this.commands).map(cmd => ({
        name: cmd,
        description: _this.getCommandDescription(cmd)
      }));
    }
  };
  
  // Enregistrement dans KibaliAI
  if (typeof KibaliAI !== 'undefined') {
    KibaliAI.registerModule('viewport', this.aiControl);
    console.log('[CameraViewport] Enregistré dans KibaliAI');
  } else {
    setTimeout(function() {
      if (typeof KibaliAI !== 'undefined') {
        KibaliAI.registerModule('viewport', _this.aiControl);
        console.log('[CameraViewport] Enregistré dans KibaliAI (différé)');
      }
    }, 100);
  }
}

CameraViewport.prototype.getCommandDescription = function(cmd) {
  var descriptions = {
    'hide': 'Cache le viewport caméra',
    'show': 'Affiche le viewport caméra',
    'toggle': 'Bascule la visibilité du viewport',
    'setPosition': 'Change la position du viewport (params: position: "top-left"|"top-right"|"bottom-left"|"bottom-right")',
    'resize': 'Redimensionne le viewport (params: large: true|false)',
    'setBorderColor': 'Change la couleur de bordure (params: color: "#rrggbb")'
  };
  return descriptions[cmd] || 'Aucune description';
}

CameraViewport.prototype.styleContainer = function() {
  this.container.style.position = 'absolute';
  this.container.style.bottom = '200px';
  this.container.style.left = '15px';
  this.container.style.width = '320px';
  this.container.style.height = '180px';
  this.container.style.border = '2px solid #00d4ff';
  this.container.style.borderRadius = '8px';
  this.container.style.overflow = 'hidden';
  this.container.style.boxShadow = '0 4px 20px rgba(0, 212, 255, 0.4)';
  this.container.style.zIndex = '1000';
  this.container.style.backgroundColor = '#1a1a2e';
  this.container.style.transition = 'all 0.3s ease';
}

CameraViewport.prototype.createControls = function() {
  var controls = document.createElement('div');
  controls.style.position = 'absolute';
  controls.style.top = '5px';
  controls.style.right = '5px';
  controls.style.display = 'flex';
  controls.style.gap = '5px';
  
  // Bouton toggle
  var toggleBtn = document.createElement('button');
  toggleBtn.innerHTML = '👁️';
  toggleBtn.title = 'Masquer/Afficher';
  toggleBtn.style.cssText = `
    background: rgba(0,212,255,0.2);
    border: 1px solid #00d4ff;
    color: #00d4ff;
    padding: 3px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.2s;
  `;
  toggleBtn.onmouseover = function() {
    this.style.background = 'rgba(0,212,255,0.4)';
  };
  toggleBtn.onmouseout = function() {
    this.style.background = 'rgba(0,212,255,0.2)';
  };
  
  var _this = this;
  toggleBtn.onclick = function() {
    _this.toggleVisibility();
  };
  
  // Bouton resize
  var resizeBtn = document.createElement('button');
  resizeBtn.innerHTML = '⛶';
  resizeBtn.title = 'Agrandir/Réduire';
  resizeBtn.style.cssText = toggleBtn.style.cssText;
  resizeBtn.onmouseover = toggleBtn.onmouseover;
  resizeBtn.onmouseout = toggleBtn.onmouseout;
  
  var isLarge = false;
  resizeBtn.onclick = function() {
    isLarge = !isLarge;
    if (isLarge) {
      _this.container.style.width = '640px';
      _this.container.style.height = '360px';
      _this.renderer.setSize(640, 360);
    } else {
      _this.container.style.width = '320px';
      _this.container.style.height = '180px';
      _this.renderer.setSize(320, 180);
    }
  };
  
  controls.appendChild(toggleBtn);
  controls.appendChild(resizeBtn);
  this.container.appendChild(controls);
}

CameraViewport.prototype.update = function() {
  if (!this.visible) return;
  
  // Synchroniser avec la caméra principale
  this.viewCamera.position.copy(this.mainCamera.position);
  this.viewCamera.rotation.copy(this.mainCamera.rotation);
  this.viewCamera.fov = this.mainCamera.fov;
  this.viewCamera.updateProjectionMatrix();
  
  // Mettre à jour les infos
  this.updateInfo();
  
  // Render la scène
  this.renderer.render(this.scene, this.viewCamera);
}

CameraViewport.prototype.updateInfo = function() {
  var pos = this.mainCamera.position;
  var rot = this.mainCamera.rotation;
  
  this.info.innerHTML = `
    X:${pos.x.toFixed(1)} Y:${pos.y.toFixed(1)} Z:${pos.z.toFixed(1)}<br>
    FOV:${this.mainCamera.fov.toFixed(0)}°
  `;
}

CameraViewport.prototype.toggleVisibility = function() {
  this.visible = !this.visible;
  this.container.style.display = this.visible ? 'block' : 'none';
}

CameraViewport.prototype.setPosition = function(position) {
  var positions = {
    'bottom-left': { bottom: '200px', left: '15px', top: 'auto', right: 'auto' },
    'bottom-right': { bottom: '200px', right: '15px', top: 'auto', left: 'auto' },
    'top-left': { top: '80px', left: '15px', bottom: 'auto', right: 'auto' },
    'top-right': { top: '80px', right: '370px', bottom: 'auto', left: 'auto' }
  };
  
  if (positions[position]) {
    Object.assign(this.container.style, positions[position]);
  }
}

CameraViewport.prototype.setBorderColor = function(color) {
  this.container.style.borderColor = color;
  this.container.style.boxShadow = `0 4px 20px ${color}80`;
  this.title.style.color = color;
}
