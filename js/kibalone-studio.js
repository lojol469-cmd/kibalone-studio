// Kibalone Studio - AI-Powered 3D Animation Interface
// Main JavaScript Controller

class KibaloneStudio {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.axisWidget = null; // Widget d'orientation des axes
        this.objects = [];
        this.currentFrame = 0;
        this.totalFrames = 120;
        this.isPlaying = false;
        this.fps = 30;
        
        // Système de caméra avancé
        this.cameraAnimations = [];
        this.cameraTarget = { x: 0, y: 0, z: 0 };
        this.cameraSpeed = 0.05;
        this.isAnimatingCamera = false;
        
        this.init();
    }

    init() {
        this.initThreeJS();
        this.initEventListeners();
        this.animate();
        console.log('🚀 Kibalone Studio initialisé');
        addLog('🚀 Kibalone Studio initialisé');
        addLog('✅ Scene 3D prête');
        addLog('💡 Utilisez le chat pour créer des objets 3D avec l\'IA');
        addLog('🧠 Powered by Mistral (raisonnement) + CodeLlama (code)');
    }
    
    async loadDemoMesh() {
        try {
            // Charge la config de démo
            const response = await fetch('/demo_config.json');
            if (!response.ok) return;
            
            const config = await response.json();
            if (!config.demo_mode || !config.default_mesh) return;
            
            addLog('📦 Chargement démo MiDaS...');
            addLog(`📄 Mesh: ${config.default_mesh}`);
            
            // Charge le mesh OBJ
            const loader = new THREE.OBJLoader();
            loader.load(
                config.default_mesh,
                (obj) => {
                    // Centre et scale l'objet
                    const box = new THREE.Box3().setFromObject(obj);
                    const center = box.getCenter(new THREE.Vector3());
                    const size = box.getSize(new THREE.Vector3());
                    const maxDim = Math.max(size.x, size.y, size.z);
                    const scale = 5 / maxDim;
                    
                    obj.position.sub(center);
                    obj.scale.set(scale, scale, scale);
                    
                    // Matériau
                    obj.traverse((child) => {
                        if (child.isMesh) {
                            child.material = new THREE.MeshStandardMaterial({
                                color: 0x4CAF50,
                                metalness: 0.3,
                                roughness: 0.7
                            });
                        }
                    });
                    
                    this.scene.add(obj);
                    this.objects.push(obj);
                    
                    addLog('✅ Démo MiDaS chargée (photogrammetrie 3D)');
                    addChatMessage('ai', '✅ Mesh de démo chargé! C\'était un objet reconstruit depuis 10 photos avec MiDaS photogrammetrie.');
                    this.updateObjectCount();
                },
                (xhr) => {
                    const percent = (xhr.loaded / xhr.total * 100).toFixed(0);
                    addLog(`⏳ Chargement: ${percent}%`);
                },
                (error) => {
                    console.error('Erreur chargement démo:', error);
                }
            );
            
        } catch (error) {
            // Pas de démo, mode normal
            console.log('Pas de démo MiDaS configurée');
        }
    }

    initThreeJS() {
        const canvas = document.getElementById('canvas3d');
        
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0f0f1e);
        
        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            canvas.clientWidth / canvas.clientHeight,
            0.1,
            1000
        );
        this.camera.position.set(5, 5, 5);
        this.camera.lookAt(0, 0, 0);
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
        this.renderer.setSize(canvas.clientWidth, canvas.clientHeight);
        this.renderer.shadowMap.enabled = true;
        
        // Lights
        const ambientLight = new THREE.AmbientLight(0x404040, 2);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 10, 5);
        directionalLight.castShadow = true;
        this.scene.add(directionalLight);
        
        // Grid
        const gridHelper = new THREE.GridHelper(20, 20, 0x00d4ff, 0x2d4059);
        this.scene.add(gridHelper);
        
        // Axes Helper
        const axesHelper = new THREE.AxesHelper(5);
        this.scene.add(axesHelper);
        
        // Axis Widget (widget d'orientation)
        this.axisWidget = new AxisWidget(this.camera);
        
        // Controls (basic mouse rotation)
        this.initControls();
    }

    initControls() {
        const canvas = document.getElementById('canvas3d');
        let isDragging = false;
        let previousMousePosition = { x: 0, y: 0 };

        canvas.addEventListener('mousedown', (e) => {
            isDragging = true;
            previousMousePosition = { x: e.clientX, y: e.clientY };
        });

        canvas.addEventListener('mousemove', (e) => {
            if (isDragging) {
                const deltaX = e.clientX - previousMousePosition.x;
                const deltaY = e.clientY - previousMousePosition.y;

                this.camera.position.x += deltaX * 0.01;
                this.camera.position.y -= deltaY * 0.01;
                this.camera.lookAt(0, 0, 0);

                previousMousePosition = { x: e.clientX, y: e.clientY };
            }
        });

        canvas.addEventListener('mouseup', () => {
            isDragging = false;
        });

        canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomSpeed = 0.1;
            const direction = e.deltaY > 0 ? 1 : -1;
            
            this.camera.position.multiplyScalar(1 + direction * zoomSpeed);
        });
    }

    initEventListeners() {
        window.addEventListener('resize', () => this.onWindowResize());
    }

    onWindowResize() {
        const canvas = document.getElementById('canvas3d');
        this.camera.aspect = canvas.clientWidth / canvas.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        if (this.isPlaying) {
            this.currentFrame++;
            if (this.currentFrame > this.totalFrames) {
                this.currentFrame = 0;
            }
            this.updateFrame();
        }
        
        // Mettre à jour le widget d'axes
        if (this.axisWidget) {
            this.axisWidget.update();
        }
        
        this.renderer.render(this.scene, this.camera);
    }

    updateFrame() {
        document.getElementById('current-frame').textContent = this.currentFrame;
        document.getElementById('timeline-frame').textContent = this.currentFrame;
        
        const progress = (this.currentFrame / this.totalFrames) * 100;
        document.getElementById('timeline-progress').style.width = progress + '%';
    }

    // AI Functions - Workflows de reconstruction 3D
    async processAICommand(prompt) {
        addChatMessage('user', prompt);
        addChatMessage('ai', '🧠 Kibali analyse avec Mistral + CodeLlama...');
        addLog(`📨 Requête utilisateur: "${prompt}"`);

        try {
            // 🚀 NOUVEAU: Utilise uniquement le générateur HYBRIDE de code
            addLog('🧠 [Mistral] Analyse de la requête...');
            addLog('💻 [CodeLlama] Génération du code Three.js...');
            addChatMessage('ai', '⚡ Génération du code 3D intelligent...');
            
            const response = await fetch('http://localhost:11000/api/generate-model', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    prompt: prompt,
                    type: 'object' // character/object/environment
                })
            });
            
            if (!response.ok) throw new Error(`API erreur: ${response.status}`);
            
            const result = await response.json();
            
            if (result.success && result.model_data && result.model_data.code) {
                const analysis = result.analysis || {};
                addLog(`✅ Analyse Mistral: ${analysis.object_type || 'object'} / ${analysis.style || 'realistic'}`);
                addLog(`✅ Code généré: ${result.model_data.code.length} caractères`);
                
                // Nettoie le code avant exécution
                let cleanCode = result.model_data.code;
                
                // Retire les blocs markdown si présents
                cleanCode = cleanCode.replace(/```javascript\n?/g, '');
                cleanCode = cleanCode.replace(/```js\n?/g, '');
                cleanCode = cleanCode.replace(/```\n?/g, '');
                
                // Retire les lignes qui créent une nouvelle scène (on utilise celle existante)
                cleanCode = cleanCode.split('\n')
                    .filter(line => {
                        const trimmed = line.trim();
                        // Retire les commentaires seuls
                        if (trimmed.startsWith('//')) return false;
                        // Retire les lignes qui créent Scene, Camera, Renderer, Controls
                        if (trimmed.includes('new THREE.Scene()')) return false;
                        if (trimmed.includes('new THREE.PerspectiveCamera')) return false;
                        if (trimmed.includes('new THREE.WebGLRenderer')) return false;
                        if (trimmed.includes('new THREE.OrbitControls')) return false;
                        if (trimmed.includes('renderer.setSize')) return false;
                        if (trimmed.includes('document.body.appendChild')) return false;
                        return trimmed.length === 0 || true;
                    })
                    .join('\n');
                
                // Remplace scene.add par studio.scene.add si oublié
                cleanCode = cleanCode.replace(/\bscene\.add\(/g, 'studio.scene.add(');
                
                // Vérifie que le code contient les éléments essentiels
                if (!cleanCode.includes('THREE.')) {
                    throw new Error('Code généré invalide (pas de Three.js détecté)');
                }
                
                // Exécute le code Three.js généré
                try {
                    addLog('🔧 Exécution du code généré...');
                    eval(cleanCode);
                    addChatMessage('ai', `✅ "${prompt}" créé avec succès!`);
                    addLog('✅ Modèle affiché dans la scène');
                } catch (evalError) {
                    console.error('Erreur exécution code:', evalError);
                    console.error('Code problématique:', cleanCode.substring(0, 500));
                    addLog(`❌ Erreur: ${evalError.message}`);
                    addLog(`🔧 Auto-correction en cours avec Mistral...`);
                    addChatMessage('ai', '🔧 Erreur détectée, correction automatique...');
                    
                    // AUTO-CORRECTION: Demande à Mistral de corriger
                    try {
                        const fixResponse = await fetch('http://localhost:11000/api/fix-code', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                code: cleanCode,
                                error: evalError.message,
                                prompt: prompt
                            })
                        });
                        
                        if (fixResponse.ok) {
                            const fixResult = await fixResponse.json();
                            if (fixResult.success && fixResult.fixed_code) {
                                addLog(`✅ Code corrigé par Mistral`);
                                // Réessaye avec le code corrigé
                                eval(fixResult.fixed_code);
                                addChatMessage('ai', `✅ "${prompt}" créé après correction!`);
                                addLog('✅ Modèle affiché (version corrigée)');
                            } else {
                                throw new Error('Correction impossible');
                            }
                        } else {
                            throw new Error('API correction non disponible');
                        }
                    } catch (fixError) {
                        addLog(`⚠️ Auto-correction échouée: ${fixError.message}`);
                        addChatMessage('ai', '⚠️ Impossible de corriger automatiquement. Reformulez votre demande.');
                    }
                }
            } else {
                const errorMsg = result.error || 'Erreur génération';
                addLog(`❌ ${errorMsg}`);
                addChatMessage('ai', `⚠️ ${errorMsg}`);
            }

        } catch (error) {
            console.error('Erreur génération 3D:', error);
            addLog(`❌ Erreur: ${error.message}`);
            addChatMessage('ai', `❌ Erreur: ${error.message}`);
        }
    }

    // ============================================
    // GÉNÉRATION PROCÉDURALE (conservée pour compatibilité)
    // ============================================
    
    async generateProceduralModel(prompt) {
        try {
            addLog(`🎭 ORCHESTRATION: "${prompt}"`);
            addLog(`📊 Analyse et création du plan...`);
            
            // Phase 1: Obtenir le plan
            const planResponse = await fetch('http://localhost:11000/api/orchestrate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    prompt: prompt,
                    execute: false  // Juste le plan
                })
            });
            
            const planData = await planResponse.json();
            
            if (!planData.understood) {
                addLog(`❌ Prompt non compris`);
                return;
            }
            
            const plan = planData.plan;
            addLog(`✅ Plan créé: ${plan.steps.length} étapes`);
            addLog(`⏱️  Temps estimé: ${plan.estimated_time}s`);
            addLog(`🎯 Complexité: ${plan.complexity}`);
            addLog(``);
            
            // Affiche les étapes
            for (const step of plan.steps) {
                addLog(`   ${step.step}. ${step.tool}: ${step.reason}`);
            }
            
            addLog(``);
            addLog(`⚡ EXÉCUTION EN TEMPS RÉEL...`);
            addLog(`${'='.repeat(50)}`);
            
            // Phase 2: Exécution
            const execResponse = await fetch('http://localhost:11000/api/orchestrate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    prompt: prompt,
                    execute: true  // Exécution réelle
                })
            });
            
            const execData = await execResponse.json();
            
            if (execData.success) {
                // Affiche les logs d'exécution
                if (execData.execution && execData.execution.logs) {
                    for (const log of execData.execution.logs) {
                        addLog(`${log.message}`);
                    }
                }
                
                addLog(`${'='.repeat(50)}`);
                addLog(`🎉 ORCHESTRATION TERMINÉE !`);
                
                // TODO: Charger les modèles générés dans la scène
                this.updateObjectCount();
            } else {
                addLog(`❌ Erreurs lors de l'exécution`);
                if (execData.error) {
                    addLog(`   Error: ${execData.error}`);
                }
            }
            
        } catch (error) {
            addLog(`❌ Erreur orchestration: ${error.message}`);
            console.error('Orchestration error:', error);
        }
    }
    
    async generateProceduralModel(prompt) {
        try {
            addLog(`🎨 Génération procédurale: "${prompt}"`);
            
            const response = await fetch('http://localhost:11000/api/generate-model', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    prompt: prompt,
                    method: 'procedural'
                })
            });
            
            const data = await response.json();
            
            // Le code peut être dans data.code OU data.model_data.code
            let code = data.code || (data.model_data && data.model_data.code);
            
            if (data.success && code) {
                // Exécute le code Three.js généré
                addLog(`✅ Code généré (${code.length} chars)`);
                
                try {
                    // Nettoie le code
                    code = code.trim();
                    // Enlève les commentaires
                    code = code.replace(/\/\/.*$/gm, '');
                    // Enlève les return statements isolés
                    code = code.replace(/\breturn\s+(\w+)\s*;?\s*$/m, '$1;');
                    
                    // Crée un contexte avec les variables Three.js
                    const scene = this.scene;
                    const THREE = window.THREE;
                    
                    // Variables communes que le code peut utiliser
                    let obj, tree, character, env, result;
                    
                    // Exécute le code directement
                    eval(code);
                    
                    // Cherche l'objet créé (par ordre de préférence)
                    const createdObject = obj || tree || character || env || result;
                    
                    // Si un objet a été créé, l'ajoute à la scène
                    if (createdObject && (createdObject.isObject3D || createdObject.isMesh || createdObject.isGroup)) {
                        scene.add(createdObject);
                        this.objects.push(createdObject);
                        addLog(`✅ Objet ajouté à la scène`);
                    } else {
                        addLog(`⚠️ Code exécuté mais aucun objet 3D détecté`);
                    }
                    
                    addLog(`✅ Génération complète`);
                    this.updateObjectCount();
                    
                } catch (execError) {
                    addLog(`❌ Erreur exécution: ${execError.message}`);
                    console.error('Code problématique:', code);
                    console.error('Erreur:', execError);
                    
                    // Fallback: crée un objet simple par défaut
                    addLog(`🔄 Création d'un objet fallback...`);
                    const fallbackObj = this.createFallbackObject(prompt);
                    if (fallbackObj) {
                        scene.add(fallbackObj);
                        this.objects.push(fallbackObj);
                        addLog(`✅ Objet fallback ajouté`);
                        this.updateObjectCount();
                    }
                }
            } else {
                addLog(`⚠️ Génération échouée: ${data.error || 'erreur inconnue'}`);
            }
            
        } catch (error) {
            addLog(`❌ Erreur API: ${error.message}`);
        }
    }
    
    createFallbackObject(prompt) {
        /**
         * Crée un objet 3D simple basé sur le prompt
         * Utilisé quand la génération IA échoue
         */
        const group = new THREE.Group();
        const promptLower = prompt.toLowerCase();
        
        // Détecte le type d'objet demandé
        if (promptLower.includes('tree') || promptLower.includes('arbre')) {
            // Arbre simple
            const trunk = new THREE.Mesh(
                new THREE.CylinderGeometry(0.3, 0.4, 3),
                new THREE.MeshStandardMaterial({ color: 0x8B4513 })
            );
            trunk.position.y = 1.5;
            group.add(trunk);
            
            const leaves = new THREE.Mesh(
                new THREE.SphereGeometry(1.5),
                new THREE.MeshStandardMaterial({ color: 0x228B22 })
            );
            leaves.position.y = 3.5;
            group.add(leaves);
            
        } else if (promptLower.includes('character') || promptLower.includes('personnage')) {
            // Personnage simple
            const body = new THREE.Mesh(
                new THREE.BoxGeometry(0.6, 1.2, 0.3),
                new THREE.MeshStandardMaterial({ color: 0x4488ff })
            );
            body.position.y = 1.2;
            group.add(body);
            
            const head = new THREE.Mesh(
                new THREE.SphereGeometry(0.25),
                new THREE.MeshStandardMaterial({ color: 0xffcc88 })
            );
            head.position.y = 2;
            group.add(head);
            
        } else if (promptLower.includes('field') || promptLower.includes('terrain')) {
            // Terrain simple
            const ground = new THREE.Mesh(
                new THREE.PlaneGeometry(20, 15),
                new THREE.MeshStandardMaterial({ color: 0x228B22 })
            );
            ground.rotation.x = -Math.PI / 2;
            group.add(ground);
            
        } else {
            // Objet générique
            const obj = new THREE.Mesh(
                new THREE.BoxGeometry(1, 1, 1),
                new THREE.MeshStandardMaterial({ color: 0xff5533 })
            );
            obj.position.y = 0.5;
            group.add(obj);
        }
        
        return group;
    }
    
    async generateTexture(style) {
        try {
            addLog(`🎨 Génération texture: style=${style}`);
            
            // Crée une texture procédurale simple
            const canvas = document.createElement('canvas');
            canvas.width = 512;
            canvas.height = 512;
            const ctx = canvas.getContext('2d');
            
            // Couleurs selon le style
            const colors = {
                'wood': ['#8B4513', '#A0522D', '#CD853F'],
                'grass': ['#228B22', '#32CD32', '#90EE90'],
                'metal': ['#C0C0C0', '#A9A9A9', '#808080'],
                'stone': ['#696969', '#778899', '#A9A9A9'],
                'marble': ['#F5F5DC', '#FFFAF0', '#FFF8DC'],
                'default': ['#808080', '#A9A9A9', '#C0C0C0']
            };
            
            const colorSet = colors[style] || colors['default'];
            
            // Pattern aléatoire
            for (let i = 0; i < 100; i++) {
                ctx.fillStyle = colorSet[Math.floor(Math.random() * colorSet.length)];
                ctx.fillRect(
                    Math.random() * 512, Math.random() * 512,
                    Math.random() * 50 + 10, Math.random() * 50 + 10
                );
            }
            
            const texture = new THREE.CanvasTexture(canvas);
            
            // Applique sur le dernier objet
            if (this.objects.length > 0) {
                const lastObj = this.objects[this.objects.length - 1];
                lastObj.traverse(child => {
                    if (child.isMesh) {
                        child.material.map = texture;
                        child.material.needsUpdate = true;
                    }
                });
                addLog(`✅ Texture ${style} appliquée`);
            } else {
                addLog(`⚠️ Aucun objet pour texture`);
            }
        } catch (error) {
            addLog(`❌ Erreur texture: ${error.message}`);
        }
    }
    
    async handleAssetFetch(assetData) {
        addLog(`🎨 Asset récupéré: ${assetData.type || 'modèle 3D'}`);
        
        if (assetData.model_url) {
            await this.loadModelFromURL(assetData.model_url, assetData.model_format || 'glb');
        }
        
        if (assetData.texture_url) {
            await this.applyTextureFromURL(assetData.texture_url);
        }
        
        if (assetData.procedural_data) {
            await this.createProceduralFromData(assetData.procedural_data);
        }
    }
    
    async loadModelFromURL(url, format) {
        try {
            addLog(`📥 Chargement modèle depuis: ${url}`);
            
            let loader;
            if (format === 'glb' || format === 'gltf') {
                loader = new THREE.GLTFLoader();
            } else if (format === 'obj') {
                loader = new THREE.OBJLoader();
            } else {
                addLog(`⚠️ Format non supporté: ${format}`);
                return;
            }
            
            const model = await loader.loadAsync(url);
            const mesh = format === 'gltf' || format === 'glb' ? model.scene : model;
            
            mesh.position.set(
                (Math.random() - 0.5) * 5,
                0,
                (Math.random() - 0.5) * 5
            );
            
            this.scene.add(mesh);
            this.objects.push(mesh);
            this.updateObjectCount();
            
            addLog(`✅ Modèle chargé: ${this.objects.length} objets`);
            
        } catch (error) {
            addLog(`❌ Erreur chargement: ${error.message}`);
        }
    }
    
    async applyTextureFromURL(url) {
        try {
            addLog(`🎨 Application texture: ${url}`);
            
            const textureLoader = new THREE.TextureLoader();
            const texture = await textureLoader.loadAsync(url);
            
            // Applique sur le dernier objet
            if (this.objects.length > 0) {
                const lastObj = this.objects[this.objects.length - 1];
                lastObj.traverse(child => {
                    if (child.isMesh) {
                        child.material.map = texture;
                        child.material.needsUpdate = true;
                    }
                });
                addLog(`✅ Texture appliquée`);
            }
            
        } catch (error) {
            addLog(`❌ Erreur texture: ${error.message}`);
        }
    }
    
    async handleTextureSearch(textureData) {
        addLog(`🎨 Textures trouvées: ${textureData.length || 0}`);
        
        if (textureData && textureData.length > 0) {
            const firstTexture = textureData[0];
            if (firstTexture.url || firstTexture.download_url) {
                await this.applyTextureFromURL(firstTexture.url || firstTexture.download_url);
            }
        }
    }
    
    async executeFrontendAction(action) {
        addLog(`🎬 Action frontend: ${action.type}`);
        
        switch(action.type) {
            case 'generate_procedural':
                // Génération procédurale via API
                await this.generateProceduralModel(action.prompt);
                break;
            
            case 'generate_texture':
                await this.generateTexture(action.style);
                break;
            
            case 'create_object':
                await this.createProceduralFromData(action.params);
                break;
                
            case 'camera_control':
                await this.executeCameraAction(action.params);
                break;
                
            case 'modify_scene':
                await this.modifyScene(action.params);
                break;
                
            default:
                console.log('Action frontend inconnue:', action);
        }
    }
    
    async executeCameraAction(params) {
        if (!this.cameraController) return;
        
        const { action, ...args } = params;
        
        if (this.cameraController[action]) {
            this.cameraController[action](args);
        }
    }

    async executeAICommand(commandType, prompt, analysis) {
        const lastMessage = document.querySelector('.chat-messages .message.ai:last-child');
        const lowerPrompt = prompt.toLowerCase();
        
        console.log('📝 Commande détectée:', commandType);
        console.log('📊 Analyse complète:', analysis);
        addLog(`🎯 Action: ${commandType} - "${prompt}"`);
        
        try {
            // DÉTECTION ACTIONS DESTRUCTIVES/MODIFICATIONS
            if (lowerPrompt.includes('retire') || lowerPrompt.includes('supprime') || 
                lowerPrompt.includes('enlève') || lowerPrompt.includes('efface') ||
                lowerPrompt.includes('remove') || lowerPrompt.includes('delete')) {
                const count = this.extractNumber(lowerPrompt) || 1;
                await this.removeObjects(count);
                lastMessage.innerHTML = `✅ ${count} objet(s) retiré(s) de la scène`;
                this.updateObjectCount();
                return;
            }
            
            if (lowerPrompt.includes('tout supprimer') || lowerPrompt.includes('vide') || 
                lowerPrompt.includes('clear') || lowerPrompt.includes('reset')) {
                await this.clearScene();
                lastMessage.innerHTML = `✅ Scène vidée complètement`;
                this.updateObjectCount();
                return;
            }
            
            // DÉTECTION CONTRÔLE CAMÉRA (prioritaire)
            if (lowerPrompt.includes('caméra') || lowerPrompt.includes('camera') ||
                lowerPrompt.includes('orbite') || lowerPrompt.includes('tourne') ||
                lowerPrompt.includes('zoom') || lowerPrompt.includes('vue') ||
                lowerPrompt.includes('rotation') || lowerPrompt.includes('360')) {
                await this.executeCameraCommand(lowerPrompt, lastMessage);
                return;
            }
            
            // ACTIONS CRÉATIVES (après avoir éliminé les autres cas)
            switch(commandType) {
                case 'character':
                case 'CREATE_CHARACTER':
                    await this.createCharacterFromPrompt(prompt, analysis);
                    lastMessage.innerHTML = `✅ Personnage créé ! (${this.objects.length} objets total)`;
                    break;
                    
                case 'environment':
                case 'CREATE_ENVIRONMENT':
                    await this.createEnvironmentFromPrompt(prompt, analysis);
                    lastMessage.innerHTML = `🌍 Environnement ajouté ! (${this.objects.length} objets)`;
                    break;
                    
                case 'animation':
                case 'CREATE_ANIMATION':
                    this.createAnimationFromPrompt(prompt);
                    lastMessage.innerHTML = `▶️ Animation créée (${this.totalFrames} frames)`;
                    break;
                    
                case 'light':
                case 'ADD_LIGHT':
                    this.addLightFromPrompt(prompt);
                    lastMessage.innerHTML = `💡 Éclairage ajouté !`;
                    break;
                    
                case 'object':
                case 'CREATE_OBJECT':
                    await this.createObjectFromPrompt(prompt, analysis);
                    lastMessage.innerHTML = `📦 Objet ajouté ! (${this.objects.length} total)`;
                    break;
                    
                default:
                    lastMessage.innerHTML = `💡 Commandes: créer objet/personnage, retirer N éléments, caméra orbite/zoom/rotation, vide scène`;
            }
        } catch (error) {
            lastMessage.innerHTML = `❌ Erreur: ${error.message}`;
            console.error(error);
        }
        
        this.updateObjectCount();
    }
    
    extractNumber(text) {
        const match = text.match(/(\d+)/);
        return match ? parseInt(match[1]) : null;
    }
    
    async removeObjects(count) {
        const removed = Math.min(count, this.objects.length);
        for (let i = 0; i < removed; i++) {
            const obj = this.objects.pop();
            if (obj) {
                this.scene.remove(obj);
                if (obj.geometry) obj.geometry.dispose();
                if (obj.material) obj.material.dispose();
            }
        }
        addLog(`🗑️ ${removed} objet(s) retiré(s)`);
    }
    
    async clearScene() {
        while (this.objects.length > 0) {
            const obj = this.objects.pop();
            this.scene.remove(obj);
            if (obj.geometry) obj.geometry.dispose();
            if (obj.material) obj.material.dispose();
        }
        addLog('✅ Scène vidée');
    }
    
    async executeCameraCommand(prompt, messageElement) {
        // Orbite 360°
        if (prompt.includes('orbite') || prompt.includes('360') || prompt.includes('tourne autour')) {
            const duration = this.extractNumber(prompt) || 8;
            cameraOrbit360(duration * 1000, 5, 8);
            messageElement.innerHTML = `🎥 Orbite 360° lancée (${duration}s)`;
            return;
        }
        
        // Rotations
        if (prompt.includes('rotation') || prompt.includes('tourne de')) {
            const degrees = this.extractNumber(prompt) || 90;
            cameraRotate('y', degrees, 1000);
            messageElement.innerHTML = `🎥 Rotation ${degrees}°`;
            return;
        }
        
        // Zoom
        if (prompt.includes('zoom')) {
            const factor = prompt.includes('arrière') || prompt.includes('out') ? 0.5 : 2;
            cameraZoom(factor, 500);
            messageElement.innerHTML = `🔍 Zoom ${factor > 1 ? 'avant' : 'arrière'}`;
            return;
        }
        
        // Déplacements directionnels
        if (prompt.includes('avance') || prompt.includes('forward')) {
            const dist = this.extractNumber(prompt) || 2;
            cameraMove('forward', dist, 1000);
            messageElement.innerHTML = `🎥 Caméra avance ${dist}m`;
            return;
        }
        if (prompt.includes('recule') || prompt.includes('backward')) {
            const dist = this.extractNumber(prompt) || 2;
            cameraMove('backward', dist, 1000);
            messageElement.innerHTML = `🎥 Caméra recule ${dist}m`;
            return;
        }
        if (prompt.includes('gauche') || prompt.includes('left')) {
            const dist = this.extractNumber(prompt) || 2;
            cameraMove('left', dist, 1000);
            messageElement.innerHTML = `🎥 Caméra → gauche ${dist}m`;
            return;
        }
        if (prompt.includes('droite') || prompt.includes('right')) {
            const dist = this.extractNumber(prompt) || 2;
            cameraMove('right', dist, 1000);
            messageElement.innerHTML = `🎥 Caméra → droite ${dist}m`;
            return;
        }
        if (prompt.includes('monte') || prompt.includes('haut') || prompt.includes('up')) {
            const dist = this.extractNumber(prompt) || 2;
            cameraMove('up', dist, 1000);
            messageElement.innerHTML = `🎥 Caméra monte ${dist}m`;
            return;
        }
        if (prompt.includes('descend') || prompt.includes('bas') || prompt.includes('down')) {
            const dist = this.extractNumber(prompt) || 2;
            cameraMove('down', dist, 1000);
            messageElement.innerHTML = `🎥 Caméra descend ${dist}m`;
            return;
        }
        
        // Vues prédéfinies
        if (prompt.includes('vue de face') || prompt.includes('front')) {
            cameraPreset('front');
            messageElement.innerHTML = `📷 Vue de face`;
            return;
        }
        if (prompt.includes('vue isométrique') || prompt.includes('iso')) {
            cameraPreset('iso');
            messageElement.innerHTML = `📷 Vue isométrique`;
            return;
        }
        if (prompt.includes('vue de haut') || prompt.includes('top')) {
            cameraPreset('top');
            messageElement.innerHTML = `📷 Vue de haut`;
            return;
        }
        
        // Shake
        if (prompt.includes('shake') || prompt.includes('tremblement')) {
            cameraShake(0.3, 500);
            messageElement.innerHTML = `💥 Camera shake !`;
            return;
        }
        
        messageElement.innerHTML = `🎥 Commande caméra: ${prompt}`;
    }

    async createCharacterFromPrompt(prompt, analysis) {
        // Essaie de générer avec l'API Meshy
        try {
            const response = await fetch('http://localhost:11003/api/text-to-3d-meshy', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    prompt: prompt,
                    art_style: 'realistic',
                    negative_prompt: 'low quality'
                })
            });

            const data = await response.json();

            if (data.success && data.model_path) {
                // Charge le modèle généré
                const loader = new THREE.OBJLoader();
                const model = await loader.loadAsync(data.model_path);
                model.position.set(
                    (Math.random() - 0.5) * 5,
                    0,
                    (Math.random() - 0.5) * 5
                );
                model.userData = { type: 'character', prompt, from_api: true };
                this.scene.add(model);
                this.objects.push(model);
            } else {
                // Fallback sur génération locale
                this.createCharacterLocal(prompt);
            }
        } catch (error) {
            console.error('API error:', error);
            this.createCharacterLocal(prompt);
        }
        
        this.addToTimeline('character', this.currentFrame);
    }

    createCharacterLocal(prompt) {
        // Crée un personnage basique (cube coloré pour l'instant)
        addLog('🎨 Création personnage procédural local');
        const geometry = new THREE.BoxGeometry(1, 2, 1);
        const material = new THREE.MeshStandardMaterial({ 
            color: Math.random() * 0xffffff,
            roughness: 0.5,
            metalness: 0.2
        });
        const character = new THREE.Mesh(geometry, material);
        character.position.set(
            (Math.random() - 0.5) * 5,
            1,
            (Math.random() - 0.5) * 5
        );
        character.castShadow = true;
        character.userData = { type: 'character', prompt };
        
        this.scene.add(character);
        this.objects.push(character);
        addLog(`✅ Personnage créé à la position (${character.position.x.toFixed(1)}, ${character.position.y.toFixed(1)}, ${character.position.z.toFixed(1)})`);
    }

    createEnvironmentFromPrompt(prompt) {
        // Crée un sol
        addLog('🌍 Génération environnement');
        const groundGeometry = new THREE.PlaneGeometry(20, 20);
        const groundMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x2d4059,
            roughness: 0.8
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        ground.userData = { type: 'environment', prompt };
        
        this.scene.add(ground);
        this.objects.push(ground);
        
        // Ajoute quelques éléments aléatoires
        let elementCount = 0;
        for (let i = 0; i < 5; i++) {
            const size = 0.5 + Math.random();
            const cubeGeometry = new THREE.BoxGeometry(size, size * 2, size);
            const cubeMaterial = new THREE.MeshStandardMaterial({ 
                color: 0x3d5a80
            });
            const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
            cube.position.set(
                (Math.random() - 0.5) * 15,
                size,
                (Math.random() - 0.5) * 15
            );
            cube.castShadow = true;
            this.scene.add(cube);
            this.objects.push(cube);
            elementCount++;
        }
        
        addLog(`✅ Environnement créé avec ${elementCount} éléments`);
        this.addToTimeline('environment', 0);
    }

    controlCameraFromPrompt(prompt) {
        addLog('🎥 Contrôle caméra');
        if (prompt.includes('orbite') || prompt.includes('orbit')) {
            // Vue orbite
            this.camera.position.set(10, 10, 10);
            addLog('📹 Caméra: Vue orbite');
        } else if (prompt.includes('haut') || prompt.includes('top')) {
            // Vue du dessus
            this.camera.position.set(0, 20, 0);
            addLog('📹 Caméra: Vue du dessus');
        } else if (prompt.includes('face') || prompt.includes('front')) {
            // Vue de face
            this.camera.position.set(0, 5, 15);
            addLog('📹 Caméra: Vue de face');
        } else {
            // Vue cinématique
            this.camera.position.set(8, 6, 12);
            addLog('📹 Caméra: Vue cinématique');
        }
        this.camera.lookAt(0, 0, 0);
        
        this.addToTimeline('camera', this.currentFrame);
    }

    createAnimationFromPrompt(prompt) {
        addLog('▶️ Génération animation');
        // Crée une animation simple pour tous les personnages
        let animatedCount = 0;
        this.objects.forEach(obj => {
            if (obj.userData.type === 'character') {
                // Animation de rotation
                animatedCount++;
                obj.userData.animation = {
                    type: 'rotation',
                    startFrame: this.currentFrame,
                    duration: 60
                };
            }
        });
        
        addLog(`✅ Animation créée pour ${animatedCount} objets`);
        this.addToTimeline('animation', this.currentFrame);
    }

    addLightFromPrompt(prompt) {
        addLog('💡 Ajout lumière');
        let light;
        
        if (prompt.includes('point')) {
            light = new THREE.PointLight(0xffffff, 1, 100);
            light.position.set(5, 5, 5);
            addLog('💡 Type: Point Light');
        } else if (prompt.includes('spot')) {
            light = new THREE.SpotLight(0xffffff, 1);
            light.position.set(0, 10, 0);
            addLog('💡 Type: Spot Light');
        } else {
            light = new THREE.DirectionalLight(0xffffff, 0.5);
            light.position.set(-5, 10, 5);
            addLog('💡 Type: Directional Light');
        }
        
        light.userData = { type: 'light', prompt };
        this.scene.add(light);
        this.objects.push(light);
    }

    createObjectFromPrompt(prompt) {
        let geometry;
        
        if (prompt.includes('sphère') || prompt.includes('sphere')) {
            geometry = new THREE.SphereGeometry(1, 32, 32);
        } else if (prompt.includes('cylindre') || prompt.includes('cylinder')) {
            geometry = new THREE.CylinderGeometry(0.5, 0.5, 2, 32);
        } else {
            geometry = new THREE.BoxGeometry(1, 1, 1);
        }
        
        const material = new THREE.MeshStandardMaterial({ 
            color: Math.random() * 0xffffff
        });
        const object = new THREE.Mesh(geometry, material);
        object.position.set(
            (Math.random() - 0.5) * 5,
            1,
            (Math.random() - 0.5) * 5
        );
        object.castShadow = true;
        object.userData = { type: 'object', prompt };
        
        this.scene.add(object);
        this.objects.push(object);
    }

    async loadGLTFModel(url, toolName) {
        /**
         * Charge un modèle GLTF depuis le Blender Backend
         */
        return new Promise((resolve, reject) => {
            const loader = new THREE.GLTFLoader();
            
            // URL complète vers le backend Blender
            const fullUrl = `http://localhost:11004${url}`;
            
            loader.load(
                fullUrl,
                (gltf) => {
                    const model = gltf.scene;
                    model.userData = { 
                        type: 'gltf', 
                        tool: toolName,
                        animations: gltf.animations 
                    };
                    
                    // Centre le modèle
                    const box = new THREE.Box3().setFromObject(model);
                    const center = box.getCenter(new THREE.Vector3());
                    model.position.sub(center);
                    
                    this.scene.add(model);
                    this.objects.push(model);
                    resolve(model);
                },
                (progress) => {
                    // Progress callback
                    console.log('Loading:', (progress.loaded / progress.total * 100) + '%');
                },
                (error) => {
                    console.error('Error loading GLTF:', error);
                    reject(error);
                }
            );
        });
    }

    addToTimeline(trackName, frame) {
        const trackId = `track-${trackName}`;
        const track = document.getElementById(trackId);
        
        if (track) {
            const keyframe = document.createElement('div');
            keyframe.className = 'keyframe';
            keyframe.style.left = ((frame / this.totalFrames) * 100) + '%';
            track.appendChild(keyframe);
        }
    }

    updateObjectCount() {
        document.getElementById('object-count').textContent = this.objects.length;
    }

    togglePlayback() {
        this.isPlaying = !this.isPlaying;
        const playBtn = document.querySelector('.play-btn');
        playBtn.textContent = this.isPlaying ? '⏸️' : '▶️';
    }

    setView(view) {
        switch(view) {
            case 'front':
                this.camera.position.set(0, 5, 15);
                break;
            case 'side':
                this.camera.position.set(15, 5, 0);
                break;
            case 'top':
                this.camera.position.set(0, 20, 0);
                break;
        }
        this.camera.lookAt(0, 0, 0);
    }

    resetView() {
        this.camera.position.set(5, 5, 5);
        this.camera.lookAt(0, 0, 0);
    }
}

