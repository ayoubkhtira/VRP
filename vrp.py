import streamlit as st
import pandas as pd
import folium
import random

from streamlit_folium import st_folium
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# =====================================================
# CONFIG STREAMLIT
# =====================================================
st.set_page_config(layout="wide")
st.title("🚚 VRP – Vehicle Routing Problem (Streamlit + SIG)")

# =====================================================
# SESSION STATE
# =====================================================
if "points" not in st.session_state:
    st.session_state.points = []

if "depot_defined" not in st.session_state:
    st.session_state.depot_defined = False

# =====================================================
# MAP CREATION (CLICKABLE)
# =====================================================
def create_clickable_map(points):
    if points:
        center = [points[-1]["lat"], points[-1]["lon"]]
    else:
        center = [33.5731, -7.5898]  # Casablanca

    m = folium.Map(location=center, zoom_start=11)

    for p in points:
        icon = "home" if p["type"] == "depot" else "info-sign"
        color = "red" if p["type"] == "depot" else "blue"

        folium.Marker(
            [p["lat"], p["lon"]],
            popup=f"{p['name']}<br>Poids: {p['weight']}<br>Volume: {p['volume']}",
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
        for order, node_idx in enumerate(route):
            node = vrp_nodes.iloc[node_idx]
            coords.append([node["lat"], node["lon"]])

            folium.Marker(
                [node["lat"], node["lon"]],
                icon=folium.DivIcon(
                    html=f"<div style='font-size:12px;color:black;'><b>{order}</b></div>"
                )
            ).add_to(map_)

        folium.PolyLine(
            coords,
            color=colors[i % len(colors)],
            weight=5,
            opacity=0.8,
            tooltip=f"Véhicule {i + 1}"
        ).add_to(map_)

    return map_

# =====================================================
# VRP SOLVER (OR-TOOLS)
# =====================================================
def solve_vrp(vrp_nodes):
    coords = vrp_nodes[["lat", "lon"]].values

    def distance(p1, p2):
        return int(((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5 * 100000)

    distance_matrix = [
        [distance(coords[i], coords[j]) for j in range(len(coords))]
        for i in range(len(coords))
    ]

    num_vehicles = 3
    depot = 0

    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix), num_vehicles, depot
    )

    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

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
        route.append(depot)
        if len(route) > 2:
            routes.append(route)

    return {
        "status": "OK",
        "routes": routes
    }

# =====================================================
# UI – MAP & ADD POINTS
# =====================================================
st.subheader("🗺️ Ajouter le dépôt et les clients (clic sur la carte)")

map_ = create_clickable_map(st.session_state.points)
map_data = st_folium(map_, height=500, width=1000)

if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    st.success(f"Point sélectionné : {lat:.5f}, {lon:.5f}")

    with st.form("add_point_form"):
        point_type = st.selectbox(
            "Type de point",
            ["depot", "client"],
            disabled=st.session_state.depot_defined
        )

        name = st.text_input("Nom")
        weight = st.number_input("Poids (kg)", min_value=0.0)
        volume = st.number_input("Volume (m³)", min_value=0.0)

        submitted = st.form_submit_button("➕ Ajouter le point")

        if submitted:
            st.session_state.points.append({
                "name": name,
                "lat": lat,
                "lon": lon,
                "weight": weight,
                "volume": volume,
                "type": point_type
            })

            if point_type == "depot":
                st.session_state.depot_defined = True

            st.rerun()

# =====================================================
# DATA TABLE
# =====================================================
if st.session_state.points:
    st.subheader("📦 Points enregistrés")
    st.dataframe(pd.DataFrame(st.session_state.points))

# =====================================================
# OPTIMISATION & VISUALISATION
# =====================================================
st.subheader("🚀 Optimisation des tournées")

if st.button("🔍 Lancer l’optimisation VRP"):

    if not st.session_state.depot_defined:
        st.error("Veuillez définir un dépôt avant l’optimisation")

    else:
        points_df = pd.DataFrame(st.session_state.points)
        depot = points_df[points_df["type"] == "depot"].iloc[0]
        clients_df = points_df[points_df["type"] == "client"].reset_index(drop=True)

        vrp_nodes = pd.concat(
            [depot.to_frame().T, clients_df],
            ignore_index=True
        )

        solution = solve_vrp(vrp_nodes)

        if solution["status"] != "OK":
            st.error("Aucune solution trouvée")
        else:
            st.success("Tournées optimisées avec succès ✅")

            map_result = create_clickable_map(st.session_state.points)
            map_result = draw_routes(
                map_result,
                vrp_nodes,
                solution["routes"]
            )

            st_folium(map_result, height=500, width=1000)

            st.subheader("📊 Résultat brut")
            st.json(solution)
