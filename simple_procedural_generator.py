#!/usr/bin/env python3
"""
Générateur Procédural Simple et Fiable
Génère du code Three.js garanti sans erreur
"""

def generate_simple_code(prompt, scene_context=None):
    """Génère du code Three.js simple et fiable basé sur des templates"""
    
    prompt_lower = prompt.lower()
    
    # Détecte le type d'objet demandé
    if any(word in prompt_lower for word in ['maison', 'house', 'building', 'bâtiment']):
        return generate_house(scene_context)
    elif any(word in prompt_lower for word in ['bateau', 'boat', 'ship', 'navire']):
        return generate_boat(scene_context)
    elif any(word in prompt_lower for word in ['mer', 'sea', 'ocean', 'eau', 'water']):
        return generate_water(scene_context)
    elif any(word in prompt_lower for word in ['sol', 'ground', 'floor', 'terrain']):
        return generate_ground(scene_context)
    elif any(word in prompt_lower for word in ['personnage', 'character', 'human']):
        return generate_character(scene_context)
    elif any(word in prompt_lower for word in ['arbre', 'tree']):
        return generate_tree(scene_context)
    elif any(word in prompt_lower for word in ['voiture', 'car', 'vehicle']):
        return generate_car(scene_context)
    elif any(word in prompt_lower for word in ['ciel', 'sky']):
        return generate_sky(scene_context)
    elif any(word in prompt_lower for word in ['ventilation', 'aeration', 'vent', 'air']):
        return generate_ventilation(scene_context)
    else:
        return generate_generic_object(prompt, scene_context)

def get_position_y(scene_context):
    """Calcule la position Y selon le contexte"""
    if scene_context and scene_context.get('total_objects', 0) > 0:
        if scene_context.get('has_vehicle') or scene_context.get('has_building'):
            return -1  # Sous les objets
    return 0

def generate_house(scene_context=None):
    """Génère une maison simple"""
    return """
const houseGroup = new THREE.Group();
houseGroup.name = 'house';

// Murs
const wallsGeo = new THREE.BoxGeometry(4, 3, 4);
const wallsMat = new THREE.MeshStandardMaterial({ 
    color: 0xD2B48C, 
    roughness: 0.8 
});
const walls = new THREE.Mesh(wallsGeo, wallsMat);
walls.position.y = 1.5;
houseGroup.add(walls);

// Toit
const roofGeo = new THREE.ConeGeometry(3, 1.5, 4);
const roofMat = new THREE.MeshStandardMaterial({ 
    color: 0x8B4513, 
    roughness: 0.9 
});
const roof = new THREE.Mesh(roofGeo, roofMat);
roof.position.y = 3.75;
roof.rotation.y = Math.PI / 4;
houseGroup.add(roof);

// Porte
const doorGeo = new THREE.BoxGeometry(0.8, 1.5, 0.1);
const doorMat = new THREE.MeshStandardMaterial({ color: 0x654321 });
const door = new THREE.Mesh(doorGeo, doorMat);
door.position.set(0, 0.75, 2.05);
houseGroup.add(door);

// Fenêtres
const windowGeo = new THREE.BoxGeometry(0.6, 0.6, 0.1);
const windowMat = new THREE.MeshStandardMaterial({ 
    color: 0x87CEEB, 
    transparent: true, 
    opacity: 0.6 
});

const window1 = new THREE.Mesh(windowGeo, windowMat);
window1.position.set(-1, 2, 2.05);
houseGroup.add(window1);

const window2 = new THREE.Mesh(windowGeo, windowMat);
window2.position.set(1, 2, 2.05);
houseGroup.add(window2);

studio.scene.add(houseGroup);
"""

