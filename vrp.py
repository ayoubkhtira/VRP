import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json

# Configuration de la page
st.set_page_config(
    page_title="VRP Route Optimizer",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS amélioré avec animations
st.markdown("""
<style>
    /* Variables CSS */
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
    
    /* Styles généraux */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.85) 100%);
        backdrop-filter: blur(10px);
        padding: 2.5rem;
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
    
    /* Cards */
    .custom-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
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
    
    /* Boutons */
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
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #E5E7EB;
        transition: var(--transition);
        background: white;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Tabs */
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
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
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
    
    /* Scrollbar personnalisée */
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
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem;
        }
    }
</style>
"""
# HTML/JavaScript avec fonctionnalité de sélection sur carte
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VRP Route Optimizer with Map Selection</title>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #f5f7fa;
            color: #333;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 100%;
            margin: 0;
            padding: 0;
        }
        
        .app-wrapper {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            margin: 20px;
            animation: fadeIn 0.6s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
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
            font-size: 4rem;
            margin-bottom: 20px;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
        }
        
        h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .subtitle {
            font-size: 1.3rem;
            opacity: 0.9;
            max-width: 800px;
            margin: 0 auto;
            font-weight: 300;
        }
        
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px;
            padding: 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            padding: 25px;
            border-radius: 16px;
            text-align: center;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            border-color: #667eea;
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.1);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #667eea;
            margin: 10px 0;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .main-layout {
            display: grid;
            grid-template-columns: 400px 1fr;
            gap: 30px;
            padding: 30px;
            min-height: 800px;
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
            border: 2px solid #eef2ff;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.08);
        }
        
        .section {
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .section:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }
        
        .section-title {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 25px;
        }
        
        .section-title i {
            color: #667eea;
            font-size: 1.4rem;
        }
        
        .mode-selector {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .mode-btn {
            flex: 1;
            padding: 15px;
            background: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: #555;
        }
        
        .mode-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        }
        
        .mode-btn:hover:not(.active) {
            background: #e9ecef;
            border-color: #667eea;
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
            font-family: 'Inter', sans-serif;
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
            font-family: 'Inter', sans-serif;
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
        
        .btn-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }
        
        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3);
        }
        
        .delivery-list {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 20px;
            border: 2px solid #f0f0f0;
            border-radius: 12px;
            padding: 15px;
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
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .delivery-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        
        .map-container {
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            height: 700px;
            position: relative;
        }
        
        #map {
            width: 100%;
            height: 100%;
            border-radius: 20px;
        }
        
        .map-overlay {
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            z-index: 1000;
            display: flex;
            gap: 10px;
            pointer-events: none;
        }
        
        .map-overlay > * {
            pointer-events: auto;
        }
        
        .map-control {
            background: white;
            padding: 15px 25px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            color: #333;
        }
        
        .map-control i {
            color: #667eea;
            font-size: 1.2rem;
        }
        
        .selection-mode {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            animation: pulse 2s infinite;
        }
        
        .selection-mode i {
            color: white;
        }
        
        .results-panel {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin: 30px;
            animation: fadeIn 0.5s ease-out;
            border: 2px solid #eef2ff;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.08);
        }
        
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .route-item {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 15px;
            transition: all 0.3s ease;
        }
        
        .route-item:hover {
            background: #e9ecef;
            transform: translateY(-2px);
        }
        
        .route-number {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            padding: 40px 60px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            z-index: 2000;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .spinner {
            width: 60px;
            height: 60px;
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
            backdrop-filter: blur(10px);
        }
        
        .notification.show {
            transform: translateX(0);
            opacity: 1;
        }
        
        .notification.success {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.95) 0%, rgba(5, 150, 105, 0.95) 100%);
            border-left: 5px solid #10b981;
        }
        
        .notification.error {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.95) 0%, rgba(220, 38, 38, 0.95) 100%);
            border-left: 5px solid #ef4444;
        }
        
        .notification.info {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.95) 0%, rgba(37, 99, 235, 0.95) 100%);
            border-left: 5px solid #3b82f6;
        }
        
        .notification.warning {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.95) 0%, rgba(217, 119, 6, 0.95) 100%);
            border-left: 5px solid #f59e0b;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #6b7280;
        }
        
        .empty-state i {
            font-size: 3rem;
            margin-bottom: 15px;
            color: #9ca3af;
        }
        
        .color-indicator {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 10px;
            border: 2px solid white;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        .search-box {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            width: 300px;
        }
        
        .search-input {
            width: 100%;
            padding: 15px 20px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            background: white;
        }
        
        .search-input:focus {
            outline: none;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
        }
        
        .leaflet-popup-content {
            font-family: 'Inter', sans-serif;
            max-width: 250px;
        }
        
        .leaflet-control-zoom {
            margin-top: 80px !important;
        }
        
        .coordinates-display {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.95);
            padding: 15px 25px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            font-family: 'Roboto Mono', monospace;
            font-size: 0.9rem;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }
    </style>
