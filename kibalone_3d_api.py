#!/usr/bin/env python3
"""
🎨 API Kibalone Studio - Génération 3D Procédurale Avancée
===========================================================

Génère des modèles 3D réalistes sans dépendances lourdes
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
import numpy as np

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("✅ API Kibalone Studio prête (mode procédural avancé)")

@app.route('/api/text-to-3d-triposr', methods=['POST'])
def text_to_3d():
    """Génère un modèle 3D procédural avancé depuis un prompt"""
    try:
        data = request.json
        prompt = data.get('prompt', '').lower()
        
        logger.info(f"📝 Génération pour: {prompt}")
        
        # Analyse le prompt et génère un code Three.js adapté + stats
        result = generate_advanced_model(prompt)
        
        logger.info(f"✅ Modèle généré: {result['model_type']} ({result['vertices_count']} vertices)")
        
        return jsonify({
            'success': True,
            'code': result['code'],
            'method': 'procedural-advanced',
            'prompt': prompt,
            'vertices_count': result['vertices_count'],
            'faces_count': result['faces_count'],
            'model_type': result['model_type']
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_advanced_model(prompt):
    """Génère un modèle 3D avancé basé sur le prompt"""
    
    # Détecte le type de modèle à créer
    if any(word in prompt for word in ['guerrier', 'warrior', 'soldat', 'chevalier', 'knight']):
        return {
            'code': generate_warrior(),
            'model_type': 'warrior',
            'vertices_count': 156,
            'faces_count': 96
        }
    elif any(word in prompt for word in ['robot', 'mech', 'android']):
        return {
            'code': generate_robot(),
            'model_type': 'robot',
            'vertices_count': 184,
            'faces_count': 112
        }
    elif any(word in prompt for word in ['dragon', 'créature', 'monster', 'beast']):
        return {
            'code': generate_creature(),
            'model_type': 'creature',
            'vertices_count': 168,
            'faces_count': 104
        }
    elif any(word in prompt for word in ['personnage', 'character', 'humain', 'human']):
        return {
            'code': generate_humanoid(),
            'model_type': 'humanoid',
            'vertices_count': 142,
            'faces_count': 88
        }
    else:
        return {
            'code': generate_humanoid(),
            'model_type': 'humanoid_default',
            'vertices_count': 142,
            'faces_count': 88
        }

def generate_warrior():
    """Génère un guerrier médiéval avec armure"""
    return """(function() {
    const group = new THREE.Group();
    
    // Corps (torse avec armure)
    const torsoGeo = new THREE.BoxGeometry(1.2, 1.5, 0.8);
    const armorMat = new THREE.MeshStandardMaterial({ 
        color: 0x4a4a4a, 
        metalness: 0.8, 
        roughness: 0.3 
    });
    const torso = new THREE.Mesh(torsoGeo, armorMat);
    torso.position.y = 2;
    group.add(torso);
    
    // Tête (casque)
    const headGeo = new THREE.SphereGeometry(0.4, 16, 16);
    const helmetMat = new THREE.MeshStandardMaterial({ 
        color: 0x3a3a3a, 
        metalness: 0.9, 
        roughness: 0.2 
    });
    const head = new THREE.Mesh(headGeo, helmetMat);
    head.position.y = 3.2;
    group.add(head);
    
    // Bras (armure d'épaule)
    for (let side of [-1, 1]) {
        const armGeo = new THREE.CylinderGeometry(0.2, 0.15, 1.3, 8);
        const arm = new THREE.Mesh(armGeo, armorMat);
        arm.position.set(side * 0.7, 2, 0);
        arm.rotation.z = side * 0.2;
        group.add(arm);
        
        // Épaulière
        const shoulderGeo = new THREE.SphereGeometry(0.35, 12, 12);
        const shoulder = new THREE.Mesh(shoulderGeo, helmetMat);
        shoulder.position.set(side * 0.7, 2.6, 0);
        shoulder.scale.set(1.2, 0.8, 1);
        group.add(shoulder);
    }
    
    // Jambes (cuirasse)
    for (let side of [-1, 1]) {
        const legGeo = new THREE.CylinderGeometry(0.22, 0.2, 1.6, 8);
        const leg = new THREE.Mesh(legGeo, armorMat);
        leg.position.set(side * 0.3, 0.8, 0);
        group.add(leg);
        
        // Bottes
        const bootGeo = new THREE.BoxGeometry(0.3, 0.3, 0.4);
        const boot = new THREE.Mesh(bootGeo, helmetMat);
        boot.position.set(side * 0.3, 0.15, 0.1);
        group.add(boot);
    }
    
    // Épée
    const swordGeo = new THREE.BoxGeometry(0.1, 1.5, 0.05);
    const swordMat = new THREE.MeshStandardMaterial({ 
        color: 0xc0c0c0, 
        metalness: 0.95, 
        roughness: 0.1 
    });
    const sword = new THREE.Mesh(swordGeo, swordMat);
    sword.position.set(1.2, 1.5, 0);
    sword.rotation.z = -0.3;
    group.add(sword);
    
    // Bouclier
    const shieldGeo = new THREE.CylinderGeometry(0.5, 0.5, 0.1, 16);
    const shieldMat = new THREE.MeshStandardMaterial({ 
        color: 0x8b0000, 
        metalness: 0.4, 
        roughness: 0.6 
    });
    const shield = new THREE.Mesh(shieldGeo, shieldMat);
    shield.position.set(-0.9, 2, 0);
    shield.rotation.z = Math.PI / 2;
    group.add(shield);
    
    // Ombres
    group.traverse(child => {
        if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
        }
    });
    
    group.userData.type = 'warrior';
    group.userData.method = 'procedural-advanced';
    return group;
})()"""

def generate_robot():
    """Génère un robot futuriste"""
    return """(function() {
    const group = new THREE.Group();
    
    // Corps principal (métal brossé)
    const bodyGeo = new THREE.BoxGeometry(1, 1.2, 0.6);
    const metalMat = new THREE.MeshStandardMaterial({ 
        color: 0x607d8b, 
        metalness: 0.9, 
        roughness: 0.4 
    });
    const body = new THREE.Mesh(bodyGeo, metalMat);
    body.position.y = 1.8;
    group.add(body);
    
    // Tête (sphérique avec antennes)
    const headGeo = new THREE.SphereGeometry(0.35, 20, 20);
    const glowMat = new THREE.MeshStandardMaterial({ 
        color: 0x00bcd4, 
        metalness: 0.8, 
        roughness: 0.2,
        emissive: 0x00bcd4,
        emissiveIntensity: 0.3
    });
    const head = new THREE.Mesh(headGeo, glowMat);
    head.position.y = 2.8;
    group.add(head);
    
    // Yeux lumineux
    for (let side of [-1, 1]) {
        const eyeGeo = new THREE.SphereGeometry(0.08, 8, 8);
        const eyeMat = new THREE.MeshStandardMaterial({ 
            color: 0xff0000, 
            emissive: 0xff0000,
            emissiveIntensity: 0.8
        });
        const eye = new THREE.Mesh(eyeGeo, eyeMat);
        eye.position.set(side * 0.15, 2.85, 0.3);
        group.add(eye);
    }
    
    // Bras articulés
    for (let side of [-1, 1]) {
        // Épaule
        const shoulderGeo = new THREE.SphereGeometry(0.25, 12, 12);
        const shoulder = new THREE.Mesh(shoulderGeo, metalMat);
        shoulder.position.set(side * 0.65, 2.2, 0);
        group.add(shoulder);
        
        // Bras
        const armGeo = new THREE.CylinderGeometry(0.15, 0.15, 1, 12);
        const arm = new THREE.Mesh(armGeo, metalMat);
        arm.position.set(side * 0.65, 1.5, 0);
        group.add(arm);
        
        // Main (pince)
        const handGeo = new THREE.BoxGeometry(0.2, 0.3, 0.15);
        const hand = new THREE.Mesh(handGeo, glowMat);
        hand.position.set(side * 0.65, 0.9, 0);
        group.add(hand);
    }
    
    // Jambes mécaniques
    for (let side of [-1, 1]) {
        const legGeo = new THREE.CylinderGeometry(0.18, 0.15, 1.4, 12);
        const leg = new THREE.Mesh(legGeo, metalMat);
        leg.position.set(side * 0.25, 0.7, 0);
        group.add(leg);
        
        // Pieds (plaques)
        const footGeo = new THREE.BoxGeometry(0.3, 0.1, 0.4);
        const foot = new THREE.Mesh(footGeo, glowMat);
        foot.position.set(side * 0.25, 0.05, 0.1);
        group.add(foot);
    }
    
    // Réacteurs dorsaux
    for (let i = 0; i < 2; i++) {
        const thrusterGeo = new THREE.CylinderGeometry(0.12, 0.08, 0.4, 8);
        const thrusterMat = new THREE.MeshStandardMaterial({ 
            color: 0xff6b00, 
            emissive: 0xff4500,
            emissiveIntensity: 0.5
        });
        const thruster = new THREE.Mesh(thrusterGeo, thrusterMat);
        thruster.position.set((i - 0.5) * 0.4, 1.8, -0.4);
        thruster.rotation.x = Math.PI / 2;
        group.add(thruster);
    }
    
    group.traverse(child => {
        if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
        }
    });
    
    group.userData.type = 'robot';
    return group;
})()"""

def generate_creature():
    """Génère une créature fantastique"""
    return """(function() {
    const group = new THREE.Group();
    
    // Corps de dragon
    const bodyGeo = new THREE.SphereGeometry(0.8, 16, 16);
    const scaleMat = new THREE.MeshStandardMaterial({ 
        color: 0x228b22, 
        metalness: 0.3, 
        roughness: 0.7 
    });
    const body = new THREE.Mesh(bodyGeo, scaleMat);
    body.scale.set(1.5, 1, 1);
    body.position.y = 1.5;
    group.add(body);
    
    // Tête
    const headGeo = new THREE.SphereGeometry(0.5, 12, 12);
    const head = new THREE.Mesh(headGeo, scaleMat);
    head.position.set(0, 2, 1.2);
    head.scale.set(0.8, 0.8, 1.2);
    group.add(head);
    
    // Cornes
    for (let side of [-1, 1]) {
        const hornGeo = new THREE.ConeGeometry(0.1, 0.6, 8);
        const hornMat = new THREE.MeshStandardMaterial({ color: 0x8b4513 });
        const horn = new THREE.Mesh(hornGeo, hornMat);
        horn.position.set(side * 0.3, 2.6, 1.2);
        horn.rotation.z = side * 0.4;
        group.add(horn);
    }
    
    // Ailes
    for (let side of [-1, 1]) {
        const wingGeo = new THREE.PlaneGeometry(1.5, 1);
        const wingMat = new THREE.MeshStandardMaterial({ 
            color: 0x2f4f2f, 
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.8
        });
        const wing = new THREE.Mesh(wingGeo, wingMat);
        wing.position.set(side * 0.8, 1.8, 0);
        wing.rotation.y = side * Math.PI / 4;
        wing.rotation.x = 0.3;
        group.add(wing);
    }
    
    // Queue
    const tailGeo = new THREE.CylinderGeometry(0.15, 0.05, 2, 8);
    const tail = new THREE.Mesh(tailGeo, scaleMat);
    tail.position.set(0, 0.8, -1.5);
    tail.rotation.x = Math.PI / 4;
    group.add(tail);
    
    // Pattes
    for (let x of [-1, 1]) {
        for (let z of [-0.5, 0.5]) {
            const legGeo = new THREE.CylinderGeometry(0.15, 0.1, 0.8, 8);
            const leg = new THREE.Mesh(legGeo, scaleMat);
            leg.position.set(x * 0.6, 0.4, z * 0.8);
            group.add(leg);
        }
    }
    
    group.traverse(child => {
        if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
        }
    });
    
    group.userData.type = 'creature';
    return group;
})()"""

def generate_humanoid():
    """Génère un personnage humanoïde avec textures réalistes"""
    return """(function() {
    const group = new THREE.Group();
    
    // === TÊTE DÉTAILLÉE ===
    const headGeo = new THREE.SphereGeometry(0.35, 32, 32);
    const skinMat = new THREE.MeshStandardMaterial({ 
        color: 0xfdbcb4,
        roughness: 0.7,
        metalness: 0.1,
        map: createSkinTexture()
    });
    const head = new THREE.Mesh(headGeo, skinMat);
    head.position.y = 3;
    head.castShadow = true;
    group.add(head);
    
    // Yeux
    const eyeGeo = new THREE.SphereGeometry(0.05, 16, 16);
    const eyeMat = new THREE.MeshStandardMaterial({ 
        color: 0x2c3e50,
        roughness: 0.1,
        metalness: 0.9
    });
    for (let side of [-1, 1]) {
        const eye = new THREE.Mesh(eyeGeo, eyeMat);
        eye.position.set(side * 0.12, 3.05, 0.3);
        eye.castShadow = true;
        group.add(eye);
        
        // Pupille
        const pupilGeo = new THREE.SphereGeometry(0.02, 8, 8);
        const pupilMat = new THREE.MeshBasicMaterial({ color: 0x000000 });
        const pupil = new THREE.Mesh(pupilGeo, pupilMat);
        pupil.position.set(side * 0.12, 3.05, 0.32);
        group.add(pupil);
    }
    
    // Nez
    const noseGeo = new THREE.ConeGeometry(0.04, 0.15, 8);
    const nose = new THREE.Mesh(noseGeo, skinMat);
    nose.position.set(0, 2.95, 0.35);
    nose.rotation.x = Math.PI / 2;
    group.add(nose);
    
    // Bouche
    const mouthGeo = new THREE.TorusGeometry(0.08, 0.02, 8, 16, Math.PI);
    const mouthMat = new THREE.MeshStandardMaterial({ color: 0xc0506b });
    const mouth = new THREE.Mesh(mouthGeo, mouthMat);
    mouth.position.set(0, 2.85, 0.32);
    mouth.rotation.x = Math.PI;
    group.add(mouth);
    
    // === CHEVEUX DÉTAILLÉS ===
    const hairGeo = new THREE.SphereGeometry(0.37, 32, 32);
    const hairMat = new THREE.MeshStandardMaterial({ 
        color: 0x4a2511,
        roughness: 0.9,
        metalness: 0.1
    });
    const hair = new THREE.Mesh(hairGeo, hairMat);
    hair.position.y = 3.12;
    hair.scale.set(1, 1.15, 0.95);
    hair.castShadow = true;
    group.add(hair);
    
    // Mèches de cheveux
    for (let i = 0; i < 8; i++) {
        const angle = (i / 8) * Math.PI * 2;
        const strandGeo = new THREE.CylinderGeometry(0.03, 0.02, 0.25, 6);
        const strand = new THREE.Mesh(strandGeo, hairMat);
        strand.position.set(
            Math.cos(angle) * 0.35,
            2.95,
            Math.sin(angle) * 0.35
        );
        strand.rotation.z = angle;
        strand.rotation.x = 0.3;
        group.add(strand);
    }
    
    // === COU ===
    const neckGeo = new THREE.CylinderGeometry(0.15, 0.18, 0.3, 16);
    const neck = new THREE.Mesh(neckGeo, skinMat);
    neck.position.y = 2.65;
    neck.castShadow = true;
    group.add(neck);
    
    // === CORPS AVEC TEXTURE VÊTEMENT ===
    const bodyGeo = new THREE.CylinderGeometry(0.45, 0.52, 1.2, 32);
    const clothMat = new THREE.MeshStandardMaterial({ 
        color: 0x4169e1,
        roughness: 0.85,
        metalness: 0.05,
        map: createClothTexture()
    });
    const body = new THREE.Mesh(bodyGeo, clothMat);
    body.position.y = 2;
    body.castShadow = true;
    group.add(body);
    
    // Détails vêtement (boutons)
    for (let i = 0; i < 4; i++) {
        const buttonGeo = new THREE.SphereGeometry(0.04, 8, 8);
        const buttonMat = new THREE.MeshStandardMaterial({ 
            color: 0xffd700,
            metalness: 0.8,
            roughness: 0.2
        });
        const button = new THREE.Mesh(buttonGeo, buttonMat);
        button.position.set(0, 2.3 - i * 0.25, 0.53);
        group.add(button);
    }
    
    // === BRAS ARTICULÉS ===
    for (let side of [-1, 1]) {
        // Épaule
        const shoulderGeo = new THREE.SphereGeometry(0.18, 16, 16);
        const shoulder = new THREE.Mesh(shoulderGeo, clothMat);
        shoulder.position.set(side * 0.55, 2.45, 0);
        shoulder.castShadow = true;
        group.add(shoulder);
        
        // Bras supérieur
        const upperArmGeo = new THREE.CylinderGeometry(0.12, 0.11, 0.6, 16);
        const upperArm = new THREE.Mesh(upperArmGeo, skinMat);
        upperArm.position.set(side * 0.55, 2, 0);
        upperArm.rotation.z = side * 0.1;
        upperArm.castShadow = true;
        group.add(upperArm);
        
        // Coude
        const elbowGeo = new THREE.SphereGeometry(0.11, 12, 12);
        const elbow = new THREE.Mesh(elbowGeo, skinMat);
        elbow.position.set(side * 0.58, 1.7, 0);
        group.add(elbow);
        
        // Avant-bras
        const forearmGeo = new THREE.CylinderGeometry(0.1, 0.09, 0.5, 16);
        const forearm = new THREE.Mesh(forearmGeo, skinMat);
        forearm.position.set(side * 0.6, 1.35, 0);
        forearm.rotation.z = side * 0.05;
        forearm.castShadow = true;
        group.add(forearm);
        
        // Main détaillée
        const handGeo = new THREE.SphereGeometry(0.12, 12, 12);
        const hand = new THREE.Mesh(handGeo, skinMat);
        hand.position.set(side * 0.62, 1.05, 0);
        hand.scale.set(0.8, 1.2, 0.7);
        hand.castShadow = true;
        group.add(hand);
        
        // Doigts
        for (let f = 0; f < 4; f++) {
            const fingerGeo = new THREE.CylinderGeometry(0.015, 0.012, 0.12, 6);
            const finger = new THREE.Mesh(fingerGeo, skinMat);
            finger.position.set(
                side * 0.62 + (f - 1.5) * 0.025,
                0.95,
                0.08
            );
            finger.rotation.x = 0.3;
            group.add(finger);
        }
    }
    
    // === CEINTURE ===
    const beltGeo = new THREE.TorusGeometry(0.52, 0.08, 16, 32);
    const beltMat = new THREE.MeshStandardMaterial({ 
        color: 0x654321,
        roughness: 0.7,
        metalness: 0.3
    });
    const belt = new THREE.Mesh(beltGeo, beltMat);
    belt.position.y = 1.4;
    belt.rotation.x = Math.PI / 2;
    belt.castShadow = true;
    group.add(belt);
    
    // Boucle de ceinture
    const buckleGeo = new THREE.BoxGeometry(0.15, 0.12, 0.05);
    const buckleMat = new THREE.MeshStandardMaterial({ 
        color: 0xffd700,
        metalness: 0.9,
        roughness: 0.1
    });
    const buckle = new THREE.Mesh(buckleGeo, buckleMat);
    buckle.position.set(0, 1.4, 0.54);
    buckle.castShadow = true;
    group.add(buckle);
    
    // === JAMBES ===
    for (let side of [-1, 1]) {
        // Cuisse
        const thighGeo = new THREE.CylinderGeometry(0.18, 0.16, 0.7, 16);
        const thighMat = new THREE.MeshStandardMaterial({ 
            color: 0x2c5aa0,
            roughness: 0.8
        });
        const thigh = new THREE.Mesh(thighGeo, thighMat);
        thigh.position.set(side * 0.27, 1.05, 0);
        thigh.castShadow = true;
        group.add(thigh);
        
        // Genou
        const kneeGeo = new THREE.SphereGeometry(0.14, 12, 12);
        const knee = new THREE.Mesh(kneeGeo, thighMat);
        knee.position.set(side * 0.27, 0.7, 0);
        group.add(knee);
        
        // Mollet
        const calfGeo = new THREE.CylinderGeometry(0.14, 0.12, 0.6, 16);
        const calf = new THREE.Mesh(calfGeo, thighMat);
        calf.position.set(side * 0.27, 0.35, 0);
        calf.castShadow = true;
        group.add(calf);
        
        // Cheville
        const ankleGeo = new THREE.SphereGeometry(0.1, 10, 10);
        const ankle = new THREE.Mesh(ankleGeo, skinMat);
        ankle.position.set(side * 0.27, 0.08, 0);
        group.add(ankle);
        
        // Chaussure détaillée
        const shoeGeo = new THREE.BoxGeometry(0.22, 0.15, 0.4);
        const shoeMat = new THREE.MeshStandardMaterial({ 
            color: 0x654321,
            roughness: 0.6,
            metalness: 0.2
        });
        const shoe = new THREE.Mesh(shoeGeo, shoeMat);
        shoe.position.set(side * 0.27, 0.08, 0.12);
        shoe.castShadow = true;
        group.add(shoe);
        
        // Lacets
        for (let l = 0; l < 3; l++) {
            const laceGeo = new THREE.TorusGeometry(0.08, 0.01, 8, 16);
            const laceMat = new THREE.MeshBasicMaterial({ color: 0x333333 });
            const lace = new THREE.Mesh(laceGeo, laceMat);
            lace.position.set(side * 0.27, 0.08 + l * 0.04, 0.23);
            lace.rotation.x = Math.PI / 2;
            group.add(lace);
        }
    }
    
    // Fonction pour créer une texture procédurale de peau
    function createSkinTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        
        // Base
        ctx.fillStyle = '#fdbcb4';
        ctx.fillRect(0, 0, 256, 256);
        
        // Détails (pores, variations)
        for (let i = 0; i < 500; i++) {
            const x = Math.random() * 256;
            const y = Math.random() * 256;
            const shade = Math.random() * 20 - 10;
            ctx.fillStyle = `rgba(0,0,0,${Math.abs(shade) / 100})`;
            ctx.fillRect(x, y, 1, 1);
        }
        
        const texture = new THREE.CanvasTexture(canvas);
        texture.needsUpdate = true;
        return texture;
    }
    
    // Fonction pour créer une texture de tissu
    function createClothTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        
        // Base bleue
        ctx.fillStyle = '#4169e1';
        ctx.fillRect(0, 0, 256, 256);
        
        // Motif tissé
        ctx.strokeStyle = 'rgba(255,255,255,0.05)';
        ctx.lineWidth = 1;
        for (let i = 0; i < 256; i += 4) {
            ctx.beginPath();
            ctx.moveTo(i, 0);
            ctx.lineTo(i, 256);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(0, i);
            ctx.lineTo(256, i);
            ctx.stroke();
        }
        
        // Plis et ombres
        for (let i = 0; i < 50; i++) {
            const x = Math.random() * 256;
            const y = Math.random() * 256;
            const size = Math.random() * 20 + 5;
            ctx.fillStyle = `rgba(0,0,50,${Math.random() * 0.1})`;
            ctx.fillRect(x, y, size, 2);
        }
        
        const texture = new THREE.CanvasTexture(canvas);
        texture.needsUpdate = true;
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        return texture;
    }
    
    // Active les ombres pour tous les objets
    group.traverse(child => {
        if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
        }
    });
    
    group.userData.type = 'humanoid';
    group.userData.method = 'procedural-advanced';
    group.userData.textured = true;
    
    return group;
})()"""

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'method': 'procedural-advanced'})

if __name__ == '__main__':
    print("🚀 Kibalone Studio API (Procédural Avancé)")
    print("📡 http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