def generate_ventilation(scene_context=None):
    """Génère des bouches d'aération sur un bâtiment existant"""
    y_pos = 2.5  # Position haute sur un bâtiment
    if scene_context:
        # Cherche un bâtiment existant
        buildings = [obj for obj in scene_context.get('objects', []) 
                    if obj.get('type') == 'building' or 'house' in obj.get('name', '').lower()]
        if buildings:
            y_pos = buildings[0]['position']['y'] + 1.5
    
    return f"""
const ventGroup = new THREE.Group();
ventGroup.name = 'ventilation';

// Bouche d'aération 1
const vent1Geo = new THREE.CylinderGeometry(0.15, 0.15, 0.3, 16);
const ventMat = new THREE.MeshStandardMaterial({{ 
    color: 0x404040, 
    metalness: 0.8, 
    roughness: 0.3 
}});
const vent1 = new THREE.Mesh(vent1Geo, ventMat);
vent1.position.set(-1.5, {y_pos}, 2.1);
vent1.rotation.x = Math.PI / 2;
ventGroup.add(vent1);

// Grille
const grillGeo = new THREE.CylinderGeometry(0.12, 0.12, 0.05, 16);
const grillMat = new THREE.MeshStandardMaterial({{ 
    color: 0x202020, 
    metalness: 0.9 
}});
const grill1 = new THREE.Mesh(grillGeo, grillMat);
grill1.position.set(-1.5, {y_pos}, 2.15);
grill1.rotation.x = Math.PI / 2;
ventGroup.add(grill1);

// Bouche d'aération 2
const vent2 = new THREE.Mesh(vent1Geo, ventMat);
vent2.position.set(1.5, {y_pos}, 2.1);
vent2.rotation.x = Math.PI / 2;
ventGroup.add(vent2);

const grill2 = new THREE.Mesh(grillGeo, grillMat);
grill2.position.set(1.5, {y_pos}, 2.15);
grill2.rotation.x = Math.PI / 2;
ventGroup.add(grill2);

studio.scene.add(ventGroup);
"""

def generate_boat(scene_context=None):
    """Génère un bateau"""
    return """
const boatGroup = new THREE.Group();
boatGroup.name = 'boat';

// Coque
const hullGeo = new THREE.BoxGeometry(5, 1.2, 2.5);
const hullMat = new THREE.MeshStandardMaterial({ 
    color: 0x8B4513, 
    roughness: 0.7 
});
const hull = new THREE.Mesh(hullGeo, hullMat);
hull.position.y = 0.6;
boatGroup.add(hull);

// Pont
const deckGeo = new THREE.BoxGeometry(4.5, 0.3, 2.3);
const deck = new THREE.Mesh(deckGeo, hullMat);
deck.position.y = 1.35;
boatGroup.add(deck);

// Cabine
const cabinGeo = new THREE.BoxGeometry(2, 1.5, 1.8);
const cabinMat = new THREE.MeshStandardMaterial({ color: 0xFFFFFF });
const cabin = new THREE.Mesh(cabinGeo, cabinMat);
cabin.position.set(0, 2.25, 0);
boatGroup.add(cabin);

// Mât
const mastGeo = new THREE.CylinderGeometry(0.1, 0.1, 4, 8);
const mastMat = new THREE.MeshStandardMaterial({ color: 0x654321 });
const mast = new THREE.Mesh(mastGeo, mastMat);
mast.position.set(-1, 3.5, 0);
boatGroup.add(mast);

studio.scene.add(boatGroup);
"""

def generate_water(scene_context=None):
    """Génère de l'eau"""
    y_pos = get_position_y(scene_context)
    
    return f"""
const waterGroup = new THREE.Group();
waterGroup.name = 'water';

const waterGeo = new THREE.PlaneGeometry(100, 100, 50, 50);
const waterMat = new THREE.MeshStandardMaterial({{ 
    color: 0x1E90FF, 
    transparent: true, 
    opacity: 0.7,
    metalness: 0.8,
    roughness: 0.2
}});
const waterMesh = new THREE.Mesh(waterGeo, waterMat);
waterMesh.rotation.x = -Math.PI / 2;
waterMesh.position.y = {y_pos};
waterGroup.add(waterMesh);

// Vagues simples
const vertices = waterGeo.attributes.position.array;
for (let i = 0; i < vertices.length; i += 3) {{
    vertices[i + 2] = Math.sin(vertices[i] * 0.1) * Math.cos(vertices[i + 1] * 0.1) * 0.2;
}}
waterGeo.attributes.position.needsUpdate = true;

studio.scene.add(waterGroup);
"""

def generate_ground(scene_context=None):
    """Génère un sol"""
    y_pos = get_position_y(scene_context)
    
    return f"""
const groundGroup = new THREE.Group();
groundGroup.name = 'ground';

const groundGeo = new THREE.PlaneGeometry(150, 150);
const groundMat = new THREE.MeshStandardMaterial({{ 
    color: 0x228B22, 
    roughness: 0.95 
}});
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.position.y = {y_pos};
ground.receiveShadow = true;
groundGroup.add(ground);

studio.scene.add(groundGroup);
"""

