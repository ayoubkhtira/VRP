"""
🧠 MRP/CBN Pro v3.12 - STYLE HOMOGÈNE PARFAIT ✅
🎨 Design uniforme partout + Navigation native
"""

import streamlit as st
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional
import pandas as pd
import plotly.express as px
import numpy as np
import io
import openpyxl

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
    page_title="🧠 MRP Pro v3.12", 
    page_icon="🧠",
    layout="wide"
)

# 🎨 CSS UNIFORME MASTER (STYLE HOMOGÈNE TOUT)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* BASE HOMOGÈNE */
* { font-family: 'Inter', sans-serif; }
body { 
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%); 
    color: #e2e8f0; margin: 0; padding: 0;
}
h1, h2, h3, h4, h5, h6 { 
    color: #f8fafc !important; 
    font-family: 'Orbitron', monospace !important; 
    text-shadow: 0 2px 10px rgba(102,126,234,0.5);
}

/* HEADER PRO */
.main-header {
    padding: 2.5rem; background: linear-gradient(135deg, rgba(10,10,16,0.95), rgba(26,26,46,0.95));
    backdrop-filter: blur(25px); border-radius: 24px; border-left: 8px solid #667eea; 
    box-shadow: 0 30px 60px rgba(0,0,0,0.8); margin-bottom: 2.5rem; position: relative;
}
.main-header::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(45deg, rgba(102,126,234,0.2), rgba(118,75,162,0.3), rgba(240,147,251,0.2));
    animation: gradientShift 8s ease infinite; z-index: 1; border-radius: 24px;
}
.header-content { position: relative; z-index: 2; text-align: center; }
.header-title {
    font-size: 3rem; font-weight: 700; letter-spacing: 6px; text-transform: uppercase;
    background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #667eea);
    background-size: 400% 400%; -webkit-background-clip: text; background-clip: text; 
    -webkit-text-fill-color: transparent; animation: gradientMove 5s ease infinite;
}

