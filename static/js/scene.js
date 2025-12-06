// Three.js Scene Management
let scene, camera, renderer, controls;
let sceneObjects = [];
let selectedObject = null;
let grid, axesHelper;

function initScene() {
    const canvas = document.getElementById('scene3d');
    
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    
    // Camera
    camera = new THREE.PerspectiveCamera(
        50,
        canvas.clientWidth / canvas.clientHeight,
        0.1,
        1000
    );
    camera.position.set(5, 5, 5);
    camera.lookAt(0, 0, 0);
    
    // Renderer
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    
    // Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxDistance = 100;
    controls.minDistance = 1;
    
    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 7.5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);
    
    const pointLight = new THREE.PointLight(0xffffff, 0.3);
    pointLight.position.set(-5, 5, -5);
    scene.add(pointLight);
    
    // Grid
    grid = new THREE.GridHelper(100, 100, 0x6e6e6e, 0x6e6e6e);
    scene.add(grid);
    
    // Axes
    axesHelper = new THREE.AxesHelper(5);
    scene.add(axesHelper);
    
    // Origin marker
    const originGeometry = new THREE.SphereGeometry(0.1, 16, 16);
    const originMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
    const originMarker = new THREE.Mesh(originGeometry, originMaterial);
    scene.add(originMarker);
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    // Start animation loop
    animate();
    
    console.log('✅ Scene initialized');
}

function onWindowResize() {
    const canvas = document.getElementById('scene3d');
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
    updateSceneInfo();
}

function updateSceneInfo() {
    document.getElementById('objectCount').textContent = `Objets: ${sceneObjects.length}`;
}

function addObject(type, position = [0, 1, 0]) {
    let geometry;
    
    switch(type) {
        case 'cube':
            geometry = new THREE.BoxGeometry(1, 1, 1);
            break;
        case 'sphere':
            geometry = new THREE.SphereGeometry(0.5, 32, 32);
            break;
        case 'cylinder':
            geometry = new THREE.CylinderGeometry(0.5, 0.5, 1, 32);
            break;
        default:
            geometry = new THREE.BoxGeometry(1, 1, 1);
    }
    
    const material = new THREE.MeshStandardMaterial({ 
        color: 0x888888,
        roughness: 0.7,
        metalness: 0.3
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(...position);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    
    mesh.userData = {
        id: `obj_${Date.now()}`,
        type: type
    };
    
    scene.add(mesh);
    sceneObjects.push(mesh);
    
    console.log(`➕ ${type} added to scene`);
    return mesh;
}

function clearScene() {
    sceneObjects.forEach(obj => {
        scene.remove(obj);
        obj.geometry.dispose();
        obj.material.dispose();
    });
    sceneObjects = [];
    selectedObject = null;
    console.log('🗑️ Scene cleared');
}

function selectObject(obj) {
    if (selectedObject) {
        selectedObject.material.emissive.setHex(0x000000);
    }
    selectedObject = obj;
    if (selectedObject) {
        selectedObject.material.emissive.setHex(0xffff00);
    }
}
