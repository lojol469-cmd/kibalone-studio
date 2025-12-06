#!/usr/bin/env node
/**
 * 🚀 THREEJS BACKEND - Manipulation 3D rapide
 * ===========================================
 * Backend Node.js avec Three.js server-side
 * Manipulations en temps réel: mesh, rigging, animation
 */

const express = require('express');
const cors = require('cors');
const THREE = require('three');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

const OUTPUT_DIR = '/tmp/kibalone_models';
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

class ThreeJSBackend {
    constructor() {
        this.scene = new THREE.Scene();
        this.objects = new Map();
    }

    // ============================================
    // GÉNÉRATION RAPIDE
    // ============================================

    createCharacter(prompt) {
        console.log(`👤 Création personnage: ${prompt}`);

        const group = new THREE.Group();
        group.name = 'Character';

        // Corps
        const bodyGeo = new THREE.BoxGeometry(0.6, 1.2, 0.3);
        const bodyMat = new THREE.MeshStandardMaterial({ color: 0xFFDDAA });
        const body = new THREE.Mesh(bodyGeo, bodyMat);
        body.position.y = 1;
        body.name = 'Body';
        group.add(body);

        // Tête
        const headGeo = new THREE.SphereGeometry(0.3);
        const headMat = new THREE.MeshStandardMaterial({ color: 0xFFCCAA });
        const head = new THREE.Mesh(headGeo, headMat);
        head.position.y = 2;
        head.name = 'Head';
        group.add(head);

        // Bras
        const armGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.8);
        const armMat = new THREE.MeshStandardMaterial({ color: 0xFFCCAA });
        
        const armL = new THREE.Mesh(armGeo, armMat);
        armL.position.set(-0.4, 1.2, 0);
        armL.name = 'Arm_L';
        group.add(armL);

        const armR = new THREE.Mesh(armGeo, armMat);
        armR.position.set(0.4, 1.2, 0);
        armR.name = 'Arm_R';
        group.add(armR);

        // Jambes
        const legGeo = new THREE.CylinderGeometry(0.12, 0.12, 1);
        const legMat = new THREE.MeshStandardMaterial({ color: 0x4444FF });
        
        const legL = new THREE.Mesh(legGeo, legMat);
        legL.position.set(-0.2, 0.2, 0);
        legL.name = 'Leg_L';
        group.add(legL);

        const legR = new THREE.Mesh(legGeo, legMat);
        legR.position.set(0.2, 0.2, 0);
        legR.name = 'Leg_R';
        group.add(legR);

        // Stocke
        const id = `character_${Date.now()}`;
        this.objects.set(id, group);

