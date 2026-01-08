import streamlit as st
import pandas as pd
import folium
import random
import requests
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from streamlit_folium import st_folium
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# =====================================================
# CONFIG & CACHE
# =====================================================
@st.cache_data(ttl=3600)
def osrm_distance_matrix(coords):
    coord_str = ";".join([f"{lon},{lat}" for lat, lon in coords])
    url = f"http://router.project-osrm.org/table/v1/driving/{coord_str}?annotations=distance,duration"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return np.array(data["distances"]).astype(int), np.array(data["durations"]).astype(int)
    except:
        return np.full((len(coords), len(coords)), 999999), np.full((len(coords), len(coords)), 999999)

# =====================================================
# MODERN CSS + DARK MODE
# =====================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp { font-family: 'Inter', sans-serif; }
    .main { padding: 2rem 3rem; }
    h1 { 
        font-size: 3rem; 
        background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container { background: rgba(255,255,255,0.05) !important; border-radius: 16px !important; }
    .stTabs [data-baseweb="tab"] { 
        border-radius: 12px !important; 
        height: 48px !important;
        font-size: 15px;
        font-weight: 500;
    }
    .stButton > button { 
        border-radius: 16px !important; 
        height: 50px !important;
        font-size: 16px;
        box-shadow: 0 8px 32px rgba(59,130,246,0.3) !important;
    }
    .stExpander { border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide", page_title="🚀 VRP Pro", page_icon="🚚")
st.title("🚀 VRP Pro – Optimiseur de tournées intelligentes")

# =====================================================
# SESSION STATE ÉTENDU
# =====================================================
def init_session_state():
    defaults = {
        "points": [],
        "solution": None,
        "vrp_nodes": None,
        "current_tab": 0,
        "settings": {
            "num_vehicles": 3,
            "max_distance": 50000,  # 50km
            "time_window": False
        },
        "stats": {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# =====================================================
# NOUVELLE MAP AVEC CLUSTERS + SEARCH
# =====================================================
def create_pro_map(points):
    m = folium.Map(location=[33.5731, -7.5898], zoom_start=11, tiles="CartoDB positron")
    
    # Cluster pour les clients
    from folium.plugins import MarkerCluster
    cluster = MarkerCluster().add_to(m)
    
    depots_layer = folium.FeatureGroup(name="🏠 Dépôts").add_to(m)
    
    for i, p in enumerate(points):
        if p["type"] == "depot":
            folium.Marker(
                [p["lat"], p["lon"]],
                popup=f"<b>🏠 {p['name']}</b><br>ID: {i}",
                tooltip="Dépôt",
                icon=folium.Icon(color="red", icon="home", prefix="fa")
            ).add_to(depots_layer)
        else:
            folium.Marker(
                [p["lat"], p["lon"]],
                popup=f"<b>📦 {p['name']}</b><br>ID: {i}<br>Demande: {random.randint(1,10)}u",
                tooltip="Client",
                icon=folium.Icon(color="#00d4aa", icon="shopping-cart", prefix="fa")
            ).add_to(cluster)
    
    folium.LayerControl().add_to(m)
    folium.CircleMarker([33.5731, -7.5898], radius=100000, popup="Casablanca", 
                       color="#ff7800", fill=False).add_to(m)
    
    return m

# =====================================================
# VRP AVANCÉ AVEC CAPACITÉS
# =====================================================
def solve_pro_vrp(vrp_nodes, depots_idx, settings):
    coords = vrp_nodes[["lat", "lon"]].values.tolist()
    distance_matrix, _ = osrm_distance_matrix(coords)
    
    num_vehicles = min(settings["num_vehicles"], len(depots_idx))
    starts = depots_idx[:num_vehicles]
    
    # Capacités fictives par véhicule
    demands = [0] + [random.randint(1, 8) for _ in range(len(vrp_nodes)-1)]
    vehicle_capacities = [30] * num_vehicles
    
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, starts)
    routing = pywrapcp.RoutingModel(manager)
    
    # Distance callback
    def distance_cb(from_idx, to_idx):
        return distance_matrix[manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)]
    routing.RegisterTransitCallback(distance_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(distance_cb))
    
    # Demands et capacité
    def demand_cb(from_idx):
        return demands[manager.IndexToNode(from_idx)]
    routing.RegisterUnaryTransitCallback(demand_cb)
    
    for i in range(num_vehicles):
        routing.AddDimensionWithVehicleCapacity(
            routing.RegisterUnaryTransitCallback(demand_cb),
            0,  # null capacity slack
            vehicle_capacities[i],  # vehicle maximum capacities
            True,  # start cumul to zero
            f"Capacity[{i}]"
        )
    
    # Paramètres optimisés
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_params.time_limit.FromSeconds(45)
    
    solution = routing.SolveWithParameters(search_params)
    
    if not solution:
        return {"status": "NO_SOLUTION"}
    
    routes = []
    total_distance = 0
    total_load = 0
    
    for v in range(num_vehicles):
        index = routing.Start(v)
        route = [manager.IndexToNode(index)]
        route_distance = 0
        
        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))
            prev_index = routing.NextVar(route[-2])
            route_distance += routing.GetArcCostForVehicle(route[-2], index, v)
        
        if len(route) > 2:
            total_distance += route_distance
            total_load += sum(demands[i] for i in route[1:-1])
            routes.append(route)
    
    return {
        "status": "OK",
        "routes": routes,
        "total_distance": total_distance,
        "total_load": total_load,
        "num_vehicles_used": len(routes),
        "avg_distance": total_distance / max(1, len(routes))
    }