// UI Functions
function addChatMessage(type, message) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const now = new Date();
    const time = now.getHours() + ':' + String(now.getMinutes()).padStart(2, '0');
    
    messageDiv.innerHTML = `
        <div>${message}</div>
        <div class="message-time">${time}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function handleChatInput(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (message) {
            studio.processAICommand(message);
            input.value = '';
        }
    }
}

function quickPrompt(prompt) {
    const input = document.getElementById('chat-input');
    input.value = prompt;
    input.focus();
}

function aiPrompt(defaultText) {
    const input = document.getElementById('chat-input');
    input.value = defaultText;
    input.focus();
}

// 📸 PHOTOGRAMMETRIE - Nouvelles fonctions
async function launchDemo() {
    addLog('🎬 Lancement démo Château...');
    try {
        const response = await fetch('http://localhost:11000/api/launch-demo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ num_photos: 11 })  // Utilise les 11 photos
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.code) {
            addLog(`✅ ${data.message}`);
            addLog(`📊 ${data.stats.photos} photos → ${data.stats.vertices} vertices`);
            
            // Exécute le code Three.js retourné
            eval(data.code);
        } else {
            addLog(`❌ Erreur: ${data.error || 'Échec reconstruction'}`);
        }
    } catch (error) {
        addLog(`❌ Erreur démo: ${error.message}`);
        console.error('Erreur launchDemo:', error);
    }
}

function uploadPhotos() {
    // Crée un input file invisible
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/jpeg,image/png,image/jpg';
    input.multiple = true;
    
    input.onchange = async (e) => {
        const files = Array.from(e.target.files);
        if (files.length === 0) return;
        
        addLog(`📤 Upload ${files.length} photos...`);
        
        const formData = new FormData();
        files.forEach((file) => {
            formData.append('photos', file);
        });
        
        try {
            addLog('🔮 Reconstruction en cours...');
            
            const response = await fetch('http://localhost:11000/api/upload-reconstruct', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.code) {
                addLog(`✅ ${data.message}`);
                addLog(`📊 ${data.stats.photos} photos → ${data.stats.vertices} vertices`);
                eval(data.code);
            } else {
                addLog(`❌ Erreur: ${data.error}`);
            }
        } catch (error) {
            addLog(`❌ Erreur upload: ${error.message}`);
            console.error('Erreur uploadPhotos:', error);
        }
    };
    
    input.click();
}

function loadObjFile() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.obj';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        addLog(`📂 Chargement ${file.name}...`);
        
        const reader = new FileReader();
        reader.onload = (evt) => {
            const objData = evt.target.result;
            
            // Parse OBJ avec THREE.OBJLoader
            const loader = new THREE.OBJLoader();
            const obj = loader.parse(objData);
            
            // Centre et scale
            const box = new THREE.Box3().setFromObject(obj);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            const scale = 5 / maxDim;
            
            obj.position.sub(center);
            obj.scale.set(scale, scale, scale);
            
            // Matériau
            obj.traverse((child) => {
                if (child.isMesh) {
                    child.material = new THREE.MeshStandardMaterial({
                        color: 0xAAAAAA,
                        roughness: 0.7,
                        metalness: 0.2
                    });
                    child.castShadow = true;
                    child.receiveShadow = true;
                }
            });
            
            studio.scene.add(obj);
            addLog(`✅ ${file.name} chargé`);
        };
        
        reader.readAsText(file);
    };
    
    input.click();
}

function togglePlayback() {
    studio.togglePlayback();
}

function seekTimeline(event) {
    const slider = event.currentTarget;
    const rect = slider.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const percentage = x / rect.width;
    studio.currentFrame = Math.floor(percentage * studio.totalFrames);
    studio.updateFrame();
}

function setView(view) {
    studio.setView(view);
}

function resetView() {
    studio.resetView();
}

function saveProject() {
    const project = {
        objects: studio.objects.map(obj => ({
            type: obj.userData.type,
            prompt: obj.userData.prompt,
            position: obj.position,
            rotation: obj.rotation,
            scale: obj.scale
        })),
        camera: {
            position: studio.camera.position,
            rotation: studio.camera.rotation
        },
        currentFrame: studio.currentFrame
    };
    
    const json = JSON.stringify(project, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'kibalone-project.json';
    a.click();
    
    addChatMessage('ai', '💾 Projet sauvegardé !');
}

function exportScene() {
    addChatMessage('ai', '📤 Export en cours... Format OBJ généré !');
    // TODO: Implémenter export réel
}

function renderVideo() {
    addChatMessage('ai', '🎬 Rendu vidéo démarré ! Cela peut prendre quelques minutes...');
    // TODO: Implémenter rendu vidéo
}

function toggleAxisWidget() {
    if (studio && studio.axisWidget) {
        studio.axisWidget.toggleVisibility();
        const visible = studio.axisWidget.container.style.display !== 'none';
        addLog(`📐 Widget d'axes ${visible ? 'affiché' : 'masqué'}`);
        return visible;
    }
    return false;
}