        return {
            success: true,
            id: id,
            type: 'character',
            parts: ['Body', 'Head', 'Arm_L', 'Arm_R', 'Leg_L', 'Leg_R'],
            geometry: this.serializeObject(group),
            message: '✅ Personnage créé'
        };
    }

    createObject(type = 'cube') {
        console.log(`📦 Création objet: ${type}`);

        let geometry;
        switch (type) {
            case 'sphere':
                geometry = new THREE.SphereGeometry(1, 32, 32);
                break;
            case 'cylinder':
                geometry = new THREE.CylinderGeometry(0.5, 0.5, 2, 32);
                break;
            default:
                geometry = new THREE.BoxGeometry(1, 1, 1);
        }

        const material = new THREE.MeshStandardMaterial({ 
            color: Math.random() * 0xFFFFFF 
        });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.name = type;

        const id = `object_${Date.now()}`;
        this.objects.set(id, mesh);

        return {
            success: true,
            id: id,
            type: type,
            geometry: this.serializeObject(mesh)
        };
    }

    // ============================================
    // ANIMATION
    // ============================================

    createAnimation(objectId, animationType) {
        console.log(`🎬 Animation: ${animationType} pour ${objectId}`);

        const obj = this.objects.get(objectId);
        if (!obj) {
            return { success: false, error: 'Object not found' };
        }

        const keyframes = [];
        const duration = 90; // frames

        switch (animationType) {
            case 'run':
                keyframes.push(
                    { frame: 0, position: { x: 0, y: 0, z: 0 } },
                    { frame: duration, position: { x: 10, y: 0, z: 0 } }
                );
                break;

            case 'jump':
                keyframes.push(
                    { frame: 0, position: { x: 0, y: 0, z: 0 } },
                    { frame: duration / 2, position: { x: 0, y: 2, z: 0 } },
                    { frame: duration, position: { x: 0, y: 0, z: 0 } }
                );
                break;

            case 'rotate':
                keyframes.push(
                    { frame: 0, rotation: { x: 0, y: 0, z: 0 } },
                    { frame: duration, rotation: { x: 0, y: Math.PI * 2, z: 0 } }
                );
                break;
        }

        return {
            success: true,
            objectId: objectId,
            animationType: animationType,
            keyframes: keyframes,
            duration: duration,
            fps: 30
        };
    }

    // ============================================
    // MESH OPERATIONS
    // ============================================

    transformMesh(objectId, operation, params) {
        console.log(`🔧 Transform: ${operation} sur ${objectId}`);

        const obj = this.objects.get(objectId);
        if (!obj) {
            return { success: false, error: 'Object not found' };
        }

        switch (operation) {
            case 'translate':
                obj.position.set(
                    params.x || obj.position.x,
                    params.y || obj.position.y,
                    params.z || obj.position.z
                );
                break;

            case 'rotate':
                obj.rotation.set(
                    params.x || obj.rotation.x,
                    params.y || obj.rotation.y,
                    params.z || obj.rotation.z
                );
                break;

            case 'scale':
                obj.scale.set(
                    params.x || obj.scale.x,
                    params.y || obj.scale.y,
                    params.z || obj.scale.z
                );
                break;
        }

        return {
            success: true,
            objectId: objectId,
            operation: operation,
            newTransform: {
                position: obj.position,
                rotation: obj.rotation,
                scale: obj.scale
            }
        };
    }

    // ============================================
    // EXPORT
    // ============================================

    serializeObject(obj) {
        /**
         * Convertit un objet Three.js en format JSON pour le frontend
         */
        const data = {
            type: obj.type,
            name: obj.name,
            position: obj.position,
            rotation: obj.rotation,
            scale: obj.scale
        };

        if (obj.geometry) {
            data.geometry = {
                type: obj.geometry.type,
                parameters: obj.geometry.parameters
            };
        }

        if (obj.material) {
            data.material = {
                type: obj.material.type,
                color: obj.material.color ? obj.material.color.getHex() : null
            };
        }

        if (obj.children && obj.children.length > 0) {
            data.children = obj.children.map(child => this.serializeObject(child));
        }

        return data;
    }
}

// ============================================
// INSTANCE GLOBALE
// ============================================

const backend = new ThreeJSBackend();

// ============================================
// ENDPOINTS API
// ============================================

app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', service: 'Three.js Backend' });
});

app.post('/api/create-character', (req, res) => {
    const { prompt } = req.body;
    const result = backend.createCharacter(prompt || 'default character');
    res.json(result);
});

app.post('/api/create-object', (req, res) => {
    const { type } = req.body;
    const result = backend.createObject(type || 'cube');
    res.json(result);
});

app.post('/api/create-animation', (req, res) => {
    const { objectId, animationType } = req.body;
    const result = backend.createAnimation(objectId, animationType);
    res.json(result);
});

app.post('/api/transform-mesh', (req, res) => {
    const { objectId, operation, params } = req.body;
    const result = backend.transformMesh(objectId, operation, params);
    res.json(result);
});

app.get('/api/objects', (req, res) => {
    const objects = Array.from(backend.objects.entries()).map(([id, obj]) => ({
        id: id,
        name: obj.name,
        type: obj.type
    }));
    res.json({ objects: objects });
});

// ============================================
// DÉMARRAGE
// ============================================

const PORT = 11005;

app.listen(PORT, '0.0.0.0', () => {
    console.log('='.repeat(60));
    console.log('🚀 THREE.JS BACKEND - Démarrage');
    console.log('='.repeat(60));
    console.log(`📁 Models output: ${OUTPUT_DIR}`);
    console.log(`🌐 API: http://localhost:${PORT}`);
    console.log('='.repeat(60));
    console.log('');
    console.log('Endpoints disponibles:');
    console.log('  POST /api/create-character');
    console.log('  POST /api/create-object');
    console.log('  POST /api/create-animation');
    console.log('  POST /api/transform-mesh');
    console.log('  GET  /api/objects');
    console.log('='.repeat(60));
});
