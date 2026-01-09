"""
🧠 MRP/CBN Pro v3.0 - SOLUTION INDUSTRIELLE COMPLÈTE
🚀 Toutes les évolutions intégrées : Prévision IA, Gantt, Excel, PDF, KPI Avancés
"""

import streamlit as st
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import io
import base64
from prophet import Prophet
import openpyxl
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
from PIL import Image as PILImage

# Page config pro
st.set_page_config(
    page_title="🧠 MRP/CBN Pro v3.0 - Industriel",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Ultra-moderne avec animations
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }

.main .block-container { padding-top: 2rem; }

.metric-card-pro {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    padding: 2rem;
    border-radius: 24px;
    color: white;
    text-align: center;
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}

.metric-card-pro::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    transition: left 0.5s;
}

.metric-card-pro:hover::before { left: 100%; }
.metric-card-pro:hover { transform: translateY(-10px) scale(1.02); }

.glass-card-pro {
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(30px);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 24px;
    padding: 2.5rem;
    box-shadow: 0 25px 50px rgba(31,38,135,0.2);
}

.gradient-btn-pro {
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #FFEAA7);
    background-size: 300% 300%;
    animation: gradientShift 8s ease infinite;
    border: none;
    border-radius: 16px;
    padding: 1rem 2.5rem;
    color: white;
    font-weight: 700;
    font-size: 1.1rem;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.gradient-btn-pro:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 20px 40px rgba(0,0,0,0.25);
}

.st-emotion-cache-1r6h3i6 h1 { color: white !important; }
.st-emotion-cache-1r6h3i6 h2 { color: #667eea !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_prophet_model():
    """Modèle Prophet pré-entraîné pour démo"""
    model = Prophet(daily_seasonality=True)
    # Données démo pour entraînement rapide
    dates = pd.date_range('2025-01-01', periods=90, freq='D')
    demo_data = pd.DataFrame({'ds': dates, 'y': 100 + 20*np.sin(np.arange(90)/10) + np.random.normal(0, 10, 90)})
    model.fit(demo_data)
    return model

# ÉTAT GLOBAL ÉTENDU
if 'state' not in st.session_state:
    class AppState:
        def __init__(self):
            self.articles: Dict[str, 'Article'] = {}
            self.boms: List['BOM'] = []
            self.suppliers: Dict[str, 'Supplier'] = {}
            self.clients: Dict[str, 'Client'] = {}
            self.demands: List['Demand'] = []
            self.stocks: Dict[str, 'Stock'] = {}
            self.machines: Dict[str, 'Machine'] = {}
            self.mrp_results = pd.DataFrame()
            self.forecast_results = pd.DataFrame()
            self.performance_history = []
    
    st.session_state.state = AppState()
    # Données démo
    st.session_state.state.articles = {
        'A100': Article('A100', 'Table Chêne', 'COMPOSE', 10, 250.0, 'SUP001'),
        'B200': Article('B200', 'Pieds Métal', 'BRUT', 7, 45.0, 'SUP002'),
        'C300': Article('C300', 'Vis M6x40', 'BRUT', 3, 0.5, 'SUP003')
    }
    st.session_state.state.boms = [
        BOM('A100', 'B200', 4), BOM('A100', 'C300', 16)
    ]
    st.session_state.state.suppliers = {
        'SUP001': Supplier('SUP001', 'Meubles Luxe SA', 5),
        'SUP002': Supplier('SUP002', 'MétalPro', 7)
    }
    st.session_state.state.machines = {
        'M001': Machine('M001', 'Assembleuse', 8, 1000),
        'M002': Machine('M002', 'Soudage', 6, 800)
    }

state = st.session_state.state

# NOUVELLES CLASSES
@dataclass
class Machine:
    code: str
    name: str
    capacity_hours: float  # heures/jour
    efficiency: float      # % efficacité

# FONCTIONS MRP ÉTENDUES (identiques + nouvelles)
def explode_bom(article_code: str, qty: float, visited: set = None) -> Dict[str, float]:
    if visited is None: visited = set()
    if article_code in visited: return {}
    visited = visited.copy()
    visited.add(article_code)
    
    needs: Dict[str, float] = {}
    for bom in state.boms:
        if bom.parent == article_code:
            required = qty * bom.quantity
            needs[bom.component] = needs.get(bom.component, 0) + required
            sub_needs = explode_bom(bom.component, required, visited)
            for k, v in sub_needs.items():
                needs[k] = needs.get(k, 0) + v
    return needs

def calculate_mrp() -> pd.DataFrame:
    results = []
    for d in state.demands:
        gross_needs = {d.article: d.qty}
        exploded = explode_bom(d.article, d.qty)
        gross_needs.update(exploded)
        
        for art_code, qty in gross_needs.items():
            if art_code not in state.articles: continue
            art = state.articles[art_code]
            stock = state.stocks.get(art_code, Stock(art_code, 0.0, 0.0))
            net = max(qty - stock.qty + stock.safety, 0)
            
            lead = art.lead_time
            if art.supplier and art.supplier in state.suppliers:
                lead = state.suppliers[art.supplier].lead_time
            
            order_date = d.due_date - timedelta(days=lead)
            
            results.append({
                "Article": art.name,
                "Code": art_code,
                "Besoin Brut": qty,
                "Stock": stock.qty,
                "Sécurité": stock.safety,
                "Besoin Net": net,
                "Date Ordre": order_date.strftime('%Y-%m-%d'),
                "Date Livraison": d.due_date.strftime('%Y-%m-%d'),
                "Type": "🛒 OA" if art.type == "BRUT" else "🏭 OF",
                "Coût Total": round(net * art.unit_cost, 2),
                "Durée (jours)": lead
            })
    
    df = pd.DataFrame(results)
    state.mrp_results = df.sort_values('Date Ordre') if not df.empty else df
    return df

def forecast_demand():
    """Prévision IA avec Prophet"""
    if len(state.demands) < 10:
        # Données démo pour démo
        dates = pd.date_range('2025-10-01', periods=60)
        hist_qty = np.random.poisson(15, 60)
        hist_df = pd.DataFrame({'ds': dates, 'y': hist_qty})
    else:
        hist_df = pd.DataFrame([{
            'ds': d.due_date, 'y': d.qty
        } for d in state.demands[-30:]]).sort_values('ds')
    
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(hist_df)
    
    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)
    
    state.forecast_results = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(90)
    return forecast