def generate_character(scene_context=None):
    """Génère un personnage simple"""
    return """
const characterGroup = new THREE.Group();
characterGroup.name = 'character';

const bodyMat = new THREE.MeshStandardMaterial({ color: 0xFFDBAC });

// Corps
const bodyGeo = new THREE.CylinderGeometry(0.3, 0.3, 1.2, 16);
const body = new THREE.Mesh(bodyGeo, bodyMat);
body.position.y = 1.2;
characterGroup.add(body);

// Tête
const headGeo = new THREE.SphereGeometry(0.3, 16, 16);
const head = new THREE.Mesh(headGeo, bodyMat);
head.position.y = 2.1;
characterGroup.add(head);

// Bras gauche
const armGeo = new THREE.CylinderGeometry(0.1, 0.1, 0.8, 8);
const armL = new THREE.Mesh(armGeo, bodyMat);
armL.position.set(-0.5, 1.2, 0);
armL.rotation.z = 0.3;
characterGroup.add(armL);

// Bras droit
const armR = new THREE.Mesh(armGeo, bodyMat);
armR.position.set(0.5, 1.2, 0);
armR.rotation.z = -0.3;
characterGroup.add(armR);

// Jambes
const legGeo = new THREE.CylinderGeometry(0.12, 0.12, 1, 8);
const legL = new THREE.Mesh(legGeo, bodyMat);
legL.position.set(-0.15, 0.5, 0);
characterGroup.add(legL);

const legR = new THREE.Mesh(legGeo, bodyMat);
legR.position.set(0.15, 0.5, 0);
characterGroup.add(legR);

studio.scene.add(characterGroup);
"""

def generate_tree(scene_context=None):
    """Génère un arbre"""
    return """
const treeGroup = new THREE.Group();
treeGroup.name = 'tree';

// Tronc
const trunkGeo = new THREE.CylinderGeometry(0.3, 0.4, 3, 8);
const trunkMat = new THREE.MeshStandardMaterial({ color: 0x8B4513 });
const trunk = new THREE.Mesh(trunkGeo, trunkMat);
trunk.position.y = 1.5;
treeGroup.add(trunk);

// Feuillage
const leavesGeo = new THREE.SphereGeometry(1.5, 16, 16);
const leavesMat = new THREE.MeshStandardMaterial({ color: 0x228B22 });
const leaves = new THREE.Mesh(leavesGeo, leavesMat);
leaves.position.y = 3.5;
leaves.scale.set(1, 1.2, 1);
treeGroup.add(leaves);

studio.scene.add(treeGroup);
"""

def generate_car(scene_context=None):
    """Génère une voiture"""
    return """
const carGroup = new THREE.Group();
carGroup.name = 'car';

// Carrosserie
const bodyGeo = new THREE.BoxGeometry(4, 1, 2);
const bodyMat = new THREE.MeshStandardMaterial({ 
    color: 0xFF0000, 
    metalness: 0.9, 
    roughness: 0.1 
});
const body = new THREE.Mesh(bodyGeo, bodyMat);
body.position.y = 0.7;
carGroup.add(body);

// Cabine
const cabinGeo = new THREE.BoxGeometry(2.5, 0.8, 1.8);
const cabin = new THREE.Mesh(cabinGeo, bodyMat);
cabin.position.set(-0.3, 1.4, 0);
carGroup.add(cabin);

// Roues
const wheelGeo = new THREE.CylinderGeometry(0.4, 0.4, 0.3, 16);
const wheelMat = new THREE.MeshStandardMaterial({ color: 0x202020 });

const wheelPositions = [
    [-1.3, 0.4, -1.1],
    [-1.3, 0.4, 1.1],
    [1.3, 0.4, -1.1],
    [1.3, 0.4, 1.1]
];

wheelPositions.forEach(pos => {
    const wheel = new THREE.Mesh(wheelGeo, wheelMat);
    wheel.position.set(pos[0], pos[1], pos[2]);
    wheel.rotation.z = Math.PI / 2;
    carGroup.add(wheel);
});

studio.scene.add(carGroup);
"""

def generate_sky(scene_context=None):
    """Génère un ciel"""
    return """
const skyGroup = new THREE.Group();
skyGroup.name = 'sky';

const skyGeo = new THREE.SphereGeometry(200, 32, 32);
const skyMat = new THREE.MeshBasicMaterial({ 
    color: 0x87CEEB, 
    side: THREE.BackSide 
});
const sky = new THREE.Mesh(skyGeo, skyMat);
skyGroup.add(sky);

studio.scene.add(skyGroup);
"""

def generate_generic_object(prompt, scene_context=None):
    """Génère un objet générique"""
    return f"""
const genericGroup = new THREE.Group();
genericGroup.name = '{prompt[:20]}';

const geo = new THREE.BoxGeometry(2, 2, 2);
const mat = new THREE.MeshStandardMaterial({{ 
    color: 0x888888, 
    roughness: 0.7 
}});
const mesh = new THREE.Mesh(geo, mat);
mesh.position.y = 1;
genericGroup.add(mesh);

studio.scene.add(genericGroup);
"""
