// --- Detect Electron ---
const isElectron = navigator.userAgent.toLowerCase().includes('electron');

// --- Scene, Camera, Renderer Setup ---
const scene = new THREE.Scene();
let camera;

const renderer = new THREE.WebGLRenderer({ alpha: true }); // Transparent background
if (isElectron) {
    camera = new THREE.PerspectiveCamera(60, 300 / 400, 0.1, 1000); // 60° FOV, aspect ratio 300/400
    renderer.setSize(300, 400); // Fixed size for Electron window

    // Position camera to focus on head + shoulders
    camera.position.set(0, 1.5, 0.5); // X=0, Y=1.5, Z=0.5 (in front of model)
} else {
    camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    renderer.setSize(window.innerWidth, window.innerHeight); // Full window size for browser

    camera.position.set(0, 1.4, 0.7);
}
document.body.appendChild(renderer.domElement);

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// --- Lighting ---
const light = new THREE.DirectionalLight(0xffffff, 0.8); // White directional light
light.position.set(0, 2, 5); // Slightly above and in front
scene.add(light);

// --- VRM Loading ---
const loader = new THREE.GLTFLoader();

// --- Clock for Animation Timing ---
const clock = new THREE.Clock();

// Add VRM support to GLTFLoader
loader.register((parser) => new THREE.VRMLoaderPlugin(parser));

let currentVrm = null;

loader.load(
    './models/kira.vrm',
    (gltf) => {
        const vrm = gltf.userData.vrm;
        currentVrm = vrm;
        scene.add(vrm.scene);

        if (vrm.expressionManager) {
            console.log('Available expressions:', vrm.expressionManager.expressions.map(e => e));
            // Log current expression values
            vrm.expressionManager.expressions.forEach(exp => {
                console.log(`Initial ${exp.expressionName}: ${vrm.expressionManager.getValue(exp.expressionName)}`);
            });
        } else {
            console.error('ExpressionManager not initialized!');
        }

        console.log('VRM loaded:', vrm);
    },
    (progress) => console.log('Loading model...', 100.0 * (progress.loaded / progress.total), '%'),
    (error) => console.error('Error loading VRM:', error)
);


// --- WebSocket Client with Reconnect Logic ---
let ws = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const maxReconnectDelay = 30000; // 30 seconds

let isSpeaking = false;