// ============================================
// SYSTÈME DE CAMÉRA AVANCÉ - KIBALI EXPERT
// ============================================

function cameraOrbit360(duration = 8000, height = 5, radius = 8) {
    // Rotation complète 360° autour de la scène
    const startTime = Date.now();
    const startPos = { 
        x: studio.camera.position.x, 
        y: studio.camera.position.y, 
        z: studio.camera.position.z 
    };
    
    studio.isAnimatingCamera = true;
    
    function animate() {
        if (!studio.isAnimatingCamera) return;
        
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const angle = progress * Math.PI * 2; // 360 degrés
        
        studio.camera.position.x = Math.cos(angle) * radius;
        studio.camera.position.y = height;
        studio.camera.position.z = Math.sin(angle) * radius;
        studio.camera.lookAt(studio.cameraTarget.x, studio.cameraTarget.y, studio.cameraTarget.z);
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            studio.isAnimatingCamera = false;
            addLog('🎥 Orbite 360° terminée');
        }
    }
    
    addLog(`🎥 Orbite 360° démarrée (${duration/1000}s)`);
    animate();
}

function cameraMove(direction, distance = 2, duration = 1000) {
    // Déplace la caméra: 'forward', 'backward', 'left', 'right', 'up', 'down'
    const startPos = { 
        x: studio.camera.position.x, 
        y: studio.camera.position.y, 
        z: studio.camera.position.z 
    };
    
    let targetPos = { ...startPos };
    
    switch(direction.toLowerCase()) {
        case 'forward':
        case 'avant':
            targetPos.z -= distance;
            break;
        case 'backward':
        case 'arriere':
        case 'recule':
            targetPos.z += distance;
            break;
        case 'left':
        case 'gauche':
            targetPos.x -= distance;
            break;
        case 'right':
        case 'droite':
            targetPos.x += distance;
            break;
        case 'up':
        case 'haut':
        case 'monte':
            targetPos.y += distance;
            break;
        case 'down':
        case 'bas':
        case 'descend':
            targetPos.y -= distance;
            break;
    }
    
    animateCameraToPosition(targetPos, duration);
    addLog(`🎥 Caméra → ${direction} (${distance}m)`);
}

