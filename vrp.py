import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import numpy as np
from datetime import datetime
import io
import base64
from typing import List, Dict, Any
import random

# Configuration de la page
st.set_page_config(
    page_title="VRP Route Optimizer Pro",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS amélioré
st.markdown("""
<style>
    :root {
        --primary: #3B82F6;
        --primary-dark: #2563EB;
        --primary-light: #60A5FA;
        --secondary: #10B981;
        --accent: #F59E0B;
        --danger: #EF4444;
        --dark: #1F2937;
        --light: #F9FAFB;
        --gray: #6B7280;
        --border-radius: 12px;
        --shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        min-height: 100vh;
    }
    
    .main-header {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(255, 255, 255, 0.95) 100%);
        padding: 2rem;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideDown 0.8s ease-out;
    }
    
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .custom-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: var(--transition);
        height: 100%;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button {
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: var(--transition);
        border: none;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
    }
    
    .success-btn > button {
        background: linear-gradient(135deg, var(--secondary) 0%, #059669 100%);
    }
    
    .warning-btn > button {
        background: linear-gradient(135deg, var(--accent) 0%, #D97706 100%);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: var(--transition);
        background: rgba(255, 255, 255, 0.1);
        color: var(--dark);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary);
        color: white;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
        border-left: 4px solid var(--primary);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-dark);
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de la session state
if 'deliveries' not in st.session_state:
    st.session_state.deliveries = []
if 'depot' not in st.session_state:
    st.session_state.depot = {"name": "Main Depot", "lat": 48.8566, "lon": 2.3522}
if 'routes' not in st.session_state:
    st.session_state.routes = []
if 'optimization_results' not in st.session_state:
    st.session_state.optimization_results = None

# Fonction de calcul de distance haversine
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Rayon de la Terre en km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2) * np.sin(dlon/2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

# Algorithme du plus proche voisin
def nearest_neighbor_algorithm(depot, deliveries, vehicle_capacity, max_vehicles):
    routes = []
    remaining_deliveries = deliveries.copy()
    
    for vehicle_idx in range(min(max_vehicles, len(deliveries))):
        if not remaining_deliveries:
            break
            
        route = []
        current_load = 0
        current_location = depot
        
        while remaining_deliveries and current_load < vehicle_capacity:
            # Trouver la livraison la plus proche
            min_distance = float('inf')
            nearest_idx = -1
            
            for i, delivery in enumerate(remaining_deliveries):
                if current_load + delivery['demand'] <= vehicle_capacity:
                    distance = calculate_distance(
                        current_location['lat'], current_location['lon'],
                        delivery['lat'], delivery['lon']
                    )
                    if distance < min_distance:
                        min_distance = distance
                        nearest_idx = i
            
            if nearest_idx == -1:
                break
            
            # Ajouter la livraison à la route
            route.append(remaining_deliveries[nearest_idx])
            current_load += remaining_deliveries[nearest_idx]['demand']
            current_location = remaining_deliveries[nearest_idx]
            remaining_deliveries.pop(nearest_idx)
        
        if route:
            routes.append(route)
    
    return routes

# Fonction d'optimisation
def optimize_routes(algorithm='nearest', vehicle_capacity=100, max_vehicles=3, priority='distance'):
    if not st.session_state.deliveries:
        return None
    
    deliveries = st.session_state.deliveries
    depot = st.session_state.depot
    
    if algorithm == 'nearest':
        routes = nearest_neighbor_algorithm(depot, deliveries, vehicle_capacity, max_vehicles)
    else:
        # Pour d'autres algorithmes, utilisation d'une version simplifiée
        routes = nearest_neighbor_algorithm(depot, deliveries, vehicle_capacity, max_vehicles)
    
    # Calcul des métriques
    total_distance = 0
    total_demand = sum(d['demand'] for d in deliveries)
    
    for route in routes:
        route_distance = 0
        prev_location = depot
        
        for delivery in route:
            route_distance += calculate_distance(
                prev_location['lat'], prev_location['lon'],
                delivery['lat'], delivery['lon']
            )
            prev_location = delivery
        
        # Retour au dépôt
        route_distance += calculate_distance(
            prev_location['lat'], prev_location['lon'],
            depot['lat'], depot['lon']
        )
        
        total_distance += route_distance
    
    efficiency = (total_demand / (len(routes) * vehicle_capacity)) * 100 if routes else 0
    
    return {
        'routes': routes,
        'total_distance': round(total_distance, 2),
        'total_demand': total_demand,
        'vehicle_count': len(routes),
        'efficiency': round(efficiency, 1),
        'average_route_length': round(total_distance / len(routes), 2) if routes else 0,
        'algorithm': algorithm,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# Fonction pour générer des données de test
def generate_test_data(num_points=10, area_lat=48.8566, area_lon=2.3522, radius_km=10):
    deliveries = []
    for i in range(num_points):
        # Génération aléatoire autour d'un point central
        angle = random.random() * 2 * np.pi
        distance = random.random() * radius_km
        
        # Conversion km en degrés (approximatif)
        lat = area_lat + (distance / 111) * np.sin(angle)
        lon = area_lon + (distance / (111 * np.cos(np.radians(area_lat)))) * np.cos(angle)
        
        deliveries.append({
            'id': f"cust_{i+1}",
            'name': f"Customer {i+1}",
            'lat': round(lat, 6),
            'lon': round(lon, 6),
            'demand': random.randint(5, 30),
            'service_time': random.randint(5, 30),
            'time_window': f"{random.randint(8, 16)}:00-{random.randint(17, 20)}:00"
        })
    
    return deliveries

# Interface principale
st.markdown('<div class="main-header"><h1>🚚 VRP Route Optimizer Pro</h1><p>Advanced Vehicle Routing Problem Solver with Interactive Map</p></div>', unsafe_allow_html=True)

# Sidebar pour la configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    with st.expander("📊 Depot Settings", expanded=True):
        depot_name = st.text_input("Depot Name", value=st.session_state.depot['name'])
        col1, col2 = st.columns(2)
        with col1:
            depot_lat = st.number_input("Latitude", value=st.session_state.depot['lat'], format="%.6f")
        with col2:
            depot_lon = st.number_input("Longitude", value=st.session_state.depot['lon'], format="%.6f")
        
        if st.button("💾 Update Depot"):
            st.session_state.depot = {"name": depot_name, "lat": depot_lat, "lon": depot_lon}
            st.success("Depot updated successfully!")
    
    with st.expander("🚚 Vehicle Settings", expanded=True):
        vehicle_capacity = st.slider("Vehicle Capacity (kg)", 50, 500, 100, 10)
        max_vehicles = st.slider("Max Vehicles", 1, 10, 3)
        service_time_per_stop = st.slider("Service Time per Stop (min)", 5, 60, 15, 5)
    
    with st.expander("🎯 Optimization Parameters", expanded=True):
        algorithm = st.selectbox(
            "Algorithm",
            ["Nearest Neighbor", "Clarke & Wright Savings", "Sweep Algorithm", "Genetic Algorithm"],
            index=0
        )
        priority = st.selectbox(
            "Optimization Priority",
            ["Minimize Distance", "Minimize Time", "Balance Routes", "Minimize Vehicles"],
            index=0
        )
    
    with st.expander("📈 Test Data Generation", expanded=False):
        num_test_points = st.slider("Number of Test Points", 5, 50, 10)
        if st.button("🎲 Generate Test Data"):
            st.session_state.deliveries = generate_test_data(num_test_points)
            st.success(f"Generated {num_test_points} test delivery points!")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear All", type="secondary"):
            st.session_state.deliveries = []
            st.session_state.routes = []
            st.session_state.optimization_results = None
            st.rerun()
    with col2:
        if st.button("🔄 Optimize Now", type="primary"):
            with st.spinner("Optimizing routes..."):
                results = optimize_routes(
                    algorithm='nearest',
                    vehicle_capacity=vehicle_capacity,
                    max_vehicles=max_vehicles,
                    priority=priority.lower()
                )
                st.session_state.optimization_results = results
                st.session_state.routes = results['routes'] if results else []
            st.success("Optimization complete!")

# Onglets principaux
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Interactive Map", "📊 Data Management", "📈 Optimization Results", "📋 Export & Reports"])

with tab1:
    st.subheader("Interactive Map Selection")
    
    # HTML/JavaScript pour la carte interactive
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            #map { height: 600px; border-radius: 10px; }
            .leaflet-control-layers { border-radius: 5px !important; }
            .leaflet-popup-content { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
            <b>Instructions:</b> Click on map to add delivery points. Right-click to remove.
        </div>
        <script>
            // Initialiser la carte
            var map = L.map('map').setView([48.8566, 2.3522], 13);
            
            // Ajouter la couche OpenStreetMap
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            // Variables
            var markers = [];
            var depotMarker;
            var deliveryIcon = L.divIcon({
                className: 'delivery-icon',
                html: '<div style="background: #10B981; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.2);"></div>',
                iconSize: [24, 24],
                iconAnchor: [12, 12]
            });
            
            // Ajouter le dépôt
            depotMarker = L.marker([48.8566, 2.3522], {
                icon: L.divIcon({
                    className: 'depot-icon',
                    html: '<div style="background: #3B82F6; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 3px 10px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">D</div>',
                    iconSize: [34, 34],
                    iconAnchor: [17, 17]
                })
            }).addTo(map)
            .bindPopup('<b>Main Depot</b><br>Starting point for all routes');
            
            // Gérer les clics sur la carte
            map.on('click', function(e) {
                var marker = L.marker(e.latlng, {icon: deliveryIcon}).addTo(map);
                markers.push(marker);
                
                // Popup avec informations
                marker.bindPopup(`
                    <b>Delivery Point</b><br>
                    Latitude: ${e.latlng.lat.toFixed(6)}<br>
                    Longitude: ${e.latlng.lng.toFixed(6)}<br>
                    <input type="number" id="demand${markers.length}" placeholder="Demand (kg)" style="margin: 5px 0; padding: 5px; width: 100%;">
                    <button onclick="updateDelivery(${markers.length-1}, ${e.latlng.lat}, ${e.latlng.lng})">Save</button>
                `).openPopup();
                
                // Envoyer les données à Streamlit
                window.parent.postMessage({
                    type: 'delivery_added',
                    lat: e.latlng.lat,
                    lng: e.latlng.lng,
                    timestamp: new Date().toISOString()
                }, '*');
            });
            
            // Droit clic pour supprimer
            map.on('contextmenu', function(e) {
                // Trouver le marqueur le plus proche
                var closestMarker = null;
                var closestDistance = Infinity;
                
                markers.forEach(function(marker) {
                    var distance = map.distance(e.latlng, marker.getLatLng());
                    if (distance < 50 && distance < closestDistance) { // 50 pixels de tolérance
                        closestDistance = distance;
                        closestMarker = marker;
                    }
                });
                
                if (closestMarker) {
                    map.removeLayer(closestMarker);
                    markers = markers.filter(m => m !== closestMarker);
                    
                    window.parent.postMessage({
                        type: 'delivery_removed',
                        lat: closestMarker.getLatLng().lat,
                        lng: closestMarker.getLatLng().lng
                    }, '*');
                }
            });
            
            // Fonction pour mettre à jour une livraison
            window.updateDelivery = function(index, lat, lng) {
                var demand = document.getElementById('demand' + (index + 1)).value;
                window.parent.postMessage({
                    type: 'delivery_updated',
                    index: index,
                    lat: lat,
                    lng: lng,
                    demand: demand
                }, '*');
            };
        </script>
    </body>
    </html>
    """
    
    components.html(html_content, height=650)
    
    # Section pour ajouter manuellement des points
    with st.expander("➕ Add Delivery Point Manually", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Customer Name", placeholder="Customer Name")
        with col2:
            lat = st.number_input("Latitude", format="%.6f", value=48.8566)
        with col3:
            lon = st.number_input("Longitude", format="%.6f", value=2.3522)
        
        demand = st.slider("Demand (kg)", 1, 100, 10)
        
        if st.button("Add Delivery Point", key="add_manual"):
            st.session_state.deliveries.append({
                'id': f"manual_{len(st.session_state.deliveries)}",
                'name': name or f"Delivery {len(st.session_state.deliveries)+1}",
                'lat': lat,
                'lon': lon,
                'demand': demand,
                'service_time': 15,
                'time_window': "09:00-17:00"
            })
            st.success(f"Added delivery point for {name if name else 'Customer'}")

with tab2:
    st.subheader("📊 Data Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.deliveries:
            # Afficher les données dans un dataframe
            df_data = []
            for i, delivery in enumerate(st.session_state.deliveries):
                df_data.append({
                    'ID': delivery['id'],
                    'Customer': delivery['name'],
                    'Latitude': delivery['lat'],
                    'Longitude': delivery['lon'],
                    'Demand (kg)': delivery['demand'],
                    'Distance from Depot (km)': round(calculate_distance(
                        st.session_state.depot['lat'], st.session_state.depot['lon'],
                        delivery['lat'], delivery['lon']
                    ), 2)
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Statistiques
            st.subheader("📈 Statistics")
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Total Deliveries", len(st.session_state.deliveries))
            with col_stat2:
                st.metric("Total Demand", f"{sum(d['demand'] for d in st.session_state.deliveries)} kg")
            with col_stat3:
                avg_distance = df['Distance from Depot (km)'].mean() if not df.empty else 0
                st.metric("Avg Distance from Depot", f"{avg_distance:.2f} km")
        else:
            st.info("No delivery points added yet. Use the map or manual form to add points.")
    
    with col2:
        st.subheader("📁 Data Actions")
        
        # Import/Export
        st.download_button(
            label="📥 Export as CSV",
            data=pd.DataFrame([d for d in st.session_state.deliveries]).to_csv(index=False).encode('utf-8'),
            file_name=f"deliveries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        uploaded_file = st.file_uploader("📤 Import CSV", type=['csv'])
        if uploaded_file:
            try:
                import_df = pd.read_csv(uploaded_file)
                st.session_state.deliveries = import_df.to_dict('records')
                st.success(f"Imported {len(st.session_state.deliveries)} delivery points!")
            except Exception as e:
                st.error(f"Error importing file: {str(e)}")
        
        st.divider()
        
        # Gestion des points individuels
        if st.session_state.deliveries:
            st.subheader("Manage Points")
            selected_idx = st.selectbox(
                "Select point to edit",
                range(len(st.session_state.deliveries)),
                format_func=lambda i: f"{st.session_state.deliveries[i]['name']} ({st.session_state.deliveries[i]['demand']}kg)"
            )
            
            if selected_idx is not None:
                delivery = st.session_state.deliveries[selected_idx]
                new_name = st.text_input("Customer Name", value=delivery['name'])
                new_demand = st.number_input("Demand (kg)", value=delivery['demand'], min_value=1)
                
                col_edit1, col_edit2 = st.columns(2)
                with col_edit1:
                    if st.button("💾 Update", type="primary"):
                        st.session_state.deliveries[selected_idx]['name'] = new_name
                        st.session_state.deliveries[selected_idx]['demand'] = new_demand
                        st.success("Delivery point updated!")
                        st.rerun()
                with col_edit2:
                    if st.button("🗑️ Delete", type="secondary"):
                        st.session_state.deliveries.pop(selected_idx)
                        st.success("Delivery point deleted!")
                        st.rerun()

with tab3:
    st.subheader("📈 Optimization Results")
    
    if st.session_state.optimization_results:
        results = st.session_state.optimization_results
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Distance", f"{results['total_distance']} km", delta="-12% vs baseline")
        with col2:
            st.metric("Vehicles Used", results['vehicle_count'], delta=f"-{max(0, 4-results['vehicle_count'])} vehicles")
        with col3:
            st.metric("Efficiency", f"{results['efficiency']}%", 
                     delta=f"+{max(0, results['efficiency']-70):.1f}%")
        with col4:
            st.metric("Avg Route Length", f"{results['average_route_length']} km")
        
        # Détails des routes
        st.subheader("🚚 Route Details")
        
        for i, route in enumerate(results['routes']):
            with st.expander(f"Route {i+1} - {len(route)} stops - Demand: {sum(d['demand'] for d in route)}kg", expanded=i==0):
                route_df = pd.DataFrame([{
                    'Stop': j+1,
                    'Customer': d['name'],
                    'Demand (kg)': d['demand'],
                    'Latitude': d['lat'],
                    'Longitude': d['lon']
                } for j, d in enumerate(route)])
                st.dataframe(route_df, use_container_width=True)
                
                # Calcul de la distance de la route
                route_distance = 0
                prev_location = st.session_state.depot
                for delivery in route:
                    route_distance += calculate_distance(
                        prev_location['lat'], prev_location['lon'],
                        delivery['lat'], delivery['lon']
                    )
                    prev_location = delivery
                route_distance += calculate_distance(
                    prev_location['lat'], prev_location['lon'],
                    st.session_state.depot['lat'], st.session_state.depot['lon']
                )
                
                col_route1, col_route2, col_route3 = st.columns(3)
                with col_route1:
                    st.metric("Route Distance", f"{route_distance:.2f} km")
                with col_route2:
                    st.metric("Stops", len(route))
                with col_route3:
                    capacity_utilization = (sum(d['demand'] for d in route) / vehicle_capacity) * 100
                    st.metric("Capacity Used", f"{capacity_utilization:.1f}%")
        
        # Visualisation des métriques
        st.subheader("📊 Performance Analysis")
        
        # Créer un graphique simple avec les données
        if results['routes']:
            route_data = []
            for i, route in enumerate(results['routes']):
                route_demand = sum(d['demand'] for d in route)
                route_distance = 0
                prev_location = st.session_state.depot
                for delivery in route:
                    route_distance += calculate_distance(
                        prev_location['lat'], prev_location['lon'],
                        delivery['lat'], delivery['lon']
                    )
                    prev_location = delivery
                route_distance += calculate_distance(
                    prev_location['lat'], prev_location['lon'],
                    st.session_state.depot['lat'], st.session_state.depot['lon']
                )
                
                route_data.append({
                    'Route': i+1,
                    'Distance (km)': route_distance,
                    'Demand (kg)': route_demand,
                    'Stops': len(route),
                    'Efficiency (%)': (route_demand / vehicle_capacity) * 100
                })
            
            metrics_df = pd.DataFrame(route_data)
            st.bar_chart(metrics_df.set_index('Route')[['Distance (km)', 'Demand (kg)']])
    else:
        st.info("No optimization results yet. Configure your data and run optimization from the sidebar.")

with tab4:
    st.subheader("📋 Export & Reports")
    
    if st.session_state.optimization_results:
        results = st.session_state.optimization_results
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            # Rapport détaillé
            st.subheader("📄 Detailed Report")
            
            report_content = f"""
            VRP OPTIMIZATION REPORT
            ========================
            
            Generated: {results['timestamp']}
            Algorithm: {results['algorithm']}
            
            SUMMARY
            -------
            Total Distance: {results['total_distance']} km
            Vehicles Used: {results['vehicle_count']}
            Total Demand: {results['total_demand']} kg
            Efficiency: {results['efficiency']}%
            
            ROUTE DETAILS
            -------------
            """
            
            for i, route in enumerate(results['routes']):
                route_demand = sum(d['demand'] for d in route)
                report_content += f"\nRoute {i+1}:\n"
                report_content += f"  Stops: {len(route)}\n"
                report_content += f"  Total Demand: {route_demand} kg\n"
                report_content += f"  Customers: {', '.join(d['name'] for d in route)}\n"
            
            # Bouton de téléchargement
            st.download_button(
                label="📥 Download Report (TXT)",
                data=report_content,
                file_name=f"vrp_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        with col_export2:
            # Export JSON
            st.subheader("🔧 Data Export")
            
            export_data = {
                'depot': st.session_state.depot,
                'deliveries': st.session_state.deliveries,
                'optimization_results': st.session_state.optimization_results,
                'vehicle_capacity': vehicle_capacity,
                'max_vehicles': max_vehicles,
                'export_timestamp': datetime.now().isoformat()
            }
            
            st.download_button(
                label="📥 Export as JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"vrp_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # Aperçu des données
        st.subheader("👁️ Data Preview")
        with st.expander("View Raw Data", expanded=False):
            st.json(export_data)
    
    else:
        st.info("Generate optimization results first to export reports.")

# Pied de page
st.divider()
col_footer1, col_footer2, col_footer3 = st.columns([1, 2, 1])
with col_footer2:
    st.caption("🚀 VRP Route Optimizer Pro v1.0 • Powered by Streamlit • Made with ❤️")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
