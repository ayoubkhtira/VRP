"""
🧠 MRP/CBN Pro v3.2 - AVEC GESTION STOCKS ✅
🏬 Onglet Stocks + Métriques + Export amélioré + HEADER PRO
"""

import streamlit as st
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional
import pandas as pd
import plotly.express as px
import numpy as np
import io
from PIL import Image
import openpyxl
from streamlit.components.v1 import html

# ✅ CLASSES DÉFINIES EN PREMIER
@dataclass
class Article:
    code: str
    name: str
    type: str
    lead_time: int
    unit_cost: float
    supplier: Optional[str] = None

@dataclass
class BOM:
    parent: str
    component: str
    quantity: float

@dataclass
class Supplier:
    sid: str
    name: str
    lead_time: int

@dataclass
class Client:
    cid: str
    name: str

@dataclass
class Demand:
    client: str
    article: str
    qty: float
    due_date: date

@dataclass
class Stock:
    article: str
    qty: float
    safety: float

@dataclass
class Machine:
    code: str
    name: str
    capacity_hours: float
    efficiency: float

# Config Streamlit
st.set_page_config(
    page_title="🧠 MRP Pro v3.2", 
    page_icon="🧠",
    layout="wide"
)

# --- 6. HEADER HTML MRP PERSONNALISÉ ---
header_code = """
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400" rel="stylesheet">
<style>
    body { margin: 0; padding: 0; background-color: transparent; font-family: 'Roboto', sans-serif; overflow: hidden; }
    .main-header { 
        position: relative; 
        padding: 30px; 
        background: #0a0a0a; 
        border-radius: 10px; 
        border-left: 12px solid #667eea; 
        overflow: hidden; 
        box-shadow: 0 20px 40px rgba(0,0,0,0.6); 
        min-height: 120px; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
    }
    #bg-carousel { 
        position: absolute; 
        top: 0; 
        left: 0; 
        width: 100%; 
        height: 100%; 
        background-size: cover; 
        background-position: center; 
        opacity: 0.3; 
        transition: background-image 1.5s ease-in-out; 
        z-index: 0; 
    }
    .overlay { 
        position: absolute; 
        top: 0; 
        left: 0; 
        width: 100%; 
        height: 100%; 
        background: linear-gradient(rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.15) 50%, rgba(240, 147, 251, 0.1) 100%); 
        background-size: 100% 4px; 
        z-index: 1; 
        pointer-events: none; 
    }
    .content { position: relative; z-index: 2; }
    h1 { 
        font-family: 'Orbitron', monospace; 
        text-transform: uppercase; 
        letter-spacing: 5px; 
        font-size: 2.2rem; 
        margin: 0; 
        color: #ffffff; 
        text-shadow: 0 0 15px rgba(102, 126, 234, 0.8); 
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        background-clip: text;
    }
    .status { 
        color: #667eea; 
        font-weight: 700; 
        letter-spacing: 4px; 
        font-size: 0.8rem; 
        text-transform: uppercase; 
        margin-top: 10px; 
    }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    .active-dot { 
        display: inline-block; 
        width: 10px; 
        height: 10px; 
        background: #667eea; 
        border-radius: 50%; 
        margin-left: 10px; 
        animation: blink 1.5s infinite; 
        box-shadow: 0 0 8px rgba(102, 126, 234, 0.8); 
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .main-header { animation: gradientShift 8s ease infinite; }
</style></head><body>
    <div class="main-header">
        <div id="bg-carousel"></div>
        <div class="overlay"></div>
        <div class="content">
            <h1>🧠 MRP/CBN <span style="color:#667eea;">Pro v3.2</span></h1>
            <div class="status">Industrial Planning Intelligence  <span class="active-dot"></span></div>
        </div>
    </div>
    <script>
        const images = [
            "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=2000",
            "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=2000",
            "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=2000"
        ];
        let index = 0; 
        const bgDiv = document.getElementById('bg-carousel');
        function changeBackground() { 
            bgDiv.style.backgroundImage = `url('${images[index]}')`; 
            index = (index + 1) % images.length; 
        }
        changeBackground(); 
        setInterval(changeBackground, 4000);
    </script>
</body></html>
"""

# AFFICHAGE HEADER PRO
components.html(header_code, height=200)

# Bouton pour passer en mode plein écran (paramètres)
if st.button("🛠️ CONFIGURATION", key="config_btn"):
    st.session_state.view_mode = 'settings'
    st.rerun()

