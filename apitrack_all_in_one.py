"""
ApiTrack Pro v2.1 — Plateforme Apicole Professionnelle
Auteur : RAHIM S. | Région de l'Oranie, Algérie
Morphométrie selon Ruttner (1988) · Données Chahbar et al. (2013)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
import hashlib
import os
from datetime import datetime, timedelta
import json

# ─────────────────────────────────────────────
# CONFIGURATION GÉNÉRALE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ApiTrack Pro",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "apitrack.db"

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
RACE_BADGES = {
    "A. m. intermissa": "badge-intermissa",
    "A. m. sahariensis": "badge-sahariensis",
    "A. m. ligustica": "badge-ligustica",
    "A. m. carnica": "badge-carnica",
    "Hybride": "badge-hybride",
}

PROFIL_ICONS = {
    "Miel": "🍯",
    "Pollen": "🌼",
    "Gelée Royale": "👑",
    "Résistance": "🛡️",
}

PROFIL_COLORS = {
    "Miel": "#D4820A",
    "Pollen": "#F59E0B",
    "Gelée Royale": "#9B59B6",
    "Résistance": "#22C55E",
}

# ─────────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg: #FDFAF4;
        --card: #FFFFFF;
        --border: rgba(180,150,80,0.2);
        --text-primary: #2C2010;
        --text-secondary: #6B6040;
        --honey: #D4820A;
        --honey-light: #F5C842;
        --green-dark: #2D4A1E;
        --purple: #9B59B6;
        --amber: #F59E0B;
    }

    html, body, [data-testid="stAppViewContainer"] { background: var(--bg) !important; }
    [data-testid="stSidebar"] { background: linear-gradient(160deg,#1A2E0F,#2D4A1E,#1A2E0F) !important; border-right:1px solid rgba(245,200,66,0.12); }
    [data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }

    .page-title {
        font-family:'Playfair Display',serif;
        font-size:28px; font-weight:700;
        color:#2C2010; margin-bottom:4px; line-height:1.2;
    }
    .page-subtitle {
        font-size:13px; color:#9B8860; margin-bottom:24px;
        letter-spacing:0.02em;
    }
    .section-header {
        font-family:'Playfair Display',serif;
        font-size:17px; font-weight:600;
        color:#2C2010; margin:20px 0 12px;
        padding-bottom:8px;
        border-bottom:2px solid rgba(212,130,10,0.2);
    }
    .section-sub { font-size:11px; color:#9B8860; font-weight:400; margin-left:8px; }

    .metric-card {
        background: var(--card);
        border-radius:16px; padding:20px 18px;
        border:1px solid var(--border);
        box-shadow:0 2px 12px rgba(180,150,80,0.06);
        transition: box-shadow 0.2s;
    }
    .metric-card:hover { box-shadow:0 4px 20px rgba(180,150,80,0.14); }
    .metric-icon { font-size:24px; margin-bottom:10px; }
    .metric-val {
        font-family:'Playfair Display',serif;
        font-size:26px; font-weight:700; color:#2C2010; line-height:1;
    }
    .metric-label { font-size:12px; color:#9B8860; margin-top:4px; letter-spacing:0.04em; }
    .metric-badge {
        font-size:10px; font-weight:600; padding:2px 8px;
        border-radius:20px; background:rgba(212,130,10,0.1);
        color:#D4820A; margin-top:8px; display:inline-block;
    }

    .ruche-card {
        background: var(--card);
        border-radius:16px; padding:18px;
        border:1px solid var(--border);
        box-shadow:0 2px 8px rgba(0,0,0,0.04);
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom:8px;
    }
    .ruche-card:hover { transform:translateY(-2px); box-shadow:0 6px 24px rgba(180,150,80,0.12); }

    .badge {
        display:inline-block; font-size:10px; font-weight:600;
        padding:3px 10px; border-radius:20px; letter-spacing:0.05em;
    }
    .badge-excellent { background:#DCFCE7; color:#166534; }
    .badge-bon       { background:#D1FAE5; color:#065F46; }
    .badge-attention { background:#FEF3C7; color:#92400E; }
    .badge-critique  { background:#FEE2E2; color:#991B1B; }
    .badge-intermissa  { background:#FFF3CD; color:#8B5200; }
    .badge-sahariensis { background:#EDE9FE; color:#5B21B6; }
    .badge-ligustica   { background:#DBEAFE; color:#1E40AF; }
    .badge-carnica     { background:#D1FAE5; color:#065F46; }
    .badge-hybride     { background:#F3F4F6; color:#374151; }

    .alert {
        border-radius:12px; padding:14px 18px;
        margin-bottom:10px; font-size:13px; line-height:1.6;
        border-left:4px solid;
    }
    .alert-danger  { background:#FEF2F2; border-color:#EF4444; color:#7F1D1D; }
    .alert-warning { background:#FFFBEB; border-color:#F59E0B; color:#78350F; }
    .alert-success { background:#F0FDF4; border-color:#22C55E; color:#14532D; }
    .alert-info    { background:#EFF6FF; border-color:#3B82F6; color:#1E3A8A; }
    .alert-royal   { background:#FAF5FF; border-color:#9B59B6; color:#4C1D95; }

    .morph-card {
        background: var(--card);
        border-radius:16px; padding:20px;
        border:1px solid var(--border);
        box-shadow:0 2px 8px rgba(0,0,0,0.04);
        margin-bottom:16px;
    }
    .measure-row {
        display:flex; justify-content:space-between; align-items:center;
        padding:8px 0; border-bottom:1px solid rgba(180,150,80,0.1);
        font-size:13px;
    }
    .measure-val-ok   { color:#16A34A; font-weight:600; font-family:'JetBrains Mono',monospace; }
    .measure-val-warn { color:#D97706; font-weight:600; font-family:'JetBrains Mono',monospace; }
    .measure-val-err  { color:#DC2626; font-weight:600; font-family:'JetBrains Mono',monospace; }

    .race-result-box {
        background:linear-gradient(135deg,#FFFBEB,#FEF3C7);
        border-radius:16px; padding:20px; text-align:center;
        border:2px solid rgba(212,130,10,0.3); margin-bottom:16px;
    }
    .race-name {
        font-family:'Playfair Display',serif;
        font-size:22px; font-weight:700; color:#92400E; margin-top:6px;
        font-style:italic;
    }
    .race-conf {
        font-size:12px; font-weight:600; padding:4px 12px;
        border-radius:20px; background:rgba(212,130,10,0.15); color:#92400E;
    }

    .timeline-item {
        border-left:3px solid rgba(212,130,10,0.3);
        padding:12px 0 12px 16px; margin-bottom:4px;
    }
    .timeline-date  { font-weight:600; font-size:13px; color:#2C2010; margin-bottom:4px; }
    .timeline-event { font-size:13px; color:#4A3728; margin-bottom:3px; }
    .timeline-note  { font-size:12px; color:#9B8860; font-style:italic; }

    /* Streamlit overrides */
    .stButton > button {
        border-radius:10px !important; font-weight:500 !important;
        transition: all 0.2s !important;
    }
    .stButton > button[kind="primary"] {
        background:linear-gradient(135deg,#D4820A,#B86E08) !important;
        border:none !important; color:white !important;
    }
    .stButton > button[kind="primary"]:hover { transform:translateY(-1px) !important; }
    [data-testid="stRadio"] label { font-size:13px !important; padding:6px 10px !important; border-radius:8px; transition:background 0.15s; }
    [data-testid="stRadio"] label:hover { background:rgba(255,255,255,0.08) !important; }
    div[data-testid="stMetricValue"] { font-family:'Playfair Display',serif !important; }
    .stTabs [data-baseweb="tab"] { font-size:13px !important; }
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS HTML
# ─────────────────────────────────────────────
def metric_card(icon, value, label, badge=None):
    badge_html = f'<div class="metric-badge">{badge}</div>' if badge else ""
    return f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-val">{value}</div>
        <div class="metric-label">{label}</div>
        {badge_html}
    </div>"""

def section_header(title, sub=None):
    sub_html = f'<span class="section-sub">{sub}</span>' if sub else ""
    st.markdown(f'<div class="section-header">{title}{sub_html}</div>', unsafe_allow_html=True)

def alert(icon, text, cls="alert-info"):
    return f'<div class="alert {cls}">{icon} {text}</div>'

def badge(text, cls="badge-bon"):
    return f'<span class="badge {cls}">{text}</span>'

def ruche_card_html(r):
    status_map = {
        "Excellent": ("badge-excellent", "🟢"),
        "Bon":       ("badge-bon",       "🟡"),
        "Attention": ("badge-attention", "🟠"),
        "Critique":  ("badge-critique",  "🔴"),
    }
    cls, dot = status_map.get(r["Statut"], ("badge-bon", "⚪"))
    return f"""
    <div class="ruche-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px">
            <div>
                <div style="font-family:'Playfair Display',serif;font-size:16px;font-weight:700;color:#2C2010">{r['Nom']}</div>
                <div style="font-size:11px;color:#9B8860;font-family:'JetBrains Mono',monospace">{r['ID']} · {r['Site']}</div>
            </div>
            <span class="badge {cls}">{dot} {r['Statut']}</span>
        </div>
        <div style="font-size:11px;color:#9B8860;margin-bottom:10px;font-style:italic">{r['Race']}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px">
            <div style="background:#FDFAF4;border-radius:8px;padding:8px;text-align:center">
                <div style="font-weight:700;color:#D4820A;font-size:15px">{r['Miel_kg']} kg</div>
                <div style="font-size:10px;color:#9B8860">🍯 Miel</div>
            </div>
            <div style="background:#FDFAF4;border-radius:8px;padding:8px;text-align:center">
                <div style="font-weight:700;color:#F59E0B;font-size:15px">{r['Pollen_kg']} kg</div>
                <div style="font-size:10px;color:#9B8860">🌼 Pollen</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
            <div style="background:#FAF5FF;border-radius:8px;padding:8px;text-align:center">
                <div style="font-weight:700;color:#9B59B6;font-size:15px">{r['gelee_g']} g</div>
                <div style="font-size:10px;color:#9B8860">👑 Gelée R.</div>
            </div>
            <div style="background:#F0FDF4;border-radius:8px;padding:8px;text-align:center">
                <div style="font-weight:700;color:#16A34A;font-size:15px">{r['VSH_pct']}%</div>
                <div style="font-size:10px;color:#9B8860">🛡️ VSH</div>
            </div>
        </div>
        <div style="margin-top:10px;display:flex;justify-content:space-between;font-size:11px;color:#9B8860">
            <span>🪲 Varroa: <strong style="color:{'#DC2626' if r['Varroa_pct']>3 else '#D97706' if r['Varroa_pct']>2 else '#16A34A'}">{r['Varroa_pct']}%</strong></span>
            <span>⚖️ {r['Poids_kg']} kg</span>
        </div>
    </div>"""

def production_radar(r):
    categories = ["Miel","Pollen","Gelée R.","VSH","Douceur","Éco. hiv."]
    values = [
        min(r["Miel_kg"]/25*100, 100),
        min(r["Pollen_kg"]/6*100, 100),
        min(r["gelee_g"]/250*100, 100),
        r["VSH_pct"],
        r["Douceur"],
        r["Economie_hiv"],
    ]
    fig = go.Figure(go.Scatterpolar(
        r=values+[values[0]], theta=categories+[categories[0]],
        fill='toself', fillcolor='rgba(212,130,10,0.12)',
        line=dict(color='#D4820A', width=2),
        marker=dict(size=6, color='#D4820A')
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(253,250,244,0.5)',
            radialaxis=dict(visible=True, range=[0,100], tickfont=dict(size=8, color='#9B8860'),
                            gridcolor='rgba(180,150,80,0.2)'),
            angularaxis=dict(tickfont=dict(size=10, color='#4A3728'))
        ),
        showlegend=False, height=280,
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=30, r=30, t=30, b=30)
    )
    return fig

# ─────────────────────────────────────────────
# BASE DE DONNÉES
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Table settings
    c.execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY, value TEXT
    )""")

    # Table users
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TEXT
    )""")

    # Table ruches
    c.execute("""CREATE TABLE IF NOT EXISTS ruches (
        ID TEXT PRIMARY KEY,
        Nom TEXT, Race TEXT, Site TEXT,
        Poids_kg REAL, Varroa_pct REAL,
        Miel_kg REAL, Pollen_kg REAL, gelee_g REAL,
        Statut TEXT, Reine_id TEXT,
        VSH_pct REAL, Douceur REAL, Economie_hiv REAL,
        Essaimage_pct REAL, Date_creation TEXT,
        Cadres_couverts INT, Cadres_couvain INT,
        Temp_int REAL, Profil_prod TEXT,
        Glossa_mm REAL, L_aile_mm REAL, Ri REAL,
        Tomentum_pct INT, Pigment_scutellum INT, Ti_L_mm REAL,
        notes TEXT DEFAULT ''
    )""")

    # Table inspections
    c.execute("""CREATE TABLE IF NOT EXISTS inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT, Ruche TEXT, Poids_kg REAL,
        Cadres_couverts INT, Varroa TEXT, Reine TEXT,
        Comportement TEXT, Notes TEXT,
        Temp_ext REAL DEFAULT 20.0
    )""")

    # Table traitements
    c.execute("""CREATE TABLE IF NOT EXISTS traitements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date_debut TEXT, Ruche TEXT, Produit TEXT,
        Pathologie TEXT, Dose TEXT, Duree_j INT,
        Statut TEXT, Progression_pct INT,
        Methode TEXT DEFAULT '', Temp_ext REAL DEFAULT 18.0
    )""")

    # Table recoltes
    c.execute("""CREATE TABLE IF NOT EXISTS recoltes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT, Ruche TEXT, Type TEXT, Produit TEXT,
        Quantite_kg REAL, Humidite_pct REAL, Prix_kg REAL,
        Certification TEXT DEFAULT 'Standard'
    )""")

    # Table morph_analyses
    c.execute("""CREATE TABLE IF NOT EXISTS morph_analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT, Ruche TEXT, Taxon TEXT,
        Confiance_pct REAL, L_aile_mm REAL, Ri REAL,
        Glossa_mm REAL, B_aile_mm REAL, DI3_mm REAL,
        A4_deg REAL, B4_deg REAL, Ti_L_mm REAL,
        T3_L_mm REAL, Tomentum_pct REAL, Pigment INT,
        OI TEXT, Analyste TEXT, N_abeilles INT DEFAULT 10
    )""")

    # Table zones mellifères
    c.execute("""CREATE TABLE IF NOT EXISTS zones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT, type_production TEXT, flore TEXT,
        coordonnees TEXT, date_creation TEXT,
        superficie_ha REAL DEFAULT 0.0,
        notes TEXT DEFAULT ''
    )""")

    # Table activité / journal
    c.execute("""CREATE TABLE IF NOT EXISTS journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT, type_action TEXT, ruche TEXT,
        description TEXT, utilisateur TEXT
    )""")

    # Admin par défaut
    c.execute("INSERT OR IGNORE INTO settings VALUES ('apiculteur','RAHIM S.')")
    c.execute("INSERT OR IGNORE INTO settings VALUES ('rucher','Rucher de l\\'Oranie')")
    c.execute("INSERT OR IGNORE INTO settings VALUES ('region','Tlemcen, Algérie')")

    # User admin par défaut (mot de passe: admin1234)
    default_pwd = hashlib.sha256("admin1234".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users VALUES ('admin', ?, 'admin', ?)",
              (default_pwd, datetime.now().strftime("%Y-%m-%d")))

    # Données de démonstration si tables vides
    c.execute("SELECT COUNT(*) FROM ruches")
    if c.fetchone()[0] == 0:
        _seed_demo_data(c)

    conn.commit()
    conn.close()

