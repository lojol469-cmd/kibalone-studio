// Grease Pencil Drawing System
let drawingMode = 'none'; // 'draw', 'erase', 'none'
let isDrawing = false;
let brushSize = 5;
let brushColor = '#ffffff';
let currentStroke = [];
let strokes = [];
let drawingPlane;
let raycaster = new THREE.Raycaster();
let mouse = new THREE.Vector2();

function initGreasePencil() {
    // Create invisible drawing plane
    const planeGeometry = new THREE.PlaneGeometry(100, 100);
    const planeMaterial = new THREE.MeshBasicMaterial({ 
        visible: false,
        side: THREE.DoubleSide 
    });
    drawingPlane = new THREE.Mesh(planeGeometry, planeMaterial);
    drawingPlane.rotation.x = -Math.PI / 2;
    scene.add(drawingPlane);
    
    // Mouse events
    const canvas = renderer.domElement;
    canvas.addEventListener('mousedown', onDrawMouseDown);
    canvas.addEventListener('mousemove', onDrawMouseMove);
    canvas.addEventListener('mouseup', onDrawMouseUp);
    canvas.addEventListener('mouseleave', onDrawMouseUp);
    
    console.log('✅ Grease Pencil initialized');
}

function setDrawMode(mode) {
    drawingMode = mode;
    
    // Update UI
    document.getElementById('drawBtn').classList.remove('active');
    document.getElementById('eraseBtn').classList.remove('active');
    document.getElementById('selectBtn').classList.remove('active');
    
    if (mode === 'draw') {
        document.getElementById('drawBtn').classList.add('active');
        controls.enabled = false;
    } else if (mode === 'erase') {
        document.getElementById('eraseBtn').classList.add('active');
        controls.enabled = false;
    } else {
        document.getElementById('selectBtn').classList.add('active');
        controls.enabled = true;
    }
}

function updateBrushSize(value) {
    brushSize = parseInt(value);
    document.getElementById('brushSizeValue').textContent = brushSize;
}

function updateBrushColor(value) {
    brushColor = value;
}

function getIntersectionPoint(event) {
    const canvas = renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    
    raycaster.setFromCamera(mouse, camera);
    
    const intersects = raycaster.intersectObject(drawingPlane);
    if (intersects.length > 0) {
        return intersects[0].point;
    }
    return null;
}

function onDrawMouseDown(event) {
    if (drawingMode === 'draw') {
        isDrawing = true;
        const point = getIntersectionPoint(event);
        if (point) {
            currentStroke = [point.clone()];
        }
    }
}

function onDrawMouseMove(event) {
    if (isDrawing && drawingMode === 'draw') {
        const point = getIntersectionPoint(event);
        if (point && currentStroke.length > 0) {
            const lastPoint = currentStroke[currentStroke.length - 1];
            if (point.distanceTo(lastPoint) > 0.1) {
                currentStroke.push(point.clone());
                updateCurrentStrokeLine();
            }
        }
    }
}

function onDrawMouseUp() {
    if (isDrawing && currentStroke.length > 1) {
        // Save stroke
        const strokeData = {
            points: currentStroke,
            color: brushColor,
            size: brushSize
        };
        strokes.push(strokeData);
        createStrokeLine(strokeData);
        currentStroke = [];
        
        // Remove temp line
        const tempLine = scene.getObjectByName('currentStroke');
        if (tempLine) {
            scene.remove(tempLine);
        }
    }
    isDrawing = false;
}

function updateCurrentStrokeLine() {
    // Remove existing temp line
    const oldLine = scene.getObjectByName('currentStroke');
    if (oldLine) {
        scene.remove(oldLine);
        oldLine.geometry.dispose();
        oldLine.material.dispose();
    }
    
    if (currentStroke.length < 2) return;
    
    // Create new temp line
    const geometry = new THREE.BufferGeometry().setFromPoints(currentStroke);
    const material = new THREE.LineBasicMaterial({ 
        color: new THREE.Color(brushColor),
        linewidth: brushSize
    });
    
    const line = new THREE.Line(geometry, material);
    line.name = 'currentStroke';
    scene.add(line);
}

function createStrokeLine(strokeData) {
    const geometry = new THREE.BufferGeometry().setFromPoints(strokeData.points);
    const material = new THREE.LineBasicMaterial({ 
        color: new THREE.Color(strokeData.color),
        linewidth: strokeData.size
    });
    
    const line = new THREE.Line(geometry, material);
    line.userData.isStroke = true;
    scene.add(line);
}

function clearStrokes() {
    strokes = [];
    scene.children.forEach(child => {
        if (child.userData.isStroke || child.name === 'currentStroke') {
            scene.remove(child);
            child.geometry.dispose();
            child.material.dispose();
        }
    });
}