function cameraRotate(axis, degrees, duration = 1000) {
    // Rotation autour d'un axe: 'x', 'y', 'z'
    const startTime = Date.now();
    const startPos = { 
        x: studio.camera.position.x, 
        y: studio.camera.position.y, 
        z: studio.camera.position.z 
    };
    const radius = Math.sqrt(startPos.x**2 + startPos.z**2);
    const startAngle = Math.atan2(startPos.z, startPos.x);
    const targetAngle = startAngle + (degrees * Math.PI / 180);
    
    studio.isAnimatingCamera = true;
    
    function animate() {
        if (!studio.isAnimatingCamera) return;
        
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = easeInOutCubic(progress);
        const currentAngle = startAngle + (targetAngle - startAngle) * eased;
        
        if (axis.toLowerCase() === 'y') {
            studio.camera.position.x = Math.cos(currentAngle) * radius;
            studio.camera.position.z = Math.sin(currentAngle) * radius;
        }
        
        studio.camera.lookAt(studio.cameraTarget.x, studio.cameraTarget.y, studio.cameraTarget.z);
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            studio.isAnimatingCamera = false;
            addLog(`🎥 Rotation ${degrees}° terminée`);
        }
    }
    
    addLog(`🎥 Rotation ${axis.toUpperCase()} ${degrees}°`);
    animate();
}