/* NAVIGATION CENTRÉE */
.nav-container { display: flex; justify-content: center; align-items: center; padding: 3rem 0; }
.nav-main-btn {
    background: linear-gradient(45deg, #667eea, #764ba2) !important; color: white !important;
    border: none !important; border-radius: 50px !important; padding: 1.5rem 3.5rem !important;
    font-weight: 700 !important; font-size: 1.3rem !important; letter-spacing: 3px !important;
    box-shadow: 0 25px 60px rgba(102,126,234,0.7) !important; transition: all 0.4s cubic-bezier(0.4,0,0.2,1) !important;
    text-transform: uppercase !important; width: 300px !important; font-family: 'Orbitron', monospace !important;
}
.nav-main-btn:hover { 
    transform: translateY(-10px) scale(1.08) !important; 
    box-shadow: 0 35px 80px rgba(102,126,234,0.9) !important;
}

/* BOUTONS NAVIGATION UNIFORMES */
.stButton > button { 
    background: linear-gradient(45deg, rgba(102,126,234,0.25), rgba(118,75,162,0.25)) !important;
    color: #f8fafc !important; border: 2px solid rgba(102,126,234,0.3) !important; 
    border-radius: 16px !important; padding: 1.2rem 1.8rem !important; 
    margin: 0.5rem 0 !important; width: 100% !important; font-weight: 600 !important; 
    font-size: 1.1rem !important; transition: all 0.35s cubic-bezier(0.4,0,0.2,1) !important;
    text-align: left !important; backdrop-filter: blur(10px);
}
.stButton > button:hover { 
    background: linear-gradient(45deg, #667eea, #764ba2) !important; 
    transform: translateX(8px) !important; box-shadow: 0 15px 35px rgba(102,126,234,0.6) !important;
    border-color: rgba(255,255,255,0.4) !important;
}

/* BOUTONS PRINCIPAUX */
button[kind="primary"] {
    background: linear-gradient(45deg, #10b981, #059669) !important; 
    border: 2px solid #10b981 !important;
}

/* MÉTRIQUES UNIFORMES */
.metric-card { 
    background: linear-gradient(145deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2)) !important;
    backdrop-filter: blur(20px); color: white !important; padding: 2rem !important; 
    border-radius: 20px !important; text-align: center !important; 
    border: 2px solid rgba(255,255,255,0.2) !important; 
    box-shadow: 0 20px 40px rgba(102,126,234,0.4) !important;
    margin: 1rem !important; transition: all 0.3s ease !important;
}
.metric-card:hover { transform: scale(1.05) !important; box-shadow: 0 30px 60px rgba(102,126,234,0.6) !important; }
.metric-value { font-size: 3rem !important; font-weight: 700 !important; margin-bottom: 0.5rem !important; }
.metric-label { font-size: 1rem !important; opacity: 0.95 !important; font-weight: 500 !important; }

/* INPUTS UNIFORMES */
.stTextInput > div > div > input, .stNumberInput > div > div > input, 
.stSelectbox > div > div > select, .stDateInput > div > div > input { 
    background: rgba(255,255,255,0.95) !important; border-radius: 16px !important; 
    border: 2px solid rgba(102,126,234,0.3) !important; padding: 1.2rem !important; 
    font-weight: 500 !important; color: #1e293b !important;
    transition: all 0.3s ease !important; box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
}
.stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus { 
    border-color: #667eea !important; box-shadow: 0 0 0 4px rgba(102,126,234,0.2) !important;
    transform: scale(1.02) !important;
}

/* DATAFRAMES */
.stDataFrame { 
    background: rgba(255,255,255,0.95) !important; border-radius: 20px !important; 
    overflow: hidden !important; box-shadow: 0 20px 50px rgba(0,0,0,0.2) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
}

/* ALERTES */
.success-box { 
    background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(5,150,105,0.2)) !important;
    backdrop-filter: blur(15px); color: white !important; padding: 1.5rem !important; 
    border-radius: 16px !important; border-left: 6px solid #10b981 !important; 
    margin: 1rem 0 !important; box-shadow: 0 10px 30px rgba(16,185,129,0.3) !important;
}
.error-box { 
    background: linear-gradient(135deg, rgba(239,68,68,0.2), rgba(220,38,38,0.2)) !important;
    backdrop-filter: blur(15px); color: white !important; padding: 1.5rem !important; 
    border-radius: 16px !important; border-left: 6px solid #ef4444 !important; 
    margin: 1rem 0 !important; box-shadow: 0 10px 30px rgba(239,68,68,0.3) !important;
}

/* TITRES HOMOGÈNES */
h3 { color: #f8fafc !important; font-size: 1.8rem !important; margin-bottom: 1.5rem !important; }

/* ANIMATIONS */
@keyframes gradientShift { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%}}
@keyframes gradientMove { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%}}
</style>
""", unsafe_allow_html=True)

# 🎨 HEADER
st.markdown("""
<div class="main-header">
    <div class="header-content">
        <h1 class="header-title">VRP SOLUTION <span>Pro</span></h1>
    </div>
