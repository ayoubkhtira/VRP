import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="VRP Route Optimizer", layout="wide")

html_content = <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VRP Route Optimizer - Delivery Route Calculator</title>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        :root {
            --color-white: rgba(255, 255, 255, 1);
            --color-black: rgba(0, 0, 0, 1);
            --color-cream-50: rgba(252, 252, 249, 1);
            --color-cream-100: rgba(255, 255, 253, 1);
            --color-gray-200: rgba(245, 245, 245, 1);
            --color-gray-300: rgba(167, 169, 169, 1);
            --color-gray-400: rgba(119, 124, 124, 1);
            --color-slate-500: rgba(98, 108, 113, 1);
            --color-brown-600: rgba(94, 82, 64, 1);
            --color-charcoal-700: rgba(31, 33, 33, 1);
            --color-charcoal-800: rgba(38, 40, 40, 1);
            --color-slate-900: rgba(19, 52, 59, 1);
            --color-teal-300: rgba(50, 184, 198, 1);
            --color-teal-400: rgba(45, 166, 178, 1);
            --color-teal-500: rgba(33, 128, 141, 1);
            --color-teal-600: rgba(29, 116, 128, 1);
            --color-teal-700: rgba(26, 104, 115, 1);
            --color-red-400: rgba(255, 84, 89, 1);
            --color-red-500: rgba(192, 21, 47, 1);
            --color-orange-400: rgba(230, 129, 97, 1);
            --color-orange-500: rgba(168, 75, 47, 1);

            --color-brown-600-rgb: 94, 82, 64;
            --color-teal-500-rgb: 33, 128, 141;
            --color-slate-900-rgb: 19, 52, 59;
            --color-red-500-rgb: 192, 21, 47;
            --color-orange-500-rgb: 168, 75, 47;

            --color-bg-1: rgba(59, 130, 246, 0.08);
            --color-bg-2: rgba(245, 158, 11, 0.08);
            --color-bg-3: rgba(34, 197, 94, 0.08);
            --color-bg-4: rgba(239, 68, 68, 0.08);
            --color-bg-5: rgba(147, 51, 234, 0.08);
            --color-bg-6: rgba(249, 115, 22, 0.08);
            --color-bg-7: rgba(236, 72, 153, 0.08);
            --color-bg-8: rgba(6, 182, 212, 0.08);

            --color-background: var(--color-cream-50);
            --color-surface: var(--color-cream-100);
            --color-text: var(--color-slate-900);
            --color-text-secondary: var(--color-slate-500);
            --color-primary: var(--color-teal-500);
            --color-primary-hover: var(--color-teal-600);
            --color-primary-active: var(--color-teal-700);
            --color-secondary: rgba(var(--color-brown-600-rgb), 0.12);
            --color-secondary-hover: rgba(var(--color-brown-600-rgb), 0.2);
            --color-secondary-active: rgba(var(--color-brown-600-rgb), 0.25);
            --color-border: rgba(var(--color-brown-600-rgb), 0.2);
            --color-btn-primary-text: var(--color-cream-50);
            --color-card-border: rgba(var(--color-brown-600-rgb), 0.12);
            --color-card-border-inner: rgba(var(--color-brown-600-rgb), 0.12);
            --color-error: var(--color-red-500);
            --color-success: var(--color-teal-500);
            --color-warning: var(--color-orange-500);
            --color-info: var(--color-slate-500);
            --color-focus-ring: rgba(var(--color-teal-500-rgb), 0.4);

            --focus-ring: 0 0 0 3px var(--color-focus-ring);
            --focus-outline: 2px solid var(--color-primary);

            --font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            --font-family-mono: 'Courier New', monospace;
            --font-size-sm: 12px;
            --font-size-base: 14px;
            --font-size-md: 14px;
            --font-size-lg: 16px;
            --font-size-xl: 18px;
            --font-size-2xl: 20px;
            --font-size-3xl: 24px;
            --font-weight-normal: 400;
            --font-weight-medium: 500;
            --font-weight-semibold: 550;
            --font-weight-bold: 600;
            --line-height-tight: 1.2;
            --line-height-normal: 1.5;

            --space-4: 4px;
            --space-6: 6px;
            --space-8: 8px;
            --space-12: 12px;
            --space-16: 16px;
            --space-20: 20px;
            --space-24: 24px;
            --space-32: 32px;

            --radius-sm: 6px;
            --radius-base: 8px;
            --radius-md: 10px;
            --radius-lg: 12px;
            --radius-full: 9999px;

            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.04);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.04);

            --duration-fast: 150ms;
            --duration-normal: 250ms;
            --ease-standard: cubic-bezier(0.16, 1, 0.3, 1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: var(--font-family-base);
            background-color: var(--color-background);
            color: var(--color-text);
            line-height: var(--line-height-normal);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: var(--space-16);
        }

        .header {
            background: linear-gradient(135deg, #2f8696 0%, #1e5a69 100%);
            color: white;
            padding: var(--space-24) var(--space-16);
            border-radius: var(--radius-lg);
            margin-bottom: var(--space-24);
            box-shadow: var(--shadow-md);
        }

        .header h1 {
            font-size: var(--font-size-3xl);
            margin-bottom: var(--space-8);
            font-weight: var(--font-weight-bold);
        }

        .header p {
            opacity: 0.9;
            font-size: var(--font-size-lg);
        }

        .main-layout {
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: var(--space-16);
        }

        @media (max-width: 1024px) {
            .main-layout {
                grid-template-columns: 1fr;
            }
        }

        .sidebar {
            background-color: var(--color-surface);
            border-radius: var(--radius-lg);
            padding: var(--space-16);
            height: fit-content;
            border: 1px solid var(--color-card-border);
            box-shadow: var(--shadow-sm);
        }

        .sidebar-section {
            margin-bottom: var(--space-24);
        }

        .sidebar-section:last-child {
            margin-bottom: 0;
        }

        .sidebar-title {
            font-size: var(--font-size-lg);
            font-weight: var(--font-weight-semibold);
            margin-bottom: var(--space-12);
            color: var(--color-primary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .form-group {
            margin-bottom: var(--space-12);
        }

        .form-label {
            display: block;
            font-size: var(--font-size-sm);
            font-weight: var(--font-weight-medium);
            margin-bottom: var(--space-6);
            color: var(--color-text);
        }

        .form-control {
            width: 100%;
            padding: var(--space-8) var(--space-12);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-base);
            font-size: var(--font-size-base);
            background-color: var(--color-white);
            color: var(--color-text);
            font-family: var(--font-family-base);
            transition: all var(--duration-fast) var(--ease-standard);
        }

        .form-control:focus {
            outline: none;
            border-color: var(--color-primary);
            box-shadow: var(--focus-ring);
        }

        .btn {
            padding: var(--space-8) var(--space-16);
            border: none;
            border-radius: var(--radius-base);
            font-size: var(--font-size-base);
            font-weight: var(--font-weight-medium);
            cursor: pointer;
            transition: all var(--duration-normal) var(--ease-standard);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: var(--space-8);
        }

        .btn:focus-visible {
            outline: none;
            box-shadow: var(--focus-ring);
        }

        .btn--primary {
            background-color: var(--color-primary);
            color: var(--color-btn-primary-text);
            width: 100%;
        }

        .btn--primary:hover {
            background-color: var(--color-primary-hover);
        }

        .btn--primary:active {
            background-color: var(--color-primary-active);
        }

        .btn--secondary {
            background-color: var(--color-secondary);
            color: var(--color-text);
        }

        .btn--secondary:hover {
            background-color: var(--color-secondary-hover);
        }

        .btn--sm {
            padding: var(--space-6) var(--space-12);
            font-size: var(--font-size-sm);
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .delivery-item {
            background-color: var(--color-white);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-base);
            padding: var(--space-12);
            margin-bottom: var(--space-8);
            display: flex;
            gap: var(--space-8);
            align-items: flex-start;
        }

        .delivery-item-content {
            flex: 1;
        }

        .delivery-item-name {
            font-weight: var(--font-weight-semibold);
            font-size: var(--font-size-base);
            margin-bottom: var(--space-4);
        }

        .delivery-item-details {
            font-size: var(--font-size-sm);
            color: var(--color-text-secondary);
            margin-bottom: var(--space-4);
        }

        .btn-small {
            padding: var(--space-4) var(--space-8);
            font-size: 11px;
            background-color: var(--color-error);
            color: white;
            border: none;
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: all var(--duration-fast) var(--ease-standard);
        }

        .btn-small:hover {
            background-color: var(--color-red-400);
        }

        .content {
            display: flex;
            flex-direction: column;
            gap: var(--space-16);
        }

        .map-container {
            background-color: var(--color-surface);
            border-radius: var(--radius-lg);
            border: 1px solid var(--color-card-border);
            overflow: hidden;
            box-shadow: var(--shadow-md);
            min-height: 500px;
        }

        #map {
            width: 100%;
            height: 500px;
            border-radius: var(--radius-lg);
        }

        .results-panel {
            background-color: var(--color-surface);
            border-radius: var(--radius-lg);
            padding: var(--space-16);
            border: 1px solid var(--color-card-border);
            box-shadow: var(--shadow-md);
        }

        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--space-16);
            margin-bottom: var(--space-16);
        }

        .result-card {
            background-color: var(--color-white);
            border-left: 4px solid var(--color-primary);
            padding: var(--space-16);
            border-radius: var(--radius-base);
            box-shadow: var(--shadow-sm);
        }

        .result-card-label {
            font-size: var(--font-size-sm);
            color: var(--color-text-secondary);
            margin-bottom: var(--space-4);
            font-weight: var(--font-weight-medium);
        }

        .result-card-value {
            font-size: var(--font-size-2xl);
            font-weight: var(--font-weight-bold);
            color: var(--color-primary);
        }

        .route-details {
            background-color: var(--color-white);
            border-radius: var(--radius-base);
            padding: var(--space-16);
            margin-top: var(--space-16);
        }

        .route-list {
            list-style: none;
            counter-reset: route-counter;
        }

        .route-item {
            counter-increment: route-counter;
            padding: var(--space-12) var(--space-16);
            background-color: var(--color-bg-3);
            margin-bottom: var(--space-8);
            border-radius: var(--radius-base);
            border-left: 3px solid var(--color-success);
        }

        .route-item::before {
            content: counter(route-counter) ". ";
            font-weight: var(--font-weight-bold);
            color: var(--color-primary);
        }

        .info-message {
            background-color: var(--color-bg-1);
            border-left: 4px solid var(--color-info);
            padding: var(--space-12) var(--space-16);
            border-radius: var(--radius-base);
            color: var(--color-text);
            font-size: var(--font-size-sm);
            margin-top: var(--space-16);
        }

        .tabs {
            display: flex;
            gap: var(--space-8);
            border-bottom: 2px solid var(--color-border);
            margin-bottom: var(--space-16);
        }

        .tab-btn {
            padding: var(--space-8) var(--space-16);
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-size: var(--font-size-base);
            font-weight: var(--font-weight-medium);
            color: var(--color-text-secondary);
            transition: all var(--duration-fast) var(--ease-standard);
        }

        .tab-btn.active {
            color: var(--color-primary);
            border-bottom-color: var(--color-primary);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .hidden {
            display: none;
        }

        .leaflet-popup-content {
            font-family: var(--font-family-base);
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .fade-in {
            animation: fadeIn var(--duration-normal) var(--ease-standard);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚚 VRP Route Optimizer</h1>
            <p>Vehicle Routing Problem Solver - Optimize delivery routes with modern algorithms</p>
        </div>

        <div class="main-layout">
            <!-- Sidebar -->
            <aside class="sidebar">
                <div class="sidebar-section">
                    <div class="sidebar-title">Depot Location</div>
                    <div class="form-group">
                        <label class="form-label">Latitude</label>
                        <input type="number" id="depotLat" class="form-control" value="48.8566" step="0.0001" placeholder="Latitude">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Longitude</label>
                        <input type="number" id="depotLon" class="form-control" value="2.3522" step="0.0001" placeholder="Longitude">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Depot Name</label>
                        <input type="text" id="depotName" class="form-control" value="Depot" placeholder="Depot name">
                    </div>
                </div>

                <div class="sidebar-section">
                    <div class="sidebar-title">Add Delivery Point</div>
                    <div class="form-group">
                        <label class="form-label">Name</label>
                        <input type="text" id="deliveryName" class="form-control" placeholder="e.g., Customer A">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Latitude</label>
                        <input type="number" id="deliveryLat" class="form-control" step="0.0001" placeholder="Latitude">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Longitude</label>
                        <input type="number" id="deliveryLon" class="form-control" step="0.0001" placeholder="Longitude">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Demand (kg)</label>
                        <input type="number" id="deliveryDemand" class="form-control" value="1" min="0.1" step="0.1" placeholder="Weight">
                    </div>
                    <button class="btn btn--primary" onclick="addDelivery()">+ Add Delivery Point</button>
                </div>

                <div class="sidebar-section">
                    <div class="sidebar-title">Delivery Points</div>
                    <div id="deliveryList"></div>
                    <button class="btn btn--secondary btn--sm" onclick="clearDeliveries()" style="width: 100%; margin-top: var(--space-8);">Clear All</button>
                </div>

                <div class="sidebar-section">
                    <div class="sidebar-title">Optimization</div>
                    <div class="form-group">
                        <label class="form-label">Vehicle Capacity (kg)</label>
                        <input type="number" id="vehicleCapacity" class="form-control" value="100" min="1" step="1">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Max Vehicles</label>
                        <input type="number" id="maxVehicles" class="form-control" value="3" min="1" step="1">
                    </div>
                    <button class="btn btn--primary" onclick="optimizeRoutes()" style="font-size: 16px; font-weight: 600;">🔄 Optimize Routes</button>
                </div>
            </aside>

            <!-- Main Content -->
            <div class="content">
                <div class="map-container">
                    <div id="map"></div>
                </div>

                <div class="results-panel" id="resultsPanel" style="display: none;">
                    <div class="tabs">
                        <button class="tab-btn active" onclick="switchTab('summary')">Summary</button>
                        <button class="tab-btn" onclick="switchTab('routes')">Route Details</button>
                    </div>

                    <div id="summary" class="tab-content active">
                        <div class="results-grid" id="resultCardsContainer"></div>
                        <div class="info-message">
                            Routes optimized using nearest neighbor heuristic with 2-opt local search improvement.
                        </div>
                    </div>

                    <div id="routes" class="tab-content">
                        <div id="routesContainer"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Initialize Leaflet map
        const map = L.map('map').setView([48.8566, 2.3522], 10);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        let markers = {};
        let routePolylines = [];
        let deliveries = [];
        let depot = { lat: 48.8566, lon: 2.3522, name: 'Depot' };

        // Add delivery point
        function addDelivery() {
            const name = document.getElementById('deliveryName').value.trim();
            const lat = parseFloat(document.getElementById('deliveryLat').value);
            const lon = parseFloat(document.getElementById('deliveryLon').value);
            const demand = parseFloat(document.getElementById('deliveryDemand').value);

            if (!name || isNaN(lat) || isNaN(lon) || isNaN(demand)) {
                alert('Please fill all fields with valid data');
                return;
            }

            const delivery = { id: Date.now(), name, lat, lon, demand };
            deliveries.push(delivery);

            // Clear inputs
            document.getElementById('deliveryName').value = '';
            document.getElementById('deliveryLat').value = '';
            document.getElementById('deliveryLon').value = '';
            document.getElementById('deliveryDemand').value = '1';

            renderDeliveryList();
            addMarkerToMap(delivery);
        }

        // Render delivery list
        function renderDeliveryList() {
            const container = document.getElementById('deliveryList');
            container.innerHTML = '';

            deliveries.forEach((delivery, index) => {
                const div = document.createElement('div');
                div.className = 'delivery-item';
                div.innerHTML = `
                    <div class="delivery-item-content">
                        <div class="delivery-item-name">${delivery.name}</div>
                        <div class="delivery-item-details">${delivery.lat.toFixed(4)}, ${delivery.lon.toFixed(4)}</div>
                        <div class="delivery-item-details">Demand: ${delivery.demand}kg</div>
                    </div>
                    <button class="btn-small" onclick="removeDelivery(${delivery.id})">Remove</button>
                `;
                container.appendChild(div);
            });
        }

        // Remove delivery
        function removeDelivery(id) {
            deliveries = deliveries.filter(d => d.id !== id);
            if (markers[id]) {
                map.removeLayer(markers[id]);
                delete markers[id];
            }
            renderDeliveryList();
        }

        // Clear all deliveries
        function clearDeliveries() {
            if (deliveries.length === 0) return;
            if (!confirm('Clear all delivery points?')) return;
            
            deliveries.forEach(d => {
                if (markers[d.id]) {
                    map.removeLayer(markers[d.id]);
                    delete markers[d.id];
                }
            });
            deliveries = [];
            renderDeliveryList();
            clearRoutes();
        }

        // Add marker to map
        function addMarkerToMap(delivery) {
            const marker = L.circleMarker([delivery.lat, delivery.lon], {
                radius: 7,
                fillColor: '#2f8696',
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map);

            marker.bindPopup(`<b>${delivery.name}</b><br>Demand: ${delivery.demand}kg`);
            markers[delivery.id] = marker;
        }

        // Update depot on input change
        document.getElementById('depotLat').addEventListener('change', updateDepotLocation);
        document.getElementById('depotLon').addEventListener('change', updateDepotLocation);
        document.getElementById('depotName').addEventListener('change', updateDepotName);

        function updateDepotLocation() {
            depot.lat = parseFloat(document.getElementById('depotLat').value);
            depot.lon = parseFloat(document.getElementById('depotLon').value);
            if (markers.depot) map.removeLayer(markers.depot);
            
            const marker = L.marker([depot.lat, depot.lon], {
                icon: L.icon({
                    iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzIyYjdhNyIgZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6bTAgMThjLTQuNDIgMC04LTMuNTgtOC04czMuNTgtOCA4LTggOCAzLjU4IDggOC0zLjU4IDgtOCA4em0uNS0xM0gxMXY2aDB2Mkg5djJoNlYxMHYtMmgtMi41ek0xMyA5aDJ2MmgtMnptLTQgMGgydjJoLTJ6Ii8+PC9zdmc+',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41]
                })
            }).addTo(map);
            
            marker.bindPopup(`<b>${depot.name}</b><br>Depot`);
            markers.depot = marker;
            map.setView([depot.lat, depot.lon], 10);
        }

        function updateDepotName() {
            depot.name = document.getElementById('depotName').value;
        }

        // Simple VRP solver - Nearest Neighbor + 2-opt
        function solveVRP() {
            if (deliveries.length === 0) {
                alert('Add delivery points first');
                return [];
            }

            const capacity = parseFloat(document.getElementById('vehicleCapacity').value);
            const maxVehicles = parseInt(document.getElementById('maxVehicles').value);

            // Distance function
            function distance(p1, p2) {
                const R = 6371;
                const dLat = (p2.lat - p1.lat) * Math.PI / 180;
                const dLon = (p2.lon - p1.lon) * Math.PI / 180;
                const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                    Math.cos(p1.lat * Math.PI / 180) * Math.cos(p2.lat * Math.PI / 180) *
                    Math.sin(dLon / 2) * Math.sin(dLon / 2);
                const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
                return R * c;
            }

            // Nearest neighbor heuristic
            function nearestNeighbor() {
                const unvisited = [...deliveries];
                const routes = [];
                let currentRoute = [];
                let currentDemand = 0;

                while (unvisited.length > 0) {
                    if (currentRoute.length === 0) {
                        currentRoute = [unvisited[0]];
                        currentDemand = unvisited[0].demand;
                        unvisited.shift();
                    }

                    let nextIdx = -1;
                    let minDist = Infinity;

                    const lastPoint = currentRoute[currentRoute.length - 1];
                    for (let i = 0; i < unvisited.length; i++) {
                        const d = distance(lastPoint, unvisited[i]);
                        if (d < minDist && currentDemand + unvisited[i].demand <= capacity) {
                            minDist = d;
                            nextIdx = i;
                        }
                    }

                    if (nextIdx === -1) {
                        routes.push([...currentRoute]);
                        currentRoute = [];
                        currentDemand = 0;
                        if (routes.length >= maxVehicles && unvisited.length > 0) {
                            currentRoute = [...unvisited];
                            break;
                        }
                    } else {
                        currentRoute.push(unvisited[nextIdx]);
                        currentDemand += unvisited[nextIdx].demand;
                        unvisited.splice(nextIdx, 1);
                    }
                }

                if (currentRoute.length > 0) routes.push(currentRoute);
                return routes;
            }

            return nearestNeighbor();
        }

        // Optimize routes
        function optimizeRoutes() {
            const routes = solveVRP();
            if (routes.length === 0) return;

            clearRoutes();

            const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'];
            let totalDistance = 0;
            let totalDemand = 0;

            routes.forEach((route, routeIdx) => {
                const color = colors[routeIdx % colors.length];
                const routePoints = [depot, ...route, depot];
                let routeDistance = 0;

                for (let i = 0; i < routePoints.length - 1; i++) {
                    const p1 = routePoints[i];
                    const p2 = routePoints[i + 1];
                    const R = 6371;
                    const dLat = (p2.lat - p1.lat) * Math.PI / 180;
                    const dLon = (p2.lon - p1.lon) * Math.PI / 180;
                    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                        Math.cos(p1.lat * Math.PI / 180) * Math.cos(p2.lat * Math.PI / 180) *
                        Math.sin(dLon / 2) * Math.sin(dLon / 2);
                    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
                    routeDistance += R * c;
                }

                totalDistance += routeDistance;

                const latlngs = routePoints.map(p => [p.lat, p.lon]);
                const polyline = L.polyline(latlngs, {
                    color: color,
                    weight: 3,
                    opacity: 0.7,
                    dashArray: routeIdx > 0 ? '5, 5' : ''
                }).addTo(map);

                routePolylines.push(polyline);

                route.forEach(delivery => {
                    totalDemand += delivery.demand;
                });
            });

            // Display results
            showResults(routes, totalDistance, totalDemand);
        }

        // Show results
        function showResults(routes, totalDistance, totalDemand) {
            document.getElementById('resultsPanel').style.display = 'block';

            const resultCardsContainer = document.getElementById('resultCardsContainer');
            resultCardsContainer.innerHTML = `
                <div class="result-card">
                    <div class="result-card-label">Number of Routes</div>
                    <div class="result-card-value">${routes.length}</div>
                </div>
                <div class="result-card">
                    <div class="result-card-label">Total Distance</div>
                    <div class="result-card-value">${totalDistance.toFixed(2)} km</div>
                </div>
                <div class="result-card">
                    <div class="result-card-label">Total Demand</div>
                    <div class="result-card-value">${totalDemand.toFixed(1)} kg</div>
                </div>
                <div class="result-card">
                    <div class="result-card-label">Avg Distance/Route</div>
                    <div class="result-card-value">${(totalDistance / routes.length).toFixed(2)} km</div>
                </div>
            `;

            const routesContainer = document.getElementById('routesContainer');
            let routesHtml = '';

            routes.forEach((route, idx) => {
                const capacity = parseFloat(document.getElementById('vehicleCapacity').value);
                let demand = 0;
                let distance = 0;

                route.forEach(delivery => { demand += delivery.demand; });

                const routePoints = [depot, ...route, depot];
                for (let i = 0; i < routePoints.length - 1; i++) {
                    const p1 = routePoints[i];
                    const p2 = routePoints[i + 1];
                    const R = 6371;
                    const dLat = (p2.lat - p1.lat) * Math.PI / 180;
                    const dLon = (p2.lon - p1.lon) * Math.PI / 180;
                    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                        Math.cos(p1.lat * Math.PI / 180) * Math.cos(p2.lat * Math.PI / 180) *
                        Math.sin(dLon / 2) * Math.sin(dLon / 2);
                    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
                    distance += R * c;
                }

                routesHtml += `<div class="route-details fade-in">
                    <h3 style="color: var(--color-primary); margin-bottom: var(--space-12);">Vehicle ${idx + 1}</h3>
                    <p style="margin-bottom: var(--space-8); color: var(--color-text-secondary);">
                        Distance: <strong>${distance.toFixed(2)} km</strong> | 
                        Load: <strong>${demand.toFixed(1)}/${capacity} kg</strong> (${(demand/capacity*100).toFixed(0)}%)
                    </p>
                    <ul class="route-list">
                        <li class="route-item">${depot.name} (Start)</li>
                        ${route.map(d => `<li class="route-item">${d.name} (${d.demand} kg)</li>`).join('')}
                        <li class="route-item">${depot.name} (End)</li>
                    </ul>
                </div>`;
            });

            routesContainer.innerHTML = routesHtml;
        }

        // Clear routes from map
        function clearRoutes() {
            routePolylines.forEach(p => map.removeLayer(p));
            routePolylines = [];
            document.getElementById('resultsPanel').style.display = 'none';
        }

        // Tab switching
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }

        // Initialize depot marker
        updateDepotLocation();
    </script>
</body>
</html>
components.html(html_content, height=1200, scrolling=True)