</head>
<body>
    <div class="loading" id="loading">
        <div class="spinner"></div>
        <h3>Optimizing Routes...</h3>
        <p>Calculating the most efficient paths</p>
        <div style="margin-top: 20px; font-size: 0.9rem; color: #6b7280;">
            <i class="fas fa-cog fa-spin"></i> Running optimization algorithms...
        </div>
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
                        Advanced Vehicle Routing Problem Solver with Interactive Map Selection
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
                <div class="control-panel">
                    <div class="section">
                        <div class="section-title">
                            <i class="fas fa-mouse-pointer"></i>
                            <span>Map Selection Mode</span>
                        </div>
                        <div class="mode-selector">
                            <button class="mode-btn" id="modeNone" onclick="setSelectionMode('none')">
                                <i class="fas fa-hand-pointer"></i> Navigation
                            </button>
                            <button class="mode-btn" id="modeDepot" onclick="setSelectionMode('depot')">
                                <i class="fas fa-warehouse"></i> Select Depot
                            </button>
                            <button class="mode-btn" id="modeDelivery" onclick="setSelectionMode('delivery')">
                                <i class="fas fa-map-marker-alt"></i> Select Delivery
                            </button>
                        </div>
                        <div class="input-group">
                            <label class="input-label">Current Mode</label>
                            <div id="currentModeDisplay" class="input-field" style="background: #f0f9ff; color: #0369a1; font-weight: 600;">
                                Navigation Mode (Click buttons to change)
                            </div>
                        </div>
                    </div>
                    
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
                            <i class="fas fa-sync-alt"></i> Update Depot Manually
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
                            <label class="input-label">Latitude (from map click)</label>
                            <input type="number" id="deliveryLat" class="input-field" step="0.0001" placeholder="Click on map or enter manually">
                        </div>
                        <div class="input-group">
                            <label class="input-label">Longitude (from map click)</label>
                            <input type="number" id="deliveryLon" class="input-field" step="0.0001" placeholder="Click on map or enter manually">
                        </div>
                        <div class="input-group">
                            <label class="input-label">Demand (kg)</label>
                            <input type="number" id="deliveryDemand" class="input-field" value="10" min="1" step="1">
                        </div>
                        <button class="btn btn-primary" onclick="addDelivery()">
                            <i class="fas fa-plus"></i> Add Delivery Point
                        </button>
                        <button class="btn btn-success" onclick="addDeliveryAndContinue()" style="margin-top: 10px;">
                            <i class="fas fa-plus-circle"></i> Add & Continue
                        </button>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">
                            <i class="fas fa-list-ol"></i>
                            <span>Delivery Points</span>
                            <span class="badge" id="deliveryCount" style="background: #667eea; color: white; padding: 5px 10px; border-radius: 20px; font-size: 0.9rem;">0</span>
                        </div>
                        <div class="delivery-list" id="deliveryList">
                            <div class="empty-state">
                                <i class="fas fa-inbox"></i>
                                <p>No delivery points added yet</p>
                                <p style="font-size: 0.9rem; margin-top: 10px;">Click on map or use the form above</p>
                            </div>
                        </div>
                        <button class="btn btn-secondary" onclick="clearDeliveries()" style="margin-top: 15px;">
                            <i class="fas fa-trash"></i> Clear All Deliveries
                        </button>
                        <button class="btn btn-secondary" onclick="exportDeliveries()" style="margin-top: 10px;">
                            <i class="fas fa-download"></i> Export to CSV
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
                            <label class="input-label">Optimization Algorithm</label>
                            <select id="algorithm" class="input-field">
                                <option value="nearest">Nearest Neighbor</option>
                                <option value="savings">Clarke & Wright Savings</option>
                                <option value="sweep">Sweep Algorithm</option>
                                <option value="genetic">Genetic Algorithm (Advanced)</option>
                            </select>
                        </div>
                        <div class="input-group">
                            <label class="input-label">Optimization Priority</label>
                            <select id="priority" class="input-field">
                                <option value="distance">Minimize Distance</option>
                                <option value="time">Minimize Time</option>
                                <option value="balance">Balance Routes</option>
                                <option value="cost">Minimize Cost</option>
                            </select>
                        </div>
                        <button class="btn btn-primary pulse" onclick="optimizeRoutes()" style="font-size: 1.1rem;">
                            <i class="fas fa-bolt"></i> Optimize Routes
                        </button>
                        <button class="btn btn-secondary" onclick="clearRoutes()" style="margin-top: 10px;">
                            <i class="fas fa-eraser"></i> Clear Routes
                        </button>
                    </div>
                </div>
                
                <div class="map-container">
                    <div class="map-overlay">
                        <div class="map-control" id="modeIndicator">
                            <i class="fas fa-hand-pointer"></i>
                            <span>Navigation Mode</span>
                        </div>
                        <div class="map-control">
                            <i class="fas fa-layer-group"></i>
                            <span>Click on map to select locations</span>
                        </div>
                    </div>
                    
                    <div class="search-box">
                        <input type="text" id="searchInput" class="search-input" placeholder="Search location...">
                    </div>
                    
                    <div class="coordinates-display" id="coordinatesDisplay">
                        <div>Lat: <span id="currentLat">48.8566</span></div>
                        <div>Lng: <span id="currentLng">2.3522</span></div>
                    </div>
                    
                    <div id="map"></div>
                </div>
            </div>
            
            <div class="results-panel" id="resultsPanel" style="display: none;">
                <h2 style="margin-bottom: 30px; color: #333; display: flex; align-items: center; gap: 10px;">
                    <i class="fas fa-chart-line"></i> Optimization Results
                </h2>
                
                <div class="results-grid" id="resultCardsContainer"></div>
                
                <div style="margin-top: 40px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3 style="color: #333; display: flex; align-items: center; gap: 10px;">
                            <i class="fas fa-route"></i> Route Details
                        </h3>
                        <button class="btn btn-secondary" onclick="exportRoutes()" style="width: auto; padding: 10px 20px;">
                            <i class="fas fa-file-export"></i> Export Routes
                        </button>
                    </div>
                    <div id="routesContainer"></div>
                </div>
                
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">
                        <i class="fas fa-chart-bar"></i>
                        <span>Performance Metrics</span>
                    </div>
                    <div id="metricsContainer"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Variables globales
        let map;
        let markers = {};
        let routePolylines = [];
        let deliveries = [];
        let depot = { lat: 48.8566, lon: 2.3522, name: 'Main Depot' };
        let selectionMode = 'none'; // 'none', 'depot', 'delivery'
        let currentMarker = null;
        let searchMarker = null;
        
        // Couleurs pour les routes
        const routeColors = [
            '#3B82F6', '#10B981', '#F59E0B', '#EF4444', 
            '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'
        ];
        
        // Initialisation de la carte
        function initMap() {
            // Créer la carte
            map = L.map('map').setView([depot.lat, depot.lon], 13);
            
            // Couches de base
            const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(map);
            
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
            
            // Contrôle de recherche
            initSearch();
            
            // Ajouter le dépôt initial
            addDepotMarker();
            
            // Écouter les clics sur la carte
            map.on('click', function(e) {
                handleMapClick(e.latlng.lat, e.latlng.lng);
            });
            
            // Mettre à jour l'affichage des coordonnées au mouvement de la souris
            map.on('mousemove', function(e) {
                updateCoordinatesDisplay(e.latlng.lat, e.latlng.lng);
            });
            
            // Afficher les coordonnées initiales
            updateCoordinatesDisplay(depot.lat, depot.lon);
        }
        
        // Initialiser la recherche
        function initSearch() {
            const searchInput = document.getElementById('searchInput');
            
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchLocation(this.value);
                }
            });
        }
        
        // Rechercher un lieu
        function searchLocation(query) {
            if (!query) return;
            
            const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`;
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.length > 0) {
                        const result = data[0];
                        const lat = parseFloat(result.lat);
                        const lon = parseFloat(result.lon);
                        
                        // Centrer la carte sur le résultat
                        map.setView([lat, lon], 15);
                        
                        // Ajouter un marqueur
                        if (searchMarker) {
                            map.removeLayer(searchMarker);
                        }
                        
                        searchMarker = L.marker([lat, lon], {
                            icon: L.icon({
                                iconUrl: 'data:image/svg+xml;base64,' + btoa(`
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#EF4444" width="32" height="32">
                                        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                                    </svg>
                                `),
                                iconSize: [32, 32],
                                iconAnchor: [16, 32]
                            })
                        }).addTo(map)
                        .bindPopup(`<b>Search Result:</b><br>${result.display_name}`)
                        .openPopup();
                        
                        showNotification(`Location found: ${result.display_name.split(',')[0]}`, 'success');
                        
                        // Si en mode sélection, remplir les champs
                        if (selectionMode === 'depot') {
                            document.getElementById('depotLat').value = lat.toFixed(6);
                            document.getElementById('depotLon').value = lon.toFixed(6);
                            showNotification('Coordinates filled for depot', 'info');
                        } else if (selectionMode === 'delivery') {
                            document.getElementById('deliveryLat').value = lat.toFixed(6);
                            document.getElementById('deliveryLon').value = lon.toFixed(6);
                            showNotification('Coordinates filled for delivery', 'info');
                        }
                    } else {
                        showNotification('Location not found', 'error');
                    }
                })
                .catch(error => {
                    console.error('Search error:', error);
                    showNotification('Search failed', 'error');
                });
        }
        
        // Gérer le clic sur la carte
        function handleMapClick(lat, lng) {
            updateCoordinatesDisplay(lat, lng);
            
            // Si un marqueur temporaire existe, le supprimer
            if (currentMarker) {
                map.removeLayer(currentMarker);
            }
            
            // Ajouter un marqueur temporaire
            currentMarker = L.circleMarker([lat, lng], {
                radius: 8,
                fillColor: getColorForMode(),
                color: '#ffffff',
                weight: 2,
                fillOpacity: 0.8
            }).addTo(map);
            
            // Selon le mode, remplir les champs appropriés
            if (selectionMode === 'depot') {
                document.getElementById('depotLat').value = lat.toFixed(6);
                document.getElementById('depotLon').value = lng.toFixed(6);
                showNotification('Depot coordinates selected from map', 'success');
                
                // Désactiver le mode après sélection
                setTimeout(() => setSelectionMode('none'), 1000);
            } else if (selectionMode === 'delivery') {
                document.getElementById('deliveryLat').value = lat.toFixed(6);
                document.getElementById('deliveryLon').value = lng.toFixed(6);
                showNotification('Delivery coordinates selected from map', 'success');
                
                // Demander le nom si vide
                if (!document.getElementById('deliveryName').value.trim()) {
                    document.getElementById('deliveryName').value = `Customer ${deliveries.length + 1}`;
                }
                
                // Désactiver le mode après sélection
                setTimeout(() => setSelectionMode('none'), 1000);
            } else {
                showNotification(`Coordinates: ${lat.toFixed(6)}, ${lng.toFixed(6)}`, 'info');
            }
        }
        
        // Mettre à jour l'affichage des coordonnées
        function updateCoordinatesDisplay(lat, lng) {
            document.getElementById('currentLat').textContent = lat.toFixed(6);
            document.getElementById('currentLng').textContent = lng.toFixed(6);
        }
        
        // Obtenir la couleur selon le mode
        function getColorForMode() {
            switch(selectionMode) {
                case 'depot': return '#3B82F6'; // Bleu
                case 'delivery': return '#10B981'; // Vert
                default: return '#6B7280'; // Gris
            }
        }
        
        // Définir le mode de sélection
        function setSelectionMode(mode) {
            selectionMode = mode;
            
            // Mettre à jour les boutons
            document.getElementById('modeNone').classList.toggle('active', mode === 'none');
            document.getElementById('modeDepot').classList.toggle('active', mode === 'depot');
            document.getElementById('modeDelivery').classList.toggle('active', mode === 'delivery');
            
            // Mettre à jour l'indicateur
            const modeIndicator = document.getElementById('modeIndicator');
            const modeDisplay = document.getElementById('currentModeDisplay');
            
            switch(mode) {
                case 'none':
                    modeIndicator.innerHTML = '<i class="fas fa-hand-pointer"></i> Navigation Mode';
                    modeIndicator.className = 'map-control';
                    modeDisplay.textContent = 'Navigation Mode';
                    modeDisplay.style.background = '#f0f9ff';
                    modeDisplay.style.color = '#0369a1';
                    showNotification('Navigation mode activated', 'info');
                    break;
                    
                case 'depot':
                    modeIndicator.innerHTML = '<i class="fas fa-warehouse"></i> Selecting Depot';
                    modeIndicator.className = 'map-control selection-mode';
                    modeDisplay.textContent = 'Depot Selection Mode - Click on map to select depot location';
                    modeDisplay.style.background = '#dbeafe';
                    modeDisplay.style.color = '#1e40af';
                    showNotification('Click on map to select depot location', 'warning');
                    break;
                    
                case 'delivery':
                    modeIndicator.innerHTML = '<i class="fas fa-map-marker-alt"></i> Selecting Delivery';
                    modeIndicator.className = 'map-control selection-mode';
                    modeDisplay.textContent = 'Delivery Selection Mode - Click on map to select delivery location';
                    modeDisplay.style.background = '#d1fae5';
                    modeDisplay.style.color = '#065f46';
                    showNotification('Click on map to select delivery location', 'warning');
                    break;
            }
            
            // Changer le curseur de la carte
            const mapContainer = document.getElementById('map');
            if (mode === 'none') {
                mapContainer.style.cursor = 'grab';
            } else {
                mapContainer.style.cursor = 'crosshair';
                showNotification(`Click on the map to select ${mode} location`, 'info');
            }
        }
        
        // Ajouter le marqueur du dépôt
        function addDepotMarker() {
            if (markers.depot) {
                map.removeLayer(markers.depot);
            }
            
            const depotIcon = L.divIcon({
                html: `
                    <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); 
                                width: 50px; height: 50px; border-radius: 50%; 
                                display: flex; align-items: center; justify-content: center; 
                                color: white; font-size: 20px; border: 3px solid white; 
                                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);">
                        <i class="fas fa-warehouse"></i>
                    </div>
                `,
                className: 'custom-depot-icon',
                iconSize: [50, 50],
                iconAnchor: [25, 50]
            });
            
            markers.depot = L.marker([depot.lat, depot.lon], { icon: depotIcon })
                .addTo(map)
                .bindPopup(`
                    <b>${depot.name}</b><br>
                    Depot Location<br>
                    Coordinates: ${depot.lat.toFixed(6)}, ${depot.lon.toFixed(6)}
                `);
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
            addDepotMarker();
            map.setView([depot.lat, depot.lon], 13);
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
            addDeliveryMarker(delivery);
            
            // Réinitialiser les champs (sauf la demande)
            document.getElementById('deliveryName').value = '';
            document.getElementById('deliveryLat').value = '';
            document.getElementById('deliveryLon').value = '';
            
            showNotification(`Delivery point "${name}" added successfully`, 'success');
        }
        
        // Ajouter et continuer
        function addDeliveryAndContinue() {
            addDelivery();
            // Réactiver le mode de sélection
            setTimeout(() => setSelectionMode('delivery'), 500);
        }
        
        // Ajouter un marqueur de livraison
        function addDeliveryMarker(delivery) {
            const deliveryIcon = L.divIcon({
                html: `
                    <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                                width: 40px; height: 40px; border-radius: 50%; 
                                display: flex; align-items: center; justify-content: center; 
                                color: white; font-size: 16px; border: 2px solid white; 
                                box-shadow: 0 3px 10px rgba(16, 185, 129, 0.4);">
                        <i class="fas fa-map-marker-alt"></i>
                    </div>
                `,
                className: 'custom-delivery-icon',
                iconSize: [40, 40],
                iconAnchor: [20, 40]
            });
            
            const marker = L.marker([delivery.lat, delivery.lon], { icon: deliveryIcon })
                .addTo(map)
                .bindPopup(`
                    <b>${delivery.name}</b><br>
                    Demand: ${delivery.demand} kg<br>
                    Location: ${delivery.lat.toFixed(6)}, ${delivery.lon.toFixed(6)}<br>
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
                        <p style="font-size: 0.9rem; margin-top: 10px;">Click on map or use the form above</p>
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
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
                            <div style="background: #10B981; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem;">
                                ${index + 1}
                            </div>
                            <div style="font-weight: 600; color: #333;">${delivery.name}</div>
                        </div>
                        <div style="font-size: 0.9rem; color: #666; margin-bottom: 3px;">
                            <i class="fas fa-map-marker-alt"></i> ${delivery.lat.toFixed(4)}, ${delivery.lon.toFixed(4)}
                        </div>
                        <div style="font-size: 0.9rem; color: #10B981; font-weight: 500;">
                            <i class="fas fa-weight-hanging"></i> ${delivery.demand} kg
                        </div>
                    </div>
                    <button onclick="removeDelivery('${delivery.id}')" 
                            style="background: #EF4444; color: white; border: none; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center;"
                            onmouseover="this.style.transform='scale(1.1)'; this.style.background='#DC2626'" 
                            onmouseout="this.style.transform='scale(1)'; this.style.background='#EF4444'">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                container.appendChild(div);
            });
        }
        
        // Supprimer une livraison
        function removeDelivery(id) {
            deliveries = deliveries.filter(d => d.id != id);
            
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
        
        // Exporter les livraisons
        function exportDeliveries() {
            if (deliveries.length === 0) {
                showNotification('No delivery points to export', 'error');
                return;
            }
            
            let csvContent = "data:text/csv;charset=utf-8,Name,Latitude,Longitude,Demand(kg),AddedAt\\n";
            
            deliveries.forEach(delivery => {
                csvContent += `${delivery.name},${delivery.lat},${delivery.lon},${delivery.demand},${delivery.addedAt}\\n`;
            });
            
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "delivery_points.csv");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showNotification('Delivery points exported to CSV', 'success');
        }
        
        // Afficher une notification
        function showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px;">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
                    <span>${message}</span>
                </div>
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
            }, 4000);
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
            showNotification('Routes cleared', 'info');
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
        
        // Algorithme du plus proche voisin amélioré
        function nearestNeighborAlgorithm(capacity, maxVehicles) {
            if (deliveries.length === 0) return [];
            
            const unvisited = [...deliveries];
            const routes = [];
            let vehicleCount = 0;
            
            // Trier par distance au dépôt
            unvisited.sort((a, b) => {
                const distA = calculateDistance(depot.lat, depot.lon, a.lat, a.lon);
                const distB = calculateDistance(depot.lat, depot.lon, b.lat, b.lon);
                return distA - distB;
            });
            
            while (unvisited.length > 0 && vehicleCount < maxVehicles) {
                const route = [];
                let currentLoad = 0;
                let currentLocation = depot;
                
                // Prendre le point le plus proche du dépôt comme premier point
                if (unvisited.length > 0) {
                    const firstPoint = unvisited.shift();
                    if (firstPoint.demand <= capacity) {
                        route.push(firstPoint);
                        currentLoad += firstPoint.demand;
                        currentLocation = firstPoint;
                    } else {
                        // Si la demande du premier point est trop grande, le remettre
                        unvisited.unshift(firstPoint);
                        break;
                    }
                }
                
                // Continuer à ajouter des points
                while (unvisited.length > 