</div>
""", unsafe_allow_html=True)

# ✅ ÉTAT GLOBAL
if 'state' not in st.session_state:
    st.session_state.state = {
        'articles': {}, 'boms': [], 'suppliers': {}, 'clients': {},
        'demands': [], 'stocks': {}, 'machines': {}, 'mrp_results': pd.DataFrame()
    }
    st.session_state.current_tab = "📊 Dashboard"
    st.session_state.show_nav = False

state = st.session_state.state

# 🆕 NAVIGATION CENTRÉE
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
if st.button("🚀 NAVIGATION", key="nav_main_uniform"):
    st.session_state.show_nav = not st.session_state.show_nav
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 🆕 MENU NAVIGATION
if st.session_state.show_nav:
    st.markdown("---")
    st.markdown("## 🚀 **MENU NAVIGATION**")
    st.markdown("---")
    
    tabs = ["📊 Dashboard", "📦 Articles", "🏬 Stocks", "🧱 Nomenclatures", "📈 Demandes", "⚡ MRP", "📁 Export"]
    
    for tab_name in tabs:
        if st.button(tab_name, key=f"nav_{tab_name.replace(' ','_')}"):
            st.session_state.current_tab = tab_name
            st.session_state.show_nav = False
            st.rerun()
    
    if st.button("🚀 CALCULER MRP", key="nav_calc_mrp"):
        st.session_state.show_nav = False
        st.rerun()

# ✅ FONCTIONS MRP (IDENTIQUES)
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
                "Article": art.name, "Code": art_code, "Besoin Brut": qty,
                "Stock": stock.qty, "Sécurité": stock.safety, "Besoin Net": net,
                "Date Ordre": order_date.strftime('%Y-%m-%d'),
                "Type": "🛒 OA" if art.type == "BRUT" else "🏭 OF",
                "Coût": round(net * art.unit_cost, 2)
            })
    df = pd.DataFrame(results)
    state['mrp_results'] = df.sort_values('Date Ordre') if not df.empty else df
    return df

# ✅ NAVIGATION MRP
if st.session_state.current_tab == "🚀 CALCULER MRP":
    with st.spinner("🧮 Calcul MRP avec explosion BOM..."):
        calculate_mrp()
    st.success("✅ MRP calculé avec succès!")
    st.session_state.current_tab = "📊 Dashboard"
    st.rerun()

# 🎨 ONGLETS HOMOGÈNES
current_tab = st.session_state.current_tab

if current_tab == "📊 Dashboard":
    st.markdown("### 🎯 Vue d'ensemble")
    col1, col2, col3, col4 = st.columns(4)
    total_stock = sum(s.qty for s in state['stocks'].values())
    
    with col1: 
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(state["demands"])}</div><div class="metric-label">📈 Demandes</div></div>', unsafe_allow_html=True)
    with col2: 
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(state["articles"])}</div><div class="metric-label">📦 Articles</div></div>', unsafe_allow_html=True)
    with col3: 
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(state["stocks"])}</div><div class="metric-label">🏬 Stocks</div></div>', unsafe_allow_html=True)
    with col4: 
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_stock:.0f}</div><div class="metric-label">📊 Total Stock</div></div>', unsafe_allow_html=True)

elif current_tab == "🏬 Stocks":  
    st.markdown("### 🏬 Gestion des Stocks")
    col1, col2, col3 = st.columns(3)
    with col1: article = st.text_input("📦 Article")
    with col2: quantity = st.number_input("📈 Quantité", min_value=0.0, value=0.0, format="%.2f")
    with col3: safety_stock = st.number_input("🛡️ Stock sécurité", min_value=0.0, value=0.0, format="%.2f")
    
    if st.button("💾 METTRE À JOUR STOCK"):
        if article and article in state['articles']:
            state['stocks'][article] = Stock(article, float(quantity), float(safety_stock))
            st.markdown('<div class="success-box">✅ Stock mis à jour!</div>', unsafe_allow_html=True)
            st.rerun()
        elif article:
            st.markdown('<div class="error-box">❌ Article non trouvé!</div>', unsafe_allow_html=True)
    
    if state['stocks']:
        st.markdown("### 📊 Stocks Actuels")
        stock_list = []
        for stock in state['stocks'].values():
            art = state['articles'].get(stock.article, None)
            stock_list.append({
                'Article': stock.article, 'Nom': art.name if art else 'N/A',
                'Stock': stock.qty, 'Sécurité': stock.safety,
                'Disponible': stock.qty - stock.safety,
                'Statut': '🟢 OK' if stock.qty >= stock.safety else '🔴 BAS'
            })
        stock_df = pd.DataFrame(stock_list)
        def color_stocks(val):
            return 'background-color: #fef2f2' if 'BAS' in str(val) else ''
        st.dataframe(stock_df.style.applymap(color_stocks, subset=['Statut']), use_container_width=True)
        
        fig_stock = px.bar(stock_df, x='Article', y='Stock', color='Statut', title="📈 Niveau Stocks",
                          color_discrete_map={'🟢 OK': '#10b981', '🔴 BAS': '#ef4444'})
        st.plotly_chart(fig_stock, use_container_width=True)

elif current_tab == "📦 Articles":
    st.markdown("### 📦 Gestion Articles")
    col1, col2 = st.columns(2)
    with col1:
        code = st.text_input("💾 Code")
        art_type = st.selectbox("Type", ["BRUT", "COMPOSE"])
    with col2:
        name = st.text_input("📝 Nom")
        lead = st.number_input("⏱️ Délai", value=5)
        cost = st.number_input("💰 Coût", value=10.0)
    
    if st.button("➕ Ajouter"):
        if code:
            state['articles'][code] = Article(code, name or "N/A", art_type, int(lead), float(cost))
            st.markdown('<div class="success-box">✅ Article ajouté!</div>', unsafe_allow_html=True)
            st.rerun()
    
    if state['articles']:
        st.markdown("### 📋 Liste Articles")
        art_df = pd.DataFrame([{**vars(a)} for a in state['articles'].values()])
        st.dataframe(art_df, use_container_width=True)

elif current_tab == "🧱 Nomenclatures":
    st.markdown("### 🧱 Nomenclatures")
    col1, col2 = st.columns(2)
    with col1: parent = st.text_input("👑 Parent")
    with col2: 
        component = st.text_input("🔧 Composant")
        qty = st.number_input("📊 Qté", value=1.0)
    
    if st.button("➕ BOM"):
        if parent and component:
            state['boms'].append(BOM(parent, component, float(qty)))
            st.markdown('<div class="success-box">✅ BOM ajouté!</div>', unsafe_allow_html=True)
            st.rerun()
    
    if state['boms']:
        st.dataframe(pd.DataFrame([{**vars(b)} for b in state['boms']]), use_container_width=True)

elif current_tab == "📈 Demandes":
    st.markdown("### 📈 Demandes Clients")
    col1, col2, col3, col4 = st.columns(4)
    with col1: client = st.text_input("👥 Client")
    with col2: article = st.text_input("📦 Article")
    with col3: qty = st.number_input("📊 Qté", value=10.0)
    with col4: due = st.date_input("📅 Date", value=pd.Timestamp.now().date())
    
    if st.button("➕ Demande"):
        if client and article:
            state['demands'].append(Demand(client, article, float(qty), due))
            st.markdown('<div class="success-box">✅ Demande ajoutée!</div>', unsafe_allow_html=True)
            st.rerun()
    
    if state['demands']:
        st.dataframe(pd.DataFrame([{**vars(d), 'due_date': d.due_date} for d in state['demands']]), use_container_width=True)

elif current_tab == "⚡ MRP":
    st.markdown("### ⚡ Résultats MRP")
    if not state['mrp_results'].empty:
        st.dataframe(state['mrp_results'], use_container_width=True)
        fig = px.bar(state['mrp_results'], x='Article', y='Besoin Net', color='Type')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Ajoutez des demandes et calculez MRP!")

elif current_tab == "📁 Export":
    st.markdown("### 📊 Export Excel COMPLET")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame([{**vars(a)} for a in state['articles'].values()]).to_excel(writer, 'Articles', index=False)
        pd.DataFrame([{**vars(b)} for b in state['boms']]).to_excel(writer, 'BOMs', index=False)
        pd.DataFrame([{**vars(d), 'due_date': d.due_date} for d in state['demands']]).to_excel(writer, 'Demandes', index=False)
        pd.DataFrame([{**vars(s)} for s in state['stocks'].values()]).to_excel(writer, 'Stocks', index=False)
        if not state['mrp_results'].empty:
            state['mrp_results'].to_excel(writer, 'MRP', index=False)
    
    st.download_button(
        "📥 Télécharger Excel", output.getvalue(),
        f"MRP_v3.12_{date.today().strftime('%Y%m%d')}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