function cameraFlyTo(x, y, z, duration = 2000) {
    // Vol cinématique vers une position
    animateCameraToPosition({ x, y, z }, duration);
    addLog(`🎥 Vol vers (${x}, ${y}, ${z})`);
}

function cameraLookAt(x, y, z) {
    // Change le point de focus de la caméra
    studio.cameraTarget = { x, y, z };
    studio.camera.lookAt(x, y, z);
    addLog(`👁️ Focus sur (${x}, ${y}, ${z})`);
}

function cameraZoom(factor, duration = 500) {
    // Zoom in/out (factor > 1 = zoom in, factor < 1 = zoom out)
    const currentDistance = Math.sqrt(
        studio.camera.position.x**2 + 
        studio.camera.position.y**2 + 
        studio.camera.position.z**2
    );
    const targetDistance = currentDistance / factor;
    const ratio = targetDistance / currentDistance;
    
    const targetPos = {
        x: studio.camera.position.x * ratio,
        y: studio.camera.position.y * ratio,
        z: studio.camera.position.z * ratio
    };
    
    animateCameraToPosition(targetPos, duration);
    addLog(`🔍 Zoom ${factor > 1 ? 'in' : 'out'} (×${factor.toFixed(1)})`);
}

function cameraPan(horizontal, vertical, duration = 1000) {
    // Pan horizontal/vertical
    const right = new THREE.Vector3();
    const up = new THREE.Vector3(0, 1, 0);
    studio.camera.getWorldDirection(new THREE.Vector3());
    right.crossVectors(studio.camera.up, studio.camera.getWorldDirection(new THREE.Vector3())).normalize();
    
    const targetPos = {
        x: studio.camera.position.x + right.x * horizontal + up.x * vertical,
        y: studio.camera.position.y + right.y * horizontal + up.y * vertical,
        z: studio.camera.position.z + right.z * horizontal + up.z * vertical
    };
    
    const targetLookAt = {
        x: studio.cameraTarget.x + right.x * horizontal + up.x * vertical,
        y: studio.cameraTarget.y + right.y * horizontal + up.y * vertical,
        z: studio.cameraTarget.z + right.z * horizontal + up.z * vertical
    };
    
    studio.cameraTarget = targetLookAt;
    animateCameraToPosition(targetPos, duration);
    addLog(`↔️ Pan (${horizontal}, ${vertical})`);
}

