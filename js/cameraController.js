/**
 * CameraController - Contrôle avancé de la caméra via KibaliAI
 * Permet de manipuler la caméra avec des commandes naturelles
 */

CameraController = function(camera, scene) {
  this.camera = camera;
  this.scene = scene;
  this.isAnimating = false;
  this.animationId = null;
  this.originalPosition = { x: camera.position.x, y: camera.position.y, z: camera.position.z };
  this.target = { x: 0, y: 0, z: 0 };
  
  // Historique des positions
  this.positionHistory = [];
  this.maxHistorySize = 10;
  
  this.initAIControl();
}

CameraController.prototype.initAIControl = function() {
  var _this = this;
  this.aiControl = {
    commands: {
      'rotate360': (params) => _this.rotate360(params.duration, params.axis),
      'orbitAround': (params) => _this.orbitAround(params.target, params.angle, params.duration),
      'moveTo': (params) => _this.moveTo(params.x, params.y, params.z, params.duration),
      'lookAt': (params) => _this.lookAt(params.x, params.y, params.z),
      'zoom': (params) => _this.zoom(params.factor, params.duration),
      'pan': (params) => _this.pan(params.x, params.y, params.duration),
      'shake': (params) => _this.shake(params.intensity, params.duration),
      'flyTo': (params) => _this.flyTo(params.target, params.duration),
      'reset': () => _this.reset(),
      'savePosition': (params) => _this.savePosition(params.name),
      'loadPosition': (params) => _this.loadPosition(params.name),
      'stopAnimation': () => _this.stopAnimation(),
      'getPosition': () => _this.getPosition(),
      'setFOV': (params) => _this.setFOV(params.fov, params.duration),
      'dollyZoom': (params) => _this.dollyZoom(params.duration)
    },
    
    execute: function(commandName, params) {
      try {
        if (!this.commands[commandName]) {
          throw new Error(`Commande inconnue: ${commandName}`);
        }
        var result = this.commands[commandName](params);
        console.log(`[CameraController AI] Commande "${commandName}" exécutée`);
        return { success: true, result: result, command: commandName };
      } catch (error) {
        console.error(`[CameraController AI] Erreur "${commandName}":`, error);
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
    KibaliAI.registerModule('camera', this.aiControl);
    console.log('[CameraController] Enregistré dans KibaliAI');
  } else {
    var _this = this;
    setTimeout(function() {
      if (typeof KibaliAI !== 'undefined') {
        KibaliAI.registerModule('camera', _this.aiControl);
        console.log('[CameraController] Enregistré dans KibaliAI (différé)');
      }
    }, 100);
  }
}

CameraController.prototype.getCommandDescription = function(cmd) {
  var descriptions = {
    'rotate360': 'Rotation 360° autour d\'un axe (params: duration ms, axis: "x"|"y"|"z")',
    'orbitAround': 'Orbite autour d\'un point (params: target {x,y,z}, angle, duration)',
    'moveTo': 'Déplace la caméra vers une position (params: x, y, z, duration)',
    'lookAt': 'Oriente la caméra vers un point (params: x, y, z)',
    'zoom': 'Zoom avant/arrière (params: factor: 0.5-2.0, duration)',
    'pan': 'Déplacement latéral (params: x, y, duration)',
    'shake': 'Effet de tremblement (params: intensity: 0-1, duration)',
    'flyTo': 'Vol cinématique vers une cible (params: target {x,y,z}, duration)',
    'reset': 'Réinitialise la position initiale',
    'savePosition': 'Sauvegarde position actuelle (params: name)',
    'loadPosition': 'Charge une position sauvegardée (params: name)',
    'stopAnimation': 'Arrête toute animation en cours',
    'getPosition': 'Retourne la position actuelle',
    'setFOV': 'Change le champ de vision (params: fov: 30-120, duration)',
    'dollyZoom': 'Effet Vertigo/Dolly Zoom (params: duration)'
  };
  return descriptions[cmd] || 'Aucune description';
}

// Rotation 360 degrés
CameraController.prototype.rotate360 = function(duration, axis) {
  duration = duration || 5000;
  axis = axis || 'y';
  
  this.stopAnimation();
  this.isAnimating = true;
  
  var startTime = Date.now();
  var initialPos = {
    x: this.camera.position.x,
    y: this.camera.position.y,
    z: this.camera.position.z
  };
  var radius = Math.sqrt(initialPos.x * initialPos.x + initialPos.z * initialPos.z);
  
  var _this = this;
  
  function animate() {
    if (!_this.isAnimating) return;
    
    var elapsed = Date.now() - startTime;
    var progress = Math.min(elapsed / duration, 1);
    var angle = progress * Math.PI * 2;
    
    if (axis === 'y') {
      _this.camera.position.x = Math.cos(angle) * radius;
      _this.camera.position.z = Math.sin(angle) * radius;
    } else if (axis === 'x') {
      _this.camera.position.y = Math.cos(angle) * radius;
      _this.camera.position.z = Math.sin(angle) * radius;
    } else if (axis === 'z') {
      _this.camera.position.x = Math.cos(angle) * radius;
      _this.camera.position.y = Math.sin(angle) * radius;
    }
    
    _this.camera.lookAt(_this.target.x, _this.target.y, _this.target.z);
    
    if (progress < 1) {
      _this.animationId = requestAnimationFrame(animate);
    } else {
      _this.isAnimating = false;
    }
  }
  
  animate();
  return { status: 'Animation démarrée', duration: duration, axis: axis };
}

// Orbite autour d'un point
CameraController.prototype.orbitAround = function(target, angle, duration) {
  target = target || { x: 0, y: 0, z: 0 };
  angle = angle || 360;
  duration = duration || 3000;
  
  this.stopAnimation();
  this.isAnimating = true;
  
  var startTime = Date.now();
  var startAngle = Math.atan2(
    this.camera.position.z - target.z,
    this.camera.position.x - target.x
  );
  var radius = Math.sqrt(
    Math.pow(this.camera.position.x - target.x, 2) +
    Math.pow(this.camera.position.z - target.z, 2)
  );
  
  var _this = this;
  
  function animate() {
    if (!_this.isAnimating) return;
    
    var elapsed = Date.now() - startTime;
    var progress = Math.min(elapsed / duration, 1);
    var currentAngle = startAngle + (angle * Math.PI / 180) * progress;
    
    _this.camera.position.x = target.x + Math.cos(currentAngle) * radius;
    _this.camera.position.z = target.z + Math.sin(currentAngle) * radius;
    _this.camera.lookAt(target.x, target.y, target.z);
    
    if (progress < 1) {
      _this.animationId = requestAnimationFrame(animate);
    } else {
      _this.isAnimating = false;
    }
  }
  
  animate();
  return { status: 'Orbite démarrée', angle: angle, duration: duration };
}

// Déplacement vers une position
CameraController.prototype.moveTo = function(x, y, z, duration) {
  duration = duration || 1000;
  
  this.stopAnimation();
  this.isAnimating = true;
  
  var startTime = Date.now();
  var startPos = {
    x: this.camera.position.x,
    y: this.camera.position.y,
    z: this.camera.position.z
  };
  
  var _this = this;
  
  function animate() {
    if (!_this.isAnimating) return;
    
    var elapsed = Date.now() - startTime;
    var progress = Math.min(elapsed / duration, 1);
    
    // Easing cubic
    var eased = progress < 0.5
      ? 4 * progress * progress * progress
      : 1 - Math.pow(-2 * progress + 2, 3) / 2;
    
    _this.camera.position.x = startPos.x + (x - startPos.x) * eased;
    _this.camera.position.y = startPos.y + (y - startPos.y) * eased;
    _this.camera.position.z = startPos.z + (z - startPos.z) * eased;
    
    if (progress < 1) {
      _this.animationId = requestAnimationFrame(animate);
    } else {
      _this.isAnimating = false;
    }
  }
  
  animate();
  return { status: 'Déplacement démarré', target: {x, y, z}, duration: duration };
}

// Orienter vers un point
CameraController.prototype.lookAt = function(x, y, z) {
  this.camera.lookAt(x, y, z);
  this.target = { x: x, y: y, z: z };
  return { target: {x, y, z} };
}

// Zoom
CameraController.prototype.zoom = function(factor, duration) {
  factor = factor || 1.5;
  duration = duration || 500;
  
  var direction = new THREE.Vector3();
  this.camera.getWorldDirection(direction);
  
  var distance = this.camera.position.length() * (1 - factor);
  var targetPos = {
    x: this.camera.position.x + direction.x * distance,
    y: this.camera.position.y + direction.y * distance,
    z: this.camera.position.z + direction.z * distance
  };
  
  return this.moveTo(targetPos.x, targetPos.y, targetPos.z, duration);
}

// Tremblement
CameraController.prototype.shake = function(intensity, duration) {
  intensity = intensity || 0.5;
  duration = duration || 500;
  
  this.stopAnimation();
  this.isAnimating = true;
  
  var startTime = Date.now();
  var originalPos = {
    x: this.camera.position.x,
    y: this.camera.position.y,
    z: this.camera.position.z
  };
  
  var _this = this;
  
  function animate() {
    if (!_this.isAnimating) return;
    
    var elapsed = Date.now() - startTime;
    var progress = Math.min(elapsed / duration, 1);
    
    if (progress < 1) {
      var shake = (1 - progress) * intensity;
      _this.camera.position.x = originalPos.x + (Math.random() - 0.5) * shake;
      _this.camera.position.y = originalPos.y + (Math.random() - 0.5) * shake;
      _this.camera.position.z = originalPos.z + (Math.random() - 0.5) * shake;
      
      _this.animationId = requestAnimationFrame(animate);
    } else {
      _this.camera.position.set(originalPos.x, originalPos.y, originalPos.z);
      _this.isAnimating = false;
    }
  }
  
  animate();
  return { status: 'Shake démarré', intensity: intensity, duration: duration };
}

// Réinitialisation
CameraController.prototype.reset = function() {
  this.stopAnimation();
  return this.moveTo(this.originalPosition.x, this.originalPosition.y, this.originalPosition.z, 1000);
}

// Arrêter animation
CameraController.prototype.stopAnimation = function() {
  this.isAnimating = false;
  if (this.animationId) {
    cancelAnimationFrame(this.animationId);
    this.animationId = null;
  }
  return { status: 'Animation arrêtée' };
}

// Obtenir position
CameraController.prototype.getPosition = function() {
  return {
    position: {
      x: this.camera.position.x,
      y: this.camera.position.y,
      z: this.camera.position.z
    },
    rotation: {
      x: this.camera.rotation.x,
      y: this.camera.rotation.y,
      z: this.camera.rotation.z
    },
    fov: this.camera.fov
  };
}

// Sauvegarder position
CameraController.prototype.savePosition = function(name) {
  name = name || 'default';
  if (!this.savedPositions) this.savedPositions = {};
  
  this.savedPositions[name] = {
    position: { ...this.camera.position },
    rotation: { ...this.camera.rotation },
    fov: this.camera.fov
  };
  
  return { status: 'Position sauvegardée', name: name };
}

// Charger position
CameraController.prototype.loadPosition = function(name) {
  name = name || 'default';
  if (!this.savedPositions || !this.savedPositions[name]) {
    throw new Error(`Position "${name}" non trouvée`);
  }
  
  var saved = this.savedPositions[name];
  return this.moveTo(saved.position.x, saved.position.y, saved.position.z, 1000);
}

// Changer FOV
CameraController.prototype.setFOV = function(fov, duration) {
  fov = Math.max(30, Math.min(120, fov));
  duration = duration || 500;
  
  var startFOV = this.camera.fov;
  var startTime = Date.now();
  var _this = this;
  
  this.stopAnimation();
  this.isAnimating = true;
  
  function animate() {
    if (!_this.isAnimating) return;
    
    var elapsed = Date.now() - startTime;
    var progress = Math.min(elapsed / duration, 1);
    
    _this.camera.fov = startFOV + (fov - startFOV) * progress;
    _this.camera.updateProjectionMatrix();
    
    if (progress < 1) {
      _this.animationId = requestAnimationFrame(animate);
    } else {
      _this.isAnimating = false;
    }
  }
  
  animate();
  return { status: 'FOV changé', fov: fov };
}

// Effet Dolly Zoom (Vertigo)
CameraController.prototype.dollyZoom = function(duration) {
  duration = duration || 2000;
  
  // Implémentation simplifiée
  var startFOV = this.camera.fov;
  var targetFOV = startFOV * 1.5;
  
  this.setFOV(targetFOV, duration / 2);
  
  var _this = this;
  setTimeout(function() {
    _this.setFOV(startFOV, duration / 2);
  }, duration / 2);
  
  return { status: 'Dolly zoom démarré', duration: duration };
}

// Pan (déplacement latéral)
CameraController.prototype.pan = function(x, y, duration) {
  duration = duration || 500;
  
  var targetPos = {
    x: this.camera.position.x + x,
    y: this.camera.position.y + y,
    z: this.camera.position.z
  };
  
  return this.moveTo(targetPos.x, targetPos.y, targetPos.z, duration);
}

// Vol cinématique
CameraController.prototype.flyTo = function(target, duration) {
  // Combinaison de mouvement + changement de regard
  var _this = this;
  this.moveTo(target.x, target.y, target.z, duration);
  setTimeout(function() {
    _this.lookAt(0, 0, 0);
  }, duration / 2);
  
  return { status: 'Vol démarré', target: target, duration: duration };
}