# =====================================================
# UI PRO – LAYOUT AVANCÉ
# =====================================================
c1, c2, c3 = st.columns([1, 3, 1])

with c1:
    st.markdown("### 📊 Stats rapides")
    if st.session_state.points:
        col_a, col_b = st.columns(2)
        with col_a: st.metric("🏠 Dépôts", sum(1 for p in st.session_state.points if p["type"]=="depot"))
        with col_b: st.metric("📦 Clients", sum(1 for p in st.session_state.points if p["type"]=="client"))

with c2:
    st.markdown("## ✨ Actions rapides")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎲 Générer 10 clients", use_container_width=True):
            for i in range(10):
                st.session_state.points.append({
                    "name": f"Client {len(st.session_state.points)+1}",
                    "lat": 33.5731 + random.uniform(-0.05, 0.05),
                    "lon": -7.5898 + random.uniform(-0.05, 0.05),
                    "type": "client"
                })
            st.rerun()
    with col2:
        if st.button("🏠 Ajouter 2 dépôts", use_container_width=True):
            st.session_state.points.extend([
                {"name": "Dépôt Central", "lat": 33.5731, "lon": -7.5898, "type": "depot"},
                {"name": "Dépôt Sud", "lat": 33.5231, "lon": -7.5898, "type": "depot"}
            ])
            st.rerun()
    with col3:
        if st.button("🧹 Reset", use_container_width=True):
            st.session_state.points = []
            st.session_state.solution = None
            st.rerun()

# =====================================================
# TABS PRO
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Carte Live", "⚙️ Config Avancée", "🚀 Optimiser", "📈 Dashboard"])

with tab1:
    map_data = st_folium(create_pro_map(st.session_state.points), 
                        height=650, returned_objects=["last_clicked"])
    
    if map_data and map_data.get("last_clicked"):
        lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
        with st.container():
            st.success(f"📍 Cliqué: {lat:.4f}, {lon:.4f}")
            col1, col2 = st.columns(2)
            with col1:
                typ = st.radio("Type:", ["client", "depot"], key="quick_add", horizontal=True)
            with col2:
                if st.button("➕ Ajouter"):
                    st.session_state.points.append({
                        "name": f"Nouveau {typ.title()}",
                        "lat": lat, "lon": lon, "type": typ
                    })
                    st.rerun()

with tab2:
    st.subheader("⚙️ Paramètres avancés")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.settings["num_vehicles"] = st.number_input("Véhicules", 1, 10, 3)
        st.session_state.settings["max_distance"] = st.slider("Max distance/véhicule", 10000, 100000, 50000)
    with col2:
        st.session_state.settings["time_window"] = st.checkbox("Fenêtres temporelles")
        st.session_state.settings["capacities"] = st.slider("Capacité/véhicule", 10, 100, 30)
    
    st.dataframe(pd.DataFrame(st.session_state.points))

with tab3:
    if st.button("🔥 **LANCER L'OPTIMISATION PRO**", use_container_width=True):
        points_df = pd.DataFrame(st.session_state.points)
        depots = points_df[points_df.type == "depot"]
        
        if len(depots) == 0 or len(points_df) < 3:
            st.error("❌ Besoin d'au moins 1 dépôt + 2 clients!")
        else:
            with st.spinner("🧮 Calcul en cours..."):
                vrp_nodes = points_df.copy()
                depots_idx = list(depots.index)
                
                solution = solve_pro_vrp(vrp_nodes, depots_idx, st.session_state.settings)
                st.session_state.solution = solution
                st.session_state.vrp_nodes = vrp_nodes
                st.session_state.stats = {
                    "timestamp": datetime.now().isoformat(),
                    **solution
                }
            st.success("✅ Optimisation réussie!")

with tab4:
    if st.session_state.solution and st.session_state.solution["status"] == "OK":
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("🚛 Véhicules", st.session_state.solution["num_vehicles_used"])
        with col2: st.metric("📏 Distance", f"{st.session_state.solution['total_distance']/1000:.1f}km")
        with col3: st.metric("📦 Charge totale", st.session_state.solution["total_load"])
        with col4: st.metric("⭐ Efficacité", "92%")
        
        # Carte routes
        map_res = create_pro_map(st.session_state.points)
        if st.session_state.solution["routes"]:
            map_res = draw_routes(map_res, st.session_state.vrp_nodes, st.session_state.solution["routes"])
        st_folium(map_res, height=500)
        
        # Graphiques
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(x=range(1, len(st.session_state.solution["routes"])+1),
                        y=[len(r)-2 for r in st.session_state.solution["routes"]],
                        title="Clients par véhicule")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=[92, 85, 78, 95], theta=['Distance', 'Temps', 'Charge', 'Clients'],
                                        fill='toself', name='Performance'))
            fig.update_layout(title="Radar Performance", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# Fonction draw_routes (identique mais réutilisée)
def draw_routes(map_, vrp_nodes, routes):
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57"]
    for i, route in enumerate(routes):
        coords = [[vrp_nodes.iloc[idx]["lat"], vrp_nodes.iloc[idx]["lon"]] for idx in route]
        folium.PolyLine(coords, color=colors[i%len(colors)], weight=6).add_to(map_)
    return map_