function connectWebSocket() {
    ws = new WebSocket('ws://localhost:8765');
    
    ws.onopen = () => {
        console.log('Connected to Python WebSocket');
        reconnectAttempts = 0; // Reset attempts on successful connection
    };

    ws.onmessage = (event) => {
        if (!currentVrm || !currentVrm.expressionManager) {
            console.warn('VRM or expressionManager not ready');
            return;
        }
        const data = JSON.parse(event.data);
     
        // Handle emotions (blendshapes/expressions)
        if (data.type === 'emotion') {
            console.log(`Handling emotion: ${data.emotion} with value ${data.value}`);

            // Reset all expressions first
            currentVrm.expressionManager.expressions.forEach(exp => {
                currentVrm.expressionManager.setValue(exp.expressionName, 0);
            });

            // Set only the requested expression
            if (currentVrm.expressionManager.getExpression(data.emotion)) {
                currentVrm.expressionManager.setValue(data.emotion, data.value);
                console.log(
                    `Set ${data.emotion} to ${data.value}, current value: ${currentVrm.expressionManager.getValue(data.emotion)}`
                );
            } else {
                console.warn(`Expression '${data.emotion}' not found in VRM model`);
            }

            currentVrm.update(0);
        }

        
        // Handle bone movements (rotation or position)
        else if (data.type === 'bone') {
            const bone = currentVrm.humanoid.getRawBoneNode(data.boneName);
            if (bone) {
                if (data.rotation) {
                    bone.rotation.x = data.rotation.x || bone.rotation.x;
                    bone.rotation.y = data.rotation.y || bone.rotation.y;
                    bone.rotation.z = data.rotation.z || bone.rotation.z;
                }
                if (data.position) {
                    bone.position.x = data.position.x || bone.position.x;
                    bone.position.y = data.position.y || bone.position.y;
                    bone.position.z = data.position.z || bone.position.z;
                }
            }
        }

        else if (data.type === 'talk') {
            if (data.action === 'start') {
                console.log('Starting to speak');
                isSpeaking = true;
            } else if (data.action === 'stop') {
                console.log('Stopped speaking');
                isSpeaking = false;
            }
        }

        // Handle VRMA animations
        else if (data.type === 'animation') {
            if (data.action === 'play') {
                loader.load(data.url, (gltf) => {
                    const vrmAnimation = gltf.userData.vrmAnimations[0];
                    if (vrmAnimation) {
                        currentAnimation = vrmAnimation;
                        animationAction = currentVrm.loadAnimation(currentAnimation);
                        animationAction.play();
                        console.log('Playing VRMA:', data.url);
                    }
                }, undefined, (error) => console.error('Error loading VRMA:', error));
            } else if (data.action === 'stop' && animationAction) {
                animationAction.stop();
                currentAnimation = null;
                animationAction = null;
                console.log('Stopped VRMA animation');
            }
        }

        else if (data.type === 'message') {
            console.log('Message from server:', data.content);
        }
        else { 
            console.warn('Unknown message type:', data);
        }
    };

    ws.onclose = (event) => {
        console.log(`WebSocket closed (code: ${event.code}). Reconnecting...`);
        if (reconnectAttempts < maxReconnectAttempts) {
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), maxReconnectDelay);
            reconnectAttempts++;
            setTimeout(connectWebSocket, delay);
        } else {
            console.error('Max reconnect attempts reached. Please check the server.');
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws.close(); // Trigger onclose to handle reconnect
    };
}

// Initial connection attempt
connectWebSocket();

// --- Blink state ---
let blinkState = {
    isBlinking: false,
    blinkProgress: 0,
    nextBlinkTime: 0,
    blinkCount: 0,
    blinksLeft: 0
};

let currentVisemeIndex = 0;
let visemeChangeTime = 0;


