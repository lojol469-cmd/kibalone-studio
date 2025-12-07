AxisWidget = function (sourceCamera) {
  this.sourceCamera = sourceCamera;
  this.camera = new THREE.OrthographicCamera(-30,30,30,-30,1,1000);
  this.camera.up = this.sourceCamera.up;

  this.container = document.createElement('div');
  document.body.appendChild(this.container);
  this.container.id = "axes";
  this.styleContainer();
  this.visible = true;

  this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  this.renderer.setClearAlpha(0);
  this.renderer.setSize(100,100);
  this.container.appendChild(this.renderer.domElement);
  this.scene = new THREE.Scene();

  this.cameraLight = new THREE.PointLight(0xffffff, 1);
  this.scene.add(this.cameraLight);
  this.scene.add(new THREE.AmbientLight(0xffffff, 0.1));

  this.size = 26;
  var cubeGeo = new THREE.BoxGeometry(this.size, this.size, this.size);
  var cubeMat = new THREE.MeshPhongMaterial({color: 0xbbbbbb, shininess: 10});
  var cubeMesh = new THREE.Mesh(cubeGeo, cubeMat);
  this.scene.add(cubeMesh);

  var _this = this;
  var fontLoader = new THREE.FontLoader();
  fontLoader.load('./js/helvetiker_regular.typeface.json', function (font) {
    var params = {
      font: font,
      size: 7,
      height: 1
    };
    var dist = _this.size/2 + 1;
    var geos = [
      new THREE.TextGeometry("x", params),
      new THREE.TextGeometry("-x", params),
      new THREE.TextGeometry("y", params),
      new THREE.TextGeometry("-y", params),
      new THREE.TextGeometry("z", params),
      new THREE.TextGeometry("-z", params),
    ];
    geos[0].rotateX(Math.PI/2);
    geos[0].rotateZ(Math.PI/2);
    geos[0].translate(-dist,-2,-2);
    geos[1].rotateX(Math.PI/2);
    geos[1].rotateZ(Math.PI/2);
    geos[1].translate(dist,-4,-2);
    geos[2].rotateX(Math.PI/2);
    geos[2].translate(-2,-dist,-2);
    geos[3].rotateX(Math.PI/2);
    geos[3].rotateZ(Math.PI);
    geos[3].translate(4,dist,-2);
    geos[4].translate(-2,-2,dist);
    geos[5].rotateY(Math.PI);
    geos[5].translate(4,-2,-dist);
    mats = [
      new THREE.MeshPhongMaterial({color: 0xff3333, shininess: 0}),
      new THREE.MeshPhongMaterial({color: 0x337733, shininess: 0}),
      new THREE.MeshPhongMaterial({color: 0x3333ff, shininess: 0})
    ];
    meshes = [
      new THREE.Mesh(geos[0],mats[0]),
      new THREE.Mesh(geos[1],mats[0]),
      new THREE.Mesh(geos[2],mats[1]),
      new THREE.Mesh(geos[3],mats[1]),
      new THREE.Mesh(geos[4],mats[2]),
      new THREE.Mesh(geos[5],mats[2])
    ];
    _this.axisMeshes = meshes; // Stockage pour manipulation par l'IA
    for (var i=0; i<meshes.length; i++) {
      _this.scene.add(meshes[i]);
    }
  });

  this.origin = new THREE.Vector3(0,0,0);
  
  // AI Control Interface - Permet à l'IA de manipuler le widget via chat
  this.initAIControl();
}

