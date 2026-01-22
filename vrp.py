import streamlit as st
import streamlit.components.v1 as components
import json

# --- CONFIGURATION STREAMLIT ---
st.set_page_config(
    page_title="VRP Route Optimizer",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar cachée pour laisser place à la Full UI
)

# --- INSTRUCTIONS SIDEBAR ---
with st.sidebar:
    st.header("🚚 Guide d'utilisation")
    st.markdown("""
    1. **Sélectionner le mode** : Cliquez sur 'Select Depot' ou 'Select Delivery' dans le panneau.
    2. **Placer les points** : Cliquez sur la carte pour ajouter le dépôt (Bleu) et les clients (Vert).
    3. **Optimiser** : Cliquez sur 'Optimize Routes' pour calculer le chemin.
    4. **Stats** : Voir la distance et l'efficacité en haut.
    """)
    st.info("Cette démo utilise un algorithme 'Nearest Neighbor' côté client pour une réactivité immédiate.")

# --- APPLICATION PRINCIPALE (HTML/JS/CSS) ---
# Nous encapsulons toute l'interface dans un seul composant HTML pour garantir 
# une interaction fluide (sans rechargement de page Streamlit à chaque clic).

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VRP Route Optimizer</title>
    
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        /* --- CSS STYLES --- */
        :root {
            --primary: #3B82F6;
            --primary-dark: #2563EB;
            --secondary: #10B981;
            --accent: #F59E0B;
            --danger: #EF4444;
            --dark: #1F2937;
            --light: #F9FAFB;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #f5f7fa;
            color: #333;
            overflow: hidden; /* Prevent double scrollbars */
        }
        
        .app-wrapper {
            display: flex;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
        }

        /* --- LEFT PANEL --- */
        .sidebar-panel {
            width: 400px;
            background: white;
            box-shadow: 2px 0 20px rgba(0,0,0,0.1);
            z-index: 1000;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }

        .header h1 { font-size: 1.5rem; font-weight: 700; margin-bottom: 5px; }
        .header p { opacity: 0.9; font-size: 0.9rem; font-weight: 300; }

        .content-area { padding: 20px; }

        /* --- SECTIONS & INPUTS --- */
        .section { margin-bottom: 25px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
        .section-title { 
            display: flex; align-items: center; gap: 10px; 
            font-weight: 600; color: var(--dark); margin-bottom: 15px; 
        }
        .section-title i { color: var(--primary); }

        .mode-selector { display: flex; gap: 10px; margin-bottom: 15px; }
        .mode-btn {
            flex: 1; padding: 10px; border: 1px solid #e5e7eb;
            background: #f9fafb; border-radius: 8px; cursor: pointer;
            transition: all 0.2s; font-size: 0.85rem; display: flex; 
            flex-direction: column; align-items: center; gap: 5px;
        }
        .mode-btn:hover { background: #eef2ff; border-color: var(--primary); }
        .mode-btn.active {
            background: var(--primary); color: white; border-color: var(--primary);
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5);
        }

        .btn {
            width: 100%; padding: 12px; border: none; border-radius: 8px;
            font-weight: 600; cursor: pointer; transition: transform 0.1s;
            display: flex; justify-content: center; align-items: center; gap: 8px;
        }
        .btn:active { transform: scale(0.98); }
        .btn-primary { background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); color: white; }
        .btn-danger { background: white; color: var(--danger); border: 1px solid var(--danger); margin-top: 10px; }

        /* --- STATS --- */
        .stats-grid {
            display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px;
        }
        .stat-card {
            background: #f3f4f6; padding: 15px; border-radius: 10px; text-align: center;
        }
        .stat-val { font-size: 1.2rem; font-weight: 700; color: var(--primary); }
        .stat-lbl { font-size: 0.75rem; color: #6b7280; text-transform: uppercase; }

        /* --- MAP AREA --- */
        .map-container { flex: 1; position: relative; }
        #map { width: 100%; height: 100%; }

        .map-overlay-info {
            position: absolute; bottom: 20px; right: 20px;
            background: rgba(255,255,255,0.9); padding: 10px 20px;
            border-radius: 50px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            z-index: 1000; font-family: monospace; font-size: 0.9rem;
            backdrop-filter: blur(5px);
        }
        
        /* List of points */
        .points-list { max-height: 150px; overflow-y: auto; font-size: 0.9rem; }
        .point-item { 
            display: flex; justify-content: space-between; padding: 8px; 
            background: #f8fafc; margin-bottom: 5px; border-radius: 6px; border-left: 3px solid #ccc;
        }
        .point-item.depot { border-left-color: var(--primary); }
        .point-item.delivery { border-left-color: var(--secondary); }

    </style>
</head>
<body>

    <div class="app-wrapper">
        <div class="sidebar-panel">
            <div class="header">
                <h1><i class="fas fa-route"></i> VRP Optimizer</h1>
                <p>Planification Intelligente de Tournées</p>
            </div>

            <div class="content-area">
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-val" id="totalDist">0 km</div>
                        <div class="stat-lbl">Distance</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-val" id="totalStops">0</div>
                        <div class="stat-lbl">Arrêts</div>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title"><i class="fas fa-mouse-pointer"></i> Mode Sélection</div>
                    <div class="mode-selector">
                        <div class="mode-btn active" id="btn-nav" onclick="setMode('nav')">
                            <i class="fas fa-hand-paper"></i> Nav
                        </div>
                        <div class="mode-btn" id="btn-depot" onclick="setMode('depot')">
                            <i class="fas fa-warehouse"></i> Dépôt
                        </div>
                        <div class="mode-btn" id="btn-delivery" onclick="setMode('delivery')">
                            <i class="fas fa-map-marker-alt"></i> Client
                        </div>
                    </div>
                    <div style="font-size: 0.85rem; color: #666; background: #eefffa; padding: 10px; border-radius: 6px; border-left: 3px solid var(--secondary);">
                        <i class="fas fa-info-circle"></i> <span id="mode-desc">Mode Navigation : Déplacez-vous sur la carte.</span>
                    </div>
                </div>

                <div class="section">
                    <button class="btn btn-primary" onclick="optimizeRoutes()">
                        <i class="fas fa-bolt"></i> Optimiser la Tournée
                    </button>
                    <button class="btn btn-danger" onclick="clearMap()">
                        <i class="fas fa-trash"></i> Tout Effacer
                    </button>
                </div>

                <div class="section">
                    <div class="section-title"><i class="fas fa-list"></i> Points (<span id="count-pts">0</span>)</div>
                    <div class="points-list" id="points-container">
                        <div style="text-align:center; color:#999; padding: 20px;">Aucun point ajouté</div>
                    </div>
                </div>

            </div>
        </div>

        <div class="map-container">
            <div id="map"></div>
            <div class="map-overlay-info">
                <i class="fas fa-location-arrow"></i> <span id="coords">48.85, 2.35</span>
            </div>
        </div>
    </div>

    <script>
        // --- JAVASCRIPT LOGIC ---

        // 1. Initialization
        const map = L.map('map').setView([48.8566, 2.3522], 12); // Paris default
        
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(map);

        // State
        let currentMode = 'nav'; // nav, depot, delivery
        let depot = null;
        let deliveries = [];
        let routeLayer = L.layerGroup().addTo(map);
        let markerLayer = L.layerGroup().addTo(map);

        // Icons
        const depotIcon = L.divIcon({
            className: 'custom-div-icon',
            html: "<div style='background-color:#3B82F6; width:15px; height:15px; border-radius:50%; border:2px solid white; box-shadow:0 0 5px rgba(0,0,0,0.5);'></div>",
            iconSize: [15, 15],
            iconAnchor: [7, 7]
        });

        const deliveryIcon = L.divIcon({
            className: 'custom-div-icon',
            html: "<div style='background-color:#10B981; width:12px; height:12px; border-radius:50%; border:2px solid white; box-shadow:0 0 5px rgba(0,0,0,0.5);'></div>",
            iconSize: [12, 12],
            iconAnchor: [6, 6]
        });

        // 2. UI Functions
        function setMode(mode) {
            currentMode = mode;
            
            // UI Updates
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-' + mode).classList.add('active');
            
            const desc = document.getElementById('mode-desc');
            if(mode === 'nav') desc.innerText = "Mode Navigation : Déplacez-vous sur la carte.";
            if(mode === 'depot') desc.innerText = "Cliquez sur la carte pour définir le point de départ.";
            if(mode === 'delivery') desc.innerText = "Cliquez sur la carte pour ajouter des clients.";
            
            // Map cursor
            document.getElementById('map').style.cursor = mode === 'nav' ? 'grab' : 'crosshair';
        }

        function updateList() {
            const container = document.getElementById('points-container');
            container.innerHTML = '';
            
            let count = 0;
            if (depot) {
                container.innerHTML += `<div class="point-item depot"><strong>Dépôt</strong> <span>${depot.lat.toFixed(4)}, ${depot.lng.toFixed(4)}</span></div>`;
                count++;
            }
            
            deliveries.forEach((d, index) => {
                container.innerHTML += `<div class="point-item delivery"><strong>Client ${index+1}</strong> <span>${d.lat.toFixed(4)}, ${d.lng.toFixed(4)}</span></div>`;
                count++;
            });
            
            document.getElementById('count-pts').innerText = count;
            document.getElementById('totalStops').innerText = deliveries.length;
        }

        function clearMap() {
            depot = null;
            deliveries = [];
            markerLayer.clearLayers();
            routeLayer.clearLayers();
            updateList();
            document.getElementById('totalDist').innerText = "0 km";
        }

        // 3. Map Interaction
        map.on('mousemove', (e) => {
            document.getElementById('coords').innerText = `${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}`;
        });

        map.on('click', (e) => {
            if (currentMode === 'nav') return;

            if (currentMode === 'depot') {
                // Remove old depot if exists
                if (depot) {
                    markerLayer.eachLayer(layer => {
                        if (layer.options.isDepot) markerLayer.removeLayer(layer);
                    });
                }
                
                depot = e.latlng;
                L.marker(depot, {icon: depotIcon, isDepot: true}).addTo(markerLayer)
                 .bindPopup("<b>Dépôt Central</b>").openPopup();
                
                // Auto switch to delivery mode after picking depot
                setMode('delivery');
            } 
            else if (currentMode === 'delivery') {
                deliveries.push(e.latlng);
                L.marker(e.latlng, {icon: deliveryIcon}).addTo(markerLayer)
                 .bindPopup(`<b>Client ${deliveries.length}</b>`);
            }
            updateList();
        });

        // 4. Optimization Logic (Nearest Neighbor Heuristic)
        function getDistance(p1, p2) {
            return p1.distanceTo(p2) / 1000; // in km
        }

        function optimizeRoutes() {
            if (!depot) {
                alert("Veuillez d'abord définir un dépôt (carré bleu) !");
                return;
            }
            if (deliveries.length === 0) {
                alert("Ajoutez au moins un client !");
                return;
            }

            // Clear old routes
            routeLayer.clearLayers();

            // Simple Greedy Algorithm (Nearest Neighbor)
            let unvisited = [...deliveries];
            let currentPos = depot;
            let routePoints = [depot];
            let totalDist = 0;

            while (unvisited.length > 0) {
                let nearest = null;
                let minDist = Infinity;
                let nearestIdx = -1;

                // Find nearest unvisited node
                unvisited.forEach((pt, index) => {
                    let d = getDistance(currentPos, pt);
                    if (d < minDist) {
                        minDist = d;
                        nearest = pt;
                        nearestIdx = index;
                    }
                });

                // Move there
                routePoints.push(nearest);
                totalDist += minDist;
                currentPos = nearest;
                unvisited.splice(nearestIdx, 1);
            }

            // Return to depot
            totalDist += getDistance(currentPos, depot);
            routePoints.push(depot);

            // Draw Route
            const polyline = L.polyline(routePoints, {
                color: '#3B82F6',
                weight: 4,
                opacity: 0.8,
                dashArray: '10, 10', 
                lineJoin: 'round'
            }).addTo(routeLayer);
            
            // Animation effect
            let dashOffset = 0;
            setInterval(() => {
                dashOffset -= 1;
                polyline.setStyle({dashOffset: dashOffset});
            }, 50);

            map.fitBounds(polyline.getBounds(), {padding: [50, 50]});
            
            document.getElementById('totalDist').innerText = totalDist.toFixed(2) + " km";
        }
    </script>
</body>
</html>
"""

# Affichage du composant HTML
# height=900 assure que ça prend toute la hauteur de l'écran
components.html(html_code, height=900, scrolling=False)