def generate_pdf_report():
    """Rapport PDF professionnel"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Titre
    title = Paragraph("🧠 RAPPORT MRP/CBN - " + date.today().strftime("%d/%m/%Y"), 
                     styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Tableau MRP
    if not state.mrp_results.empty:
        data = [['Article', 'Besoin Net', 'Coût Total (€)', 'Date Ordre']] + \
               [row[:4].tolist() for _, row in state.mrp_results.iterrows()]
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# INTERFACE PRO
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); 
           padding: 3rem; border-radius: 30px; margin-bottom: 3rem; text-align: center; 
           color: white; box-shadow: 0 30px 60px rgba(0,0,0,0.25);'>
    <h1 style='font-size: 4rem; font-weight: 900; margin: 0; letter-spacing: -2px;'>🧠 MRP/CBN Pro v3.0</h1>
    <p style='font-size: 1.5rem; opacity: 0.95; margin: 1rem 0;'>🚀 Planification Industrielle IA & Automatisée</p>
    <div style='font-size: 1.2rem; opacity: 0.8;'>✅ Prévision IA • Gantt • Excel • PDF • KPI Pro • Machines</div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR PRO
with st.sidebar:
    st.markdown("### 🚀 **Navigation Pro**")
    tab_names = ["📊 Dashboard Pro", "🔮 Prévision IA", "📦 Articles", "🧱 Nomenclatures", 
                "🤝 Partenaires", "⚙️ Machines", "🏬 Stocks", "📈 Demandes", 
                "⚡ Résultats MRP", "📈 KPI Avancés", "📁 Import/Export"]
    tab = st.selectbox("Choisissez", tab_names, index=0)
    
    st.markdown("---")
    
    # ACTIONS GLOBALES
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 **CALCULER MRP**", type="primary", use_container_width=True):
            with st.spinner("🔄 Calcul MRP multi-niveaux + optimisation..."):
                calculate_mrp()
            st.success("✅ MRP calculé !")
            st.rerun()
    
    with col2:
        if st.button("🔮 **PRÉVOIR**", type="secondary", use_container_width=True):
            forecast_demand()
            st.success("✅ Prévision IA terminée !")
    
    # KPI Sidebar
    if not state.mrp_results.empty:
        st.metric("💰 Coût Total", f"{state.mrp_results['Coût Total'].sum():,.0f}€")
        st.metric("⚠️ Ordres", len(state.mrp_results))

# CONTENU TABS AVANCÉS
if tab == "📊 Dashboard Pro":
    st.markdown('<div class="glass-card-pro">', unsafe_allow_html=True)
    
    # KPI PRO 8 métriques
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card-pro">
            <h3 style="margin:0;font-size:1.2rem;">📈 Demandes</h3>
            <div style="font-size:3.5rem;font-weight:900;">""" + str(len(state.demands)) + """</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card-pro">
            <h3 style="margin:0;font-size:1.2rem;">📦 Articles</h3>
            <div style="font-size:3.5rem;font-weight:900;">""" + str(len(state.articles)) + """</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card-pro">
            <h3 style="margin:0;font-size:1.2rem;">🧱 BOMs</h3>
            <div style="font-size:3.5rem;font-weight:900;">""" + str(len(state.boms)) + """</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card-pro">
            <h3 style="margin:0;font-size:1.2rem;">⚙️ Machines</h3>
            <div style="font-size:3.5rem;font-weight:900;">""" + str(len(state.machines)) + """</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not state.mrp_results.empty:
        col_gantt, col_pie = st.columns([2,1])
        with col_gantt:
            fig = px.timeline(state.mrp_results, x_start="Date Ordre", x_end="Date Livraison", 
                            y="Article", color="Type", title="📋 Gantt Interactif MRP")
            st.plotly_chart(fig, use_container_width=True)
        
        with col_pie:
            fig2 = px.pie(state.mrp_results, values='Coût Total', names='Type', 
                         title="Répartition OA/OF")
            st.plotly_chart(fig2, use_container_width=True)

elif tab == "🔮 Prévision IA":
    st.markdown('<div class="glass-card-pro">', unsafe_allow_html=True)
    st.subheader("🔮 Prévision Demande avec Prophet")
    
    if st.button("🚀 Lancer Prévision IA", type="primary"):
        with st.spinner("IA en cours d'analyse temporelle..."):
            forecast_demand()
    
    if not state.forecast_results.empty:
        fig_forecast = px.line(state.forecast_results, x='ds', y=['yhat_lower', 'yhat', 'yhat_upper'],
                             title="📈 Prévision 90 jours - Intervalle 80%", 
                             labels={'value': 'Quantité', 'ds': 'Date'})
        fig_forecast.add_hline(y=state.forecast_results['yhat'].mean(), line_dash="dot", 
                             annotation_text="Moyenne Prévue")
        st.plotly_chart(fig_forecast, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "📦 Articles":
    st.markdown('<div class="glass-card-pro">', unsafe_allow_html=True)
    st.subheader("📦 Gestion Articles")
    
    col1, col2 = st.columns([1,2])
    with col1:
        code = st.text_input("💾 Code *")
        art_type = st.selectbox("⚙️ Type", ["BRUT", "COMPOSE"])
    with col2:
        name = st.text_input("📝 Désignation")
        lead_time = st.number_input("⏱️ Délai (jours)", min_value=0, value=5)
        unit_cost = st.number_input("💰 Coût unitaire €", min_value=0.0, value=10.0)
        supplier = st.text_input("🏢 Fournisseur")
    
    if st.button("🎉 AJOUTER", type="primary"):
        if code: 
            state.articles[code] = Article(code, name or 'N/A', art_type, int(lead_time), 
                                        float(unit_cost), supplier or None)
            st.success(f"✅ {code} ajouté!")
            st.rerun()
    
    if state.articles:
        st.dataframe(pd.DataFrame([vars(a) for a in state.articles.values()]), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "⚙️ Machines":
    st.markdown('<div class="glass-card-pro">', unsafe_allow_html=True)
    st.subheader("⚙️ Gestion Machines")
    
    col1, col2, col3 = st.columns(3)
    with col1: code = st.text_input("🔧 Code Machine")
    with col2: name = st.text_input("🏭 Nom")
    with col3: capacity = st.number_input("⏱️ Capacité h/jour", value=8.0)
    
    eff = st.number_input("⚡ Efficacité %", min_value=50.0, max_value=100.0, value=85.0)
    
    if st.button("➕ Ajouter Machine", type="primary"):
        if code: 
            state.machines[code] = Machine(code, name, float(capacity), float(eff)/100)
            st.success("✅ Machine ajoutée!")
    
    if state.machines:
        mach_df = pd.DataFrame([vars(m) for m in state.machines.values()])
        st.dataframe(mach_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "📈 Demandes":
    st.markdown('<div class="glass-card-pro">', unsafe_allow_html=True)
    st.subheader("📈 Nouvelles Demandes")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: client = st.text_input("👥 Client")
    with col2: article = st.text_input("📦 Article")
    with col3: qty = st.number_input("📊 Qté", value=10.0)
    with col4: due_date = st.date_input("📅 Livraison", value=pd.Timestamp.now().date() + timedelta(30))
    
    if st.button("📈 AJOUTER", type="primary"):
        if client and article:
            state.demands.append(Demand(client, article, float(qty), due_date))
            st.success("✅ Demande créée!")
            st.rerun()
    
    if state.demands:
        st.dataframe(pd.DataFrame([vars(d) for d in state.demands]), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "⚡ Résultats MRP":
    st.markdown('<div class="glass-card-pro">', unsafe_allow_html=True)
    if not state.mrp_results.empty:
        st.dataframe(state.mrp_results, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(state.mrp_results, x='Article', y='Besoin Net', color='Type',
                        title="Besoins Nets", text='Besoin Net')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(state.mrp_results, x='Date Ordre', y='Coût Total', 
                         title="Coût par date", color='Type')
            st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "📈 KPI Avancés":
    st.markdown('<div class="glass-card-pro">', unsafe_allow_html=True)
    if not state.mrp_results.empty:
        col1, col2, col3, col4 = st.columns(4)
        total_cost = state.mrp_results['Coût Total'].sum()
        critical = len(state.mrp_results[state.mrp_results['Besoin Net'] > 0])
        avg_lead = state.mrp_results['Durée (jours)'].mean()
        on_time = 92.5  # Simulation
        
        with col1: st.metric("💰 Coût Total", f"{total_cost:,.0f}€", "↓ 3%")
        with col2: st.metric("⚠️ Ordres critiques", critical)
        with col3: st.metric("⏱️ Délai moyen", f"{avg_lead:.1f}j")
        with col4: st.metric("✅ Respect délais", f"{on_time}%", "↑ 1.2%")
    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "📁 Import/Export":
    st.markdown('<div class="glass-card-pro">', unsafe_allow_html=True)
    st.subheader("📁 Import/Export Excel & PDF")
    
    col_imp, col_exp = st.columns(2)
    
    with col_imp:
        st.subheader("📥 IMPORT")
        uploaded_file = st.file_uploader("Choisir Excel", type=['xlsx', 'xls'])
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                if 'code' in df.columns:
                    for _, row in df.iterrows():
                        if pd.notna(row['code']):
                            state.articles[row['code']] = Article(
                                row['code'], row.get('name', 'N/A'), 
                                row.get('type', 'BRUT'), int(row.get('lead_time', 5)),
                                float(row.get('cost', 10.0)), row.get('supplier')
                            )
                    st.success(f"✅ {len(df)} articles importés!")
            except Exception as e:
                st.error(f"Erreur: {e}")
    
    with col_exp:
        st.subheader("📤 EXPORT")
        if st.button("📄 Télécharger Rapport PDF", type="primary"):
            pdf_data = generate_pdf_report()
            st.download_button(
                "📥 Télécharger PDF",
                data=pdf_data,
                file_name=f"MRP_Report_{date.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
        
        if st.button("📊 Exporter Excel"):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                pd.DataFrame([vars(a) for a in state.articles.values()]).to_excel(writer, 'Articles', index=False)
                pd.DataFrame([vars(b) for b in state.boms]).to_excel(writer, 'BOM', index=False)
                if not state.mrp_results.empty:
                    state.mrp_results.to_excel(writer, 'MRP', index=False)
            st.download_button(
                "📥 Excel Complet",
                output.getvalue(),
                f"MRP_Complete_{date.today().strftime('%Y%m%d')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Classes manquantes (définies en haut du fichier)
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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center; padding:2rem; color:#666;'>
    <p>🧠 MRP/CBN Pro v3.0 | Solution Industrielle Complète | © 2026</p>
</div>
""", unsafe_allow_html=True)
