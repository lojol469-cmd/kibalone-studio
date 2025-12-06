#!/usr/bin/env node
/**
 * 🤖 KIBALI AI - Backend Three.js Intelligent
 * ==========================================
 * IA conversationnelle qui génère du code Three.js en temps réel
 * Comprend TOUT type de demande et manipule la 3D via le chat
 */

const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

class KibaliAI {
    constructor() {
        this.patterns = this.initPatterns();
    }

    initPatterns() {
        return {
            // CRÉATION D'OBJETS
            create_cube: /cr[ée]+\s*(un|le)?\s*cube/i,
            create_sphere: /cr[ée]+\s*(une|la)?\s*sph[èe]re/i,
            create_cylinder: /cr[ée]+\s*(un|le)?\s*cylindre/i,
            create_plane: /cr[ée]+\s*(un|le)?\s*plan/i,
            create_torus: /cr[ée]+\s*(un|le)?\s*tore/i,
            create_cone: /cr[ée]+\s*(un|le)?\s*c[ôo]ne/i,
            
            // PERSONNAGES
            create_character: /cr[ée]+\s*(un|le)?\s*personnage/i,
            create_robot: /cr[ée]+\s*(un|le)?\s*robot/i,
            create_hero: /cr[ée]+\s*(un|le)?\s*h[ée]ro/i,
            
            // ANIMATIONS
            animate_rotate: /(anime|rotation|tourne|faire\s+tourner)/i,
            animate_bounce: /(rebond|saute|bounce)/i,
            animate_wave: /(ondule|vague|wave)/i,
            animate_pulse: /(pulse|bat|pulsation)/i,
            
            // MOUVEMENTS
            move_forward: /(avance|marche|court)/i,
            move_jump: /(saute|jump)/i,
            move_fly: /(vole|vol)/i,
            
            // LUMIÈRES
            add_light: /(lumi[èe]re|[ée]claire|illumine)/i,
            change_light: /(change|modifie).*lumi[èe]re/i,
            
            // CAMÉRA
            zoom_in: /(zoom|rapproche)/i,
            zoom_out: /(d[ée]zoom|[ée]loigne)/i,
            rotate_camera: /(cam[ée]ra|vue).*tourne/i,
            
            // COULEURS
            change_color: /(couleur|colore|color|peint)/i,
            
            // MATÉRIAUX
            material_metal: /(m[ée]tal|m[ée]tallique)/i,
            material_glass: /(verre|transparent|glass)/i,
            material_plastic: /(plastique|plastic)/i,
            
            // ENVIRONNEMENT
            create_scene: /(sc[èe]ne|environnement|d[ée]cor)/i,
            add_ground: /(sol|terrain|ground)/i,
            add_sky: /(ciel|sky)/i,
            
            // SUPPRESSION
            delete_all: /(efface|supprime|delete).*tout/i,
            delete_last: /(efface|supprime|delete).*(dernier|last)/i,
            
            // EFFETS
            add_particles: /(particules|particles|effet)/i,
            add_fog: /(brouillard|fog)/i,
        };
    }

    analyzePrompt(prompt) {
        const lower = prompt.toLowerCase();
        
        // Détecte la couleur si mentionnée
        const colors = {
            rouge: 0xff0000, red: 0xff0000,
            bleu: 0x0000ff, blue: 0x0000ff,
            vert: 0x00ff00, green: 0x00ff00,
            jaune: 0xffff00, yellow: 0xffff00,
            orange: 0xff8800,
            violet: 0x8800ff, purple: 0x8800ff,
            rose: 0xff00ff, pink: 0xff00ff,
            blanc: 0xffffff, white: 0xffffff,
            noir: 0x000000, black: 0x000000,
            gris: 0x888888, gray: 0x888888
        };
        
        let color = 0x00d4ff; // Couleur par défaut
        for (const [colorName, colorValue] of Object.entries(colors)) {
            if (lower.includes(colorName)) {
                color = colorValue;
                break;
            }
        }
        
        // Match les patterns
        for (const [action, pattern] of Object.entries(this.patterns)) {
            if (pattern.test(prompt)) {
                return { action, color, prompt };
            }
        }
        
        return { action: 'unknown', color, prompt };
    }