def _seed_demo_data(c):
    """Insère des données de démonstration réalistes."""
    ruches_demo = [
        ("A-01","La Dorée","A. m. intermissa","Verger du Cèdre",22.5,1.2,18,2.8,120,"Excellent","R-2024-01",82,88,80,25,"2022-03-15",8,6,35.2,"Miel",6.12,9.22,2.45,38,5,3.02,"Belle colonie, très productive"),
        ("A-02","La Sauvage","A. m. intermissa","Verger du Cèdre",19.8,2.3,14,2.2,80,"Bon","R-2024-02",75,72,75,35,"2022-05-10",7,5,35.0,"Résistance",6.08,9.18,2.42,36,6,3.00,"Bonne résistance varroa"),
        ("B-01","La Reine du Miel","A. m. sahariensis","Plaine du Romarin",24.1,0.8,22,1.8,60,"Excellent","R-2024-03",88,92,85,20,"2021-04-20",9,7,35.5,"Miel",6.02,9.08,2.38,32,7,2.92,"Exceptionnelle productrice de miel"),
        ("B-02","L'Italienne","A. m. ligustica","Plaine du Romarin",20.3,1.8,15,3.2,180,"Bon","R-2023-04",70,78,72,30,"2023-06-01",7,5,35.1,"Gelée Royale",6.42,9.52,2.78,52,2,3.18,"Très bonne pour la gelée royale"),
        ("C-01","La Carnica","A. m. carnica","Colline des Abeilles",21.2,1.5,16,3.8,150,"Bon","R-2024-05",78,85,88,22,"2022-09-12",8,6,35.3,"Pollen",6.58,9.62,3.02,45,2,3.22,"Excellente collectrice de pollen"),
        ("C-02","La Hybride","Hybride","Colline des Abeilles",18.5,3.8,10,1.5,40,"Critique","R-2023-06",58,65,70,45,"2023-02-28",5,3,34.8,"Miel",6.18,9.28,2.55,40,4,3.05,"Traitement varroa en cours - surveillance"),
        ("D-01","La Berbère","A. m. intermissa","Rucher de la Mosquée",23.0,0.5,20,2.5,90,"Excellent","R-2024-07",90,95,82,18,"2021-11-05",9,7,35.6,"Miel",6.10,9.20,2.40,37,5,3.00,"Meilleure colonie du rucher"),
        ("D-02","La Sahara","A. m. sahariensis","Rucher de la Mosquée",17.8,2.8,12,1.8,65,"Attention","R-2024-08",65,70,68,38,"2023-08-15",6,4,34.9,"Résistance",6.00,9.05,2.35,30,8,2.88,"Surveiller le niveau varroa"),
    ]
    c.executemany("""INSERT INTO ruches VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", ruches_demo)

    # Récoltes démo
    recoltes_demo = [
        ("2024-06-15","A-01","Miel","Miel de jujubier",12.5,17.2,1500,"Standard"),
        ("2024-06-15","B-01","Miel","Miel de romarin",15.0,17.8,1600,"Bio (certifié)"),
        ("2024-06-20","D-01","Miel","Miel toutes fleurs",10.0,17.5,1400,"Standard"),
        ("2024-05-10","C-01","Pollen","Pollen — Romarin, Jujubier",2.2,7.2,4500,"Standard"),
        ("2024-05-15","B-02","Pollen","Pollen — Oranger",1.8,7.8,4200,"Standard"),
        ("2024-06-01","B-02","Gelée Royale","Gelée royale fraîche",0.08,68.0,120000,"Standard"),
        ("2024-06-15","C-01","Gelée Royale","Gelée royale fraîche",0.06,67.5,120000,"Standard"),
    ]
    c.executemany("INSERT INTO recoltes (Date,Ruche,Type,Produit,Quantite_kg,Humidite_pct,Prix_kg,Certification) VALUES (?,?,?,?,?,?,?,?)", recoltes_demo)

    # Inspections démo
    inspections_demo = [
        ("2024-06-10","A-01",22.5,8,"Faible (<1%)","Observée","Calme","Couvain sain, ponte régulière. Très bonne colonie.",20.0),
        ("2024-06-10","C-02",18.5,5,"Élevée (>3%)","Observée","Nerveux","Varroa élevé, traitement à l'acide oxalique démarré.",22.0),
        ("2024-06-12","D-01",23.0,9,"Aucune visible","Observée","Calme","Excellente colonie. Risque d'essaimage à surveiller.",19.0),
        ("2024-06-12","D-02",17.8,6,"Modérée (1–3%)","Observée","Calme","Colonie en progrès. Surveiller varroa.",20.0),
    ]
    c.executemany("INSERT INTO inspections (Date,Ruche,Poids_kg,Cadres_couverts,Varroa,Reine,Comportement,Notes,Temp_ext) VALUES (?,?,?,?,?,?,?,?,?)", inspections_demo)

    # Traitements démo
    traitements_demo = [
        ("2024-06-01","C-02","Acide oxalique","Varroa destructor","5 ml/ruche",21,"En cours",48,"Sublimation",22.0),
        ("2024-04-15","Toutes les ruches","Apiguard (thymol)","Varroa destructor","25g gel/ruche",28,"Terminé",100,"Lanière",18.0),
    ]
    c.executemany("INSERT INTO traitements (Date_debut,Ruche,Produit,Pathologie,Dose,Duree_j,Statut,Progression_pct,Methode,Temp_ext) VALUES (?,?,?,?,?,?,?,?,?,?)", traitements_demo)

    # Zones démo
    zones_demo = [
        ("Plaine du Romarin","Miel","Rosmarinus officinalis","34.8900,-1.3100","2024-01-10",5.0,"Zone principale"),
        ("Verger du Jujubier","Miel","Ziziphus lotus","34.8750,-1.3250","2024-02-15",3.0,"Excellente floraison en mai-juin"),
        ("Colline des Orangers","Pollen","Citrus sinensis","34.8950,-1.3050","2024-03-01",2.0,"Bonne source de pollen au printemps"),
    ]
    c.executemany("INSERT INTO zones (nom,type_production,flore,coordonnees,date_creation,superficie_ha,notes) VALUES (?,?,?,?,?,?,?)", zones_demo)

# ─────────────────────────────────────────────
# CRUD FUNCTIONS
# ─────────────────────────────────────────────
def get_setting(key):
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else ""

def set_setting(key, value):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, value))
    conn.commit()
    conn.close()

def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def verify_login(username, password):
    conn = get_db()
    row = conn.execute("SELECT password_hash FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return row and row["password_hash"] == hash_pwd(password)

def change_password(username, new_pwd):
    conn = get_db()
    conn.execute("UPDATE users SET password_hash=? WHERE username=?", (hash_pwd(new_pwd), username))
    conn.commit()
    conn.close()

def load_dataframes():
    conn = get_db()
    data = {
        "ruches":         pd.read_sql("SELECT * FROM ruches", conn),
        "inspections":    pd.read_sql("SELECT * FROM inspections", conn),
        "traitements":    pd.read_sql("SELECT * FROM traitements", conn),
        "recoltes":       pd.read_sql("SELECT * FROM recoltes", conn),
        "morph_analyses": pd.read_sql("SELECT * FROM morph_analyses", conn),
        "zones":          pd.read_sql("SELECT * FROM zones", conn),
        "journal":        pd.read_sql("SELECT * FROM journal", conn),
    }
    conn.close()
    # Nettoyage types
    for col in ["Miel_kg","Pollen_kg","gelee_g","VSH_pct","Douceur","Economie_hiv",
                "Essaimage_pct","Poids_kg","Varroa_pct","Glossa_mm","L_aile_mm",
                "Ri","Tomentum_pct","Ti_L_mm"]:
        if col in data["ruches"].columns:
            data["ruches"][col] = pd.to_numeric(data["ruches"][col], errors="coerce").fillna(0)
    return data

def add_ruche(row_dict):
    conn = get_db()
    df = pd.DataFrame([row_dict])
    df.to_sql("ruches", conn, if_exists="append", index=False)
    _log_action(conn, "Ajout ruche", row_dict.get("ID",""), f"Nouvelle ruche : {row_dict.get('Nom','')}")
    conn.commit()
    conn.close()

def update_ruche(row_dict):
    conn = get_db()
    cols = [k for k in row_dict if k != "ID"]
    sets = ", ".join(f"{k}=?" for k in cols)
    vals = [row_dict[k] for k in cols] + [row_dict["ID"]]
    conn.execute(f"UPDATE ruches SET {sets} WHERE ID=?", vals)
    conn.commit()
    conn.close()

def delete_ruche(ruche_id):
    conn = get_db()
    conn.execute("DELETE FROM ruches WHERE ID=?", (ruche_id,))
    for table in ["inspections","traitements","recoltes","morph_analyses"]:
        conn.execute(f"DELETE FROM {table} WHERE Ruche=?", (ruche_id,))
    _log_action(conn, "Suppression ruche", ruche_id, f"Ruche supprimée avec toutes ses données")
    conn.commit()
    conn.close()

def add_inspection(row):
    conn = get_db()
    conn.execute("""INSERT INTO inspections (Date,Ruche,Poids_kg,Cadres_couverts,Varroa,Reine,Comportement,Notes,Temp_ext)
                    VALUES (?,?,?,?,?,?,?,?,?)""",
                 (row["Date"], row["Ruche"], row["Poids_kg"], row["Cadres_couverts"],
                  row["Varroa"], row["Reine"], row["Comportement"], row["Notes"],
                  row.get("Temp_ext", 20.0)))
    _log_action(conn, "Inspection", row["Ruche"], row.get("Notes","")[:80])
    conn.commit()
    conn.close()

def add_traitement(row):
    conn = get_db()
    conn.execute("""INSERT INTO traitements (Date_debut,Ruche,Produit,Pathologie,Dose,Duree_j,Statut,Progression_pct,Methode,Temp_ext)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                 (row["Date_debut"], row["Ruche"], row["Produit"], row["Pathologie"],
                  row["Dose"], row["Duree_j"], row["Statut"], row["Progression_pct"],
                  row.get("Methode",""), row.get("Temp_ext", 20.0)))
    conn.commit()
    conn.close()

def update_traitement_progression(t_id, pct, statut):
    conn = get_db()
    conn.execute("UPDATE traitements SET Progression_pct=?, Statut=? WHERE id=?", (pct, statut, t_id))
    conn.commit()
    conn.close()

def add_recolte(row):
    conn = get_db()
    conn.execute("""INSERT INTO recoltes (Date,Ruche,Type,Produit,Quantite_kg,Humidite_pct,Prix_kg,Certification)
                    VALUES (?,?,?,?,?,?,?,?)""",
                 (row["Date"], row["Ruche"], row["Type"], row["Produit"],
                  row["Quantite_kg"], row["Humidite_pct"], row["Prix_kg"],
                  row.get("Certification","Standard")))
    _log_action(conn, f"Récolte {row['Type']}", row["Ruche"], f"{row['Quantite_kg']} kg")
    conn.commit()
    conn.close()