AxisWidget.prototype.initAIControl = function() {
  var _this = this;
  this.aiControl = {
    // Commandes disponibles pour l'IA
    commands: {
      'hide': () => _this.hide(),
      'show': () => _this.show(),
      'toggle': () => _this.toggleVisibility(),
      'setPosition': (params) => _this.setPosition(params.x, params.y, params.corner),
      'setSize': (params) => _this.setSize(params.size),
      'setAxisColor': (params) => _this.setAxisColor(params.axis, params.color),
      'rotateCameraTo': (params) => _this.rotateCameraTo(params.axis, params.duration),
      'setOpacity': (params) => _this.setOpacity(params.opacity),
      'resetCamera': () => _this.resetCamera(),
      'getStatus': () => _this.getStatus()
    },
    
    // Exécute une commande
    execute: function(commandName, params) {
      try {
        if (!this.commands[commandName]) {
          throw new Error(`Commande inconnue: ${commandName}`);
        }
        var result = this.commands[commandName](params);
        console.log(`[AxisWidget AI] Commande "${commandName}" exécutée avec succès`);
        return { success: true, result: result, command: commandName };
      } catch (error) {
        console.error(`[AxisWidget AI] Erreur lors de l'exécution de "${commandName}":`, error);
        return { success: false, error: error.message, command: commandName };
      }
    },
    
    // Liste toutes les commandes disponibles
    listCommands: function() {
      return Object.keys(this.commands).map(cmd => ({
        name: cmd,
        description: _this.getCommandDescription(cmd)
      }));
    }
  };
  
  // Enregistrement global pour accès depuis le chat
  if (typeof KibaliAI !== 'undefined') {
    KibaliAI.registerModule('axisWidget', this.aiControl);
    console.log('[AxisWidget] Enregistré dans KibaliAI');
  } else {
    console.warn('[AxisWidget] KibaliAI non disponible, enregistrement différé');
    // Enregistrement différé si KibaliAI se charge après
    var _this = this;
    setTimeout(function() {
      if (typeof KibaliAI !== 'undefined') {
        KibaliAI.registerModule('axisWidget', _this.aiControl);
        console.log('[AxisWidget] Enregistré dans KibaliAI (différé)');
      }
    }, 100);
  }
}

AxisWidget.prototype.getCommandDescription = function(cmd) {
  var descriptions = {
    'hide': 'Cache le widget des axes',
    'show': 'Affiche le widget des axes',
    'toggle': 'Bascule la visibilité du widget',
    'setPosition': 'Positionne le widget (params: x, y, corner: "top-left"|"top-right"|"bottom-left"|"bottom-right")',
    'setSize': 'Redimensionne le widget (params: size en pixels)',
    'setAxisColor': 'Change la couleur d\'un axe (params: axis: "x"|"y"|"z", color: hex)',
    'rotateCameraTo': 'Oriente la caméra vers un axe (params: axis: "x"|"-x"|"y"|"-y"|"z"|"-z", duration: ms)',
    'setOpacity': 'Définit l\'opacité du widget (params: opacity: 0-1)',
    'resetCamera': 'Réinitialise la position de la caméra',
    'getStatus': 'Retourne l\'état actuel du widget'
  };
  return descriptions[cmd] || 'Aucune description disponible';
}

AxisWidget.prototype.hide = function() {
  this.visible = false;
  if (this.scene) this.scene.visible = false;
  this.container.style.display = 'none';
}

AxisWidget.prototype.show = function() {
  this.visible = true;
  if (this.scene) this.scene.visible = true;
  this.container.style.display = 'block';
}

AxisWidget.prototype.toggleVisibility = function() {
  this.visible = !this.visible;
  if (this.scene) this.scene.visible = this.visible;
  this.container.style.display = this.visible ? 'block' : 'none';
}

AxisWidget.prototype.update = function() {
  var camPos = new THREE.Vector3();
  this.sourceCamera.getWorldDirection(camPos);
  var up = this.camera.up.clone();
  // reflect camera position along camera up axis
  camPos.sub(up.multiplyScalar(2 * camPos.dot(up)));
  this.camera.position.copy(camPos);
  this.camera.position.setLength(this.size*1.5);
  this.camera.lookAt(this.origin);
  this.cameraLight.position.copy(camPos).multiplyScalar(this.size*1.2);
  this.renderer.render(this.scene, this.camera);
}