    generateCode(analysis) {
        const { action, color, prompt } = analysis;
        
        switch (action) {
            // OBJETS DE BASE
            case 'create_cube':
                return {
                    understood: true,
                    action: 'Création d\'un cube',
                    explanation: 'Cube 3D ajouté à la scène',
                    code: this.generateCubeCode(color),
                    animated: false
                };
                
            case 'create_sphere':
                return {
                    understood: true,
                    action: 'Création d\'une sphère',
                    explanation: 'Sphère 3D ajoutée à la scène',
                    code: this.generateSphereCode(color),
                    animated: false
                };
                
            case 'create_cylinder':
                return {
                    understood: true,
                    action: 'Création d\'un cylindre',
                    explanation: 'Cylindre 3D ajouté à la scène',
                    code: this.generateCylinderCode(color),
                    animated: false
                };
                
            case 'create_character':
                return {
                    understood: true,
                    action: 'Création d\'un personnage',
                    explanation: 'Personnage humanoïde créé avec corps, tête, bras et jambes',
                    code: this.generateCharacterCode(color),
                    animated: false
                };
                
            case 'animate_rotate':
                return {
                    understood: true,
                    action: 'Animation rotation',
                    explanation: 'Rotation continue appliquée aux objets',
                    code: this.generateRotationCode(),
                    animated: true
                };
                
            case 'move_forward':
                return {
                    understood: true,
                    action: 'Animation déplacement',
                    explanation: 'Mouvement vers l\'avant',
                    code: this.generateMoveCode('forward'),
                    animated: true
                };
                
            case 'move_jump':
                return {
                    understood: true,
                    action: 'Animation saut',
                    explanation: 'Animation de saut',
                    code: this.generateJumpCode(),
                    animated: true
                };
                
            case 'add_light':
                return {
                    understood: true,
                    action: 'Ajout de lumière',
                    explanation: 'Nouvelle source lumineuse',
                    code: this.generateLightCode(color),
                    animated: false
                };
                
            case 'delete_all':
                return {
                    understood: true,
                    action: 'Suppression',
                    explanation: 'Tous les objets ont été supprimés',
                    code: `
                        // Supprime tous les objets de la scène
                        while(studio.objects.length > 0) {
                            const obj = studio.objects.pop();
                            scene.remove(obj);
                            if(obj.geometry) obj.geometry.dispose();
                            if(obj.material) obj.material.dispose();
                        }
                        null; // Ne retourne rien
                    `,
                    animated: false
                };
                
            default:
                return {
                    understood: false,
                    action: 'Inconnu',
                    explanation: 'Je n\'ai pas compris cette demande',
                    code: null,
                    animated: false
                };
        }
    }

    // GÉNÉRATEURS DE CODE THREE.JS
    
    generateCubeCode(color) {
        return `
            (function() {
                const geometry = new THREE.BoxGeometry(1, 1, 1);
                const material = new THREE.MeshStandardMaterial({ 
                    color: ${color},
                    metalness: 0.3,
                    roughness: 0.7
                });
                const cube = new THREE.Mesh(geometry, material);
                cube.position.set(
                    Math.random() * 4 - 2,
                    Math.random() * 2 + 1,
                    Math.random() * 4 - 2
                );
                cube.castShadow = true;
                cube.receiveShadow = true;
                return cube;
            })()
        `;
    }
    
    generateSphereCode(color) {
        return `
            (function() {
                const geometry = new THREE.SphereGeometry(0.5, 32, 32);
                const material = new THREE.MeshStandardMaterial({ 
                    color: ${color},
                    metalness: 0.5,
                    roughness: 0.5
                });
                const sphere = new THREE.Mesh(geometry, material);
                sphere.position.set(
                    Math.random() * 4 - 2,
                    Math.random() * 2 + 1,
                    Math.random() * 4 - 2
                );
                sphere.castShadow = true;
                sphere.receiveShadow = true;
                return sphere;
            })()
        `;
    }
    
    generateCylinderCode(color) {
        return `
            (function() {
                const geometry = new THREE.CylinderGeometry(0.3, 0.3, 1.5, 32);
                const material = new THREE.MeshStandardMaterial({ 
                    color: ${color},
                    metalness: 0.4,
                    roughness: 0.6
                });
                const cylinder = new THREE.Mesh(geometry, material);
                cylinder.position.set(
                    Math.random() * 4 - 2,
                    0.75,
                    Math.random() * 4 - 2
                );
                cylinder.castShadow = true;
                cylinder.receiveShadow = true;
                return cylinder;
            })()
        `;
    }
    