function cameraShake(intensity = 0.3, duration = 500) {
    // Effet shake (explosion, impact)
    const startTime = Date.now();
    const originalPos = { 
        x: studio.camera.position.x, 
        y: studio.camera.position.y, 
        z: studio.camera.position.z 
    };
    
    studio.isAnimatingCamera = true;
    
    function animate() {
        if (!studio.isAnimatingCamera) return;
        
        const elapsed = Date.now() - startTime;
        const progress = elapsed / duration;
        
        if (progress < 1) {
            const decay = 1 - progress;
            studio.camera.position.x = originalPos.x + (Math.random() - 0.5) * intensity * decay;
            studio.camera.position.y = originalPos.y + (Math.random() - 0.5) * intensity * decay;
            studio.camera.position.z = originalPos.z + (Math.random() - 0.5) * intensity * decay;
            requestAnimationFrame(animate);
        } else {
            studio.camera.position.set(originalPos.x, originalPos.y, originalPos.z);
            studio.isAnimatingCamera = false;
            addLog('💥 Shake terminé');
        }
    }
    
    addLog('💥 Camera shake!');
    animate();
}

function cameraPreset(preset) {
    // Positions prédéfinies: 'front', 'back', 'left', 'right', 'top', 'bottom', 'iso'
    const presets = {
        'front': { x: 0, y: 5, z: 10 },
        'back': { x: 0, y: 5, z: -10 },
        'left': { x: -10, y: 5, z: 0 },
        'right': { x: 10, y: 5, z: 0 },
        'top': { x: 0, y: 15, z: 0 },
        'bottom': { x: 0, y: -15, z: 0 },
        'iso': { x: 7, y: 7, z: 7 },
        'isometric': { x: 7, y: 7, z: 7 },
        'perspective': { x: 5, y: 5, z: 10 }
    };
    
    const pos = presets[preset.toLowerCase()];
    if (pos) {
        cameraFlyTo(pos.x, pos.y, pos.z, 1500);
        addLog(`📷 Vue ${preset}`);
    }
}