AxisWidget.prototype.setPosition = function(x, y, corner) {
  if (corner) {
    // Positionnement par coin
    this.container.style.top = "auto";
    this.container.style.bottom = "auto";
    this.container.style.left = "auto";
    this.container.style.right = "auto";
    
    switch(corner) {
      case "top-left":
        this.container.style.top = (y || 15) + "px";
        this.container.style.left = (x || 15) + "px";
        break;
      case "top-right":
        this.container.style.top = (y || 15) + "px";
        this.container.style.right = (x || 15) + "px";
        break;
      case "bottom-left":
        this.container.style.bottom = (y || 15) + "px";
        this.container.style.left = (x || 15) + "px";
        break;
      case "bottom-right":
        this.container.style.bottom = (y || 15) + "px";
        this.container.style.right = (x || 15) + "px";
        break;
    }
  } else {
    // Positionnement absolu
    this.container.style.left = (x || 15) + "px";
    this.container.style.bottom = (y || 15) + "px";
  }
}

AxisWidget.prototype.setSize = function(size) {
  if (size < 50 || size > 500) {
    console.warn('[AxisWidget] Taille invalide (50-500px autorisés)');
    return;
  }
  this.container.style.width = size + "px";
  this.container.style.height = size + "px";
  this.renderer.setSize(size, size);
}

AxisWidget.prototype.setAxisColor = function(axis, color) {
  // Cette fonction nécessite de stocker les meshes des axes
  if (!this.axisMeshes) {
    console.warn('[AxisWidget] Les meshes des axes ne sont pas encore chargés');
    return;
  }
  var axisIndex = {
    'x': [0, 1],
    'y': [2, 3],
    'z': [4, 5]
  };
  if (axisIndex[axis]) {
    var indices = axisIndex[axis];
    indices.forEach(i => {
      if (this.axisMeshes[i]) {
        this.axisMeshes[i].material.color.setHex(color);
      }
    });
  }
}

AxisWidget.prototype.setOpacity = function(opacity) {
  if (opacity < 0 || opacity > 1) {
    console.warn('[AxisWidget] Opacité invalide (0-1 autorisé)');
    return;
  }
  this.container.style.opacity = opacity;
}

AxisWidget.prototype.rotateCameraTo = function(axis, duration) {
  if (!this.sourceCamera) return;
  
  duration = duration || 1000; // 1 seconde par défaut
  
  var targetPosition = new THREE.Vector3();
  var distance = this.sourceCamera.position.length();
  
  switch(axis) {
    case 'x': targetPosition.set(distance, 0, 0); break;
    case '-x': targetPosition.set(-distance, 0, 0); break;
    case 'y': targetPosition.set(0, distance, 0); break;
    case '-y': targetPosition.set(0, -distance, 0); break;
    case 'z': targetPosition.set(0, 0, distance); break;
    case '-z': targetPosition.set(0, 0, -distance); break;
    default:
      console.warn('[AxisWidget] Axe invalide:', axis);
      return;
  }
  
  // Animation de la caméra (si GSAP est disponible)
  if (window.GSAP || window.gsap) {
    var gsap = window.GSAP || window.gsap;
    gsap.to(this.sourceCamera.position, {
      x: targetPosition.x,
      y: targetPosition.y,
      z: targetPosition.z,
      duration: duration / 1000,
      ease: "power2.inOut"
    });
  } else {
    // Fallback sans animation
    this.sourceCamera.position.copy(targetPosition);
  }
  
  this.sourceCamera.lookAt(0, 0, 0);
}

AxisWidget.prototype.resetCamera = function() {
  if (!this.sourceCamera) return;
  this.sourceCamera.position.set(50, 50, 50);
  this.sourceCamera.lookAt(0, 0, 0);
}

AxisWidget.prototype.getStatus = function() {
  return {
    visible: this.visible,
    size: this.size,
    position: {
      left: this.container.style.left,
      bottom: this.container.style.bottom,
      top: this.container.style.top,
      right: this.container.style.right
    },
    opacity: this.container.style.opacity || 1,
    cameraPosition: this.sourceCamera ? {
      x: this.sourceCamera.position.x,
      y: this.sourceCamera.position.y,
      z: this.sourceCamera.position.z
    } : null
  };
}

AxisWidget.prototype.styleContainer = function() {
  this.container.style.width = "100px";
  this.container.style.height = "100px";
  this.container.style.position = "absolute";
  this.container.style.bottom = "15px";
  this.container.style.left = "15px";
  this.container.style.backgroundColor = "transparent";
  this.container.style.pointerEvents = "none";
}
