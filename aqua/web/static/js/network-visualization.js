/**
 * Aqua IoT Security Platform
 * Network Visualization Module
 */

class NetworkVisualization {
    constructor(containerId) {
        console.log("Initializing network visualization for container:", containerId);
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        
        if (!this.container) {
            console.error(`Container element with ID '${containerId}' not found.`);
            return;
        }

        // Check if Three.js is available
        if (typeof THREE === 'undefined') {
            console.error('Three.js library not loaded!');
            return;
        }

        // Get container dimensions
        this.width = this.container.clientWidth;
        this.height = this.container.clientHeight;
        console.log("Container dimensions:", this.width, "x", this.height);

        // Initialize Three.js components
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(60, this.width / this.height, 0.1, 1000);
        this.camera.position.z = 200;
        
        // Create renderer with better options for visibility
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true, 
            alpha: true 
        });
        this.renderer.setSize(this.width, this.height);
        this.renderer.setClearColor(0x1e3a5c, 1); // Set explicit background color
        this.container.appendChild(this.renderer.domElement);
        
        // Add ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);
        
        // Add directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(100, 100, 100);
        this.scene.add(directionalLight);
        
        // Add controls for rotation/zooming
        if (typeof THREE.OrbitControls !== 'undefined') {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.05;
        } else {
            console.warn("THREE.OrbitControls not available, skipping controls initialization");
        }
        
        // Handle window resize
        window.addEventListener('resize', this.onWindowResize.bind(this));
        
        // Storage for nodes and links
        this.nodes = {};
        this.links = [];
        
        // Device type colors
        this.deviceColors = {
            router: 0x3498db,   // Blue
            camera: 0xe74c3c,   // Red
            thermostat: 0x2ecc71, // Green
            lock: 0xf39c12,     // Yellow
            tv: 0x9b59b6,       // Purple
            speaker: 0x1abc9c,  // Teal
            default: 0x95a5a6   // Grey
        };
        
        // Start animation loop
        this.animate();
        
        console.log("Network visualization initialized successfully");
    }
    
    onWindowResize() {
        if (!this.container) return;
        
        this.width = this.container.clientWidth;
        this.height = this.container.clientHeight;
        this.camera.aspect = this.width / this.height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.width, this.height);
    }
    
    animate() {
        if (!this.container || !this.scene || !this.camera || !this.renderer) return;
        
        requestAnimationFrame(this.animate.bind(this));
        
        if (this.controls && this.controls.update) {
            this.controls.update();
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    loadData(devices, connections) {
        console.log("Loading network data:", devices.length, "devices,", connections.length, "connections");
        
        if (!this.scene) {
            console.error("Scene not initialized!");
            return;
        }
        
        // Clear previous visualization - keep only lights
        const objectsToRemove = [];
        this.scene.traverse(object => {
            if (object.type === 'Mesh' || object.type === 'Line' || object.type === 'Sprite') {
                objectsToRemove.push(object);
            }
        });
        
        objectsToRemove.forEach(object => {
            this.scene.remove(object);
        });
        
        this.nodes = {};
        this.links = [];
        
        // Create router first (center node)
        const router = devices.find(d => d.device_type === 'router');
        if (router) {
            console.log("Adding router node:", router.ip);
            this.addNode(router, new THREE.Vector3(0, 0, 0));
        } else {
            console.warn("No router found in device data");
        }
        
        // Position other devices in a circle around the router
        const otherDevices = devices.filter(d => d.device_type !== 'router');
        const angleStep = (2 * Math.PI) / Math.max(otherDevices.length, 1);
        const radius = 80;
        
        otherDevices.forEach((device, index) => {
            const angle = angleStep * index;
            const x = radius * Math.cos(angle);
            const y = radius * Math.sin(angle);
            console.log("Adding device node:", device.ip, "at position:", x, y);
            this.addNode(device, new THREE.Vector3(x, y, 0));
        });
        
        // Add connections
        connections.forEach(conn => {
            console.log("Adding connection:", conn.source, "->", conn.destination);
            this.addLink(conn);
        });
    }
    
    addNode(device, position) {
        if (!this.scene) return;
        
        // Create node geometry based on device type
        const color = this.deviceColors[device.device_type] || this.deviceColors.default;
        
        // Create sphere for device
        const geometry = new THREE.SphereGeometry(8, 16, 16);
        const material = new THREE.MeshPhongMaterial({ 
            color: color,
            emissive: color,
            emissiveIntensity: 0.2,
            specular: 0xffffff,
            shininess: 50
        });
        
        // If device has vulnerabilities, add warning indicator
        if (device.vulnerabilities && device.vulnerabilities.length > 0) {
            // Find most severe vulnerability
            const hasCritical = device.vulnerabilities.some(v => v.severity === 'critical');
            const hasHigh = device.vulnerabilities.some(v => v.severity === 'high');
            
            if (hasCritical) {
                material.emissive = new THREE.Color(0xff0000);
                material.emissiveIntensity = 0.8;
                // Pulse animation
                this.addPulsingEffect(material);
            } else if (hasHigh) {
                material.emissive = new THREE.Color(0xff5500);
                material.emissiveIntensity = 0.5;
            }
        }
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.copy(position);
        mesh.userData = {
            type: 'device',
            data: device
        };
        
        this.scene.add(mesh);
        this.nodes[device.ip] = mesh;
        
        // Add device label
        this.addLabel(device.hostname || device.ip, position.clone().add(new THREE.Vector3(0, -15, 0)));
    }
    
    addLabel(text, position) {
        if (!this.scene) return;
        
        // Create canvas for label
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        context.font = 'Bold 14px Arial';
        const textWidth = context.measureText(text).width;
        
        canvas.width = textWidth + 10;
        canvas.height = 20;
        
        // Draw text on canvas
        context.font = 'Bold 14px Arial';
        context.fillStyle = 'white';
        context.fillText(text, 5, 15);
        
        // Create texture from canvas
        const texture = new THREE.Texture(canvas);
        texture.needsUpdate = true;
        
        // Create sprite material with texture
        const material = new THREE.SpriteMaterial({
            map: texture,
            transparent: true
        });
        
        // Create sprite
        const sprite = new THREE.Sprite(material);
        sprite.scale.set(20, 10, 1);
        sprite.position.copy(position);
        
        this.scene.add(sprite);
    }
    
    addLink(connection) {
        if (!this.scene) return;
        
        const sourceNode = this.nodes[connection.source];
        const targetNode = this.nodes[connection.destination];
        
        if (!sourceNode || !targetNode) {
            console.warn('Could not find nodes for connection:', connection);
            return;
        }
        
        // Create line geometry
        const points = [sourceNode.position, targetNode.position];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        
        // Determine line color and style based on connection state
        let color;
        let dashed = false;
        
        switch(connection.protocol) {
            case 'TCP':
                color = 0x40e0d0;  // Turquoise
                break;
            case 'UDP':
                color = 0xffbf00;  // Amber
                break;
            default:
                color = 0xeeeeee;  // White
        }
        
        // Highlight vulnerable connections
        if (connection.isVulnerable) {
            color = 0xff0000;  // Red
            dashed = true;
        }
        
        const material = new THREE.LineBasicMaterial({
            color: color
        });
        
        if (dashed && material.dashSize !== undefined) {
            material.dashSize = 3;
            material.gapSize = 2;
        }
        
        const line = new THREE.Line(geometry, material);
        line.userData = {
            type: 'connection',
            data: connection
        };
        
        this.scene.add(line);
        this.links.push(line);
        
        // Add traffic pulse animation
        this.addTrafficAnimation(sourceNode.position, targetNode.position, color);
    }
    
    addTrafficAnimation(source, target, color) {
        if (!this.scene) return;
        
        // Create small sphere for traffic visualization
        const geometry = new THREE.SphereGeometry(2, 8, 8);
        const material = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.8
        });
        
        const sphere = new THREE.Mesh(geometry, material);
        
        // Position at source
        sphere.position.copy(source);
        
        this.scene.add(sphere);
        
        // Animate sphere from source to target
        const startTime = Date.now();
        const duration = 2000; // 2 seconds for full journey
        
        const animate = () => {
            if (!this.scene || !sphere.parent) return;
            
            const elapsedTime = Date.now() - startTime;
            const progress = (elapsedTime % duration) / duration;
            
            // Interpolate position
            sphere.position.lerpVectors(source, target, progress);
            
            if (this.container && this.container.parentNode) {
                requestAnimationFrame(animate);
            } else {
                // Clean up if container is no longer in DOM
                this.scene.remove(sphere);
            }
        };
        
        animate();
    }
    
    addPulsingEffect(material) {
        if (!material) return;
        
        const startTime = Date.now();
        
        const animate = () => {
            if (!material) return;
            
            const elapsedTime = Date.now() - startTime;
            const pulseFactor = 0.5 + 0.5 * Math.sin(elapsedTime * 0.005);
            
            material.emissiveIntensity = 0.3 + 0.5 * pulseFactor;
            
            if (this.container && this.container.parentNode) {
                requestAnimationFrame(animate);
            }
        };
        
        animate();
    }
}