function cameraStop() {
    // Arrête toute animation de caméra
    studio.isAnimatingCamera = false;
    addLog('⏹️ Animation caméra arrêtée');
}

function animateCameraToPosition(targetPos, duration) {
    // Animation fluide avec easing
    const startTime = Date.now();
    const startPos = { 
        x: studio.camera.position.x, 
        y: studio.camera.position.y, 
        z: studio.camera.position.z 
    };
    
    studio.isAnimatingCamera = true;
    
    function animate() {
        if (!studio.isAnimatingCamera) return;
        
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = easeInOutCubic(progress);
        
        studio.camera.position.x = startPos.x + (targetPos.x - startPos.x) * eased;
        studio.camera.position.y = startPos.y + (targetPos.y - startPos.y) * eased;
        studio.camera.position.z = startPos.z + (targetPos.z - startPos.z) * eased;
        
        studio.camera.lookAt(studio.cameraTarget.x, studio.cameraTarget.y, studio.cameraTarget.z);
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            studio.isAnimatingCamera = false;
        }
    }
    
    animate();
}

function easeInOutCubic(t) {
    // Fonction d'easing pour animations fluides
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function addLog(message) {
    const logsContainer = document.getElementById('console-logs');
    if (!logsContainer) return;
    
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.style.marginBottom = '2px';
    logEntry.innerHTML = `<span style="color: #666;">[${timestamp}]</span> ${message}`;
    
    logsContainer.appendChild(logEntry);
    logsContainer.scrollTop = logsContainer.scrollHeight;
    
    // Limiter à 100 logs
    while (logsContainer.children.length > 100) {
        logsContainer.removeChild(logsContainer.firstChild);
    }
}

function clearLogs() {
    const logsContainer = document.getElementById('console-logs');
    if (logsContainer) {
        logsContainer.innerHTML = '';
        addLog('🗑️ Logs cleared');
    }
}

// === TUTORIEL ===
async function showTutorial() {
    addLog('📖 Ouverture du tutoriel...');
    const modal = document.getElementById('tutorial-modal');
    const content = document.getElementById('tutorial-content');
    
    if (modal && content) {
        // Affiche la modal
        modal.style.display = 'block';
        
        // Charge le tutoriel
        try {
            const response = await fetch('/TUTORIAL_COMPLET.md');
            if (response.ok) {
                const markdown = await response.text();
                // Convertit Markdown en HTML (utilise marked.js)
                if (typeof marked !== 'undefined') {
                    content.innerHTML = marked.parse(markdown);
                } else {
                    // Fallback: affiche brut avec <pre>
                    content.innerHTML = `<pre style="white-space: pre-wrap; font-size: 14px;">${markdown}</pre>`;
                }
                addLog('✅ Tutoriel chargé');
            } else {
                content.innerHTML = `
                    <h2 style="color: #f5576c;">❌ Tutoriel non disponible</h2>
                    <p>Le fichier TUTORIAL_COMPLET.md n'est pas accessible.</p>
                    <p>Chemin: <code>/home/belikan/Isol/Meshy/TUTORIAL_COMPLET.md</code></p>
                    <h3>📋 Aide Rapide - 33 Outils Disponibles:</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li>🎨 <strong>Génération (5):</strong> MeshyGenerate, ProceduralGenerate, AdvancedGenerate, RealisticGenerate, TextureGenerate</li>
                        <li>🔬 <strong>Reconstruction (4):</strong> MiDaSCreateSession, MiDaSUploadImage, MiDaSGenerateMesh, TripoSRImageTo3D</li>
                        <li>🎬 <strong>Animation (4):</strong> GenerateAnimation, CameraAnimation, KeyframesCreate, OrganicMovement</li>
                        <li>🔧 <strong>Modification (6):</strong> RepairMesh, OptimizeMesh, SubdivideMesh, TransformMesh, MergeMeshes, BooleanOperation</li>
                        <li>📐 <strong>Mesures (5):</strong> MeasureDistance, MeasureVolume, CalculateBounds, DetectCollisions, AnalyzeScene</li>
                        <li>🏗️ <strong>Impression 3D (4):</strong> SliceMesh, GenerateSupports, OrientForPrint, CheckPrintability</li>
                        <li>💾 <strong>Import/Export (5):</strong> ExportGLTF, ExportOBJ, ExportSTL, ExportFBX, ImportMesh</li>
                    </ul>
                    <h3>💡 Exemples de Commandes:</h3>
                    <pre style="background: rgba(0,0,0,0.5); padding: 15px; border-radius: 5px;">
"Crée un personnage héroïque"
"Génère un cube rouge de 2 mètres"
"Répare ce mesh qui a des trous"
"Anime cet objet qui tourne"
"Calcule le volume de cet objet"
"Exporte en STL pour impression"
"Que peux-tu faire?"</pre>
                `;
            }
        } catch (error) {
            content.innerHTML = `<p style="color: #f5576c;">Erreur: ${error.message}</p>`;
            addLog(`❌ Erreur tutoriel: ${error.message}`);
        }
    }
}

function closeTutorial() {
    const modal = document.getElementById('tutorial-modal');
    if (modal) {
        modal.style.display = 'none';
        addLog('📖 Tutoriel fermé');
    }
}

// Ferme la modal en cliquant en dehors
document.addEventListener('click', (e) => {
    const modal = document.getElementById('tutorial-modal');
    if (modal && e.target === modal) {
        closeTutorial();
    }
});

// Initialize
let studio;
window.addEventListener('DOMContentLoaded', () => {
    studio = new KibaloneStudio();
    
    // Rend studio accessible globalement pour le code généré
    window.studio = studio;
    
    // Message de bienvenue simple
    setTimeout(() => {
        addChatMessage('ai', '👋 Bienvenue ! Tapez une demande pour créer des objets 3D (ex: "forêt", "robot", "château")');
    }, 2000);
});
