import streamlit as st
import pandas as pd
import folium
import random
import requests
import numpy as np

from streamlit_folium import st_folium
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# Modern CSS styling [web:7][web:16]
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    .stApp {
        background-color: #0e1117;
    }
    h1 {
        color: white;
        font-family: 'Segoe UI', sans-serif;
        font-size: 2.5rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 8px;
        font-weight: 600;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(255,255,255,0.2);
        color: white;
    }
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6, #1d4ed8);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(59,130,246,0.4);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59,130,246,0.6);
    }
    .stNumberInput > div > div > div > input {
        background: rgba(255,255,255,0.1);
        border: 2px solid rgba(255,255,255,0.2);
        border-radius: 12px;
        color: white;
        padding: 0.75rem;
    }
    .stDataFrame {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    .stInfo, .stSuccess, .stError {
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# CONFIG STREAMLIT
# =====================================================
st.set_page_config(layout="wide", page_title="🚚 VRP Avancé")
st.title("🚚 VRP Avancé – Multi-Dépôts | Routes Réelles | SIG")

# =====================================================
# SESSION STATE
# =====================================================
if "points" not in st.session_state:
    st.session_state.points = []

# =====================================================
# UTILS – OSRM DISTANCE MATRIX
# =====================================================
@st.cache_data
def osrm_distance_matrix(coords):
    coord_str = ";".join([f"{lon},{lat}" for lat, lon in coords])

    url = (
        "http://router.project-osrm.org/table/v1/driving/"
        + coord_str
        + "?annotations=distance,duration"
    )

    response = requests.get(url)
    if response.status_code != 200:
        st.error("Erreur OSRM. Vérifiez votre connexion.")
        return np.zeros((len(coords), len(coords))), np.zeros((len(coords), len(coords)))

    data = response.json()

    distances = np.array(data["distances"]).astype(int)
    durations = np.array(data["durations"]).astype(int)

    return distances, durations

# =====================================================
# MAP CREATION
# =====================================================
def create_clickable_map(points):
    if points:
        center = [points[-1]["lat"], points[-1]["lon"]]
    else:
        center = [33.5731, -7.5898]  # Casablanca

    m = folium.Map(location=center, zoom_start=11, tiles="CartoDB positron")

    for p in points:
        if p["type"] == "depot":
            icon = "home"
            color = "red"
        else:
            icon = "shopping-cart"
            color = "#00d4aa"

        folium.Marker(
            [p["lat"], p["lon"]],
            popup=f"<b>{p['name']}</b><br>Type: {p['type'].title()}",
            tooltip=p['name'],
            icon=folium.Icon(color=color, icon=icon, prefix="fa")
        ).add_to(m)

    return m

# =====================================================
# DRAW ROUTES
# =====================================================
def draw_routes(map_, vrp_nodes, routes):
    colors = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
        "#FECA57", "#FF9FF3", "#54A0FF"
    ]

    for i, route in enumerate(routes):
        if len(route) < 2:
            continue
        coords = []
        for order, idx in enumerate(route):
            node = vrp_nodes.iloc[idx]
            coords.append([node["lat"], node["lon"]])

            # Numéros des étapes
            folium.Marker(
                [node["lat"], node["lon"]],
                icon=folium.DivIcon(
                    html=f'<div style="background: {colors[i % len(colors)]}; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px;">{order}</div>'
                )
            ).add_to(map_)

        folium.PolyLine(
            coords,
            color=colors[i % len(colors)],
            weight=6,
            opacity=0.8,
            tooltip=f"🚛 Véhicule {i+1} ({len(route)-2} clients)"
        ).add_to(map_)

    return map_

# =====================================================
# VRP SOLVER – MULTI DEPOT + OSRM
# =====================================================
def solve_vrp(vrp_nodes, depots_idx, num_vehicles):
    if len(vrp_nodes) < 2:
        return {"status": "INSUFFICIENT_POINTS"}

    coords = vrp_nodes[["lat", "lon"]].values.tolist()
    distance_matrix, time_matrix = osrm_distance_matrix(coords)

    # Limiter au nombre de dépôts disponibles
    actual_vehicles = min(num_vehicles, len(depots_idx))
    starts = depots_idx[:actual_vehicles]
    ends = depots_idx[:actual_vehicles]

    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        actual_vehicles,
        starts,
        ends
    ) [web:2][web:6]

    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_index)

    # Interdire les routes vides [web:12]
    for v in range(actual_vehicles):
        routing.AddDisjunction([routing.Start(v)], 10000, True)  # Grande pénalité

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.time_limit.seconds = 30

    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        return {"status": "NO_SOLUTION"}

    routes = []

    total_distance = 0
    for vehicle_id in range(actual_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        route_distance = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route.append(node_index)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        route.append(manager.IndexToNode(index))
        
        total_distance += route_distance
        
        # Filtrer les routes vides ou trop courtes
        if len(route) > 2:
            routes.append(route)

    return {
        "status": "OK",
        "routes": routes,
        "total_distance": total_distance,
        "num_vehicles_used": len(routes)
    }

# =====================================================
# SIDEBAR – CONFIGURATION
# =====================================================
with st.sidebar:
    st.header("⚙️ Configuration")
    num_vehicles = st.number_input(
        "Nombre de véhicules", min_value=1, value=3, format="%d"
    )
    
    st.markdown("---")
    st.markdown("**Points ajoutés:**")
    st.markdown(f"**{len(st.session_state.points)}**")

# =====================================================
# TABS UI
# =====================================================
tab1, tab2, tab3 = st.tabs([
    "📍 Carte Interactive",
    "🚀 Optimisation",
    "📊 Résultats & Métriques"
])

# =====================================================
# TAB 1 – ADD POINTS
# =====================================================
with tab1:
    st.info("👆 **Cliquez sur la carte** pour ajouter un dépôt ou un client")
    
    # Activer returned_objects pour last_clicked [web:1][web:5][web:11][web:14]
    map_ = create_clickable_map(st.session_state.points)
    map_data = st_folium(
        map_, 
        height=600, 
        width=1200,
        returned_objects=["last_clicked"]
    )

    # Correction: Vérifier map_data et utiliser 'lng' correctement
    if map_data and "last_clicked" in map_data and map_data["last_clicked"]:
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]  # Correct: 'lng' pas 'lon'

        with st.expander("📥 Ajouter le point cliqué", expanded=True):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                point_type = st.radio("Type", ["depot", "client"], horizontal=True, key="type")
            with col2:
                name = st.text_input("Nom du point", key="name")
            with col3:
                if st.button("➕ Ajouter", use_container_width=True):
                    st.session_state.points.append({
                        "name": name or f"Point {len(st.session_state.points)+1}",
                        "lat": lat,
                        "lon": lon,
                        "type": point_type
                    })
                    st.success("✅ Point ajouté!")
                    st.rerun()

    if st.session_state.points:
        st.subheader("📋 Liste des points")
        df_points = pd.DataFrame(st.session_state.points)
        st.dataframe(df_points, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Vider tout"):
                st.session_state.points = []
                st.rerun()
        with col2:
            if st.button("🔄 Optimiser maintenant", use_container_width=True):
                st.switch_page("app.py")  # Force rerun vers tab2

# =====================================================
# TAB 2 – OPTIMISATION
# =====================================================
with tab2:
    st.subheader("🚀 Lancer l'optimisation VRP")
    
    col1, col2 = st.columns([3,1])
    with col1:
        if st.button("🔥 **OPTIMISER LES ROUTES**", use_container_width=True):
            points_df = pd.DataFrame(st.session_state.points)

            depots_df = points_df[points_df["type"] == "depot"]
            clients_df = points_df[points_df["type"] == "client"]

            if depots_df.empty:
                st.error("❌ **Ajoutez au moins 1 DÉPÔT** (icône maison)")
            elif clients_df.empty:
                st.error("❌ **Ajoutez au moins 1 CLIENT** (icône chariot)")
            elif len(points_df) < 3:
                st.warning("⚠️ Ajoutez plus de points pour un VRP intéressant")
            else:
                with st.spinner("🧠 Calcul des distances OSRM..."):
                    vrp_nodes = pd.concat([depots_df, clients_df], ignore_index=True)
                    depots_idx = list(range(len(depots_df)))

                    solution = solve_vrp(vrp_nodes, depots_idx, num_vehicles)
                    st.session_state.solution = solution
                    st.session_state.vrp_nodes = vrp_nodes

                st.success(f"✅ **Optimisation terminée!** {len(solution.get('routes',[]))} routes générées.")

    st.info("**Paramètres:** Matrice de distances OSRM + OR-Tools VRP")

# =====================================================
# TAB 3 – RESULTS
# =====================================================
with tab3:
    if "solution" in st.session_state and st.session_state.solution["status"] == "OK":
        solution = st.session_state.solution
        vrp_nodes = st.session_state.vrp_nodes

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🚛 Véhicules utilisés", solution["num_vehicles_used"])
            st.metric("📍 Clients servis", sum(len(r)-2 for r in solution["routes"]))
            st.metric("📏 Distance totale", f"{solution['total_distance']/1000:.1f} km")
        
        st.subheader("🗺️ Routes optimisées")
        map_res = create_clickable_map(st.session_state.points)
        map_res = draw_routes(map_res, vrp_nodes, solution["routes"])
        st_folium(map_res, height=600, width=1200)

        with st.expander("🔍 Détails techniques"):
            st.json({k: v for k,v in solution.items() if k != "routes"})
            
            st.subheader("Routes par véhicule:")
            for i, route in enumerate(solution["routes"]):
                nodes = [vrp_nodes.iloc[idx]["name"] if idx < len(vrp_nodes) else f"Depot_{idx}" for idx in route]
                st.write(f"**Véhicule {i+1}:** {' → '.join(nodes)}")
                
    else:
        st.info("🚀 **Aucun résultat** - Lancez l'optimisation dans l'onglet 2")
        if "solution" in st.session_state:
            st.error(f"Erreur: {st.session_state.solution.get('status', 'Inconnu')}")