# CSS amélioré avec métriques stocks (APRES HEADER)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.metric-card { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 1.5rem; border-radius: 16px; text-align: center; }
.metric-card-stock { background: linear-gradient(135deg, #10b981, #059669); color: white; }
.glass-card { background: rgba(255,255,255,0.9); border-radius: 16px; padding: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-top: 2rem; }
.gradient-btn { background: linear-gradient(45deg, #FF6B6B, #4ECDC4); color: white; border-radius: 12px; padding: 0.75rem 2rem; border: none; font-weight: 600; }
.stock-low { background: linear-gradient(135deg, #ef4444, #dc2626) !important; }
</style>
""", unsafe_allow_html=True)

# État global
if 'state' not in st.session_state:
    st.session_state.state = {
        'articles': {},
        'boms': [],
        'suppliers': {},
        'clients': {},
        'demands': [],
        'stocks': {},
        'machines': {},
        'mrp_results': pd.DataFrame()
    }

state = st.session_state.state

# Fonctions MRP (inchangées)
def explode_bom(article_code: str, qty: float, visited=None):
    if visited is None: visited = set()
    if article_code in visited: return {}
    visited = visited.copy()
    visited.add(article_code)
    
    needs = {}
    for bom in state['boms']:
        if bom.parent == article_code:
            required = qty * bom.quantity
            needs[bom.component] = needs.get(bom.component, 0) + required
            sub_needs = explode_bom(bom.component, required, visited)
            for k, v in sub_needs.items():
                needs[k] = needs.get(k, 0) + v
    return needs

def calculate_mrp():
    results = []
    for d in state['demands']:
        gross_needs = {d.article: d.qty}
        exploded = explode_bom(d.article, d.qty)
        gross_needs.update(exploded)
        
        for art_code, qty in gross_needs.items():
            if art_code not in state['articles']: continue
            art = state['articles'][art_code]
            stock = state['stocks'].get(art_code, Stock(art_code, 0, 0))
            
            net = max(qty - stock.qty + stock.safety, 0)
            lead = art.lead_time
            
            order_date = d.due_date - timedelta(days=lead)
            
            results.append({
                "Article": art.name,
                "Code": art_code,
                "Besoin Brut": qty,
                "Stock": stock.qty,
                "Sécurité": stock.safety,
                "Besoin Net": net,
                "Date Ordre": order_date.strftime('%Y-%m-%d'),
                "Type": "🛒 OA" if art.type == "BRUT" else "🏭 OF",
                "Coût": round(net * art.unit_cost, 2)
            })
    
    df = pd.DataFrame(results)
    state['mrp_results'] = df.sort_values('Date Ordre') if not df.empty else df
    return df

# Sidebar améliorée
with st.sidebar:
    st.title("🚀 Navigation")
    tabs = ["📊 Dashboard", "📦 Articles", "🏬 Stocks", "🧱 Nomenclatures", "📈 Demandes", "⚡ MRP", "📁 Export"]
    tab = st.selectbox("Sélection", tabs)
    
    if st.button("🚀 CALCULER MRP", type="primary"):
        with st.spinner("Calcul MRP avec stocks..."):
            calculate_mrp()
        st.success("✅ MRP calculé!")

# Contenu des onglets (IDENTIQUE - AUCUNE REDUCTION)
if tab == "📊 Dashboard":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🎯 Vue d'ensemble")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        total_stock = sum(s.qty for s in state['stocks'].values())
        st.markdown(f'<div class="metric-card"><div style="font-size:2rem">{len(state["demands"])}</div><div>📈 Demandes</div></div>', unsafe_allow_html=True)
    with col2: 
        st.markdown(f'<div class="metric-card"><div style="font-size:2rem">{len(state["articles"])}</div><div>📦 Articles</div></div>', unsafe_allow_html=True)
    with col3: 
        st.markdown(f'<div class="metric-card-stock"><div style="font-size:2rem">{len(state["stocks"])}</div><div>🏬 Stocks</div></div>', unsafe_allow_html=True)
    with col4: 
        st.markdown(f'<div class="metric-card"><div style="font-size:2rem">{total_stock:.0f}</div><div>📊 Total Stock</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "🏬 Stocks":  # 🆕 NOUVEAU ONGLETS STOCKS
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🏬 Gestion des Stocks")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        article = st.text_input("📦 Article")
    with col2:
        quantity = st.number_input("📈 Quantité", min_value=0.0, value=0.0, format="%.2f")
    with col3:
        safety_stock = st.number_input("🛡️ Stock sécurité", min_value=0.0, value=0.0, format="%.2f")
    
    if st.button("💾 METTRE À JOUR STOCK", type="primary"):
        if article and article in state['articles']:
            state['stocks'][article] = Stock(article, float(quantity), float(safety_stock))
            st.success(f"✅ Stock {article} mis à jour!")
            st.rerun()
        elif article:
            st.error("❌ Article non trouvé. Créez-le d'abord!")
    
    # Tableau stocks avec alerte couleurs
    if state['stocks']:
        st.subheader("📊 Stocks Actuels")
        stock_list = []
        for stock in state['stocks'].values():
            art = state['articles'].get(stock.article, None)
            stock_list.append({
                'Article': stock.article,
                'Nom': art.name if art else 'N/A',
                'Stock': stock.qty,
                'Sécurité': stock.safety,
                'Disponible': stock.qty - stock.safety,
                'Statut': '🟢 OK' if stock.qty >= stock.safety else '🔴 BAS'
            })
        
        stock_df = pd.DataFrame(stock_list)
        # Colorer lignes bas de stock
        def color_stocks(val):
            return 'background-color: #fef2f2' if 'BAS' in str(val) else ''
        
        st.dataframe(stock_df.style.applymap(color_stocks, subset=['Statut']), use_container_width=True)
        
        # Graphique stocks
        fig_stock = px.bar(stock_df, x='Article', y='Stock', 
                          color='Statut', title="📈 Niveau Stocks",
                          color_discrete_map={'🟢 OK': '#10b981', '🔴 BAS': '#ef4444'})
        st.plotly_chart(fig_stock, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "📦 Articles":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        code = st.text_input("💾 Code")
        art_type = st.selectbox("Type", ["BRUT", "COMPOSE"])
    with col2:
        name = st.text_input("📝 Nom")
        lead = st.number_input("⏱️ Délai", value=5)
        cost = st.number_input("💰 Coût", value=10.0)
    
    if st.button("➕ Ajouter", key="add_art"):
        if code:
            state['articles'][code] = Article(code, name or "N/A", art_type, int(lead), float(cost))
            st.success("✅ Article ajouté!")
            st.rerun()
    
    if state['articles']:
        st.subheader("Articles")
        art_df = pd.DataFrame([{**vars(a)} for a in state['articles'].values()])
        st.dataframe(art_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "🧱 Nomenclatures":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: parent = st.text_input("👑 Parent")
    with col2: 
        component = st.text_input("🔧 Composant")
        qty = st.number_input("📊 Qté", value=1.0)
    
    if st.button("➕ BOM", key="add_bom"):
        if parent and component:
            state['boms'].append(BOM(parent, component, float(qty)))
            st.success("✅ BOM ajouté!")
            st.rerun()
    
    if state['boms']:
        st.dataframe(pd.DataFrame([{**vars(b)} for b in state['boms']]), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "📈 Demandes":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: client = st.text_input("👥 Client")
    with col2: article = st.text_input("📦 Article")
    with col3: qty = st.number_input("📊 Qté", value=10.0)
    with col4: due = st.date_input("📅 Date", value=pd.Timestamp.now().date())
    
    if st.button("➕ Demande", key="add_demand"):
        if client and article:
            state['demands'].append(Demand(client, article, float(qty), due))
            st.success("✅ Demande ajoutée!")
            st.rerun()
    
    if state['demands']:
        st.dataframe(pd.DataFrame([{**vars(d), 'due_date': d.due_date} for d in state['demands']]), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "⚡ MRP":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if not state['mrp_results'].empty:
        st.dataframe(state['mrp_results'], use_container_width=True)
        fig = px.bar(state['mrp_results'], x='Article', y='Besoin Net', color='Type')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Ajoutez des demandes et calculez MRP!")
    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "📁 Export":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📊 Export Excel COMPLET")
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame([{**vars(a)} for a in state['articles'].values()]).to_excel(writer, 'Articles', index=False)
        pd.DataFrame([{**vars(b)} for b in state['boms']]).to_excel(writer, 'BOMs', index=False)
        pd.DataFrame([{**vars(d), 'due_date': d.due_date} for d in state['demands']]).to_excel(writer, 'Demandes', index=False)
        pd.DataFrame([{**vars(s)} for s in state['stocks'].values()]).to_excel(writer, 'Stocks', index=False)
        if not state['mrp_results'].empty:
            state['mrp_results'].to_excel(writer, 'MRP', index=False)
    
    st.download_button(
        "📥 Télécharger Excel",
        output.getvalue(),
        f"MRP_v3.2_{date.today().strftime('%Y%m%d')}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.markdown('</div>', unsafe_allow_html=True)
