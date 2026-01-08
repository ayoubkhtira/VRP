import streamlit as st
import pandas as pd
import folium
import random
import requests
import numpy as np

from streamlit_folium import st_folium
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# =====================================================
# CONFIG STREAMLIT
# =====================================================
st.set_page_config(layout="wide")
st.title("🚚 VRP Avancé – Multi-Dépôts | Routes Réelles | SIG")

# =====================================================
# SESSION STATE
# =====================================================
if "points" not in st.session_state:
    st.session_state.points = []

# =====================================================
# UTILS – OSRM DISTANCE MATRIX
# =====================================================
def osrm_distance_matrix(coords):
    coord_str = ";".join([f"{lon},{lat}" for lat, lon in coords])

    url = (
        "https://router.project-osrm.org/table/v1/driving/"
        + coord_str
        + "?annotations=distance,duration"
    )

    response = requests.get(url)
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
        center = [33.5731, -7.5898]

    m = folium.Map(location=center, zoom_start=11)

    for p in points:
        if p["type"] == "depot":
            icon = "home"
            color = "red"
        else:
            icon = "info-sign"
            color = "blue"

        folium.Marker(
            [p["lat"], p["lon"]],
            popup=f"{p['name']}<br>Type: {p['type']}",
            icon=folium.Icon(color=color, icon=icon)
        ).add_to(m)

    return m

# =====================================================
# DRAW ROUTES
# =====================================================
def draw_routes(map_, vrp_nodes, routes):
    colors = [
        "red", "blue", "green", "purple",
        "orange", "darkred", "cadetblue"
    ]

    for i, route in enumerate(routes):
        coords = []
        for order, idx in enumerate(route):
            node = vrp_nodes.iloc[idx]
            coords.append([node["lat"], node["lon"]])

            folium.Marker(
                [node["lat"], node["lon"]],
                icon=folium.DivIcon(
                    html=f"<b>{order}</b>"
                )
            ).add_to(map_)

        folium.PolyLine(
            coords,
            color=colors[i % len(colors)],
            weight=5,
            tooltip=f"Véhicule {i+1}"
        ).add_to(map_)

    return map_

# =====================================================
# VRP SOLVER – MULTI DEPOT + OSRM
# =====================================================
def solve_vrp(vrp_nodes, depots_idx, num_vehicles):
    coords = vrp_nodes[["lat", "lon"]].values
    distance_matrix, time_matrix = osrm_distance_matrix(coords)

    starts = depots_idx[:num_vehicles]
    ends = depots_idx[:num_vehicles]

    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        num_vehicles,
        starts,
        ends
    )

    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        return {"status": "NO_SOLUTION"}

    routes = []

    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))
        if len(route) > 2:
            routes.append(route)

    return {
        "status": "OK",
        "routes": routes
    }

# =====================================================
# SIDEBAR – CONFIGURATION
# =====================================================
st.sidebar.header("⚙️ Configuration")

num_vehicles = st.sidebar.number_input(
    "Nombre de véhicules",
    min_value=1,
    value=3
)

# =====================================================
# TABS UI
# =====================================================
tab1, tab2, tab3 = st.tabs([
    "📍 Carte & Points",
    "🚛 Optimisation",
    "📊 Résultats"
])

# =====================================================
# TAB 1 – ADD POINTS
# =====================================================
with tab1:
    st.info("Cliquez sur la carte pour ajouter un dépôt ou un client")

    map_ = create_clickable_map(st.session_state.points)
    map_data = st_folium(map_, height=500, width=1000)

    if map_data and map_data["last_clicked"]:
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]

        with st.form("add_point"):
            point_type = st.selectbox("Type", ["depot", "client"])
            name = st.text_input("Nom")
            submitted = st.form_submit_button("Ajouter")

            if submitted:
                st.session_state.points.append({
                    "name": name,
                    "lat": lat,
                    "lon": lon,
                    "type": point_type
                })
                st.rerun()

    if st.session_state.points:
        st.dataframe(pd.DataFrame(st.session_state.points))

# =====================================================
# TAB 2 – OPTIMISATION
# =====================================================
with tab2:
    st.subheader("🚀 Lancer l'optimisation")

    if st.button("Optimiser"):
        points_df = pd.DataFrame(st.session_state.points)

        depots_df = points_df[points_df["type"] == "depot"]
        clients_df = points_df[points_df["type"] == "client"]

        if depots_df.empty or clients_df.empty:
            st.error("Ajoutez au moins un dépôt et un client")
        else:
            vrp_nodes = pd.concat([depots_df, clients_df], ignore_index=True)
            depots_idx = list(range(len(depots_df)))

            solution = solve_vrp(vrp_nodes, depots_idx, num_vehicles)
            st.session_state.solution = solution
            st.session_state.vrp_nodes = vrp_nodes

            st.success("Optimisation terminée")

# =====================================================
# TAB 3 – RESULTS
# =====================================================
with tab3:
    if "solution" in st.session_state:
        solution = st.session_state.solution
        vrp_nodes = st.session_state.vrp_nodes

        map_res = create_clickable_map(st.session_state.points)
        map_res = draw_routes(map_res, vrp_nodes, solution["routes"])
        st_folium(map_res, height=500, width=1000)

        st.json(solution)
    else:
        st.info("Aucun résultat pour le moment")