// --- Animation Loop ---
function animate() {
    requestAnimationFrame(animate);
    const delta = clock.getDelta();
    const elapsedTime = clock.getElapsedTime();

    if (currentVrm) {
        currentVrm.update(delta);

        // --- Arm Pose ---
        let rightUpperArm = currentVrm.humanoid.getRawBoneNode('rightUpperArm');
        let rightLowerArm = currentVrm.humanoid.getRawBoneNode('rightLowerArm');
        if (rightUpperArm) rightUpperArm.rotation.z = Math.PI / 3 + 0.05 * Math.sin(elapsedTime * 0.8); // Dynamic shoulder movement
        if (rightLowerArm) rightLowerArm.rotation.z = Math.PI / 7 + 0.03 * Math.cos(elapsedTime * 0.9); // Subtle elbow movement

        let leftUpperArm = currentVrm.humanoid.getRawBoneNode('leftUpperArm');
        let leftLowerArm = currentVrm.humanoid.getRawBoneNode('leftLowerArm');
        if (leftUpperArm) leftUpperArm.rotation.z = -Math.PI / 3 - 0.05 * Math.sin(elapsedTime * 0.8); // Mirror right arm
        if (leftLowerArm) leftLowerArm.rotation.z = -Math.PI / 7 - 0.03 * Math.cos(elapsedTime * 0.9); // Mirror right arm


        // --- Breathing ---
        let chest = currentVrm.humanoid.getRawBoneNode('chest');
        if (chest) {
            const breatheScale = 1 + 0.01 * Math.sin(elapsedTime * 1.5);
            chest.scale.set(1, breatheScale, 1);

            // Add subtle chest rotation, more pronounced when speaking
            const chestRotationIntensity = isSpeaking ? 0.1 : 0.05; // Stronger when speaking
            chest.rotation.y = chestRotationIntensity * Math.sin(elapsedTime * 0.6); // Side-to-side sway
            chest.rotation.x = chestRotationIntensity * 0.3 * Math.cos(elapsedTime * 0.7); // Forward-back tilt
        }

        // --- Spine Movement for Idle Realism ---
        let spine = currentVrm.humanoid.getRawBoneNode('spine');
        if (spine) {
            const spineRotationIntensity = isSpeaking ? 0.08 : 0.04; // More movement when speaking
            spine.rotation.y = spineRotationIntensity * Math.sin(elapsedTime * 0.5); // Gentle sway
            spine.rotation.x = spineRotationIntensity * 0.3 * Math.cos(elapsedTime * 0.6); // Subtle tilt
        }

        // --- Head Movement ---
        let head = currentVrm.humanoid.getRawBoneNode('head');
        if (head) {
            const headRotationIntensity = isSpeaking ? 0.1 : 0.075; // More expressive when speaking
            head.rotation.y = headRotationIntensity * Math.sin(elapsedTime * 0.2);
            head.rotation.x = headRotationIntensity * 0.67 * Math.cos(elapsedTime * 0.7);
        }

        // --- Blinking Logic ---
        if (currentVrm.expressionManager) {
            if (!blinkState.isBlinking && elapsedTime > blinkState.nextBlinkTime) {
                // Start a new blink series
                blinkState.isBlinking = true;
                blinkState.blinkProgress = 0;
                blinkState.blinksLeft = (Math.random() < 0.3) ? 2 + Math.floor(Math.random() * 2) : 1; // 30% chance for 2–3 blinks
            }

            if (blinkState.isBlinking) {
                blinkState.blinkProgress += delta * 3; // blink speed

                // Blink curve (0→1→0)
                let blinkValue = Math.sin(Math.min(blinkState.blinkProgress, Math.PI));
                currentVrm.expressionManager.setValue('blink', blinkValue);

                if (blinkState.blinkProgress >= Math.PI) {
                    blinkState.blinkProgress = 0;
                    blinkState.blinksLeft--;

                    if (blinkState.blinksLeft <= 0) {
                        blinkState.isBlinking = false;
                        blinkState.nextBlinkTime = elapsedTime + 2 + Math.random() * 4; // wait 2–6s
                    }
                }
            }
        }
        // --- Speaking Animation (Viseme-Based) ---
        if (currentVrm && currentVrm.expressionManager && isSpeaking) {
            // List of visemes available in your model
            const visemes = ['aa', 'ih', 'ou', 'ee', 'oh'];

            // Change viseme randomly every 0.1-0.3 seconds for natural speech flow
            if (elapsedTime > visemeChangeTime) {
                currentVisemeIndex = Math.floor(Math.random() * visemes.length);
                visemeChangeTime = elapsedTime + (0.1 + Math.random() * 0.2); // Random hold duration
            }

            const currentViseme = visemes[currentVisemeIndex];
            const mouthIntensity = 0.6 * Math.abs(Math.sin(elapsedTime * 8)); // Smooth pulsing, adjust speed/intensity

            // Reset all visemes to avoid overlap
            visemes.forEach(exp => {
                currentVrm.expressionManager.setValue(exp, 0);
            });

            // Apply the current random viseme
            currentVrm.expressionManager.setValue(currentViseme, mouthIntensity);
            console.log(`Speaking: Set ${currentViseme} to ${mouthIntensity}`);
        } else if (!isSpeaking && currentVrm && currentVrm.expressionManager) {
            // Reset all visemes when not speaking
            const visemes = ['aa', 'ih', 'ou', 'ee', 'oh'];
            visemes.forEach(exp => {
                currentVrm.expressionManager.setValue(exp, 0);
            });
            // Reset viseme tracking variables
            currentVisemeIndex = 0;
            visemeChangeTime = 0;
        }
    }

    renderer.render(scene, camera);
}
animate();


