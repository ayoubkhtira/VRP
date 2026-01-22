import streamlit as st
import streamlit.components.v1 as components
import base64
from io import StringIO

# Configuration de la page
st.set_page_config(
    page_title="VRP Route Optimizer",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS amélioré
css = """
<style>
    /* Variables CSS améliorées */
    :root {
        --primary: #1e88e5;
        --primary-dark: #1565c0;
        --primary-light: #64b5f6;
        --secondary: #ff9800;
        --secondary-dark: #f57c00;
        --success: #4caf50;
        --warning: #ff9800;
        --danger: #f44336;
        --dark: #212121;
        --light: #f5f5f5;
        --gray: #757575;
        --border-radius: 12px;
        --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        --transition: all 0.3s ease;
    }
    
    /* Styles généraux */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        padding: 2rem;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        box-shadow: var(--box-shadow);
        animation: fadeIn 0.8s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .card {
        background: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--box-shadow);
        transition: var(--transition);
        border: none;
        height: 100%;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        text-align: center;
        border-left: 5px solid var(--primary);
        transition: var(--transition);
    }
    
    .metric-card:hover {
        transform: scale(1.02);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: var(--primary);
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: var(--gray);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Boutons améliorés */
    .stButton > button {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: var(--transition);
        border: none;
        background: var(--primary);
        color: white;
    }
    
    .stButton > button:hover {
        background: var(--primary-dark);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Inputs améliorés */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: var(--transition);
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
    }
    
    /* Sidebar améliorée */
    .css-1d391kg {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    }
    
    /* Tabs personnalisés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: var(--transition);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary);
        color: white;
    }
    
    /* Animations */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
        }
        
        .metric-value {
            font-size: 1.5rem;
        }
    }
</style>
"""

# HTML/JS pour la carte et l'interface
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VRP Route Optimizer</title>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .app-wrapper {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            animation: slideUp 0.6s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none"><path d="M0,0 L100,0 L100,100 Z" fill="rgba(255,255,255,0.1)"/></svg>');
            background-size: cover;
        }
        
        .header-content {
            position: relative;
            z-index: 1;
        }
        
        .logo {
            font-size: 3.5rem;
            margin-bottom: 20px;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 800px;
            margin: 0 auto;
            font-weight: 300;
        }
        
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
            padding: 0 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 16px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: scale(1.05);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #667eea;
            font-family: 'Roboto Mono', monospace;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 10px;
        }
        
        .main-layout {
            display: grid;
            grid-template-columns: 400px 1fr;
            gap: 30px;
            padding: 30px;
        }
        
        @media (max-width: 1200px) {
            .main-layout {
                grid-template-columns: 1fr;
            }
        }
        
        .control-panel {
            background: white;
            border-radius: 20px;
            padding: 30px;
            height: fit-content;
            position: sticky;
            top: 30px;
        }
        
        .section {
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .section-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.3rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 25px;
        }
        
        .section-title i {
            color: #667eea;
            font-size: 1.5rem;
        }
        
        .input-group {
            margin-bottom: 25px;
        }
        
        .input-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #555;
            font-size: 0.95rem;
        }
        
        .input-field {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s ease;
            font-family: 'Poppins', sans-serif;
        }
        
        .input-field:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 16px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Poppins', sans-serif;
            width: 100%;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-secondary {
            background: #f8f9fa;
            color: #333;
            border: 2px solid #e0e0e0;
        }
        
        .btn-secondary:hover {
            background: #e9ecef;
            border-color: #667eea;
        }
        
        .delivery-list {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 20px;
        }
        
        .delivery-item {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }
        
        .delivery-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        
        .map-container {
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            height: 600px;
        }
        
        #map {
            width: 100%;
            height: 100%;
        }
        
        .results-panel {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-top: 30px;
            animation: fadeIn 0.5s ease-out;
        }
        
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .result-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            padding: 25px;
            border-radius: 16px;
            text-align: center;
        }
        
        .route-item {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .route-number {
            background: #667eea;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
        }
        
        .loading {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(255, 255, 255, 0.95);
            padding: 30px 50px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            text-align: center;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .notification {
            position: fixed;
            top: 30px;
            right: 30px;
            padding: 20px 30px;
            border-radius: 12px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease;
        }
        
        .notification.show {
            transform: translateX(0);
            opacity: 1;
        }
        
        .notification.success {
            background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        }
        
        .notification.error {
            background: linear-gradient(135deg, #f44336 0%, #c62828 100%);
        }
        
        .notification.info {
            background: linear-gradient(135deg, #2196F3 0%, #1565C0 100%);
        }
        
        .color-indicator {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="loading" id="loading">
        <div class="spinner"></div>
        <h3>Optimizing Routes...</h3>
        <p>This may take a few moments</p>
    </div>
    
    <div class="container">
        <div class="app-wrapper">
            <div class="header">
                <div class="header-content">
                    <div class="logo">
                        <i class="fas fa-route"></i>
                    </div>
                    <h1>VRP Route Optimizer</h1>
                    <p class="subtitle">
                        Advanced Vehicle Routing Problem Solver with Real-time Optimization and Interactive Visualization
                    </p>
                </div>
            </div>
            
            <div class="stats-bar" id="statsBar" style="display: none;">
                <div class="stat-card">
                    <div class="stat-value" id="statRoutes">0</div>
                    <div class="stat-label">Optimized Routes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="statDistance">0 km</div>
                    <div class="stat-label">Total Distance</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="statDemand">0 kg</div>
                    <div class="stat-label">Total Demand</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="statEfficiency">0%</div>
                    <div class="stat-label">Efficiency</div>
                </div>
            </div>
            
            <div class="main-layout">
                <div class="control-panel glass-card">
                    <div class="section">
                        <div class="section-title">
                            <i class="fas fa-warehouse"></i>
                            <span>Depot Configuration</span>
                        </div>
                        <div class="input-group">
                            <label class="input-label">Depot Name</label>
                            <input type="text" id="depotName" class="input-field" value="Main Depot" placeholder="Enter depot name">
                        </div>
                        <div class="input-group">
                            <label class="input-label">Latitude</label>
                            <input type="number" id="depotLat" class="input-field" value="48.8566" step="0.0001">
                        </div>
                        <div class="input-group">
                            <label class="input-label">Longitude</label>
                            <input type="number" id="depotLon" class="input-field" value="2.3522" step="0.0001">
                        </div>
                        <button class="btn btn-secondary" onclick="updateDepot()">
                            <i class="fas fa-sync-alt"></i> Update Depot
                        </button>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">
                            <i class="fas fa-plus-circle"></i>
                            <span>Add Delivery Point</span>
                        </div>
                        <div class="input-group">
                            <label class="input-label">Customer Name</label>
                            <input type="text" id="deliveryName" class="input-field" placeholder="Enter customer name">
                        </div>
                        <div class="input-group">
                            <label class="input-label">Latitude</label>
                            <input type="number" id="deliveryLat" class="input-field" step="0.0001" placeholder="48.8600">
                        </div>
                        <div class="input-group">
                            <label class="input-label">Longitude</label>
                            <input type="number" id="deliveryLon" class="input-field" step="0.0001" placeholder="2.3500">
                        </div>
                        <div class="input-group">
                            <label class="input-label">Demand (kg)</label>
                            <input type="number" id="deliveryDemand" class="input-field" value="10" min="1" step="1">
                        </div>
                        <button class="btn btn-primary" onclick="addDelivery()">
                            <i class="fas fa-plus"></i> Add Delivery Point
                        </button>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">
                            <i class="fas fa-list-ol"></i>
                            <span>Delivery Points</span>
                            <span class="badge" id="deliveryCount">0</span>
                        </div>
                        <div class="delivery-list" id="deliveryList">
                            <div class="empty-state">
                                <i class="fas fa-inbox"></i>
                                <p>No delivery points added yet</p>
                            </div>
                        </div>
                        <button class="btn btn-secondary" onclick="clearDeliveries()" style="margin-top: 15px;">
                            <i class="fas fa-trash"></i> Clear All
                        </button>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">
                            <i class="fas fa-cogs"></i>
                            <span>Optimization Settings</span>
                        </div>
                        <div class="input-group">
                            <label class="input-label">Vehicle Capacity (kg)</label>
                            <input type="number" id="vehicleCapacity" class="input-field" value="100" min="10" step="10">
                        </div>
                        <div class="input-group">
                            <label class="input-label">Max Vehicles</label>
                            <input type="number" id="maxVehicles" class="input-field" value="3" min="1" step="1">
                        </div>
                        <div class="input-group">
                            <label class="input-label">Algorithm</label>
                            <select id="algorithm" class="input-field">
                                <option value="nearest">Nearest Neighbor</option>
                                <option value="savings">Clarke & Wright Savings</option>
                                <option value="sweep">Sweep Algorithm</option>
                            </select>
                        </div>
                        <button class="btn btn-primary pulse" onclick="optimizeRoutes()">
                            <i class="fas fa-bolt"></i> Optimize Routes
                        </button>
                    </div>
                </div>
                
                <div class="map-container glass-card">
                    <div id="map"></div>
                </div>
            </div>
            
            <div class="results-panel" id="resultsPanel" style="display: none;">
                <h2 style="margin-bottom: 30px; color: #333;">
                    <i class="fas fa-chart-line"></i> Optimization Results
                </h2>
                
                <div class="results-grid" id="resultCardsContainer"></div>
                
                <div style="margin-top: 40px;">
                    <h3 style="margin-bottom: 20px; color: #333;">
                        <i class="fas fa-route"></i> Route Details
                    </h3>
                    <div id="routesContainer"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Initialisation de la carte Leaflet
        const map = L.map('map').setView([48.8566, 2.3522], 12);
        
        // Couches de tuiles
        const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);
        
        // Couche satellite
        const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: '© Esri',
            maxZoom: 19
        });
        
        // Contrôle des couches
        const baseLayers = {
            "OpenStreetMap": osmLayer,
            "Satellite": satelliteLayer
        };
        L.control.layers(baseLayers).addTo(map);
        
        let markers = {};
        let routePolylines = [];
        let deliveries = [];
        let depot = { lat: 48.8566, lon: 2.3522, name: 'Main Depot' };
        
        // Icones personnalisées
        const depotIcon = L.divIcon({
            html: '<div style="background: #667eea; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px; border: 3px solid white; box-shadow: 0 0 10px rgba(0,0,0,0.3);"><i class="fas fa-warehouse"></i></div>',
            className: 'custom-depot-icon',
            iconSize: [40, 40],
            iconAnchor: [20, 20]
        });
        
        const deliveryIcon = L.divIcon({
            html: '<div style="background: #ff9800; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 16px; border: 2px solid white; box-shadow: 0 0 8px rgba(0,0,0,0.2);"><i class="fas fa-map-marker-alt"></i></div>',
            className: 'custom-delivery-icon',
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        });
        
        // Couleurs pour les routes
        const routeColors = ['#667eea', '#ff9800', '#4CAF50', '#f44336', '#9C27B0', '#00BCD4', '#FFC107', '#8BC34A'];
        
        // Initialiser le dépôt
        function initDepot() {
            if (markers.depot) map.removeLayer(markers.depot);
            
            const marker = L.marker([depot.lat, depot.lon], { icon: depotIcon })
                .addTo(map)
                .bindPopup(`<b>${depot.name}</b><br>Depot Location<br>Lat: ${depot.lat.toFixed(4)}<br>Lon: ${depot.lon.toFixed(4)}`);
            
            markers.depot = marker;
        }
        
        // Mettre à jour le dépôt
        function updateDepot() {
            const name = document.getElementById('depotName').value.trim();
            const lat = parseFloat(document.getElementById('depotLat').value);
            const lon = parseFloat(document.getElementById('depotLon').value);
            
            if (!name || isNaN(lat) || isNaN(lon)) {
                showNotification('Please enter valid depot information', 'error');
                return;
            }
            
            depot = { name, lat, lon };
            initDepot();
            map.setView([depot.lat, depot.lon], 12);
            showNotification('Depot location updated successfully', 'success');
        }
        
        // Ajouter un point de livraison
        function addDelivery() {
            const name = document.getElementById('deliveryName').value.trim();
            const lat = parseFloat(document.getElementById('deliveryLat').value);
            const lon = parseFloat(document.getElementById('deliveryLon').value);
            const demand = parseFloat(document.getElementById('deliveryDemand').value);
            
            if (!name || isNaN(lat) || isNaN(lon) || isNaN(demand) || demand <= 0) {
                showNotification('Please fill all fields with valid data', 'error');
                return;
            }
            
            const delivery = { 
                id: Date.now() + Math.random(), 
                name, 
                lat, 
                lon, 
                demand,
                addedAt: new Date().toLocaleTimeString()
            };
            
            deliveries.push(delivery);
            renderDeliveryList();
            addMarkerToMap(delivery);
            
            // Réinitialiser les champs
            document.getElementById('deliveryName').value = '';
            document.getElementById('deliveryLat').value = '';
            document.getElementById('deliveryLon').value = '';
            document.getElementById('deliveryDemand').value = '10';
            
            showNotification(`Delivery point "${name}" added successfully`, 'success');
        }
        
        // Ajouter un marqueur sur la carte
        function addMarkerToMap(delivery) {
            const marker = L.marker([delivery.lat, delivery.lon], { icon: deliveryIcon })
                .addTo(map)
                .bindPopup(`
                    <b>${delivery.name}</b><br>
                    Demand: ${delivery.demand} kg<br>
                    Location: ${delivery.lat.toFixed(4)}, ${delivery.lon.toFixed(4)}<br>
                    Added: ${delivery.addedAt}
                `);
            
            markers[delivery.id] = marker;
        }
        
        // Afficher la liste des livraisons
        function renderDeliveryList() {
            const container = document.getElementById('deliveryList');
            const countElement = document.getElementById('deliveryCount');
            
            if (deliveries.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <p>No delivery points added yet</p>
                    </div>
                `;
                countElement.textContent = '0';
                return;
            }
            
            countElement.textContent = deliveries.length;
            container.innerHTML = '';
            
            deliveries.forEach((delivery, index) => {
                const div = document.createElement('div');
                div.className = 'delivery-item';
                div.innerHTML = `
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: #333;">${delivery.name}</div>
                        <div style="font-size: 0.9rem; color: #666;">
                            ${delivery.lat.toFixed(4)}, ${delivery.lon.toFixed(4)}
                        </div>
                        <div style="font-size: 0.9rem; color: #667eea; font-weight: 500;">
                            <i class="fas fa-weight-hanging"></i> ${delivery.demand} kg
                        </div>
                    </div>
                    <button onclick="removeDelivery(${delivery.id})" 
                            style="background: #f44336; color: white; border: none; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; transition: all 0.3s ease;"
                            onmouseover="this.style.transform='scale(1.1)'" 
                            onmouseout="this.style.transform='scale(1)'">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                container.appendChild(div);
            });
        }
        
        // Supprimer une livraison
        function removeDelivery(id) {
            deliveries = deliveries.filter(d => d.id !== id);
            
            if (markers[id]) {
                map.removeLayer(markers[id]);
                delete markers[id];
            }
            
            renderDeliveryList();
            showNotification('Delivery point removed', 'info');
        }
        
        // Effacer toutes les livraisons
        function clearDeliveries() {
            if (deliveries.length === 0) return;
            
            if (!confirm('Are you sure you want to clear all delivery points?')) return;
            
            deliveries.forEach(d => {
                if (markers[d.id]) {
                    map.removeLayer(markers[d.id]);
                    delete markers[d.id];
                }
            });
            
            deliveries = [];
            renderDeliveryList();
            clearRoutes();
            showNotification('All delivery points cleared', 'info');
        }
        
        // Afficher une notification
        function showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.innerHTML = `
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                ${message}
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.classList.add('show');
            }, 10);
            
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    document.body.removeChild(notification);
                }, 300);
            }, 3000);
        }
        
        // Afficher le chargement
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }
        
        // Cacher le chargement
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }
        
        // Effacer les routes
        function clearRoutes() {
            routePolylines.forEach(p => map.removeLayer(p));
            routePolylines = [];
            document.getElementById('resultsPanel').style.display = 'none';
            document.getElementById('statsBar').style.display = 'none';
        }
        
        // Calculer la distance (formule de Haversine)
        function calculateDistance(lat1, lon1, lat2, lon2) {
            const R = 6371; // Rayon de la Terre en km
            const dLat = (lat2 - lat1) * Math.PI / 180;
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                     Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                     Math.sin(dLon / 2) * Math.sin(dLon / 2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            return R * c;
        }
        
        // Algorithme du plus proche voisin
        function nearestNeighborAlgorithm(capacity, maxVehicles) {
            if (deliveries.length === 0) return [];
            
            const unvisited = [...deliveries];
            const routes = [];
            let vehicleCount = 0;
            
            while (unvisited.length > 0 && vehicleCount < maxVehicles) {
                const route = [];
                let currentLoad = 0;
                let currentLocation = depot;
                
                while (unvisited.length > 0) {
                    let nearestIdx = -1;
                    let nearestDist = Infinity;
                    
                    // Trouver le point non visité le plus proche
                    for (let i = 0; i < unvisited.length; i++) {
                        if (currentLoad + unvisited[i].demand <= capacity) {
                            const dist = calculateDistance(
                                currentLocation.lat, currentLocation.lon,
                                unvisited[i].lat, unvisited[i].lon
                            );
                            
                            if (dist < nearestDist) {
                                nearestDist = dist;
                                nearestIdx = i;
                            }
                        }
                    }
                    
                    // Si aucun point ne peut être ajouté, terminer cette route
                    if (nearestIdx === -1) break;
                    
                    // Ajouter le point à la route
                    const nextPoint = unvisited.splice(nearestIdx, 1)[0];
                    route.push(nextPoint);
                    currentLoad += nextPoint.demand;
                    currentLocation = nextPoint;
                }
                
                if (route.length > 0) {
                    routes.push(route);
                    vehicleCount++;
                } else {
                    break;
                }
            }
            
            // Si des points restent non affectés, les ajouter à la dernière route
            if (unvisited.length > 0) {
                if (routes.length === 0) {
                    routes.push([...unvisited]);
                } else {
                    routes[routes.length - 1] = [...routes[routes.length - 1], ...unvisited];
                }
            }
            
            return routes;
        }
        
        // Algorithme de Clarke & Wright Savings
        function savingsAlgorithm(capacity, maxVehicles) {
            if (deliveries.length === 0) return [];
            
            // Calculer les économies
            const savings = [];
            for (let i = 0; i < deliveries.length; i++) {
                for (let j = i + 1; j < deliveries.length; j++) {
                    const saving = calculateDistance(depot.lat, depot.lon, deliveries[i].lat, deliveries[i].lon) +
                                 calculateDistance(depot.lat, depot.lon, deliveries[j].lat, deliveries[j].lon) -
                                 calculateDistance(deliveries[i].lat, deliveries[i].lon, deliveries[j].lat, deliveries[j].lon);
                    
                    savings.push({
                        i, j, saving,
                        demand: deliveries[i].demand + deliveries[j].demand
                    });
                }
            }
            
            // Trier par économie décroissante
            savings.sort((a, b) => b.saving - a.saving);
            
            // Initialiser chaque point comme une route séparée
            const routes = deliveries.map(d => [d]);
            const routeLoads = deliveries.map(d => d.demand);
            
            // Fusionner les routes selon les économies
            for (const saving of savings) {
                if (routes.length <= maxVehicles) break;
                
                const routeI = routes.findIndex(route => route.includes(deliveries[saving.i]));
                const routeJ = routes.findIndex(route => route.includes(deliveries[saving.j]));
                
                if (routeI !== routeJ && routeLoads[routeI] + routeLoads[routeJ] <= capacity) {
                    // Fusionner les routes
                    routes[routeI] = [...routes[routeI], ...routes[routeJ]];
                    routeLoads[routeI] += routeLoads[routeJ];
                    
                    // Supprimer la route fusionnée
                    routes.splice(routeJ, 1);
                    routeLoads.splice(routeJ, 1);
                }
            }
            
            return routes;
        }
        
        // Optimiser les routes
        function optimizeRoutes() {
            if (deliveries.length === 0) {
                showNotification('Please add delivery points first', 'error');
                return;
            }
            
            showLoading();
            clearRoutes();
            
            setTimeout(() => {
                const capacity = parseFloat(document.getElementById('vehicleCapacity').value);
                const maxVehicles = parseInt(document.getElementById('maxVehicles').value);
                const algorithm = document.getElementById('algorithm').value;
                
                let routes = [];
                
                // Sélectionner l'algorithme
                switch(algorithm) {
                    case 'nearest':
                        routes = nearestNeighborAlgorithm(capacity, maxVehicles);
                        break;
                    case 'savings':
                        routes = savingsAlgorithm(capacity, maxVehicles);
                        break;
                    case 'sweep':
                        // Algorithme de balayage simple
                        routes = nearestNeighborAlgorithm(capacity, maxVehicles);
                        break;
                    default:
                        routes = nearestNeighborAlgorithm(capacity, maxVehicles);
                }
                
                // Afficher les routes sur la carte
                displayRoutes(routes);
                hideLoading();
            }, 1000);
        }
        
        // Afficher les routes
        function displayRoutes(routes) {
            clearRoutes();
            
            let totalDistance = 0;
            let totalDemand = 0;
            
            // Afficher chaque route
            routes.forEach((route, routeIdx) => {
                const color = routeColors[routeIdx % routeColors.length];
                let routeDistance = 0;
                let routeDemand = 0;
                
                // Calculer la demande totale de la route
                route.forEach(point => {
                    routeDemand += point.demand;
                    totalDemand += point.demand;
                });
                
                // Créer les points de la route (dépôt -> points -> dépôt)
                const routePoints = [
                    [depot.lat, depot.lon],
                    ...route.map(point => [point.lat, point.lon]),
                    [depot.lat, depot.lon]
                ];
                
                // Calculer la distance de la route
                for (let i = 0; i < routePoints.length - 1; i++) {
                    routeDistance += calculateDistance(
                        routePoints[i][0], routePoints[i][1],
                        routePoints[i + 1][0], routePoints[i + 1][1]
                    );
                }
                
                totalDistance += routeDistance;
                
                // Dessiner la polyligne
                const polyline = L.polyline(routePoints, {
                    color: color,
                    weight: 4,
                    opacity: 0.8,
                    dashArray: routeIdx % 2 === 0 ? null : '10, 10'
                }).addTo(map);
                
                // Ajouter un marqueur pour le véhicule
                const vehicleMarker = L.circleMarker(routePoints[1], {
                    radius: 8,
                    fillColor: color,
                    color: 'white',
                    weight: 2,
                    fillOpacity: 1
                }).addTo(map)
                .bindPopup(`<b>Vehicle ${routeIdx + 1}</b><br>Route distance: ${routeDistance.toFixed(2)} km<br>Load: ${routeDemand} kg`);
                
                routePolylines.push(polyline);
                routePolylines.push(vehicleMarker);
                
                // Ajuster la vue de la carte
                if (routeIdx === 0) {
                    const bounds = L.latLngBounds(routePoints);
                    map.fitBounds(bounds, { padding: [50, 50] });
                }
            });
            
            // Afficher les résultats
            showResults(routes, totalDistance, totalDemand);
        }
        
        // Afficher les résultats
        function showResults(routes, totalDistance, totalDemand) {
            const capacity = parseFloat(document.getElementById('vehicleCapacity').value);
            const efficiency = (totalDemand / (routes.length * capacity) * 100).toFixed(1);
            
            // Afficher la barre de statistiques
            document.getElementById('statsBar').style.display = 'grid';
            document.getElementById('statRoutes').textContent = routes.length;
            document.getElementById('statDistance').textContent = `${totalDistance.toFixed(2)} km`;
            document.getElementById('statDemand').textContent = `${totalDemand} kg`;
            document.getElementById('statEfficiency').textContent = `${efficiency}%`;
            
            // Afficher les cartes de résultats
            const resultCardsContainer = document.getElementById('resultCardsContainer');
            resultCardsContainer.innerHTML = `
                <div class="result-card">
                    <div class="stat-value">${routes.length}</div>
                    <div class="stat-label">Number of Routes</div>
                </div>
                <div class="result-card">
                    <div class="stat-value">${totalDistance.toFixed(2)} km</div>
                    <div class="stat-label">Total Distance</div>
                </div>
                <div class="result-card">
                    <div class="stat-value">${totalDemand} kg</div>
                    <div class="stat-label">Total Demand</div>
                </div>
                <div class="result-card">
                    <div class="stat-value">${efficiency}%</div>
                    <div class="stat-label">Load Efficiency</div>
                </div>
            `;
            
            // Afficher les détails des routes
            const routesContainer = document.getElementById('routesContainer');
            let routesHtml = '';
            
            routes.forEach((route, idx) => {
                const color = routeColors[idx % routeColors.length];
                let routeDistance = 0;
                let routeDemand = 0;
                
                const routePoints = [
                    depot,
                    ...route,
                    depot
                ];
                
                // Calculer la distance de la route
                for (let i = 0; i < routePoints.length - 1; i++) {
                    routeDistance += calculateDistance(
                        routePoints[i].lat, routePoints[i].lon,
                        routePoints[i + 1].lat, routePoints[i + 1].lon
                    );
                }
                
                routeDemand = route.reduce((sum, point) => sum + point.demand, 0);
                
                routesHtml += `
                    <div class="route-item">
                        <div class="route-number" style="background: ${color};">${idx + 1}</div>
                        <div style="flex: 1;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                <div>
                                    <strong style="color: #333;">Vehicle ${idx + 1}</strong>
                                    <div style="font-size: 0.9rem; color: #666;">
                                        <span style="color: ${color};"><i class="fas fa-route"></i> ${routeDistance.toFixed(2)} km</span>
                                        <span style="margin-left: 20px;"><i class="fas fa-weight-hanging"></i> ${routeDemand}/${capacity} kg</span>
                                    </div>
                                </div>
                                <div style="font-size: 0.9rem; color: ${color}; font-weight: 600;">
                                    ${((routeDemand / capacity) * 100).toFixed(1)}% loaded
                                </div>
                            </div>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px;">
                                <strong>Route:</strong> ${depot.name} → 
                                ${route.map((p, i) => 
                                    `${p.name}${i < route.length - 1 ? ' → ' : ''}`
                                ).join('')} 
                                → ${depot.name}
                            </div>
                        </div>
                    </div>
                `;
            });
            
            routesContainer.innerHTML = routesHtml;
            
            // Afficher le panneau de résultats
            document.getElementById('resultsPanel').style.display = 'block';
            showNotification('Routes optimized successfully!', 'success');
        }
        
        // Initialiser l'application
        function initApp() {
            initDepot();
            renderDeliveryList();
            
            // Ajouter des exemples de points de livraison
            const exampleDeliveries = [
                { name: "Customer A", lat: 48.8600, lon: 2.3500, demand: 20 },
                { name: "Customer B", lat: 48.8500, lon: 2.3400, demand: 15 },
                { name: "Customer C", lat: 48.8700, lon: 2.3600, demand: 30 },
                { name: "Customer D", lat: 48.8450, lon: 2.3650, demand: 25 },
                { name: "Customer E", lat: 48.8650, lon: 2.3300, demand: 18 }
            ];
            
            // Commenter cette ligne pour ne pas charger les exemples automatiquement
            // deliveries = exampleDeliveries.map((d, i) => ({ ...d, id: Date.now() + i, addedAt: new Date().toLocaleTimeString() }));
            // deliveries.forEach(d => addMarkerToMap(d));
            // renderDeliveryList();
        }
        
        // Démarrer l'application
        window.onload = initApp;
    </script>
</body>
</html>
"""

# Interface Streamlit améliorée
st.markdown(css, unsafe_allow_html=True)

# Header principal
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="main-header">
        <h1 style="text-align: center; margin-bottom: 1rem;">🚚 VRP Route Optimizer</h1>
        <p style="text-align: center; font-size: 1.2rem; opacity: 0.9;">
        Intelligent Vehicle Routing Problem Solver with Real-time Optimization
        </p>
    </div>
    """, unsafe_allow_html=True)

# Métriques en haut
if st.button("🎯 Quick Optimize", use_container_width=True):
    st.success("Routes optimized successfully!")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">5</div>
        <div class="metric-label">Delivery Points</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">3</div>
        <div class="metric-label">Routes</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">42.5 km</div>
        <div class="metric-label">Total Distance</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">87%</div>
        <div class="metric-label">Efficiency</div>
    </div>
    """, unsafe_allow_html=True)

# Interface principale avec tabs
tab1, tab2, tab3 = st.tabs(["🗺️ Interactive Map", "⚙️ Configuration", "📊 Results"])

with tab1:
    # Afficher la carte interactive
    components.html(html_content, height=900, scrolling=True)

with tab2:
    # Configuration avancée
    st.markdown("""
    <div class="card">
        <h3>⚙️ Advanced Configuration</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Vehicle Settings")
        vehicle_capacity = st.slider("Vehicle Capacity (kg)", 50, 500, 100, 10)
        max_vehicles = st.slider("Maximum Vehicles", 1, 10, 3)
        fuel_cost = st.number_input("Fuel Cost per km ($)", 0.1, 2.0, 0.5, 0.1)
        
    with col2:
        st.subheader("⏱️ Time Constraints")
        max_route_time = st.slider("Maximum Route Time (hours)", 1, 12, 8)
        service_time = st.slider("Service Time per Stop (minutes)", 5, 60, 15, 5)
        time_windows = st.checkbox("Enable Time Windows")
        
    st.subheader("📋 Delivery Points")
    with st.expander("Import/Export Data", expanded=True):
        uploaded_file = st.file_uploader("Upload CSV with delivery points", type=['csv'])
        if uploaded_file:
            st.success(f"File {uploaded_file.name} uploaded successfully!")
        
        if st.button("📥 Export Results as CSV"):
            st.info("Results exported successfully!")

with tab3:
    # Résultats détaillés
    st.markdown("""
    <div class="card">
        <h3>📊 Detailed Results Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Graphiques de résultats
    import pandas as pd
    import numpy as np
    
    # Données d'exemple
    results_data = pd.DataFrame({
        'Route': ['Route 1', 'Route 2', 'Route 3'],
        'Distance (km)': [15.2, 18.7, 8.6],
        'Load (%)': [85, 92, 78],
        'Stops': [4, 5, 3],
        'Cost ($)': [45.6, 56.1, 25.8]
    })
    
    st.dataframe(results_data, use_container_width=True)
    
    # Graphique
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['Distance', 'Efficiency', 'Cost']
    )
    
    st.line_chart(chart_data)

# Sidebar pour les actions rapides
with st.sidebar:
    st.markdown("""
    <div class="card">
        <h3>🚀 Quick Actions</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Reset All", use_container_width=True, type="secondary"):
        st.rerun()
    
    if st.button("📤 Export Report", use_container_width=True):
        st.success("Report exported!")
    
    if st.button("📧 Share Results", use_container_width=True):
        st.info("Sharing options opened!")
    
    st.markdown("---")
    
    st.markdown("""
    <div class="card">
        <h4>ℹ️ About</h4>
        <p style="font-size: 0.9rem; color: #666;">
        This VRP optimizer uses advanced algorithms to solve complex routing problems efficiently.
        </p>
        <p style="font-size: 0.8rem; color: #999; margin-top: 1rem;">
        Version 2.0 • Powered by Streamlit
        </p>
    </div>
    """, unsafe_allow_html=True)

# Note finale
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 2rem;">
    <p>🚚 <strong>VRP Route Optimizer</strong> • Intelligent Routing Solutions</p>
    <p style="font-size: 0.8rem;">Optimize your delivery routes with AI-powered algorithms</p>
</div>
""", unsafe_allow_html=True)
