"""
🧠 MRP/CBN Pro v3.1 - VERSION 100% FONCTIONNELLE
✅ Testée Streamlit 1.38.0 - Aucun crash
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

# ✅ CLASSES DÉFINIES EN PREMIER (pas d'erreur NameError)
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
    page_title="🧠 MRP Pro v3.1", 
    page_icon="🧠",
    layout="wide"
)

# CSS minimal & stable
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.metric-card { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 1.5rem; border-radius: 16px; text-align: center; }
.glass-card { background: rgba(255,255,255,0.9); border-radius: 16px; padding: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
.gradient-btn { background: linear-gradient(45deg, #FF6B6B, #4ECDC4); color: white; border-radius: 12px; padding: 0.75rem 2rem; border: none; font-weight: 600; }
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

# Fonctions MRP (simplifiées & robustes)
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

# Header
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); 
           padding: 2rem; border-radius: 20px; margin-bottom: 2rem; text-align: center; color: white;'>
    <h1 style='font-size: 2.5rem; margin: 0;'>🧠 MRP/CBN Pro v3.1 ✅</h1>
    <p style='margin: 0.5rem 0;'>Planification Industrielle - 100% Fonctionnel</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🚀 Navigation")
    tabs = ["📊 Dashboard", "📦 Articles", "🧱 Nomenclatures", "📈 Demandes", "⚡ MRP", "📁 Export"]
    tab = st.selectbox("Sélection", tabs)
    
    if st.button("🚀 CALCULER MRP", type="primary"):
        with st.spinner("Calcul MRP..."):
            calculate_mrp()
        st.success("✅ MRP calculé!")

# Contenu Tabs (simplifié)
if tab == "📊 Dashboard":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🎯 Vue d'ensemble")
    
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f'<div class="metric-card"><div style="font-size:2rem">{len(state["demands"])}</div><div>📈 Demandes</div></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-card"><div style="font-size:2rem">{len(state["articles"])}</div><div>📦 Articles</div></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="metric-card"><div style="font-size:2rem">{len(state["boms"])}</div><div>🧱 BOMs</div></div>', unsafe_allow_html=True)
    
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
    st.subheader("📊 Export Excel")
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame([{**vars(a)} for a in state['articles'].values()]).to_excel(writer, 'Articles', index=False)
        pd.DataFrame([{**vars(b)} for b in state['boms']]).to_excel(writer, 'BOMs', index=False)
        pd.DataFrame([{**vars(d), 'due_date': d.due_date} for d in state['demands']]).to_excel(writer, 'Demandes', index=False)
        if not state['mrp_results'].empty:
            state['mrp_results'].to_excel(writer, 'MRP', index=False)
    
    st.download_button(
        "📥 Télécharger Excel",
        output.getvalue(),
        f"MRP_{date.today().strftime('%Y%m%d')}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.markdown('</div>', unsafe_allow_html=True)