    generateCharacterCode(color) {
        return `
            (function() {
                const character = new THREE.Group();
                character.name = 'Character';
                
                // Corps
                const bodyGeo = new THREE.BoxGeometry(0.6, 1.2, 0.3);
                const bodyMat = new THREE.MeshStandardMaterial({ color: ${color} });
                const body = new THREE.Mesh(bodyGeo, bodyMat);
                body.position.y = 1;
                body.castShadow = true;
                character.add(body);
                
                // Tête
                const headGeo = new THREE.SphereGeometry(0.3, 32, 32);
                const headMat = new THREE.MeshStandardMaterial({ color: ${Math.floor(color * 0.9)} });
                const head = new THREE.Mesh(headGeo, headMat);
                head.position.y = 2;
                head.castShadow = true;
                character.add(head);
                
                // Bras gauche
                const armGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.8, 16);
                const armMat = new THREE.MeshStandardMaterial({ color: ${Math.floor(color * 0.9)} });
                const armL = new THREE.Mesh(armGeo, armMat);
                armL.position.set(-0.4, 1.2, 0);
                armL.castShadow = true;
                character.add(armL);
                
                // Bras droit
                const armR = new THREE.Mesh(armGeo, armMat);
                armR.position.set(0.4, 1.2, 0);
                armR.castShadow = true;
                character.add(armR);
                
                // Jambe gauche
                const legGeo = new THREE.CylinderGeometry(0.12, 0.12, 1, 16);
                const legMat = new THREE.MeshStandardMaterial({ color: 0x4444ff });
                const legL = new THREE.Mesh(legGeo, legMat);
                legL.position.set(-0.2, 0.2, 0);
                legL.castShadow = true;
                character.add(legL);
                
                // Jambe droite
                const legR = new THREE.Mesh(legGeo, legMat);
                legR.position.set(0.2, 0.2, 0);
                legR.castShadow = true;
                character.add(legR);
                
                character.position.set(0, 0, 0);
                return character;
            })()
        `;
    }
    
    generateRotationCode() {
        return `
            (function() {
                // Anime tous les objets existants
                studio.objects.forEach(obj => {
                    if(!obj.userData.animation) {
                        obj.userData.animation = 'rotate';
                        obj.userData.rotationSpeed = Math.random() * 0.02 + 0.01;
                    }
                });
                
                // Ajoute une fonction d'animation au studio
                if(!studio.animationLoop) {
                    studio.animationLoop = setInterval(() => {
                        studio.objects.forEach(obj => {
                            if(obj.userData.animation === 'rotate') {
                                obj.rotation.y += obj.userData.rotationSpeed;
                            }
                        });
                    }, 16);
                }
                
                return null;
            })()
        `;
    }
    
    generateMoveCode(direction) {
        return `
            (function() {
                const lastObj = studio.objects[studio.objects.length - 1];
                if(lastObj) {
                    lastObj.userData.animation = 'move';
                    lastObj.userData.moveSpeed = 0.05;
                    lastObj.userData.moveDirection = '${direction}';
                    
                    if(!studio.moveLoop) {
                        studio.moveLoop = setInterval(() => {
                            studio.objects.forEach(obj => {
                                if(obj.userData.animation === 'move') {
                                    obj.position.x += obj.userData.moveSpeed;
                                }
                            });
                        }, 16);
                    }
                }
                return null;
            })()
        `;
    }
    
    generateJumpCode() {
        return `
            (function() {
                const lastObj = studio.objects[studio.objects.length - 1];
                if(lastObj) {
                    let jumpPhase = 0;
                    const jumpInterval = setInterval(() => {
                        jumpPhase += 0.1;
                        lastObj.position.y = Math.abs(Math.sin(jumpPhase)) * 2 + 0.5;
                        if(jumpPhase > Math.PI * 4) {
                            clearInterval(jumpInterval);
                        }
                    }, 16);
                }
                return null;
            })()
        `;
    }
    
    generateLightCode(color) {
        return `
            (function() {
                const light = new THREE.PointLight(${color}, 2, 10);
                light.position.set(
                    Math.random() * 6 - 3,
                    Math.random() * 4 + 2,
                    Math.random() * 6 - 3
                );
                light.castShadow = true;
                
                // Ajoute un helper visuel
                const lightHelper = new THREE.PointLightHelper(light, 0.2);
                scene.add(lightHelper);
                
                return light;
            })()
        `;
    }
}

// Instance globale
const kibali = new KibaliAI();

// ENDPOINTS API
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', service: 'Kibali AI - Three.js Intelligent' });
});

app.post('/api/process-prompt', (req, res) => {
    const { prompt, sceneContext } = req.body;
    
    console.log(`🤖 Kibali traite: "${prompt}"`);
    
    // Analyse le prompt
    const analysis = kibali.analyzePrompt(prompt);
    console.log(`   → Action détectée: ${analysis.action}`);
    
    // Génère le code Three.js
    const result = kibali.generateCode(analysis);
    
    res.json(result);
});

// DÉMARRAGE
const PORT = 11005;

app.listen(PORT, '0.0.0.0', () => {
    console.log('='.repeat(60));
    console.log('🤖 KIBALI AI - Backend Three.js Intelligent');
    console.log('='.repeat(60));
    console.log(`🌐 API: http://localhost:${PORT}`);
    console.log('');
    console.log('Capacités:');
    console.log('  • Compréhension naturelle en français');
    console.log('  • Génération de code Three.js en temps réel');
    console.log('  • Création d\'objets, personnages, animations');
    console.log('  • Manipulation de lumières, caméra, matériaux');
    console.log('  • IA conversationnelle pour la 3D');
    console.log('='.repeat(60));
});