def add_morph_analyse(row):
    conn = get_db()
    conn.execute("""INSERT INTO morph_analyses
        (Date,Ruche,Taxon,Confiance_pct,L_aile_mm,Ri,Glossa_mm,B_aile_mm,DI3_mm,A4_deg,B4_deg,
         Ti_L_mm,T3_L_mm,Tomentum_pct,Pigment,OI,Analyste,N_abeilles)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (row["Date"], row["Ruche"], row["Taxon"], row["Confiance_pct"],
         row["L_aile_mm"], row["Ri"], row["Glossa_mm"], row["B_aile_mm"],
         row["DI3_mm"], row["A4_deg"], row["B4_deg"], row["Ti_L_mm"],
         row["T3_L_mm"], row["Tomentum_pct"], row["Pigment"],
         row["OI"], row["Analyste"], row.get("N_abeilles", 10)))
    conn.commit()
    conn.close()

def add_zone(row):
    conn = get_db()
    conn.execute("""INSERT INTO zones (nom,type_production,flore,coordonnees,date_creation,superficie_ha,notes)
                    VALUES (?,?,?,?,?,?,?)""",
                 (row["nom"], row["type_production"], row["flore"], row["coordonnees"],
                  row["date_creation"], row.get("superficie_ha", 0.0), row.get("notes", "")))
    conn.commit()
    conn.close()

def delete_zone(zone_id):
    conn = get_db()
    conn.execute("DELETE FROM zones WHERE id=?", (zone_id,))
    conn.commit()
    conn.close()

def _log_action(conn, type_action, ruche, description):
    user = st.session_state.get("username", "système")
    conn.execute("INSERT INTO journal (date,type_action,ruche,description,utilisateur) VALUES (?,?,?,?,?)",
                 (datetime.now().strftime("%Y-%m-%d %H:%M"), type_action, ruche, description, user))

# ─────────────────────────────────────────────
# CLASSIFICATION MORPHOMÉTRIQUE
# ─────────────────────────────────────────────
def classify_bee(L, Ri, Ac, pv, tom, ti):
    scores = {
        "A. m. intermissa": 0,
        "A. m. sahariensis": 0,
        "A. m. ligustica": 0,
        "A. m. carnica": 0,
    }
    # Longueur aile
    if 8.9<=L<=9.6: scores["A. m. intermissa"]+=20
    if 8.7<=L<=9.3: scores["A. m. sahariensis"]+=20
    if 9.1<=L<=9.8: scores["A. m. ligustica"]+=15; scores["A. m. carnica"]+=15
    # Indice cubital
    if 2.0<=Ri<=2.8: scores["A. m. intermissa"]+=20
    if 2.1<=Ri<=2.9: scores["A. m. sahariensis"]+=18
    if 2.4<=Ri<=3.2: scores["A. m. ligustica"]+=20
    if 2.6<=Ri<=3.5: scores["A. m. carnica"]+=20
    # Glossa
    if 5.9<=Ac<=6.3: scores["A. m. intermissa"]+=25
    if 5.8<=Ac<=6.2: scores["A. m. sahariensis"]+=20
    if 6.3<=Ac<=6.7: scores["A. m. ligustica"]+=25
    if 6.4<=Ac<=6.8: scores["A. m. carnica"]+=25
    # Pigmentation
    if 4<=pv<=7: scores["A. m. intermissa"]+=15
    if 5<=pv<=8: scores["A. m. sahariensis"]+=15
    if 1<=pv<=3: scores["A. m. ligustica"]+=15; scores["A. m. carnica"]+=15
    # Tomentum
    if 30<=tom<=45: scores["A. m. intermissa"]+=20
    if 25<=tom<=40: scores["A. m. sahariensis"]+=15
    if 45<=tom<=60: scores["A. m. ligustica"]+=20
    if 35<=tom<=50: scores["A. m. carnica"]+=15

    total = sum(scores.values()) or 1
    probs = {k: v/total*100 for k, v in scores.items()}
    best = max(probs, key=probs.get)
    if probs[best] < 38: best = "Hybride"; probs["Hybride"] = probs[best]
    return best, probs

# ─────────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────────
init_db()
inject_css()

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "apiculteur" not in st.session_state:
    st.session_state.apiculteur = get_setting("apiculteur")
if "data" not in st.session_state:
    st.session_state.data = load_dataframes()

# ─────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("""
    <div style="max-width:420px;margin:80px auto 0;text-align:center">
        <div style="background:linear-gradient(135deg,#D4820A,#8B5200);border-radius:20px;
                    width:72px;height:72px;display:flex;align-items:center;justify-content:center;
                    font-size:38px;margin:0 auto 20px">🐝</div>
        <div style="font-family:'Playfair Display',serif;font-size:32px;font-weight:700;color:#2C2010">ApiTrack Pro</div>
        <div style="font-size:13px;color:#9B8860;margin-bottom:32px;letter-spacing:0.08em">Plateforme Apicole Professionnelle</div>
    </div>
    """, unsafe_allow_html=True)

    col_login = st.columns([1, 2, 1])[1]
    with col_login:
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur", placeholder="admin")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("🔐 Se connecter", use_container_width=True, type="primary")
            if submitted:
                if verify_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.apiculteur = get_setting("apiculteur")
                    st.session_state.data = load_dataframes()
                    st.rerun()
                else:
                    st.error("Identifiants incorrects")
        st.markdown("""
        <div style="text-align:center;font-size:12px;color:#9B8860;margin-top:16px">
            Compte démo : <strong>admin</strong> / <strong>admin1234</strong>
        </div>""", unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    rucher_name = get_setting("rucher")
    st.markdown(f"""
    <div style="padding:16px 0 20px">
        <div style="background:linear-gradient(135deg,#D4820A,#8B5200);border-radius:14px;
                    width:52px;height:52px;display:flex;align-items:center;justify-content:center;
                    font-size:26px;margin-bottom:12px">🐝</div>
        <div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700;
                    color:#F5C842;line-height:1.1">ApiTrack Pro</div>
        <div style="font-size:10px;letter-spacing:0.14em;text-transform:uppercase;
                    color:rgba(255,255,255,0.45);margin-top:3px">Plateforme Apicole v2.1</div>
    </div>
    <hr style="border-color:rgba(255,255,255,0.1);margin:0 0 12px">
    """, unsafe_allow_html=True)

    pages = {
        "📊 Vue d'ensemble":      "dashboard",
        "🏠 Mes Ruches":          "ruches",
        "🔍 Inspections":         "inspections",
        "💊 Traitements":         "traitements",
        "🍯 Miel":                "miel",
        "🌼 Pollen":              "pollen",
        "👑 Gelée Royale":        "gelee",
        "🔬 Morphométrie":        "morphometrie",
        "🧬 Génétique & Races":   "genetique",
        "📈 Caractérisation":     "caracterisation",
        "🗺️ Cartographie":        "carte",
        "🌸 Flore Mellifère":     "flore",
        "🌤️ Météo & Miellée":    "meteo",
        "📋 Rapports":            "rapports",
        "🚨 Alertes":             "alertes",
        "📓 Journal":             "journal",
        "💾 Administration":      "admin",
    }

    selected_label = st.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
    current_page = pages[selected_label]

    st.markdown("<hr style='border-color:rgba(255,255,255,0.1)'>", unsafe_allow_html=True)

    nb_ruches = len(st.session_state.data["ruches"])
    df_r = st.session_state.data["ruches"]
    nb_alertes = int(df_r["Statut"].isin(["Critique","Attention"]).sum()) if nb_ruches > 0 else 0
    total_miel = float(df_r["Miel_kg"].sum()) if nb_ruches > 0 else 0

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:14px 16px;font-size:12px">
        <div style="color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:0.1em;font-size:10px;margin-bottom:8px">Aperçu rapide</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:6px">
            <span style="color:rgba(255,255,255,0.7)">🏠 Ruches actives</span>
            <strong style="color:#F5C842">{nb_ruches}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:6px">
            <span style="color:rgba(255,255,255,0.7)">🚨 Alertes</span>
            <strong style="color:#ef4444">{nb_alertes}</strong>
        </div>
        <div style="display:flex;justify-content:space-between">
            <span style="color:rgba(255,255,255,0.7)">🍯 Total miel</span>
            <strong style="color:#F5C842">{total_miel:.0f} kg</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    initiale = st.session_state.apiculteur[0].upper() if st.session_state.apiculteur else "A"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding-bottom:10px">
        <div style="width:36px;height:36px;background:#D4820A;border-radius:50%;
                    display:flex;align-items:center;justify-content:center;font-weight:700;
                    color:#2D4A1E;font-size:14px;flex-shrink:0">{initiale}</div>
        <div>
            <div style="font-size:13px;color:rgba(255,255,255,0.85);font-weight:500">{st.session_state.apiculteur}</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.4)">Apiculteur professionnel</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ─────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────
if current_page == "dashboard":
    df = st.session_state.data["ruches"]
    rec = st.session_state.data["recoltes"]

    st.markdown('<div class="page-title">🐝 Vue d\'ensemble — ApiTrack Pro</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Tableau de bord centralisé · {get_setting("rucher")} · Saison 2024–2025</div>', unsafe_allow_html=True)

    total_miel = df["Miel_kg"].sum()
    total_pollen = df["Pollen_kg"].sum()
    total_gelee_g = df["gelee_g"].sum()
    ca_miel   = (rec[rec["Type"]=="Miel"]["Quantite_kg"] * rec[rec["Type"]=="Miel"]["Prix_kg"]).sum()
    ca_pollen = (rec[rec["Type"]=="Pollen"]["Quantite_kg"] * rec[rec["Type"]=="Pollen"]["Prix_kg"]).sum()
    ca_gelee  = (rec[rec["Type"]=="Gelée Royale"]["Quantite_kg"] * rec[rec["Type"]=="Gelée Royale"]["Prix_kg"]).sum()
    ca_total  = ca_miel + ca_pollen + ca_gelee

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(metric_card("🏠", str(len(df)), "Ruches actives"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("🍯", f"{total_miel:.0f} kg", "Miel récolté", "+18% vs 2023"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("🌼", f"{total_pollen:.1f} kg", "Pollen récolté", "+22% vs 2023"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("👑", f"{total_gelee_g:.0f} g", "Gelée royale", "+35% vs 2023"), unsafe_allow_html=True)
    with c5: st.markdown(metric_card("💰", f"{ca_total:,.0f} DA", "Chiffre d'affaires", "+25% vs 2023"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])

    with col_l:
        section_header("📊 Production par type — Valeur en DA")
        rec_df = rec.copy()
        rec_df["Valeur"] = rec_df["Quantite_kg"] * rec_df["Prix_kg"]
        prod_by_type = rec_df.groupby("Type").agg({"Quantite_kg":"sum","Valeur":"sum"}).reset_index()

        fig = go.Figure()
        colors_type = {"Miel":"#D4820A","Pollen":"#F59E0B","Gelée Royale":"#9B59B6"}
        for _, row in prod_by_type.iterrows():
            fig.add_trace(go.Bar(
                x=[row["Type"]], y=[row["Valeur"]],
                name=row["Type"],
                marker_color=colors_type.get(row["Type"], "#6B7280"),
                text=f"{row['Valeur']:,.0f} DA", textposition="outside",
                textfont=dict(size=12, color="#4A3728"),
            ))
        fig.update_layout(height=280, showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
            yaxis=dict(showgrid=True, gridcolor='rgba(180,150,80,0.15)', tickfont=dict(color='#6B6040')),
            xaxis=dict(tickfont=dict(size=13, color='#4A3728', family='Playfair Display')),
            margin=dict(l=10,r=10,t=30,b=10), bargap=0.35)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        section_header("📈 Évolution mensuelle de la production")
        months = ["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Août","Sep","Oct","Nov","Déc"]
        miel_m   = [0,8,12,35,60,75,55,40,22,5,0,0]
        pollen_m = [0,5,18,28,22,15,10,8,5,2,0,0]
        gelee_m  = [0,0,8,18,35,48,38,25,12,0,0,0]

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=months, y=miel_m, name="Miel (kg)", fill='tozeroy',
            fillcolor='rgba(212,130,10,0.12)', line=dict(color='#D4820A', width=2.5),
            mode='lines+markers', marker=dict(size=6, color='#D4820A')))
        fig2.add_trace(go.Scatter(x=months, y=pollen_m, name="Pollen (kg)", fill='tozeroy',
            fillcolor='rgba(245,158,11,0.1)', line=dict(color='#F59E0B', width=2, dash='dot'),
            mode='lines+markers', marker=dict(size=5, color='#F59E0B')))
        fig2.add_trace(go.Scatter(x=months, y=[g*10 for g in gelee_m], name="Gelée royale (g×10)", fill='tozeroy',
            fillcolor='rgba(155,89,182,0.1)', line=dict(color='#9B59B6', width=2, dash='dash'),
            mode='lines+markers', marker=dict(size=5, color='#9B59B6')))
        fig2.update_layout(height=280,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(size=11, color='#4A3728'), bgcolor='rgba(255,255,255,0.8)'),
            xaxis=dict(tickfont=dict(color='#6B6040'), gridcolor='rgba(180,150,80,0.1)'),
            yaxis=dict(tickfont=dict(color='#6B6040'), gridcolor='rgba(180,150,80,0.1)'),
            margin=dict(l=10,r=10,t=40,b=10))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    with col_r:
        section_header("🚨 Alertes prioritaires")
        alertes_dash = []
        for _, r in df.iterrows():
            if r["Varroa_pct"] > 3:
                alertes_dash.append(("🔴", f"CRITIQUE — {r['ID']} : Varroa {r['Varroa_pct']}%", "alert-danger"))
            elif r["Varroa_pct"] > 2:
                alertes_dash.append(("🟠", f"ATTENTION — {r['ID']} : Varroa {r['Varroa_pct']}%", "alert-warning"))
        if not alertes_dash:
            alertes_dash.append(("✅", "Aucune alerte varroa critique en ce moment.", "alert-success"))
        for icon, txt, cls in alertes_dash[:4]:
            st.markdown(alert(icon, txt, cls), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("🌤️ Conditions du rucher")
        st.markdown("""
        <div style="background:linear-gradient(135deg,#2D4A1E,#3D6B2C);border-radius:16px;padding:22px;color:white">
            <div style="font-size:10px;opacity:0.6;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:8px">Aujourd'hui — Tlemcen</div>
            <div style="font-family:'Playfair Display',serif;font-size:44px;font-weight:700;line-height:1">22°C</div>
            <div style="font-size:14px;opacity:0.85;margin-top:4px">☀️ Ensoleillé — Excellent pour la miellée</div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:18px;
                        padding-top:16px;border-top:1px solid rgba(255,255,255,0.15)">
                <div style="text-align:center"><div style="font-size:18px;font-weight:600">65%</div>
                    <div style="font-size:10px;opacity:0.55;text-transform:uppercase">Humidité</div></div>
                <div style="text-align:center"><div style="font-size:18px;font-weight:600">12 km/h</div>
                    <div style="font-size:10px;opacity:0.55;text-transform:uppercase">Vent</div></div>
                <div style="text-align:center"><div style="font-size:18px;font-weight:600">8/10</div>
                    <div style="font-size:10px;opacity:0.55;text-transform:uppercase">Miellée</div></div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("🥧 Répartition du CA par produit")
        fig_pie = go.Figure(go.Pie(
            labels=["🍯 Miel","🌼 Pollen","👑 Gelée Royale"],
            values=[max(ca_miel,1), max(ca_pollen,1), max(ca_gelee,1)],
            hole=0.55,
            marker=dict(colors=["#D4820A","#F59E0B","#9B59B6"], line=dict(color='white',width=3)),
            textfont=dict(size=12, color='#4A3728'),
            hovertemplate="%{label}: %{value:,.0f} DA<extra></extra>"
        ))
        fig_pie.update_layout(height=240,
            paper_bgcolor='rgba(0,0,0,0)', showlegend=True,
            legend=dict(font=dict(size=11, color='#4A3728'), bgcolor='rgba(0,0,0,0)'),
            margin=dict(l=0,r=0,t=10,b=10),
            annotations=[dict(text=f"{ca_total:,.0f}<br>DA", x=0.5, y=0.5,
                              font=dict(size=12, color='#4A3728', family='Playfair Display'), showarrow=False)])
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar":False})

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("🏠 Aperçu des ruches", "Statut en temps réel")
    cols = st.columns(4)
    for i, (_, r) in enumerate(df.iterrows()):
        with cols[i % 4]:
            st.markdown(ruche_card_html(r), unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: RUCHES
# ─────────────────────────────────────────────
elif current_page == "ruches":
    st.markdown('<div class="page-title">🏠 Gestion des Ruches</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Inventaire complet · Profils de production · Santé des colonies</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🃏 Cartes ruches","📋 Tableau détaillé","📊 Analyses","✏️ Modifier ruche","➕ Nouvelle ruche"])

    with tab1:
        df = st.session_state.data["ruches"]
        c1, c2, c3 = st.columns(3)
        with c1: f_statut = st.selectbox("Statut", ["Tous","Excellent","Bon","Attention","Critique"])
        with c2: f_profil = st.selectbox("Profil", ["Tous","Miel","Pollen","Gelée Royale","Résistance"])
        with c3: f_race   = st.selectbox("Race",   ["Toutes"] + list(df["Race"].unique()))

        filtered = df.copy()
        if f_statut != "Tous":    filtered = filtered[filtered["Statut"]==f_statut]
        if f_profil != "Tous":    filtered = filtered[filtered["Profil_prod"]==f_profil]
        if f_race != "Toutes":    filtered = filtered[filtered["Race"]==f_race]

        if filtered.empty:
            st.info("Aucune ruche ne correspond aux filtres.")
        else:
            cols = st.columns(4)
            for i, (_, r) in enumerate(filtered.iterrows()):
                with cols[i % 4]:
                    st.markdown(ruche_card_html(r), unsafe_allow_html=True)
                    if st.button("🔍 Détails", key=f"btn_{r['ID']}"):
                        st.session_state["selected_ruche"] = r["ID"]

        if "selected_ruche" in st.session_state:
            rid = st.session_state["selected_ruche"]
            row_list = df[df["ID"]==rid]
            if not row_list.empty:
                row = row_list.iloc[0]
                st.markdown("---")
                section_header(f"🔍 Détail — {row['Nom']} ({rid})")
                dc1, dc2 = st.columns([2, 1])
                with dc1:
                    st.markdown(f"""
                    <div class="morph-card">
                        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:16px">
                            <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase">Race</div><div style="font-weight:600;margin-top:3px">{row['Race']}</div></div>
                            <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase">Site</div><div style="font-weight:600;margin-top:3px">{row['Site']}</div></div>
                            <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase">Reine</div><div style="font-weight:600;margin-top:3px;font-family:monospace;font-size:11px">{row['Reine_id']}</div></div>
                            <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase">Création</div><div style="font-weight:600;margin-top:3px">{row['Date_creation']}</div></div>
                        </div>
                        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px">
                            <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase">🍯 Miel</div><div style="font-weight:700;font-size:18px;color:#D4820A;margin-top:3px">{row['Miel_kg']} kg</div></div>
                            <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase">🌼 Pollen</div><div style="font-weight:700;font-size:18px;color:#F59E0B;margin-top:3px">{row['Pollen_kg']} kg</div></div>
                            <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase">👑 Gelée</div><div style="font-weight:700;font-size:18px;color:#9B59B6;margin-top:3px">{row['gelee_g']} g</div></div>
                            <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase">🛡️ VSH</div><div style="font-weight:700;font-size:18px;color:#22C55E;margin-top:3px">{row['VSH_pct']}%</div></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                with dc2:
                    st.plotly_chart(production_radar(row), use_container_width=True, config={"displayModeBar":False})

    with tab2:
        df = st.session_state.data["ruches"]
        display_cols = ["ID","Nom","Race","Site","Statut","Profil_prod","Poids_kg","Varroa_pct","Miel_kg","Pollen_kg","gelee_g","VSH_pct"]
        st.dataframe(
            df[display_cols].rename(columns={"Profil_prod":"Profil","Varroa_pct":"Varroa %",
                "Miel_kg":"Miel (kg)","Pollen_kg":"Pollen (kg)","gelee_g":"Gelée (g)","VSH_pct":"VSH %"}),
            use_container_width=True, hide_index=True,
            column_config={
                "Varroa %": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=5),
                "Miel (kg)": st.column_config.NumberColumn(format="%.1f kg"),
                "VSH %": st.column_config.ProgressColumn(format="%d%%", min_value=0, max_value=100),
            })
        st.markdown("#### Supprimer une ruche")
        del_id = st.selectbox("ID ruche à supprimer", df["ID"].tolist(), key="del_ruche_tab2")
        if st.button("🗑 Supprimer définitivement", type="primary", key="del_btn_tab2"):
            delete_ruche(del_id)
            st.session_state.data = load_dataframes()
            st.success(f"Ruche {del_id} supprimée.")
            st.rerun()

    with tab3:
        df = st.session_state.data["ruches"]
        section_header("📊 Comparaison des productions")
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(x=df["ID"], y=df["Miel_kg"], name="🍯 Miel (kg)", marker_color='#D4820A', text=df["Miel_kg"], textposition='outside'))
        fig_comp.add_trace(go.Bar(x=df["ID"], y=df["Pollen_kg"]*5, name="🌼 Pollen (kg×5)", marker_color='#F59E0B'))
        fig_comp.add_trace(go.Bar(x=df["ID"], y=df["gelee_g"]/10, name="👑 Gelée (g/10)", marker_color='#9B59B6'))
        fig_comp.update_layout(barmode='group', height=360,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
            legend=dict(font=dict(size=11), bgcolor='rgba(255,255,255,0.8)'),
            margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar":False})

        section_header("🎯 Score global par ruche")
        df["Score"] = (df["Miel_kg"]/20*25 + df["Pollen_kg"]/5*15 + df["gelee_g"]/200*15 +
                       df["VSH_pct"]/100*25 + df["Douceur"]/100*10 + df["Economie_hiv"]/100*10).clip(0,100)
        fig_score = go.Figure(go.Bar(
            x=df["Score"].round(1), y=df["Nom"], orientation='h',
            marker=dict(color=df["Score"], colorscale=[[0,'#fee2e2'],[0.5,'#fef9c3'],[1,'#dcfce7']],
                        line=dict(color='white',width=1)),
            text=[f"{s:.0f}/100" for s in df["Score"]], textposition='inside',
            textfont=dict(color='#1E1A0F', size=12)
        ))
        fig_score.update_layout(height=300,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
            xaxis=dict(range=[0,105], tickfont=dict(color='#6B6040')),
            yaxis=dict(tickfont=dict(color='#4A3728', size=12)),
            margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig_score, use_container_width=True, config={"displayModeBar":False})

    with tab4:
        # NOUVEAU : onglet modification de ruche
        df = st.session_state.data["ruches"]
        section_header("✏️ Modifier une ruche existante")
        selected_edit = st.selectbox("Sélectionner la ruche à modifier", [f"{r['ID']} — {r['Nom']}" for _,r in df.iterrows()])
        rid_edit = selected_edit.split("—")[0].strip()
        row_edit = df[df["ID"]==rid_edit].iloc[0]

        c1, c2 = st.columns(2)
        with c1:
            e_nom      = st.text_input("Nom",  value=row_edit["Nom"])
            e_site     = st.text_input("Site", value=row_edit["Site"])
            e_statut   = st.selectbox("Statut", ["Excellent","Bon","Attention","Critique"],
                                       index=["Excellent","Bon","Attention","Critique"].index(row_edit["Statut"]))
            e_profil   = st.selectbox("Profil de production", ["Miel","Pollen","Gelée Royale","Résistance"],
                                       index=["Miel","Pollen","Gelée Royale","Résistance"].index(row_edit["Profil_prod"]))
            e_varroa   = st.number_input("Varroa (%)", min_value=0.0, max_value=10.0, value=float(row_edit["Varroa_pct"]), step=0.1)
        with c2:
            e_miel     = st.number_input("Miel (kg)", min_value=0.0, value=float(row_edit["Miel_kg"]), step=0.5)
            e_pollen   = st.number_input("Pollen (kg)", min_value=0.0, value=float(row_edit["Pollen_kg"]), step=0.1)
            e_gelee    = st.number_input("Gelée royale (g)", min_value=0.0, value=float(row_edit["gelee_g"]), step=1.0)
            e_poids    = st.number_input("Poids (kg)", min_value=0.0, value=float(row_edit["Poids_kg"]), step=0.5)
            e_vsh      = st.number_input("VSH (%)", min_value=0, max_value=100, value=int(row_edit["VSH_pct"]))
        e_notes = st.text_area("Notes", value=str(row_edit.get("notes","")))

        if st.button("💾 Enregistrer les modifications", type="primary"):
            update_ruche({
                "ID": rid_edit, "Nom": e_nom, "Site": e_site,
                "Statut": e_statut, "Profil_prod": e_profil,
                "Varroa_pct": e_varroa, "Miel_kg": e_miel,
                "Pollen_kg": e_pollen, "gelee_g": e_gelee,
                "Poids_kg": e_poids, "VSH_pct": e_vsh, "notes": e_notes
            })
            st.session_state.data = load_dataframes()
            st.success(f"✅ Ruche {rid_edit} mise à jour !")
            st.rerun()

    with tab5:
        section_header("➕ Enregistrer une nouvelle ruche")
        c1, c2 = st.columns(2)
        with c1:
            nid     = st.text_input("Identifiant *", placeholder="Ex : E-01")
            nnom    = st.text_input("Nom *", placeholder="Ex : La Dorée")
            nrace   = st.selectbox("Race", ["A. m. intermissa","A. m. sahariensis","A. m. ligustica","A. m. carnica","Hybride","Indéterminée"])
            nsite   = st.text_input("Site / Rucher", placeholder="Ex : Verger du Cèdre")
            nprofil = st.selectbox("Profil de production", ["Miel","Pollen","Gelée Royale","Résistance"])
        with c2:
            ndate   = st.date_input("Date de création", value=datetime.now())
            npoids  = st.number_input("Poids initial (kg)", min_value=0.0, value=18.0, step=0.5)
            nstatut = st.selectbox("Statut initial", ["Excellent","Bon","Attention","Critique"])
            nreine  = st.text_input("ID Reine", placeholder="Ex : R-2025-01")
        nnotes = st.text_area("Observations initiales")

        if st.button("✓ Enregistrer la ruche", type="primary"):
            if not nid or not nnom:
                st.error("Renseignez l'identifiant et le nom.")
            elif nid in st.session_state.data["ruches"]["ID"].values:
                st.error(f"L'ID {nid} existe déjà.")
            else:
                add_ruche({
                    "ID":nid,"Nom":nnom,"Race":nrace,"Site":nsite,
                    "Poids_kg":npoids,"Varroa_pct":0.0,
                    "Miel_kg":0,"Pollen_kg":0,"gelee_g":0,
                    "Statut":nstatut,"Reine_id":nreine or "À définir",
                    "VSH_pct":70,"Douceur":80,"Economie_hiv":75,"Essaimage_pct":30,
                    "Date_creation":str(ndate),"Cadres_couverts":0,"Cadres_couvain":0,
                    "Temp_int":35.0,"Profil_prod":nprofil,
                    "Glossa_mm":6.0,"L_aile_mm":9.2,"Ri":2.5,
                    "Tomentum_pct":35,"Pigment_scutellum":5,"Ti_L_mm":3.0,"notes":nnotes
                })
                st.session_state.data = load_dataframes()
                st.success(f"✅ Ruche {nid} « {nnom} » enregistrée !")
                st.balloons()

# ─────────────────────────────────────────────
# PAGE: INSPECTIONS
# ─────────────────────────────────────────────
elif current_page == "inspections":
    st.markdown('<div class="page-title">🔍 Inspections</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Journal de terrain · Suivi sanitaire · Historique complet</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 Nouvelle inspection","📅 Historique"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            ruche_noms = [f"{r['ID']} — {r['Nom']}" for _,r in st.session_state.data["ruches"].iterrows()]
            insp_ruche = st.selectbox("Ruche inspectée *", ruche_noms)
            insp_date  = st.date_input("Date *", value=datetime.now())
            insp_poids = st.number_input("Poids pesée (kg)", min_value=0.0, value=20.0, step=0.1)
            insp_temp  = st.number_input("Température intérieure (°C)", min_value=0.0, value=35.0, step=0.1)
            insp_cadres  = st.slider("Cadres couverts", 0, 10, 7)
            insp_couvain = st.slider("Cadres de couvain", 0, 10, 5)
        with c2:
            insp_reine    = st.selectbox("Présence reine", ["Observée","Non observée (ponte présente)","Absente"])
            insp_varroa   = st.selectbox("Niveau varroa", ["Aucune visible","Faible (<1%)","Modérée (1–3%)","Élevée (>3%)"])
            insp_reserves = st.selectbox("Réserves de miel", ["Excellentes (>15 kg)","Bonnes (8–15 kg)","Faibles (3–8 kg)","Insuffisantes (<3 kg)"])
            insp_comport  = st.selectbox("Comportement", ["Calme","Nerveux","Agressif"])
            insp_maladie  = st.multiselect("Signes de maladie", ["Aucun","Loque américaine","Loque européenne","Nosémose","Teigne","Sacbrood"])
            insp_notif    = st.selectbox("Statut général", ["Excellent","Bon","Attention","Critique"])
            insp_temp_ext = st.number_input("Température extérieure (°C)", min_value=-10, max_value=50, value=20, step=1)
        insp_notes = st.text_area("Observations", height=100)

        if st.button("✓ Enregistrer l'inspection", type="primary"):
            add_inspection({
                "Date": str(insp_date),
                "Ruche": insp_ruche.split("—")[0].strip(),
                "Poids_kg": insp_poids,
                "Cadres_couverts": insp_cadres,
                "Varroa": insp_varroa,
                "Reine": insp_reine,
                "Comportement": insp_comport,
                "Notes": insp_notes,
                "Temp_ext": float(insp_temp_ext),
            })
            st.session_state.data = load_dataframes()
            st.success("✅ Inspection enregistrée !")

    with tab2:
        df_insp = st.session_state.data["inspections"].sort_values("Date", ascending=False)
        section_header(f"📅 Journal — {len(df_insp)} inspections")

        # Filtre par ruche
        ruches_list = ["Toutes"] + list(df_insp["Ruche"].unique())
        f_ruche_insp = st.selectbox("Filtrer par ruche", ruches_list, key="f_insp_ruche")
        if f_ruche_insp != "Toutes":
            df_insp = df_insp[df_insp["Ruche"]==f_ruche_insp]

        for _, row in df_insp.iterrows():
            varroa_icon = "🔴" if "Élevée" in str(row.get("Varroa","")) else "🟡" if "Modérée" in str(row.get("Varroa","")) else "🟢"
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-date">{row['Date']} — Ruche {row['Ruche']}</div>
                <div class="timeline-event">{varroa_icon} {row.get('Comportement','—')} · Poids : {row['Poids_kg']} kg · Cadres : {row.get('Cadres_couverts','?')}</div>
                <div class="timeline-note">👑 Reine : {row.get('Reine','?')} · 🌡️ {row.get('Temp_ext','?')}°C ext.</div>
                <div class="timeline-note">{row.get('Notes','—')}</div>
            </div>""", unsafe_allow_html=True)

        if not df_insp.empty:
            csv_insp = df_insp.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Exporter CSV", csv_insp, "inspections.csv", "text/csv")

# ─────────────────────────────────────────────
# PAGE: TRAITEMENTS
# ─────────────────────────────────────────────
elif current_page == "traitements":
    st.markdown('<div class="page-title">💊 Traitements Vétérinaires</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Conformité réglementaire · Suivi anti-varroa · Historique médicamenteux</div>', unsafe_allow_html=True)
    st.markdown(alert("ℹ️","Consigner tous les traitements vétérinaires est obligatoire. Données exportables pour conformité réglementaire.","alert-info"), unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["💊 Enregistrer traitement","📊 Suivi en cours"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            t_ruche   = st.selectbox("Ruche(s)", ["Toutes les ruches"] + st.session_state.data["ruches"]["ID"].tolist())
            t_date    = st.date_input("Date de début", value=datetime.now())
            t_produit = st.selectbox("Produit", ["Acide oxalique","Acide formique","Apivar (amitraz)","Apiguard (thymol)","Thymovar","CheckMite+","Autre"])
            t_patho   = st.selectbox("Pathologie", ["Varroa destructor","Loque américaine","Loque européenne","Nosémose","Teigne","Autre"])
        with c2:
            t_dose    = st.text_input("Dose", placeholder="Ex : 5 ml / ruche")
            t_duree   = st.number_input("Durée (jours)", min_value=1, value=21)
            t_methode = st.selectbox("Méthode", ["Sublimation","Lanière","Vaporisation","Nourrissement","Autre"])
            t_temp    = st.number_input("Température ext. (°C)", min_value=-10, max_value=50, value=18)
        t_notes = st.text_area("Observations")
        if st.button("✓ Enregistrer le traitement", type="primary"):
            add_traitement({
                "Date_debut": str(t_date), "Ruche": t_ruche, "Produit": t_produit,
                "Pathologie": t_patho, "Dose": t_dose, "Duree_j": t_duree,
                "Statut": "En cours", "Progression_pct": 0,
                "Methode": t_methode, "Temp_ext": float(t_temp)
            })
            st.session_state.data = load_dataframes()
            st.success("✅ Traitement enregistré !")

    with tab2:
        df_trt = st.session_state.data["traitements"]
        for _, t in df_trt.iterrows():
            color = "#22c55e" if t["Statut"]=="Terminé" else "#ef4444"
            prog  = int(t["Progression_pct"])
            col_a, col_b = st.columns([4,1])
            with col_a:
                st.markdown(f"""
                <div style="background:white;border-radius:14px;padding:18px;border:1px solid rgba(180,150,80,0.2);
                            border-left:4px solid {color};margin-bottom:12px">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">
                        <div>
                            <div style="font-weight:600;font-size:14px">{t['Produit']} — {t['Ruche']}</div>
                            <div style="font-size:12px;color:#6B6040">{t['Pathologie']} · Débuté le {t['Date_debut']} · {t.get('Methode','')}</div>
                        </div>
                        <span class="badge {'badge-excellent' if t['Statut']=='Terminé' else 'badge-critique'}">{t['Statut']}</span>
                    </div>
                    <div style="height:10px;background:#F5EDD8;border-radius:5px;overflow:hidden">
                        <div style="height:100%;width:{prog}%;background:{'linear-gradient(90deg,#86EFAC,#22C55E)' if prog==100 else 'linear-gradient(90deg,#FB923C,#EF4444)'};border-radius:5px"></div>
                    </div>
                    <div style="font-size:11px;color:#6B6040;margin-top:5px">{prog}% · {t['Duree_j']} jours prévus</div>
                </div>""", unsafe_allow_html=True)
            with col_b:
                new_prog = st.number_input(f"Prog. %", 0, 100, prog, key=f"prog_{t['id']}", label_visibility="collapsed")
                if st.button("💾", key=f"save_prog_{t['id']}", help="Mettre à jour la progression"):
                    statut = "Terminé" if new_prog >= 100 else "En cours"
                    update_traitement_progression(int(t["id"]), new_prog, statut)
                    st.session_state.data = load_dataframes()
                    st.rerun()

# ─────────────────────────────────────────────
# PAGE: MIEL
# ─────────────────────────────────────────────
elif current_page == "miel":
    st.markdown('<div class="page-title">🍯 Production de Miel</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Récoltes · Qualité · Traçabilité · Analyse sensorielle</div>', unsafe_allow_html=True)

    df = st.session_state.data["ruches"]
    rec = st.session_state.data["recoltes"]
    miel_rec = rec[rec["Type"]=="Miel"].copy()

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(metric_card("🍯", f"{df['Miel_kg'].sum():.1f} kg", "Total produit"), unsafe_allow_html=True)
    with c2:
        ca = (miel_rec["Quantite_kg"]*miel_rec["Prix_kg"]).sum() if len(miel_rec)>0 else 0
        st.markdown(metric_card("💰", f"{ca:,.0f} DA", "Chiffre d'affaires"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("🏆", f"{df['Miel_kg'].max():.1f} kg", "Meilleure ruche"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("📊", f"{df['Miel_kg'].mean():.1f} kg", "Moyenne/ruche"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📊 Analyses","➕ Enregistrer récolte","📋 Historique"])

    with tab1:
        c_l, c_r = st.columns(2)
        with c_l:
            section_header("🏆 Production par ruche")
            df_s = df.sort_values("Miel_kg", ascending=True)
            fig = go.Figure(go.Bar(x=df_s["Miel_kg"], y=df_s["Nom"], orientation='h',
                marker=dict(color=df_s["Miel_kg"], colorscale=[[0,'#FFF8E6'],[1,'#8B5200']], line=dict(color='white',width=1)),
                text=[f"{v:.1f} kg" for v in df_s["Miel_kg"]], textposition='inside',
                textfont=dict(color='#4A3728',size=11)))
            fig.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                xaxis=dict(title="kg",tickfont=dict(color='#6B6040')),
                yaxis=dict(tickfont=dict(color='#4A3728',size=12)),
                margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        with c_r:
            section_header("📊 Répartition par type")
            if len(miel_rec)>0:
                tg = miel_rec.groupby("Produit")["Quantite_kg"].sum().reset_index()
                fig2 = go.Figure(go.Pie(labels=tg["Produit"], values=tg["Quantite_kg"], hole=0.45,
                    marker=dict(colors=["#D4820A","#F5C842","#E8A020","#8B5200","#C4773A"], line=dict(color='white',width=2))))
                fig2.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=10,b=10))
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

        section_header("💧 Contrôle qualité — Taux d'humidité")
        st.markdown(alert("ℹ️","Taux optimal : 17–18%. Au-delà de 18.5% : risque de fermentation.","alert-info"), unsafe_allow_html=True)
        if len(miel_rec)>0:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=miel_rec["Produit"], y=miel_rec["Humidite_pct"],
                mode='markers+text', marker=dict(size=14, color=miel_rec["Humidite_pct"],
                colorscale=[[0,'#22c55e'],[0.5,'#f59e0b'],[1,'#ef4444']], cmin=15, cmax=20,
                line=dict(color='white',width=2)),
                text=[f"{h}%" for h in miel_rec["Humidite_pct"]], textposition='top center',
                textfont=dict(size=11,color='#4A3728')))
            fig3.add_hline(y=18.5, line_dash="dash", line_color="#ef4444", annotation_text="Max (18.5%)")
            fig3.add_hline(y=16.0, line_dash="dash", line_color="#f59e0b", annotation_text="Min (16%)")
            fig3.update_layout(height=260, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                yaxis=dict(range=[14,21],title="Humidité (%)",tickfont=dict(color='#6B6040')),
                margin=dict(l=10,r=10,t=30,b=10))
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

    with tab2:
        section_header("Enregistrer une récolte de miel")
        c1, c2 = st.columns(2)
        with c1:
            r_date  = st.date_input("Date", value=datetime.now(), key="m_r_date")
            r_ruche = st.selectbox("Ruche", [f"{r['ID']} — {r['Nom']}" for _,r in st.session_state.data["ruches"].iterrows()])
            r_type  = st.selectbox("Type de miel", ["Miel toutes fleurs","Miel de jujubier","Miel de romarin","Miel d'eucalyptus","Miel d'oranger","Miel de thym"])
            r_qte   = st.number_input("Quantité (kg)", min_value=0.0, value=10.0, step=0.5)
        with c2:
            r_hum   = st.number_input("Humidité (%)", min_value=14.0, max_value=25.0, value=17.5, step=0.1)
            r_prix  = st.number_input("Prix (DA/kg)", min_value=0, value=1500, step=100)
            r_cert  = st.selectbox("Certification", ["Standard","Bio (certifié)","AOC/IGP","À certifier"])
        r_notes = st.text_area("Notes organoleptiques")
        if st.button("✓ Enregistrer", type="primary", key="btn_miel_rec"):
            add_recolte({"Date":str(r_date),"Ruche":r_ruche.split("—")[0].strip(),
                         "Type":"Miel","Produit":r_type,"Quantite_kg":r_qte,
                         "Humidite_pct":r_hum,"Prix_kg":r_prix,"Certification":r_cert})
            st.session_state.data = load_dataframes()
            st.success(f"✅ {r_qte} kg de miel enregistrés !")

    with tab3:
        st.dataframe(miel_rec.sort_values("Date",ascending=False), use_container_width=True, hide_index=True)
        if len(miel_rec)>0:
            csv = miel_rec.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Exporter CSV", csv, "recoltes_miel.csv","text/csv")

# ─────────────────────────────────────────────
# PAGE: POLLEN
# ─────────────────────────────────────────────
elif current_page == "pollen":
    st.markdown('<div class="page-title">🌼 Production de Pollen</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Collecte · Séchage · Qualité pollinique · Traçabilité botanique</div>', unsafe_allow_html=True)

    df = st.session_state.data["ruches"]
    rec = st.session_state.data["recoltes"]
    pol_rec = rec[rec["Type"]=="Pollen"].copy()

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(metric_card("🌼", f"{df['Pollen_kg'].sum():.1f} kg", "Total collecté"), unsafe_allow_html=True)
    with c2:
        ca_pol = (pol_rec["Quantite_kg"]*pol_rec["Prix_kg"]).sum() if len(pol_rec)>0 else 0
        st.markdown(metric_card("💰", f"{ca_pol:,.0f} DA", "CA Pollen"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("🏆", f"{df['Pollen_kg'].max():.1f} kg", "Meilleure collectrice"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("🌸", "8", "Espèces recensées"), unsafe_allow_html=True)

    st.markdown(alert("🌼","<strong>Conservation :</strong> Pollen frais à réfrigérer à 4°C ou congeler. Séchage à ≤40°C pendant 24–48h. Humidité cible après séchage : <8%.","alert-info"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📊 Analyses","➕ Enregistrer récolte","🔬 Palynologie"])

    with tab1:
        c_l, c_r = st.columns(2)
        with c_l:
            section_header("📊 Collecte par ruche")
            df_pol = df.sort_values("Pollen_kg",ascending=True)
            fig = go.Figure(go.Bar(x=df_pol["Pollen_kg"], y=df_pol["Nom"], orientation='h',
                marker_color='#F59E0B', text=[f"{v:.1f} kg" for v in df_pol["Pollen_kg"]], textposition='inside',
                textfont=dict(color='#4A3728',size=11)))
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        with c_r:
            section_header("🌸 Espèces pollinisées")
            especes = ["Romarin","Jujubier","Oranger","Thym","Lavande","Chardon","Alfa","Tournesol"]
            pcts = [28,22,18,12,9,5,4,2]
            fig2 = go.Figure(go.Pie(labels=especes, values=pcts, hole=0.45,
                marker=dict(colors=["#F59E0B","#D4820A","#E8A020","#B45309","#92400E","#78350F","#FBBF24","#FCD34D"],
                            line=dict(color='white',width=2)), textfont=dict(size=10)))
            fig2.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=10,b=10))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    with tab2:
        section_header("Enregistrer une collecte de pollen")
        c1, c2 = st.columns(2)
        with c1:
            p_date   = st.date_input("Date", value=datetime.now(), key="p_date")
            p_ruche  = st.selectbox("Ruche", [f"{r['ID']} — {r['Nom']}" for _,r in st.session_state.data["ruches"].iterrows()])
            p_qte    = st.number_input("Quantité brute (kg)", min_value=0.0, value=1.5, step=0.1)
            p_qte_s  = st.number_input("Après séchage (kg)", min_value=0.0, value=1.2, step=0.1)
        with c2:
            p_hum    = st.number_input("Humidité après séchage (%)", min_value=4.0, max_value=15.0, value=7.5, step=0.1)
            p_espece = st.text_input("Espèces florales", placeholder="Ex : Romarin, oranger")
            p_prix   = st.number_input("Prix (DA/kg)", min_value=0, value=4500, step=100)
        if st.button("✓ Enregistrer la collecte", type="primary", key="btn_pollen_rec"):
            add_recolte({"Date":str(p_date),"Ruche":p_ruche.split("—")[0].strip(),
                         "Type":"Pollen","Produit":f"Pollen — {p_espece or 'Mixte'}",
                         "Quantite_kg":p_qte_s,"Humidite_pct":p_hum,"Prix_kg":p_prix,"Certification":"Standard"})
            st.session_state.data = load_dataframes()
            st.success(f"✅ {p_qte_s} kg de pollen enregistrés !")

    with tab3:
        section_header("🔬 Analyse palynologique de référence")
        pal_data = {
            "Espèce": ["Ziziphus lotus","Rosmarinus off.","Citrus sinensis","Lavandula sp.","Thymus vulgaris","Eucalyptus glob."],
            "Famille": ["Rhamnaceae","Lamiaceae","Rutaceae","Lamiaceae","Lamiaceae","Myrtaceae"],
            "Taille (µm)": ["25–35","15–25","25–35","30–40","18–28","20–30"],
            "Valeur mellifère": ["★★★★★","★★★★","★★★★★","★★★★","★★★★","★★★★"],
            "Période": ["Mai–Juin","Fév–Avr","Avr–Mai","Juin–Jul","Avr–Juin","Nov–Jan"],
        }
        st.dataframe(pd.DataFrame(pal_data), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# PAGE: GELÉE ROYALE
# ─────────────────────────────────────────────
elif current_page == "gelee":
    st.markdown('<div class="page-title">👑 Gelée Royale</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Production · Qualité · Conservation · Commercialisation</div>', unsafe_allow_html=True)

    df = st.session_state.data["ruches"]
    rec = st.session_state.data["recoltes"]
    gr_rec = rec[rec["Type"]=="Gelée Royale"].copy()

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(metric_card("👑", f"{df['gelee_g'].sum()} g", "Total produit"), unsafe_allow_html=True)
    with c2:
        ca_gr = (gr_rec["Quantite_kg"]*gr_rec["Prix_kg"]).sum() if len(gr_rec)>0 else 0
        st.markdown(metric_card("💰", f"{ca_gr:,.0f} DA", "CA Gelée Royale"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("🏆", f"{df['gelee_g'].max()} g", "Meilleure productrice"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("🔬", str(int((df['gelee_g']>0).sum())), "Ruches productrices"), unsafe_allow_html=True)

    st.markdown(alert("👑","Conservation : fraîche à −18°C ou 4°C max 6 mois. pH optimal 3.5–4.5. Taux 10-HDA minimum 1.4% selon norme européenne.","alert-royal"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📊 Analyses","➕ Enregistrer récolte","🔬 Contrôle qualité"])

    with tab1:
        c_l, c_r = st.columns(2)
        with c_l:
            section_header("📊 Production par ruche (g)")
            df_gr = df[df["gelee_g"]>0].sort_values("gelee_g",ascending=True)
            if not df_gr.empty:
                fig = go.Figure(go.Bar(x=df_gr["gelee_g"], y=df_gr["Nom"], orientation='h',
                    marker_color='#9B59B6', text=[f"{v} g" for v in df_gr["gelee_g"]], textposition='inside',
                    textfont=dict(color='white',size=11)))
                fig.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(250,245,255,0.5)',
                    margin=dict(l=10,r=10,t=10,b=10))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        with c_r:
            section_header("📅 Calendrier de production GR")
            mois = ["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Août","Sep","Oct","Nov","Déc"]
            gr_m = [0,0,15,45,80,95,75,50,20,5,0,0]
            fig2 = go.Figure(go.Scatter(x=mois, y=gr_m, fill='tozeroy',
                fillcolor='rgba(155,89,182,0.15)', line=dict(color='#9B59B6',width=2.5),
                mode='lines+markers', marker=dict(size=7,color='#9B59B6')))
            fig2.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(250,245,255,0.5)',
                margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    with tab2:
        section_header("Enregistrer une récolte de gelée royale")
        c1, c2 = st.columns(2)
        with c1:
            gr_date   = st.date_input("Date", value=datetime.now(), key="gr_date")
            gr_ruche  = st.selectbox("Ruche", [f"{r['ID']} — {r['Nom']}" for _,r in st.session_state.data["ruches"].iterrows()])
            gr_qte_g  = st.number_input("Quantité (g)", min_value=0.0, value=50.0, step=1.0)
            gr_cellul = st.number_input("Nombre de cellules royales", min_value=0, value=30, step=1)
        with c2:
            gr_hda    = st.number_input("Taux 10-HDA (%)", min_value=0.0, max_value=5.0, value=1.8, step=0.1)
            gr_ph     = st.number_input("pH mesuré", min_value=3.0, max_value=6.0, value=3.8, step=0.1)
            gr_cons   = st.selectbox("Conservation", ["Congélation (−18°C)","Réfrigération (4°C)","Lyophilisation","Mélange au miel"])
            gr_prix   = st.number_input("Prix (DA/g)", min_value=0, value=120, step=10)
        if st.button("✓ Enregistrer la récolte GR", type="primary", key="btn_gr_rec"):
            add_recolte({"Date":str(gr_date),"Ruche":gr_ruche.split("—")[0].strip(),
                         "Type":"Gelée Royale","Produit":"Gelée royale fraîche",
                         "Quantite_kg":gr_qte_g/1000,"Humidite_pct":68.0,
                         "Prix_kg":gr_prix*1000,"Certification":"Standard"})
            st.session_state.data = load_dataframes()
            hda_ok = gr_hda >= 1.4
            ph_ok  = 3.5 <= gr_ph <= 4.5
            if hda_ok and ph_ok:
                st.success(f"✅ {gr_qte_g}g enregistrés ! Qualité conforme (10-HDA: {gr_hda}%, pH: {gr_ph})")
            else:
                st.warning(f"⚠️ Enregistrée mais attention : {'10-HDA < 1.4%' if not hda_ok else ''} {'pH hors norme' if not ph_ok else ''}")

    with tab3:
        section_header("🔬 Normes de qualité (Codex Alimentarius CAC/RCP 82-2013)")
        st.markdown(alert("📋","Humidité : 60–70% · Protéines totales : ≥11% · Acide 10-HDA : ≥1.4% · pH : 3.5–4.5 · Sucres réducteurs : ≤15%","alert-info"), unsafe_allow_html=True)
        if len(gr_rec)>0:
            st.dataframe(gr_rec[["Date","Ruche","Produit","Quantite_kg","Humidite_pct"]].rename(
                columns={"Quantite_kg":"Quantité (kg)","Humidite_pct":"Humidité (%)"}),
                use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# PAGE: MORPHOMÉTRIE
# ─────────────────────────────────────────────
elif current_page == "morphometrie":
    st.markdown('<div class="page-title">🔬 Morphométrie des Abeilles</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Caractérisation morphologique selon Ruttner (1988) · Analyse discriminante · Classification raciale</div>', unsafe_allow_html=True)

    st.markdown(alert("🔬","Protocole morphométrique basé sur Ruttner (1988), Cornuet & Fresnaye (1989), Kandemir et al. (2011). 36 caractères mesurables.","alert-info"), unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📷 Saisie mesures","📐 Référentiel","📊 Analyses comparatives","📋 Historique"])

    with tab1:
        c_form, c_result = st.columns([3, 2])
        with c_form:
            m_ruche     = st.selectbox("Ruche", [f"{r['ID']} — {r['Nom']}" for _,r in st.session_state.data["ruches"].iterrows()])
            m_date      = st.date_input("Date d'analyse", value=datetime.now(), key="m_date")
            m_analyste  = st.text_input("Analyste", value=st.session_state.apiculteur)
            m_n         = st.number_input("Nombre d'abeilles mesurées", min_value=1, value=10)

            st.markdown("**📏 Mesures de l'aile antérieure**")
            col1,col2,col3 = st.columns(3)
            with col1: m_L  = st.number_input("Longueur L (mm)", 7.0,12.0,9.18,0.01, format="%.2f")
            with col2: m_B  = st.number_input("Largeur B (mm)",  2.5,4.5, 3.21,0.01, format="%.2f")
            with col3: m_Ri = st.number_input("Indice cubital",  1.0,5.0, 2.45,0.01, format="%.2f")
            col4,col5 = st.columns(2)
            with col4: m_DI3 = st.number_input("Cellule 3 DI3 (mm)", 1.0,2.5,1.72,0.01, format="%.2f")
            with col5: m_OI  = st.selectbox("Indice discoïdal", ["+ (positif)","- (négatif)"])

            st.markdown("**📐 Angles alaires**")
            col6,col7 = st.columns(2)
            with col6: m_A4 = st.number_input("Angle A4 (°)", 85.0,115.0,99.2,0.1, format="%.1f")
            with col7: m_B4 = st.number_input("Angle B4 (°)", 80.0,110.0,91.5,0.1, format="%.1f")

            st.markdown("**🦵 Patte postérieure**")
            col8,col9,col10 = st.columns(3)
            with col8:  m_Ti  = st.number_input("Tibia Ti-L (mm)",     2.0,4.0,3.01,0.01, format="%.2f")
            with col9:  m_Ba  = st.number_input("Basitarse Ba-L (mm)", 1.2,2.5,1.88,0.01, format="%.2f")
            with col10: m_BaW = st.number_input("Larg. basitarse (mm)",0.7,1.5,1.09,0.01, format="%.2f")

            st.markdown("**🫀 Abdomen**")
            col11,col12 = st.columns(2)
            with col11: m_T3  = st.number_input("Tergite 3 T3-L (mm)", 3.5,5.5,4.78,0.01, format="%.2f")
            with col12: m_Tom = st.number_input("Tomentum T4 (%)",      0,100,37,1)

            st.markdown("**👅 Langue & pigmentation**")
            col13,col14 = st.columns(2)
            with col13: m_Ac = st.number_input("Glossa (mm)", 5.0,8.0,6.12,0.01, format="%.2f")
            with col14: m_Pv = st.slider("Pigmentation scutellum (1–9)", 1, 9, 5)

        with c_result:
            section_header("🧬 Classification")
            best_race, probs = classify_bee(m_L, m_Ri, m_Ac, m_Pv, m_Tom, m_Ti)
            conf = probs.get(best_race, 0)
            st.markdown(f"""
            <div class="race-result-box">
                <div style="font-size:11px;color:#6B6040;margin-bottom:4px;text-transform:uppercase">Taxon identifié</div>
                <div class="race-name">{best_race}</div>
                <div style="margin-top:8px"><span class="race-conf">Confiance : {conf:.0f}%</span></div>
            </div>""", unsafe_allow_html=True)

            for race, pct in sorted(probs.items(), key=lambda x:-x[1]):
                st.markdown(f"""
                <div style="margin-bottom:8px">
                    <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">
                        <span style="color:#4A3728;font-weight:500">{race}</span>
                        <span style="font-family:monospace;color:#6B6040">{pct:.0f}%</span>
                    </div>
                    <div style="height:8px;background:#F5EDD8;border-radius:4px;overflow:hidden">
                        <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#F5C842,#D4820A);border-radius:4px"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

        if st.button("💾 Sauvegarder l'analyse morphométrique", type="primary"):
            add_morph_analyse({
                "Date":str(m_date),"Ruche":m_ruche.split("—")[0].strip(),"Taxon":best_race,
                "Confiance_pct":round(conf,0),"L_aile_mm":m_L,"Ri":m_Ri,"Glossa_mm":m_Ac,
                "B_aile_mm":m_B,"DI3_mm":m_DI3,"A4_deg":m_A4,"B4_deg":m_B4,
                "Ti_L_mm":m_Ti,"T3_L_mm":m_T3,"Tomentum_pct":m_Tom,"Pigment":m_Pv,
                "OI":m_OI.split()[0],"Analyste":m_analyste,"N_abeilles":int(m_n)
            })
            st.session_state.data = load_dataframes()
            st.success(f"✅ {best_race} ({conf:.0f}% confiance) sauvegardé !")

    with tab2:
        section_header("📐 Référentiel morphométrique (Ruttner 1988)")
        ref_data = {
            "Code":["L","B","Ri","DI3","Ti-L","Ba-L","Ac","T3-L","Tom%","Pv"],
            "Caractère":["Long. aile ant.","Larg. aile ant.","Indice cubital","Cellule 3","Tibia P3","Basitarse","Glossa","Tergite 3","Tomentum T4","Pigmentation"],
            "A.m. intermissa":["8.9–9.6","3.0–3.4","2.0–2.8","1.5–1.9","2.8–3.2","1.7–2.0","5.9–6.3","4.6–5.0","30–45","4–7"],
            "A.m. ligustica": ["9.1–9.8","3.1–3.5","2.4–3.2","1.6–2.0","2.9–3.3","1.8–2.1","6.3–6.7","4.7–5.1","45–60","1–3"],
            "A.m. carnica":   ["9.1–9.8","3.1–3.4","2.6–3.5","1.6–2.0","3.0–3.4","1.8–2.1","6.4–6.8","4.7–5.2","35–50","1–3"],
            "A.m. sahariensis":["8.7–9.3","2.9–3.2","2.1–2.9","1.4–1.8","2.7–3.1","1.6–1.9","5.8–6.2","4.4–4.8","25–40","5–8"],
        }
        st.dataframe(pd.DataFrame(ref_data), use_container_width=True, hide_index=True)

    with tab3:
        df_m = st.session_state.data["morph_analyses"]
        if len(df_m) >= 2:
            section_header("📊 Comparaison des mesures clés")
            fig_box = go.Figure()
            for (label, col), color in zip({"L aile (mm)":"L_aile_mm","Ri cubital":"Ri","Glossa (mm)":"Glossa_mm"}.items(),
                                            ["#D4820A","#F59E0B","#9B59B6"]):
                if col in df_m.columns:
                    fig_box.add_trace(go.Box(y=df_m[col], name=label, marker_color=color, boxmean=True))
            fig_box.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig_box, use_container_width=True, config={"displayModeBar":False})
        else:
            st.info("Enregistrez au moins 2 analyses pour voir les comparaisons.")

    with tab4:
        df_m = st.session_state.data["morph_analyses"]
        if not df_m.empty:
            st.dataframe(df_m.sort_values("Date",ascending=False), use_container_width=True, hide_index=True,
                column_config={"Confiance_pct": st.column_config.ProgressColumn(format="%d%%", min_value=0, max_value=100)})
        else:
            st.info("Aucune analyse enregistrée.")

# ─────────────────────────────────────────────
# PAGE: GÉNÉTIQUE
# ─────────────────────────────────────────────
elif current_page == "genetique":
    st.markdown('<div class="page-title">🧬 Génétique & Sélection</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Lignées reines · Élevage · VSH · Programme de sélection</div>', unsafe_allow_html=True)

    df = st.session_state.data["ruches"]
    tab1, tab2 = st.tabs(["👑 Registre des reines","🧬 Programme de sélection"])

    with tab1:
        st.dataframe(df[["Reine_id","ID","Race","VSH_pct","Douceur","Economie_hiv","Essaimage_pct","Profil_prod"]].rename(
            columns={"Reine_id":"ID Reine","ID":"Ruche","VSH_pct":"VSH%","Douceur":"Douceur%",
                     "Economie_hiv":"Éco. hiv.%","Essaimage_pct":"Essaimage%","Profil_prod":"Profil"}),
            use_container_width=True, hide_index=True,
            column_config={
                "VSH%": st.column_config.ProgressColumn(format="%d%%", min_value=0, max_value=100),
                "Douceur%": st.column_config.ProgressColumn(format="%d%%", min_value=0, max_value=100),
            })

        section_header("📊 Critères de sélection moyens")
        criteria = ["VSH","Douceur","Productivité miel","Économie hivernale","Anti-essaimage"]
        values = [df["VSH_pct"].mean(), df["Douceur"].mean(),
                  df["Miel_kg"].mean()/20*100, df["Economie_hiv"].mean(), 100-df["Essaimage_pct"].mean()]
        colors_c = ["#22c55e","#3b82f6","#D4820A","#9B59B6","#f59e0b"]
        for c, v, col in zip(criteria, values, colors_c):
            st.markdown(f"""
            <div style="margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px">
                    <span style="color:#4A3728;font-weight:500">{c}</span>
                    <span style="font-family:monospace;font-weight:600;color:#4A3728">{v:.0f}%</span>
                </div>
                <div style="height:10px;background:#F5EDD8;border-radius:5px;overflow:hidden">
                    <div style="height:100%;width:{v}%;background:{col};border-radius:5px"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab2:
        section_header("🏆 Top 3 — Candidates à l'élevage de reines")
        top3 = df.nlargest(3, "VSH_pct")
        for i, (_,r) in enumerate(top3.iterrows()):
            medal = ["🥇","🥈","🥉"][i]
            st.markdown(f"""
            <div style="background:white;border-radius:14px;padding:16px;border:1px solid rgba(180,150,80,0.2);
                        margin-bottom:10px;display:flex;align-items:center;gap:16px">
                <div style="font-size:28px">{medal}</div>
                <div style="flex:1">
                    <div style="font-family:'Playfair Display',serif;font-size:16px;font-weight:700">{r['Nom']} ({r['ID']})</div>
                    <div style="font-size:12px;color:#6B6040">{r['Race']} · VSH: {r['VSH_pct']}% · Douceur: {r['Douceur']}%</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:22px;font-weight:700;color:#22c55e">{r['VSH_pct']}%</div>
                    <div style="font-size:10px;color:#6B6040;text-transform:uppercase">VSH</div>
                </div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: CARACTÉRISATION
# ─────────────────────────────────────────────
elif current_page == "caracterisation":
    st.markdown('<div class="page-title">📈 Caractérisation des Abeilles</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Profils de production · Morphologie · Résistance · ACP</div>', unsafe_allow_html=True)

    df = st.session_state.data["ruches"]
    tab1, tab2, tab3 = st.tabs(["🎯 Profils production","🛡️ Résistance & comportement","🗺️ Analyse ACP"])

    with tab1:
        section_header("📊 Comparaison des profils")
        fig = go.Figure()
        metrics_labels = ["Miel (kg)","Pollen (kg×3)","Gelée R. (g/10)"]
        for profil in df["Profil_prod"].unique():
            sub = df[df["Profil_prod"]==profil]
            fig.add_trace(go.Scatter(
                x=metrics_labels,
                y=[sub["Miel_kg"].mean(), sub["Pollen_kg"].mean()*3, sub["gelee_g"].mean()/10],
                name=f"{PROFIL_ICONS.get(profil,'')} {profil}",
                mode='lines+markers', fill='toself', line=dict(width=2), marker=dict(size=8)
            ))
        fig.update_layout(height=360, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
            legend=dict(font=dict(size=11), bgcolor='rgba(255,255,255,0.8)'),
            margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        section_header("🔬 Détail par ruche")
        for _, r in df.iterrows():
            with st.expander(f"{PROFIL_ICONS.get(r['Profil_prod'],'🐝')} {r['Nom']} ({r['ID']}) — {r['Profil_prod']}"):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown(f"""<div class="morph-card">
                        <div style="font-size:11px;font-weight:600;color:#6B6040;text-transform:uppercase;margin-bottom:10px">🏭 Production</div>
                        <div class="measure-row"><span>🍯 Miel</span><span class="measure-val-ok">{r['Miel_kg']} kg</span></div>
                        <div class="measure-row"><span>🌼 Pollen</span><span class="measure-val-ok">{r['Pollen_kg']} kg</span></div>
                        <div class="measure-row"><span>👑 Gelée</span><span class="measure-val-ok">{r['gelee_g']} g</span></div>
                    </div>""", unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"""<div class="morph-card">
                        <div style="font-size:11px;font-weight:600;color:#6B6040;text-transform:uppercase;margin-bottom:10px">🔬 Morphologie</div>
                        <div class="measure-row"><span>Glossa</span><span class="measure-val-ok">{r['Glossa_mm']} mm</span></div>
                        <div class="measure-row"><span>L. aile</span><span class="measure-val-ok">{r['L_aile_mm']} mm</span></div>
                        <div class="measure-row"><span>Ri cubital</span><span class="measure-val-ok">{r['Ri']}</span></div>
                        <div class="measure-row"><span>Tomentum</span><span class="measure-val-ok">{r['Tomentum_pct']}%</span></div>
                    </div>""", unsafe_allow_html=True)
                with col_c:
                    st.markdown(f"""<div class="morph-card">
                        <div style="font-size:11px;font-weight:600;color:#6B6040;text-transform:uppercase;margin-bottom:10px">🧬 Génétique</div>
                        <div class="measure-row"><span>Race</span><span class="measure-val-ok" style="font-size:10px">{r['Race'][:18]}</span></div>
                        <div class="measure-row"><span>VSH</span><span class="{'measure-val-ok' if r['VSH_pct']>=70 else 'measure-val-warn'}">{r['VSH_pct']}%</span></div>
                        <div class="measure-row"><span>Douceur</span><span class="measure-val-ok">{r['Douceur']}%</span></div>
                        <div class="measure-row"><span>Éco. hiv.</span><span class="measure-val-ok">{r['Economie_hiv']}%</span></div>
                    </div>""", unsafe_allow_html=True)
                st.plotly_chart(production_radar(r), use_container_width=True, config={"displayModeBar":False})

    with tab2:
        section_header("🛡️ Score VSH par ruche")
        df_vsh = df.sort_values("VSH_pct")
        colors_vsh = ["#ef4444" if v<60 else "#f59e0b" if v<70 else "#22c55e" for v in df_vsh["VSH_pct"]]
        fig_vsh = go.Figure(go.Bar(x=df_vsh["VSH_pct"], y=df_vsh["Nom"], orientation='h',
            marker_color=colors_vsh, text=[f"{v}%" for v in df_vsh["VSH_pct"]], textposition='inside',
            textfont=dict(color='white',size=11)))
        fig_vsh.add_vline(x=70, line_dash="dash", line_color="#6b7280", annotation_text="Seuil cible (70%)")
        fig_vsh.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
            xaxis=dict(range=[0,105],title="VSH (%)",tickfont=dict(color='#6B6040')),
            margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig_vsh, use_container_width=True, config={"displayModeBar":False})

        section_header("🏆 Classement général")
        df["Score_prod"] = (df["Miel_kg"]/20*40 + df["Pollen_kg"]/5*20 + df["gelee_g"]/200*20 +
                            df["VSH_pct"]/100*10 + df["Douceur"]/100*10).clip(0,100).round(1)
        df_rank = df[["Nom","Race","Profil_prod","Score_prod","VSH_pct","Douceur","Varroa_pct"]].sort_values("Score_prod",ascending=False)
        df_rank.columns = ["Ruche","Race","Profil","Score global","VSH%","Douceur%","Varroa%"]
        st.dataframe(df_rank, use_container_width=True, hide_index=True,
            column_config={"Score global": st.column_config.ProgressColumn(format="%.1f/100", min_value=0, max_value=100),
                           "VSH%": st.column_config.ProgressColumn(format="%d%%", min_value=0, max_value=100)})

    with tab3:
        section_header("🗺️ Analyse en Composantes Principales (ACP)")
        try:
            from sklearn.decomposition import PCA
            from sklearn.preprocessing import StandardScaler

            features = ["L_aile_mm","Ri","Glossa_mm","Tomentum_pct","Pollen_kg","Miel_kg","gelee_g","VSH_pct"]
            X = df[features].values
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            pca = PCA(n_components=2, random_state=42)
            X_pca = pca.fit_transform(X_scaled)

            color_map = {"A. m. intermissa":"#D4820A","A. m. sahariensis":"#9B59B6",
                         "A. m. ligustica":"#3b82f6","A. m. carnica":"#22c55e","Hybride":"#6b7280"}
            fig_pca = go.Figure()
            for race in df["Race"].unique():
                mask = df["Race"]==race
                fig_pca.add_trace(go.Scatter(
                    x=X_pca[mask,0], y=X_pca[mask,1], mode='markers+text',
                    text=df.loc[mask,"ID"].values, textposition='top center',
                    textfont=dict(size=10,color='#4A3728'),
                    marker=dict(size=18, color=color_map.get(race,"#6b7280"), opacity=0.8,
                                symbol="hexagon", line=dict(color='white',width=2)), name=race
                ))
            fig_pca.update_layout(height=440, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                xaxis=dict(title=f"CP1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)"),
                yaxis=dict(title=f"CP2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)"),
                legend=dict(font=dict(size=11), bgcolor='rgba(255,255,255,0.85)'),
                margin=dict(l=10,r=10,t=30,b=10))
            st.plotly_chart(fig_pca, use_container_width=True, config={"displayModeBar":False})
        except ImportError:
            st.info("scikit-learn requis : `pip install scikit-learn`")

# ─────────────────────────────────────────────
# PAGE: CARTOGRAPHIE
# ─────────────────────────────────────────────
elif current_page == "carte":
    st.markdown('<div class="page-title">🗺️ Cartographie des zones mellifères</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Placez vos ruches et zones florales sur la carte satellite</div>', unsafe_allow_html=True)

    try:
        import folium
        from streamlit_folium import st_folium
    except ImportError:
        st.error("Installez folium et streamlit-folium : `pip install folium streamlit-folium`")
        st.stop()

    center = [34.8825, -1.3167]
    m = folium.Map(location=center, zoom_start=12,
                   tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Satellite')

    zones_df = st.session_state.data["zones"]
    color_map = {"Miel":"orange","Pollen":"beige","Gelée Royale":"purple","Propolis":"green"}

    for _, zone in zones_df.iterrows():
        try:
            lat, lng = map(float, zone['coordonnees'].split(','))
            popup_text = f"<b>{zone['nom']}</b><br>{zone['type_production']}<br>{zone['flore']}<br>Superficie : {zone.get('superficie_ha',0)} ha"
            folium.Marker([lat, lng], popup=folium.Popup(popup_text, max_width=200),
                icon=folium.Icon(color=color_map.get(zone['type_production'],"blue"), icon='leaf', prefix='fa')).add_to(m)
        except Exception:
            pass

    section_header("🗺️ Cliquez sur la carte pour placer une zone")
    output = st_folium(m, width=None, height=480, use_container_width=True)

    if output and output.get('last_clicked'):
        st.session_state['temp_lat'] = output['last_clicked']['lat']
        st.session_state['temp_lng'] = output['last_clicked']['lng']
        st.success(f"📍 Position sélectionnée : {st.session_state['temp_lat']:.5f}, {st.session_state['temp_lng']:.5f}")

    col_f, col_z = st.columns([1,1])
    with col_f:
        with st.form("add_zone_form"):
            section_header("➕ Ajouter une zone")
            nom      = st.text_input("Nom de la zone", placeholder="Ex: Plaine du Romarin")
            type_prod = st.selectbox("Type de production", ["Miel","Pollen","Gelée Royale","Propolis"])
            flore    = st.text_input("Flore mellifère", placeholder="Ex: Romarin, Jujubier")
            superficie = st.number_input("Superficie (ha)", min_value=0.0, value=1.0, step=0.5)
            notes_zone = st.text_area("Notes", height=60)
            coords   = f"{st.session_state.get('temp_lat','')},{st.session_state.get('temp_lng','')}"
            cap_txt = coords if (',' in coords and len(coords)>3) else "Cliquez d'abord sur la carte"
            st.caption(f"Coordonnées : {cap_txt}")
            submitted = st.form_submit_button("💾 Enregistrer la zone")
            if submitted:
                if not nom or not flore or not st.session_state.get('temp_lat'):
                    st.error("Remplissez tous les champs et cliquez sur la carte.")
                else:
                    add_zone({"nom":nom,"type_production":type_prod,"flore":flore,"coordonnees":coords,
                              "date_creation":datetime.now().strftime("%Y-%m-%d"),
                              "superficie_ha":superficie,"notes":notes_zone})
                    st.session_state.data = load_dataframes()
                    st.success(f"✅ Zone '{nom}' ajoutée !")
                    st.rerun()

    with col_z:
        section_header("📋 Zones enregistrées")
        if not zones_df.empty:
            st.dataframe(zones_df[["nom","type_production","flore","superficie_ha","date_creation"]],
                         use_container_width=True, hide_index=True)
            # Suppression
            zone_del = st.selectbox("Supprimer une zone", zones_df["nom"].tolist(), key="zone_del")
            if st.button("🗑 Supprimer", key="btn_del_zone"):
                zone_id = zones_df[zones_df["nom"]==zone_del]["id"].values[0]
                delete_zone(int(zone_id))
                st.session_state.data = load_dataframes()
                st.success(f"Zone '{zone_del}' supprimée.")
                st.rerun()
        else:
            st.info("Aucune zone enregistrée.")

# ─────────────────────────────────────────────
# PAGE: FLORE
# ─────────────────────────────────────────────
elif current_page == "flore":
    st.markdown('<div class="page-title">🌸 Flore Mellifère</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Calendrier de floraison · Valeur apicole · Région de l\'Oranie — Algérie</div>', unsafe_allow_html=True)

    flore_data = {
        "Espèce": ["🌳 Jujubier (Ziziphus lotus)","🌿 Romarin (Rosmarinus off.)","🍊 Oranger (Citrus sinensis)",
                   "🌼 Lavande (Lavandula sp.)","🌱 Thym (Thymus vulgaris)","🌳 Eucalyptus (E. globulus)",
                   "🌻 Tournesol","🌺 Chardon (Cynara sp.)","🌱 Alfa (Stipa tenacissima)","🌼 Phacélie"],
        "Floraison": ["Mai–Juin","Fév–Avr","Avr–Mai","Juin–Jul","Avr–Juin","Nov–Jan","Juil–Août","Mai–Jul","Mar–Avr","Avr–Jun"],
        "Nectarifère": ["★★★★★","★★★★","★★★★★","★★★★","★★★★","★★★★","★★★","★★★","★★","★★★★★"],
        "Pollinifère": ["★★★★","★★★","★★★★","★★★★","★★★","★★★★","★★★★★","★★★","★★★★","★★★★"],
        "Habitat": ["Steppes, maquis","Garrigues","Vergers","Garrigues","Zones sèches","Forêts plantées","Cultures","Steppes","Steppes arides","Cultures"],
        "Miellée principale": ["Oui","Non","Oui","Non","Non","Partielle","Non","Non","Non","Oui"],
    }
    st.dataframe(pd.DataFrame(flore_data), use_container_width=True, hide_index=True)

    section_header("📅 Calendrier mellifère — Disponibilité nectar")
    mois = ["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Août","Sep","Oct","Nov","Déc"]
    disponibilite = [15,35,50,80,95,90,65,40,25,15,20,18]
    fig = go.Figure(go.Scatter(x=mois, y=disponibilite, fill='tozeroy', name="Disponibilité nectar",
        fillcolor='rgba(212,130,10,0.15)', line=dict(color='#D4820A',width=2.5),
        mode='lines+markers', marker=dict(size=7,color='#D4820A')))
    fig.update_layout(height=260, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
        yaxis=dict(title="Indice",tickfont=dict(color='#6B6040'),gridcolor='rgba(180,150,80,0.1)'),
        margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# ─────────────────────────────────────────────
# PAGE: MÉTÉO
# ─────────────────────────────────────────────
elif current_page == "meteo":
    st.markdown('<div class="page-title">🌤️ Météo & Miellée</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Conditions de butinage · Indice de miellée · Tlemcen — Algérie</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    meteos = [
        ("Aujourd'hui","22°C","☀️ Ensoleillé","65%","12 km/h","8/10","linear-gradient(135deg,#2D4A1E,#3D6B2C)"),
        ("Demain","19°C","⛅ Nuageux","72%","20 km/h","5/10","linear-gradient(135deg,#2D5A3D,#3D6B2C)"),
        ("Après-demain","16°C","🌧️ Pluie","88%","35 km/h","1/10","linear-gradient(135deg,#3A2F1E,#5A4030)"),
    ]
    for col, (jour, temp, cond, hum, vent, miel, grad) in zip([c1,c2,c3], meteos):
        with col:
            st.markdown(f"""
            <div style="background:{grad};border-radius:18px;padding:22px;color:white;margin-bottom:16px">
                <div style="font-size:10px;opacity:0.6;text-transform:uppercase;margin-bottom:8px">{jour}</div>
                <div style="font-family:'Playfair Display',serif;font-size:44px;font-weight:700;line-height:1">{temp}</div>
                <div style="font-size:14px;opacity:0.85;margin-top:4px">{cond}</div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:16px;
                            padding-top:14px;border-top:1px solid rgba(255,255,255,0.15)">
                    <div style="text-align:center"><div style="font-size:16px;font-weight:600">{hum}</div><div style="font-size:9px;opacity:0.55">Humidité</div></div>
                    <div style="text-align:center"><div style="font-size:16px;font-weight:600">{vent}</div><div style="font-size:9px;opacity:0.55">Vent</div></div>
                    <div style="text-align:center"><div style="font-size:16px;font-weight:600">{miel}</div><div style="font-size:9px;opacity:0.55">Miellée</div></div>
                </div>
            </div>""", unsafe_allow_html=True)

    section_header("📊 Indice de butinage — 7 derniers jours")
    jours = ["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"]
    indice = [4,8,9,8,6,5,4]
    fig = go.Figure(go.Scatter(x=jours, y=indice, fill='tozeroy',
        fillcolor='rgba(212,130,10,0.15)', line=dict(color='#D4820A',width=2.5),
        mode='lines+markers', marker=dict(size=10,color='#D4820A',line=dict(color='white',width=2)),
        text=[f"{v}/10" for v in indice], textposition='top center', textfont=dict(size=11,color='#4A3728')))
    fig.update_layout(height=240, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
        yaxis=dict(range=[0,11],title="Indice (0–10)"),margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    st.markdown(alert("💡","<strong>Conseil :</strong> Les journées idéales pour le butinage : température > 15°C, vent < 25 km/h, humidité < 80%, ciel dégagé ou partiellement nuageux.","alert-info"), unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: RAPPORTS
# ─────────────────────────────────────────────
elif current_page == "rapports":
    st.markdown('<div class="page-title">📋 Rapports & Exports</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Rapports réglementaires · Analyses statistiques · Export données</div>', unsafe_allow_html=True)

    df  = st.session_state.data["ruches"]
    rec = st.session_state.data["recoltes"]

    section_header("📊 Résumé de la saison 2024")
    c1, c2, c3 = st.columns(3)
    with c1:
        ca_total = rec.apply(lambda r: r["Quantite_kg"]*r["Prix_kg"], axis=1).sum() if len(rec)>0 else 0
        st.markdown(f"""<div class="morph-card">
            <div style="font-weight:700;color:#D4820A;margin-bottom:12px">🍯 Production</div>
            <div class="measure-row"><span>Miel total</span><span class="measure-val-ok">{df['Miel_kg'].sum():.0f} kg</span></div>
            <div class="measure-row"><span>Pollen total</span><span class="measure-val-ok">{df['Pollen_kg'].sum():.1f} kg</span></div>
            <div class="measure-row"><span>Gelée royale</span><span class="measure-val-ok">{df['gelee_g'].sum()} g</span></div>
            <div class="measure-row"><span>CA estimé</span><span class="measure-val-ok">{ca_total:,.0f} DA</span></div>
        </div>""", unsafe_allow_html=True)
    with c2:
        varroa_moy = df["Varroa_pct"].mean()
        st.markdown(f"""<div class="morph-card">
            <div style="font-weight:700;color:#22c55e;margin-bottom:12px">🩺 Santé</div>
            <div class="measure-row"><span>Varroa moyen</span><span class="{'measure-val-ok' if varroa_moy<2 else 'measure-val-warn'}">{varroa_moy:.1f}%</span></div>
            <div class="measure-row"><span>VSH moyen</span><span class="measure-val-ok">{df['VSH_pct'].mean():.0f}%</span></div>
            <div class="measure-row"><span>Traitements</span><span class="measure-val-ok">{len(st.session_state.data['traitements'])}</span></div>
            <div class="measure-row"><span>Inspections</span><span class="measure-val-ok">{len(st.session_state.data['inspections'])}</span></div>
        </div>""", unsafe_allow_html=True)
    with c3:
        df_m = st.session_state.data["morph_analyses"]
        race_dom = df["Race"].value_counts().idxmax() if len(df)>0 else "—"
        conf_moy = df_m["Confiance_pct"].mean() if len(df_m)>0 else 0
        st.markdown(f"""<div class="morph-card">
            <div style="font-weight:700;color:#9B59B6;margin-bottom:12px">🔬 Science</div>
            <div class="measure-row"><span>Analyses morpho.</span><span class="measure-val-ok">{len(df_m)}</span></div>
            <div class="measure-row"><span>Race dominante</span><span class="measure-val-ok" style="font-size:11px">{race_dom[:18]}</span></div>
            <div class="measure-row"><span>Confiance moy.</span><span class="measure-val-ok">{conf_moy:.0f}%</span></div>
            <div class="measure-row"><span>Profils actifs</span><span class="measure-val-ok">{df['Profil_prod'].nunique()}</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("⬇️ Exports disponibles")
    export_items = [
        ("📊","Ruches","ruches",st.session_state.data["ruches"]),
        ("🔬","Morphométrie","morph_analyses",st.session_state.data["morph_analyses"]),
        ("🍯","Récoltes","recoltes",st.session_state.data["recoltes"]),
        ("💊","Traitements","traitements",st.session_state.data["traitements"]),
        ("🔍","Inspections","inspections",st.session_state.data["inspections"]),
        ("🗺️","Zones","zones",st.session_state.data["zones"]),
        ("📓","Journal","journal",st.session_state.data["journal"]),
    ]
    cols_ex = st.columns(4)
    for i, (icon, title, fname, data) in enumerate(export_items):
        with cols_ex[i % 4]:
            if not data.empty:
                csv = data.to_csv(index=False).encode("utf-8")
                st.download_button(f"{icon} {title}", csv, f"apitrack_{fname}.csv","text/csv", use_container_width=True)

# ─────────────────────────────────────────────
# PAGE: ALERTES
# ─────────────────────────────────────────────
elif current_page == "alertes":
    st.markdown('<div class="page-title">🚨 Alertes & Notifications</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Surveillance en temps réel · Priorisation · Actions correctives</div>', unsafe_allow_html=True)

    df = st.session_state.data["ruches"]
    alertes_auto = []
    for _, r in df.iterrows():
        if r["Varroa_pct"] > 3:
            alertes_auto.append(("🔴","danger",f"CRITIQUE — {r['Nom']} ({r['ID']}) : Varroa {r['Varroa_pct']}% — Traitement urgent requis."))
        elif r["Varroa_pct"] > 2:
            alertes_auto.append(("🟠","warning",f"ATTENTION — {r['Nom']} ({r['ID']}) : Varroa {r['Varroa_pct']}% — À surveiller de près."))
        if r["Statut"] == "Critique":
            alertes_auto.append(("🔴","danger",f"CRITIQUE — {r['Nom']} ({r['ID']}) : Statut critique. Inspection urgente requise."))
        if r["VSH_pct"] < 60:
            alertes_auto.append(("🟡","warning",f"SÉLECTION — {r['Nom']} ({r['ID']}) : VSH {r['VSH_pct']}% < 60%. Renouveler la reine."))
        if r["gelee_g"] > 150 and r["Profil_prod"] == "Gelée Royale":
            alertes_auto.append(("👑","royal",f"RÉCOLTE — {r['Nom']} ({r['ID']}) : Excellente production GR ({r['gelee_g']}g). Planifier la prochaine récolte."))

    alertes_auto.append(("✅","success",f"Bonne nouvelle : {int((df['VSH_pct']>=70).sum())} colonies montrent un VSH ≥ 70% !"))

    cls_map = {"danger":"alert-danger","warning":"alert-warning","success":"alert-success","info":"alert-info","royal":"alert-royal"}
    nb_crit = sum(1 for _,l,_ in alertes_auto if l=="danger")
    nb_att  = sum(1 for _,l,_ in alertes_auto if l=="warning")

    c1,c2,c3 = st.columns(3)
    with c1: st.markdown(metric_card("🔴", str(nb_crit), "Alertes critiques"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("🟠", str(nb_att), "Alertes attention"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("✅", str(len(df)-nb_crit-nb_att), "Ruches sans alerte"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    for icon, level, txt in alertes_auto:
        st.markdown(alert(icon, txt, cls_map.get(level,"alert-info")), unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: JOURNAL
# ─────────────────────────────────────────────
elif current_page == "journal":
    st.markdown('<div class="page-title">📓 Journal d\'activité</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Historique complet de toutes les actions · Traçabilité totale</div>', unsafe_allow_html=True)

    df_j = st.session_state.data["journal"].sort_values("date", ascending=False)
    if df_j.empty:
        st.info("Aucune activité enregistrée pour le moment. Les actions effectuées apparaîtront ici.")
    else:
        section_header(f"📓 {len(df_j)} actions enregistrées")
        for _, row in df_j.head(50).iterrows():
            icon_map = {"Ajout ruche":"🏠","Inspection":"🔍","Récolte Miel":"🍯","Récolte Pollen":"🌼",
                        "Récolte Gelée Royale":"👑","Suppression ruche":"🗑️"}
            icon = icon_map.get(row.get("type_action",""), "📝")
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-date">{row.get('date','—')} · {row.get('utilisateur','—')}</div>
                <div class="timeline-event">{icon} {row.get('type_action','—')} — Ruche : {row.get('ruche','—')}</div>
                <div class="timeline-note">{row.get('description','—')}</div>
            </div>""", unsafe_allow_html=True)

        csv_j = df_j.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Exporter le journal", csv_j, "journal_apitrack.csv","text/csv")

# ─────────────────────────────────────────────
# PAGE: ADMINISTRATION
# ─────────────────────────────────────────────
elif current_page == "admin":
    st.markdown('<div class="page-title">💾 Administration</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Sauvegarde · Restauration · Gestion · Profil</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💾 Sauvegarde","🗑 Supprimer ruche","👤 Profil","⚙️ Paramètres","🔐 Sécurité"])

    with tab1:
        section_header("💾 Sauvegarder la base de données")
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "rb") as f:
                st.download_button("📥 Télécharger la base (.db)", f, "apitrack_backup.db", "application/octet-stream",
                                   use_container_width=True, type="primary")
        section_header("📤 Restaurer une base existante")
        st.markdown(alert("⚠️","La restauration remplacera TOUTES les données actuelles. Sauvegardez d'abord !","alert-warning"), unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choisir un fichier .db", type=["db"])
        if uploaded_file and st.button("⚠️ Restaurer", type="primary"):
            with open(DB_PATH, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Base restaurée ! Rechargez la page.")
            st.rerun()

    with tab2:
        section_header("🗑 Supprimer une ruche")
        st.markdown(alert("⚠️","La suppression est irréversible et inclut toutes les données associées (inspections, récoltes, traitements, analyses).","alert-warning"), unsafe_allow_html=True)
        ruche_list = st.session_state.data["ruches"]["ID"].tolist()
        if ruche_list:
            ruche_to_delete = st.selectbox("Ruche à supprimer", ruche_list)
            if st.button("🗑 Supprimer définitivement", type="primary"):
                delete_ruche(ruche_to_delete)
                st.session_state.data = load_dataframes()
                st.success(f"Ruche {ruche_to_delete} supprimée.")
                st.rerun()

    with tab3:
        section_header("👤 Profil apiculteur")
        new_name  = st.text_input("Nom de l'apiculteur",  value=st.session_state.apiculteur)
        new_ruche = st.text_input("Nom du rucher",        value=get_setting("rucher"))
        new_region= st.text_input("Région",               value=get_setting("region"))
        if st.button("💾 Enregistrer le profil", type="primary"):
            set_setting("apiculteur", new_name)
            set_setting("rucher", new_ruche)
            set_setting("region", new_region)
            st.session_state.apiculteur = new_name
            st.success("Profil mis à jour !")
            st.rerun()

    with tab4:
        section_header("⚙️ Paramètres de l'application")
        st.markdown(f"""
        <div class="morph-card">
            <div class="measure-row"><span>Version</span><span class="measure-val-ok">ApiTrack Pro v2.1</span></div>
            <div class="measure-row"><span>Base de données</span><span class="measure-val-ok">{DB_PATH}</span></div>
            <div class="measure-row"><span>Ruches enregistrées</span><span class="measure-val-ok">{len(st.session_state.data['ruches'])}</span></div>
            <div class="measure-row"><span>Inspections</span><span class="measure-val-ok">{len(st.session_state.data['inspections'])}</span></div>
            <div class="measure-row"><span>Récoltes</span><span class="measure-val-ok">{len(st.session_state.data['recoltes'])}</span></div>
            <div class="measure-row"><span>Analyses morpho.</span><span class="measure-val-ok">{len(st.session_state.data['morph_analyses'])}</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 Recharger les données", use_container_width=True):
            st.session_state.data = load_dataframes()
            st.success("Données rechargées !")
            st.rerun()

    with tab5:
        section_header("🔐 Changer le mot de passe")
        old_pwd = st.text_input("Ancien mot de passe", type="password")
        new_pwd = st.text_input("Nouveau mot de passe", type="password")
        confirm = st.text_input("Confirmer", type="password")
        if st.button("🔐 Changer le mot de passe", type="primary"):
            if verify_login(st.session_state.username, old_pwd):
                if new_pwd == confirm and len(new_pwd) >= 4:
                    change_password(st.session_state.username, new_pwd)
                    st.success("✅ Mot de passe modifié avec succès !")
                else:
                    st.error("Le nouveau mot de passe doit faire au moins 4 caractères et correspondre à la confirmation.")
            else:
                st.error("❌ Ancien mot de passe incorrect.")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:32px 0 16px;font-size:12px;color:#9B8860;
            border-top:1px solid rgba(180,150,80,0.15);margin-top:40px">
    <strong style="font-family:'Playfair Display',serif;font-size:14px;color:#4A3728">ApiTrack Pro v2.1</strong> ·
    Plateforme Apicole Professionnelle<br>
    Morphométrie selon <em>Ruttner (1988)</em> · Données <em>Chahbar et al. (2013)</em> ·
    Région de l'Oranie, Algérie<br><br>
    🐝 Développé pour l'apiculture scientifique et professionnelle
</div>
""", unsafe_allow_html=True)