// Initialize network visualization when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, checking for network visualization container");
    
    const networkContainer = document.getElementById('networkVisualization');
    if (networkContainer) {
        console.log("Network visualization container found, initializing");
        
        // Make sure THREE is available
        if (typeof THREE === 'undefined') {
            console.error("THREE.js is not loaded!");
            
            // Add notification to the container
            networkContainer.innerHTML = `
                <div class="alert alert-danger m-3">
                    <strong>Error:</strong> THREE.js library not loaded correctly.
                    Please check your internet connection and reload the page.
                </div>
            `;
            return;
        }
        
        // Initialize visualization
        try {
            window.networkViz = new NetworkVisualization('networkVisualization');
            
            // If demo data is available, load it
            if (window.demoDevices && window.demoConnections) {
                console.log("Demo data found, loading into visualization");
                window.networkViz.loadData(window.demoDevices, window.demoConnections);
            } else {
                console.log("No demo data found for network visualization");
                
                // Add placeholder data for testing
                const testDevices = [
                    { id: "router", ip: "192.168.1.1", hostname: "router", device_type: "router", vulnerabilities: [] },
                    { id: "camera", ip: "192.168.1.101", hostname: "camera", device_type: "camera", vulnerabilities: [{ severity: "high" }] },
                    { id: "thermostat", ip: "192.168.1.102", hostname: "thermostat", device_type: "thermostat", vulnerabilities: [] }
                ];
                
                const testConnections = [
                    { source: "192.168.1.101", destination: "192.168.1.1", protocol: "TCP", state: "ESTABLISHED" },
                    { source: "192.168.1.102", destination: "192.168.1.1", protocol: "TCP", state: "ESTABLISHED" }
                ];
                
                window.networkViz.loadData(testDevices, testConnections);
            }
        } catch (error) {
            console.error("Failed to initialize network visualization:", error);
            networkContainer.innerHTML = `
                <div class="alert alert-danger m-3">
                    <strong>Error:</strong> Failed to initialize network visualization.
                    <pre class="mt-2">${error.message}</pre>
                </div>
            `;
        }
    } else {
        console.log("Network visualization container not found");
    }
});
