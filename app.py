import os
# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
import seaborn as sns
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv, set_key
import numpy as np
from collections import Counter

# Page Config
st.set_page_config(
    page_title="Save the Tasmanian Devil - Tracker",
    page_icon="😈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Premium Look
st.markdown("""
    <style>
        /* Base styles */
        .main {
            background-color: #0d0f12;
            color: #e2e8f0;
        }
        /* Custom Title */
        .title-container {
            background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
            padding: 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            border: 1px solid #3b0764;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5);
            text-align: center;
        }
        .title-text {
            color: #f3e8ff;
            font-family: 'Outfit', 'Inter', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.05em;
        }
        .subtitle-text {
            color: #c084fc;
            font-size: 1.1rem;
            margin-top: 0.5rem;
            font-weight: 300;
        }
        /* Metric Cards */
        .metric-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: #7c3aed;
        }
        .metric-title {
            color: #8b949e;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #f3e8ff;
        }
        /* Status Badges */
        .status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .badge-clean { background-color: #065f46; color: #34d399; }
        .badge-threat { background-color: #7f1d1d; color: #fca5a5; }
        
        /* Sidebar layout styling */
        section[data-testid="stSidebar"] {
            background-color: #0b0d10 !important;
            border-right: 1px solid #1f2937;
        }

        /* Pedigree Tree CSS */
        .pedigree-tree-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
            padding: 1.5rem;
            background-color: #111418;
            border-radius: 16px;
            border: 1px solid #1f2937;
            margin-top: 2rem;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.6);
        }
        .pedigree-row {
            display: flex;
            justify-content: space-around;
            width: 100%;
        }
        .pedigree-pair {
            display: flex;
            gap: 1rem;
        }
        .pedigree-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 0.8rem;
            width: 150px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
            transition: transform 0.2s ease;
        }
        .pedigree-card:hover {
            transform: scale(1.02);
        }
        .pedigree-card.empty {
            border-style: dashed;
            color: #8b949e;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-style: italic;
        }
        .pedigree-card.healthy {
            border-color: #10b981;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.15);
        }
        .pedigree-card.infected {
            border-color: #ef4444;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.25);
        }
        .card-title {
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #8b949e;
            margin-bottom: 0.3rem;
            font-weight: 600;
        }
        .card-id {
            font-size: 0.8rem;
            color: #c084fc;
            font-weight: 700;
        }
        .card-name {
            font-size: 1rem;
            font-weight: 800;
            margin: 0.2rem 0;
            color: #f3e8ff;
        }
        .card-status {
            font-size: 0.7rem;
        }
        .healthy .card-status { color: #34d399; }
        .infected .card-status { color: #fca5a5; }
        .female { color: #f472b6; }
        .male { color: #60a5fa; }
        
        /* Pedigree Connectors */
        .pedigree-connectors {
            display: flex;
            justify-content: space-around;
            width: 100%;
            height: 20px;
            position: relative;
        }
        .connector-block {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 50%;
            position: relative;
        }
        .pedigree-connectors-single {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            height: 20px;
            position: relative;
        }
        .connector-line {
            background-color: #4b5563;
        }
        .vertical {
            width: 2px;
            height: 10px;
        }
        .horizontal {
            width: 50%;
            height: 2px;
        }
        .vertical-single {
            width: 2px;
            height: 20px;
        }
        
        /* Timeline Styling */
        .timeline {
            border-left: 2px solid #30363d;
            padding-left: 1.5rem;
            margin-left: 0.5rem;
            position: relative;
            margin-top: 1.5rem;
        }
        .timeline-item {
            position: relative;
            margin-bottom: 1.5rem;
        }
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -1.95rem;
            top: 0.25rem;
            background-color: #0d0f12;
            border: 2px solid #c084fc;
            border-radius: 50%;
            width: 12px;
            height: 12px;
            z-index: 10;
        }
        .timeline-date {
            font-size: 0.85rem;
            font-weight: 700;
            color: #c084fc;
            margin-bottom: 0.3rem;
        }
        .timeline-content {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 0.8rem 1.2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .timeline-badge {
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

# Ensure .env is loaded
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)

# Initialize SQLite session state flag
if "use_sqlite" not in st.session_state:
    st.session_state["use_sqlite"] = False

# Global SQLite check
USE_SQLITE = st.session_state["use_sqlite"] or os.getenv("USE_SQLITE", "False").lower() == "true"

# Retrieve configuration
def get_db_config():
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", 3306)),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "root"),
        "database": os.getenv("DB_NAME", "devil_tracker")
    }

def test_db_connection(config):
    """Test connection without database name first, to check access permissions."""
    if USE_SQLITE:
        return True, ""
    try:
        conn = mysql.connector.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            connection_timeout=3
        )
        conn.close()
        return True, ""
    except Error as e:
        return False, str(e)

def get_connection():
    """Retrieve connection to devil_tracker database (MySQL or SQLite fallback)."""
    global USE_SQLITE
    if USE_SQLITE:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "devil_tracker.db")
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        # Register the POWER function for SQLite
        conn.create_function("POWER", 2, lambda x, y: x ** y)
        return conn
        
    try:
        cfg = get_db_config()
        return mysql.connector.connect(**cfg)
    except Exception:
        USE_SQLITE = True
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "devil_tracker.db")
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.create_function("POWER", 2, lambda x, y: x ** y)
        return conn

def translate_query(query):
    """Translate SQL query from MySQL syntax to SQLite syntax if in SQLite fallback mode."""
    if not USE_SQLITE:
        return query
    
    query = query.replace("%s", "?")
    query = query.replace("SHOW TABLES", "SELECT name FROM sqlite_master WHERE type='table'")
    
    # Translate MySQL DATEDIFF to SQLite equivalent using julianday
    query = query.replace("DATEDIFF('2026-06-10', birth_date)", "(julianday('2026-06-10') - julianday(birth_date))")
    query = query.replace("DATEDIFF(log_date, prev_positive_date)", "(julianday(log_date) - julianday(prev_positive_date))")
    
    return query

# Title Header
st.markdown("""
    <div class='title-container'>
        <h1 class='title-text'>Save the Tasmanian Devil</h1>
        <p class='subtitle-text'>Disease Transmission Tracking, Pedigree Kinship Analysis & Biosecurity Control Center</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Credentials & Setup Management
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/ea/Tasmanian_devil_port_arthur.jpg", caption="Sarcophilus harrisii", use_container_width=True)

if USE_SQLITE:
    st.sidebar.markdown("### ☁️ SQLite Mode (Active)")
    st.sidebar.info("The application is running in serverless SQLite fallback mode. All data is saved locally in `devil_tracker.db`.")
    if st.sidebar.button("Switch to MySQL Mode"):
        st.session_state["use_sqlite"] = False
        st.rerun()
else:
    st.sidebar.markdown("### 🛠️ Database Control Panel")
    db_host = st.sidebar.text_input("Host", os.getenv("DB_HOST", "localhost"))
    db_port = st.sidebar.number_input("Port", value=int(os.getenv("DB_PORT", 3306)))
    db_user = st.sidebar.text_input("User", os.getenv("DB_USER", "root"))
    db_pass = st.sidebar.text_input("Password", os.getenv("DB_PASSWORD", "root"), type="password")
    db_name = st.sidebar.text_input("Database Name", os.getenv("DB_NAME", "devil_tracker"))

    # Update configuration if changed
    if (db_host != os.getenv("DB_HOST") or 
        str(db_port) != os.getenv("DB_PORT") or 
        db_user != os.getenv("DB_USER") or 
        db_pass != os.getenv("DB_PASSWORD") or 
        db_name != os.getenv("DB_NAME")):
        
        set_key(ENV_PATH, "DB_HOST", db_host)
        set_key(ENV_PATH, "DB_PORT", str(db_port))
        set_key(ENV_PATH, "DB_USER", db_user)
        set_key(ENV_PATH, "DB_PASSWORD", db_pass)
        set_key(ENV_PATH, "DB_NAME", db_name)
        # Reload environment
        load_dotenv(ENV_PATH, override=True)

config = get_db_config()
connected, err_msg = test_db_connection(config)

if not connected:
    st.error(f"⚠️ **Unable to connect to local MySQL Server.**")
    st.markdown(f"""
        **Connection Error:** `{err_msg}`
        
        Please make sure your local MySQL server is running with the correct credentials entered in the sidebar.
    """)
    
    col_setup, col_sqlite = st.columns(2)
    with col_sqlite:
        st.markdown("### ☁️ SQLite Fallback (Free & Serverless)")
        st.write("No database server? Run in **SQLite Fallback Mode** instantly. The app will create and populate a local database file autonomously.")
        if st.button("Start in SQLite Fallback Mode", type="primary", use_container_width=True):
            st.session_state["use_sqlite"] = True
            st.rerun()
            
    with col_setup:
        st.markdown("### 🚀 MySQL Initialization Wizard")
        st.write("Initialize tables, triggers, and mock data on your local MySQL server once connected.")
        if st.button("Initialize MySQL Database (~50k rows)", type="secondary", use_container_width=True):
            with st.status("Initializing Database...", expanded=True) as status:
                try:
                    import data_factory
                    data_factory.USE_SQLITE = False
                    data_factory.init_schema()
                    conn = get_connection()
                    data_factory.populate_static_data(conn)
                    data_factory.generate_demographics(conn)
                    conn.close()
                    status.update(label="MySQL Database Populated Successfully!", state="complete")
                    st.success("Success! Please refresh or interact with the app.")
                    st.rerun()
                except Exception as ex:
                    status.update(label="Setup Failed!", state="error")
                    st.error(f"Error: {ex}")
    st.stop()

# If connected, check if database and tables exist
try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(translate_query("SHOW TABLES"))
    tables = [t[0] for t in cursor.fetchall()]
    cursor.close()
    conn.close()
except Exception as e:
    st.warning("⚠️ **Database does not contain expected schema.**")
    st.markdown(f"Error: {e}")
    if st.button("Create Schema and Populate Data"):
        with st.status("Running Factory...", expanded=True) as status:
            import data_factory
            data_factory.USE_SQLITE = USE_SQLITE
            data_factory.init_schema()
            conn = get_connection()
            data_factory.populate_static_data(conn)
            data_factory.generate_demographics(conn)
            conn.close()
            st.success("Database populated!")
            st.rerun()
    st.stop()

# Navigation tabs
tab_overview, tab_breeding, tab_outbreaks, tab_biosecurity, tab_profile = st.tabs([
    "📊 Metapopulation Overview",
    "🧬 Breeding & Kinship Engine",
    "📈 Outbreak Surveillance Monitor",
    "🛡️ Biosecurity Transfer Guard",
    "😈 Individual Profile Lookup"
])

# Utility to fetch query results into DataFrame
@st.cache_data(ttl=60)
def run_query(query, params=None):
    conn = get_connection()
    translated_sql = translate_query(query)
    df = pd.read_sql(translated_sql, conn, params=params)
    conn.close()
    return df

# Helper to fetch individual devil pedigree & health metadata
def get_devil_ancestry(devil_id):
    query = """
        SELECT d.devil_id, d.name, d.sex, d.mother_id, d.father_id, d.mhc_allele_1, d.mhc_allele_2,
               (SELECT pcr_result FROM health_logs WHERE devil_id = d.devil_id ORDER BY log_date DESC, log_id DESC LIMIT 1) AS latest_pcr,
               (SELECT strain_name FROM strains WHERE strain_id = (SELECT detected_strain_id FROM health_logs WHERE devil_id = d.devil_id ORDER BY log_date DESC, log_id DESC LIMIT 1)) AS latest_strain
        FROM devils d
        WHERE d.devil_id = %s
    """
    df = run_query(query, params=(devil_id,))
    if df.empty:
        return None
    row = df.iloc[0]
    return {
        "id": int(row['devil_id']),
        "name": row['name'],
        "sex": row['sex'],
        "mother_id": int(row['mother_id']) if row['mother_id'] else None,
        "father_id": int(row['father_id']) if row['father_id'] else None,
        "mhc_1": row['mhc_allele_1'] or "Unknown",
        "mhc_2": row['mhc_allele_2'] or "Unknown",
        "pcr": row['latest_pcr'] or "Negative",
        "strain": row['latest_strain'] or "Healthy"
    }

def fetch_node(node_id):
    if not node_id:
        return None
    return get_devil_ancestry(node_id)

def evaluate_mhc_compatibility(mother_node, father_node):
    m_alleles = {mother_node['mhc_1'], mother_node['mhc_2']}
    f_alleles = {father_node['mhc_1'], father_node['mhc_2']}
    
    shared = m_alleles.intersection(f_alleles)
    
    if len(shared) == 0:
        status = "🟢 HIGH IMMUNE DIVERSITY POTENTIAL"
        desc = "The parents share **zero** MHC alleles. All potential offspring combinations will have 100% complementary immune profiles, maximizing disease resilience."
        color = "#10b981"
        border = "#059669"
    elif len(shared) == 1:
        status = "🟡 MODERATE IMMUNE DIVERSITY POTENTIAL"
        desc = f"The parents share **one** MHC allele ({list(shared)[0]}). Offspring have a 25% chance of homozygous expression, reducing diversity."
        color = "#f59e0b"
        border = "#d97706"
    else:
        status = "🔴 LOW IMMUNE DIVERSITY POTENTIAL (GENETIC OVERLAP)"
        desc = "The parents share **both** MHC alleles. Offspring will have highly restricted immune diversity, making them highly susceptible to disease clonal evasion."
        color = "#ef4444"
        border = "#dc2626"
        
    return status, desc, color, border

def render_pedigree_visualizer(female_id, male_id):
    # Fetch mother/father and grandparent details
    mother = fetch_node(female_id)
    father = fetch_node(male_id)
    
    m_mother = fetch_node(mother['mother_id']) if mother else None
    m_father = fetch_node(mother['father_id']) if mother else None
    
    f_mother = fetch_node(father['mother_id']) if father else None
    f_father = fetch_node(father['father_id']) if father else None
    
    def format_card_html(node, title):
        if not node:
            return f"""
                <div class="pedigree-card empty">
                    <div class="card-title">{title}</div>
                    <div class="card-id">Unknown</div>
                    <div class="card-name">-</div>
                    <div class="card-status">No Record</div>
                </div>
            """
        is_infected = node["strain"] in ["DFT1", "DFT2"] and node["pcr"] == "Positive"
        status_class = "infected" if is_infected else "healthy"
        gender_symbol = "♀️" if node["sex"] == "F" else "♂️"
        gender_class = "female" if node["sex"] == "F" else "male"
        
        return f"""
            <div class="pedigree-card {status_class}">
                <div class="card-title">{title}</div>
                <div class="card-id">#{node['id']} <span class="{gender_class}">{gender_symbol}</span></div>
                <div class="card-name">{node['name']}</div>
                <div class="card-status">{node['strain']} [{node['pcr']}]</div>
                <div style="font-size: 0.75rem; font-weight: bold; color: #a78bfa; margin-top: 4px;">
                    {node['mhc_1']} | {node['mhc_2']}
                </div>
            </div>
        """

    html = f"""
    <div class="pedigree-tree-container">
        <h4 style="color: #e2e8f0; font-family: sans-serif; margin-top: 0; margin-bottom: 1.5rem;">🧬 Proposed Pairing Lineage Visualizer</h4>
        
        <!-- Generation 3: Grandparents -->
        <div class="pedigree-row gp-row">
            <div class="pedigree-pair">
                {format_card_html(m_father, "Maternal Grandfather")}
                {format_card_html(m_mother, "Maternal Grandmother")}
            </div>
            <div class="pedigree-pair">
                {format_card_html(f_father, "Paternal Grandfather")}
                {format_card_html(f_mother, "Paternal Grandmother")}
            </div>
        </div>
        
        <!-- Connectors GP to Parents -->
        <div class="pedigree-connectors">
            <div class="connector-block">
                <div class="connector-line vertical"></div>
                <div class="connector-line horizontal"></div>
            </div>
            <div class="connector-block">
                <div class="connector-line vertical"></div>
                <div class="connector-line horizontal"></div>
            </div>
        </div>

        <!-- Generation 2: Candidate Parents -->
        <div class="pedigree-row p-row">
            {format_card_html(mother, "Candidate Mother")}
            {format_card_html(father, "Candidate Father")}
        </div>
        
        <!-- Connectors Parents to Offspring -->
        <div class="pedigree-connectors-single">
            <div class="connector-line vertical-single"></div>
        </div>

        <!-- Generation 1: Proposed Offspring -->
        <div class="pedigree-row self-row">
            <div class="pedigree-card healthy" style="border-color: #a78bfa; box-shadow: 0 0 12px rgba(167, 139, 250, 0.3);">
                <div class="card-title" style="color: #c084fc;">Proposed Offspring</div>
                <div class="card-id" style="color: #c084fc;">Generation F1</div>
                <div class="card-name" style="font-size: 1rem;">Genetic Blend</div>
                <div class="card-status" style="color: #a78bfa;">Status: Evaluation Check</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# TAB 1: METAPOPULATION OVERVIEW
# ==========================================
with tab_overview:
    st.markdown("### Metapopulation Health Dashboard")
    
    # KPI metrics row
    c1, c2, c3, c4 = st.columns(4)
    
    # Query metrics
    q_total_devils = "SELECT COUNT(*) FROM devils"
    q_alive_devils = "SELECT COUNT(*) FROM devils WHERE status = 'Alive'"
    q_infected = """
        SELECT COUNT(DISTINCT d.devil_id) 
        FROM devils d
        INNER JOIN health_logs hl ON d.devil_id = hl.devil_id
        INNER JOIN strains s ON hl.detected_strain_id = s.strain_id
        WHERE d.status = 'Alive' AND s.strain_name IN ('DFT1', 'DFT2') AND hl.pcr_result = 'Positive'
    """
    q_sanctuaries = "SELECT COUNT(*) FROM sanctuaries"
    
    total_d = run_query(q_total_devils).iloc[0,0]
    alive_d = run_query(q_alive_devils).iloc[0,0]
    infected_d = run_query(q_infected).iloc[0,0]
    sanc_d = run_query(q_sanctuaries).iloc[0,0]
    
    with c1:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>Total Monitored (Historical)</div>
                <div class='metric-value'>{total_d:,}</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>Current Alive Population</div>
                <div class='metric-value'>{alive_d:,}</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>Active Infections (DFT1/DFT2)</div>
                <div class='metric-value' style='color: #ef4444;'>{infected_d:,}</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>Active Sanctuaries</div>
                <div class='metric-value' style='color: #a78bfa;'>{sanc_d}</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Coordinate data for sanctuaries mapping
    coords = {
        "7190": (-42.617, 148.067),
        "7030": (-42.684, 147.261),
        "7306": (-41.583, 145.933),
        "7112": (-43.190, 147.112),
        "7150": (-43.297, 147.319),
        "7155": (-43.125, 147.246),
        "7264": (-40.912, 148.172),
        "7321": (-41.505, 145.228),
        "7215": (-42.115, 148.272),
        "7179": (-43.048, 147.859),
    }
    
    q_map_data = """
        WITH LatestLogs AS (
            SELECT 
                hl.devil_id,
                hl.pcr_result,
                s.strain_name,
                ROW_NUMBER() OVER (PARTITION BY hl.devil_id ORDER BY hl.log_date DESC, hl.log_id DESC) as rn
            FROM health_logs hl
            INNER JOIN strains s ON hl.detected_strain_id = s.strain_id
        )
        SELECT 
            s.name, 
            s.postcode,
            s.type,
            s.capacity,
            s.is_clean_zone,
            COUNT(d.devil_id) AS current_population,
            SUM(CASE WHEN ll.pcr_result = 'Positive' AND ll.strain_name IN ('DFT1', 'DFT2') THEN 1 ELSE 0 END) AS infected_population
        FROM sanctuaries s
        LEFT JOIN devils d ON s.sanctuary_id = d.current_sanctuary_id AND d.status = 'Alive'
        LEFT JOIN LatestLogs ll ON d.devil_id = ll.devil_id AND ll.rn = 1
        GROUP BY s.sanctuary_id
    """
    df_sanc = run_query(q_map_data)
    df_sanc['Fill Rate (%)'] = round((df_sanc['current_population'] / df_sanc['capacity']) * 100, 1)
    df_sanc['lat'] = df_sanc['postcode'].map(lambda p: coords.get(p, (-42.0, 147.0))[0])
    df_sanc['lon'] = df_sanc['postcode'].map(lambda p: coords.get(p, (-42.0, 147.0))[1])
    df_sanc['size'] = df_sanc['current_population'] * 20 + 2000
    
    def determine_color(row):
        if row['is_clean_zone']:
            return [16, 185, 129, 160] # Green
        rate = row['infected_population'] / max(1, row['current_population'])
        if rate == 0:
            return [16, 185, 129, 160] # Green
        elif rate < 0.15:
            return [245, 158, 11, 180] # Orange
        else:
            return [239, 68, 68, 200] # Red
            
    df_sanc['color'] = df_sanc.apply(determine_color, axis=1)
    
    st.markdown("#### 🗺️ Geographic Distribution & Sanctuary Status Map")
    col_map, col_table = st.columns([3, 2])
    
    with col_map:
        st.map(df_sanc, latitude='lat', longitude='lon', size='size', color='color', use_container_width=True)
        st.markdown("<p style='font-size: 0.85rem; color: #8b949e; text-align: center; margin: 0;'>Circle sizes reflect populations. Colors: <span style='color: #10b981;'>■ Healthy/Clean</span> | <span style='color: #f59e0b;'>■ Mild DFTD Rate</span> | <span style='color: #ef4444;'>■ High DFTD Prevalence</span></p>", unsafe_allow_html=True)
        
    with col_table:
        st.markdown("<br>", unsafe_allow_html=True)
        def highlight_clean(row):
            return ['background-color: #065f46; color: #d1fae5' if row.is_clean_zone else '' for _ in row]
            
        st.dataframe(
            df_sanc[['name', 'type', 'capacity', 'current_population', 'Fill Rate (%)', 'is_clean_zone']]
                   .style.apply(highlight_clean, axis=1)
                   .format({"capacity": "{:,}", "current_population": "{:,}", "Fill Rate (%)": "{:.1f}%"}),
            use_container_width=True,
            hide_index=True
        )
        
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("#### Disease Strain Prevalence (Active Strains in Living Population)")
        # Query active strain breakdown
        q_strain_prevalence = """
            WITH LatestLogs AS (
                SELECT 
                    hl.devil_id,
                    hl.detected_strain_id,
                    ROW_NUMBER() OVER (PARTITION BY hl.devil_id ORDER BY hl.log_date DESC, hl.log_id DESC) as rn
                FROM health_logs hl
                INNER JOIN devils d ON hl.devil_id = d.devil_id
                WHERE d.status = 'Alive'
            )
            SELECT 
                s.strain_name,
                COUNT(*) as count
            FROM LatestLogs ll
            INNER JOIN strains s ON ll.detected_strain_id = s.strain_id
            WHERE ll.rn = 1
            GROUP BY s.strain_name
        """
        df_strains = run_query(q_strain_prevalence)
        
        # Plot
        fig, ax = plt.subplots(figsize=(8, 4.5))
        fig.patch.set_facecolor('#0d0f12')
        ax.set_facecolor('#161b22')
        
        colors = ['#10b981', '#f59e0b', '#ef4444'] # Green, Orange, Red
        sns.barplot(data=df_strains, x='strain_name', y='count', palette=colors, ax=ax)
        
        ax.set_xlabel("Disease Strain Status", color='#e2e8f0', fontsize=12)
        ax.set_ylabel("Number of Living Devils", color='#e2e8f0', fontsize=12)
        ax.tick_params(colors='#8b949e')
        ax.spines['bottom'].set_color('#30363d')
        ax.spines['left'].set_color('#30363d')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.1)
        
        for p in ax.patches:
            ax.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height() + 5),
                        ha='center', va='center', xytext=(0, 5), textcoords='offset points', color='#e2e8f0', fontweight='bold')
            
        st.pyplot(fig)
        
    with col_chart2:
        st.markdown("#### Clinical Bite Scar Severity Analysis")
        q_bites = """
            WITH LatestLogs AS (
                SELECT 
                    hl.devil_id,
                    hl.bite_scars,
                    s.strain_name,
                    ROW_NUMBER() OVER (PARTITION BY hl.devil_id ORDER BY hl.log_date DESC, hl.log_id DESC) as rn
                FROM health_logs hl
                INNER JOIN devils d ON hl.devil_id = d.devil_id
                INNER JOIN strains s ON hl.detected_strain_id = s.strain_id
                WHERE d.status = 'Alive'
            )
            SELECT 
                strain_name as "Health Class",
                ROUND(AVG(bite_scars), 2) as "Avg Bite Scars"
            FROM LatestLogs
            WHERE rn = 1
            GROUP BY strain_name
        """
        df_bites = run_query(q_bites)
        
        fig, ax = plt.subplots(figsize=(8, 4.5))
        fig.patch.set_facecolor('#0d0f12')
        ax.set_facecolor('#161b22')
        
        sns.barplot(data=df_bites, x='Health Class', y='Avg Bite Scars', palette=['#10b981', '#f59e0b', '#ef4444'], ax=ax)
        ax.set_xlabel("Health Condition", color='#e2e8f0', fontsize=12)
        ax.set_ylabel("Average Bite Scars Logged", color='#e2e8f0', fontsize=12)
        ax.tick_params(colors='#8b949e')
        ax.spines['bottom'].set_color('#30363d')
        ax.spines['left'].set_color('#30363d')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.1)
        
        for p in ax.patches:
            ax.annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height() + 0.1),
                        ha='center', va='center', xytext=(0, 5), textcoords='offset points', color='#e2e8f0', fontweight='bold')
                        
        st.pyplot(fig)
        
    st.markdown("---")
    st.markdown("#### 🌲 Re-wilding Candidate Selection Console")
    st.write("Identify and rank healthy devils from captive breeding facilities (Bonorong & Devils@Cradle) for re-introduction into the wild. Recommendations prioritize prime reproductive ages (1.5–3.0 years) and rare MHC profiles to supplement wild genetic diversity.")
    
    # 1. Fetch wild alleles to compute frequencies
    df_wild = run_query("""
        SELECT mhc_allele_1, mhc_allele_2 
        FROM devils d
        INNER JOIN sanctuaries s ON d.current_sanctuary_id = s.sanctuary_id
        WHERE d.status = 'Alive' AND s.is_clean_zone = 0
    """)
    
    if not df_wild.empty:
        all_wild_alleles = list(df_wild['mhc_allele_1'].dropna()) + list(df_wild['mhc_allele_2'].dropna())
        counts = Counter(all_wild_alleles)
        total = len(all_wild_alleles)
        allele_freqs = {allele: count/total for allele, count in counts.items()}
    else:
        allele_freqs = {}
        
    # 2. Fetch captive candidates
    q_candidates = """
        WITH LatestLogs AS (
            SELECT 
                hl.devil_id,
                hl.pcr_result,
                s.strain_name,
                ROW_NUMBER() OVER (PARTITION BY hl.devil_id ORDER BY hl.log_date DESC, hl.log_id DESC) as rn
            FROM health_logs hl
            INNER JOIN strains s ON hl.detected_strain_id = s.strain_id
        )
        SELECT 
            d.devil_id, 
            d.name, 
            d.sex, 
            d.birth_date,
            s.name AS current_location,
            d.mhc_allele_1,
            d.mhc_allele_2,
            (julianday('2026-06-10') - julianday(d.birth_date)) / 365.25 AS age
        FROM devils d
        INNER JOIN sanctuaries s ON d.current_sanctuary_id = s.sanctuary_id
        INNER JOIN LatestLogs ll ON d.devil_id = ll.devil_id AND ll.rn = 1
        WHERE d.status = 'Alive' 
          AND s.name IN ('Bonorong Wildlife Sanctuary', 'Devils@Cradle')
          AND ll.pcr_result = 'Negative' 
          AND ll.strain_name = 'Healthy'
    """
    df_cand = run_query(q_candidates)
    
    if df_cand.empty:
        st.info("No healthy adult devils found in captive sanctuaries at this time.")
    else:
        # Calculate suitability score
        def calc_suitability(row):
            age = row['age']
            if 1.5 <= age <= 3.0:
                age_score = 100.0
            elif age < 1.5:
                age_score = (age / 1.5) * 100.0
            else:
                age_score = max(0.0, 100.0 - (age - 3.0) * 30.0)
                
            a1, a2 = row['mhc_allele_1'], row['mhc_allele_2']
            f1 = allele_freqs.get(a1, 0.16)
            f2 = allele_freqs.get(a2, 0.16)
            avg_freq = (f1 + f2) / 2.0
            
            rarity_score = max(0.0, min(100.0, (0.33 - avg_freq) / 0.28 * 100.0))
            total_score = age_score * 0.6 + rarity_score * 0.4
            return pd.Series([round(age_score, 1), round(rarity_score, 1), round(total_score, 1)])
            
        df_cand[['Age Fit', 'MHC Rarity', 'Suitability Score']] = df_cand.apply(calc_suitability, axis=1)
        
        df_top = df_cand.sort_values(by='Suitability Score', ascending=False).head(10).copy()
        df_top['Rank'] = range(1, len(df_top) + 1)
        
        destinations = [
            "Maria Island Reserve (Island Quarantine)", 
            "Mount William National Park (Wild Release)", 
            "Savage River National Park (Wild Release)",
            "Bruny Island Sanctuary (Island quarantine)"
        ]
        df_top['Recommended Destination'] = [destinations[i % len(destinations)] for i in range(len(df_top))]
        
        st.dataframe(
            df_top[['Rank', 'devil_id', 'name', 'sex', 'age', 'mhc_allele_1', 'mhc_allele_2', 'Suitability Score', 'Recommended Destination']]
                  .rename(columns={
                      "devil_id": "Devil ID",
                      "name": "Name",
                      "sex": "Sex",
                      "age": "Age (yrs)",
                      "mhc_allele_1": "Allele 1",
                      "mhc_allele_2": "Allele 2",
                      "Suitability Score": "Suitability Score (%)"
                  }).style.format({"Age (yrs)": "{:.1f}", "Suitability Score (%)": "{:.1f}%"}),
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# TAB 2: BREEDING & KINSHIP ENGINE
# ==========================================
with tab_breeding:
    st.markdown("### 🧬 Breeding Lineage Kinship Assessor")
    st.write("Calculate shared ancestry and inbreeding coefficients before pairing captive devils up to 3 generations backward.")
    
    # Fetch lists of living adult females and adult males for breeding selection
    # Mature breeding age: >= 1.5 years (540 days old)
    q_breeders = """
        SELECT 
            devil_id, 
            name, 
            sex, 
            birth_date,
            DATEDIFF('2026-06-10', birth_date) / 365.25 AS age
        FROM devils 
        WHERE status = 'Alive' 
          AND DATEDIFF('2026-06-10', birth_date) >= 540
    """
    df_all_breeders = run_query(q_breeders)
    
    females = df_all_breeders[df_all_breeders['sex'] == 'F']
    males = df_all_breeders[df_all_breeders['sex'] == 'M']
    
    col_fem, col_male = st.columns(2)
    
    with col_fem:
        female_list = [f"#{row.devil_id} - {row.name} (Age: {row.age:.1f} yr)" for row in females.itertuples()]
        selected_female_str = st.selectbox("Select Female Candidate (Mother):", female_list)
        female_id = int(selected_female_str.split(" - ")[0].replace("#", ""))
        
    with col_male:
        male_list = [f"#{row.devil_id} - {row.name} (Age: {row.age:.1f} yr)" for row in males.itertuples()]
        selected_male_str = st.selectbox("Select Male Candidate (Father):", male_list)
        male_id = int(selected_male_str.split(" - ")[0].replace("#", ""))
        
    if st.button("Evaluate Breeding Pair Compatibility", type="primary"):
        # Run recursive query to find shared ancestors
        q_kinship = """
            WITH RECURSIVE Ancestry AS (
                SELECT 
                    devil_id, 
                    mother_id, 
                    father_id, 
                    name,
                    0 AS generation,
                    devil_id AS lineage_start
                FROM devils
                WHERE devil_id IN (%s, %s)
                
                UNION ALL
                
                SELECT 
                    d.devil_id, 
                    d.mother_id, 
                    d.father_id, 
                    d.name,
                    a.generation + 1 AS generation,
                    a.lineage_start
                FROM devils d
                INNER JOIN Ancestry a ON d.devil_id = a.mother_id OR d.devil_id = a.father_id
                WHERE a.generation < 3
            )
            SELECT 
                a.devil_id AS shared_ancestor_id,
                a.name AS shared_ancestor_name,
                a.generation AS female_side_gen,
                b.generation AS male_side_gen,
                (a.generation + b.generation) AS degree_of_relationship,
                POWER(0.5, a.generation + b.generation + 1) AS kinship_contribution
            FROM Ancestry a
            INNER JOIN Ancestry b ON a.devil_id = b.devil_id
            WHERE a.lineage_start = %s 
              AND b.lineage_start = %s
        """
        
        df_kinship = run_query(q_kinship, params=(female_id, male_id, female_id, male_id))
        
        st.markdown("#### evaluation results")
        
        # Calculate and display MHC compatibility
        mother_node = get_devil_ancestry(female_id)
        father_node = get_devil_ancestry(male_id)
        if mother_node and father_node:
            mhc_status, mhc_desc, mhc_color, mhc_border = evaluate_mhc_compatibility(mother_node, father_node)
            st.markdown(f"""
                <div style="background-color: #161b22; border: 1px solid {mhc_border}; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;">
                    <h4 style="color: {mhc_color}; margin: 0 0 0.5rem 0;">{mhc_status}</h4>
                    <p style="color: #e2e8f0; margin: 0; font-size: 0.95rem;">
                        <strong>Mother's Haplotype:</strong> {mother_node['mhc_1']} | {mother_node['mhc_2']}<br/>
                        <strong>Father's Haplotype:</strong> {father_node['mhc_1']} | {father_node['mhc_2']}<br/>
                        <span style="font-size: 0.9rem; color: #9ca3af; display: block; margin-top: 0.4rem;">{mhc_desc}</span>
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
        if df_kinship.empty:
            st.success("✅ **SAFE PAIRING APPROVED**")
            st.markdown(f"""
                **No shared ancestors** were found between female **#{female_id}** and male **#{male_id}** up to 3 generations backward.
                
                - Inbreeding Coefficient contribution within 3 generations: **0.000 (0.0%)**
                - Breeding recommendation: **High Priority Match** (promotes genetic diversity).
            """)
        else:
            total_coefficient = df_kinship['kinship_contribution'].sum()
            inbreeding_pct = total_coefficient * 100
            
            if inbreeding_pct >= 6.25:
                st.markdown(f"""
                    <div style="background-color: #7f1d1d; border: 1px solid #dc2626; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;">
                        <h4 style="color: #fca5a5; margin: 0 0 0.5rem 0;">🚨 HIGH INBREEDING RISK DETECTED ({inbreeding_pct:.2f}%)</h4>
                        <p style="color: #fca5a5; margin: 0;">This pair shares ancestor(s) too recently in their family tree. Pairing is <strong>strongly discouraged</strong>.</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style="background-color: #7c2d12; border: 1px solid #ea580c; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;">
                        <h4 style="color: #ffedd5; margin: 0 0 0.5rem 0;">⚠️ MODERATE COMPATIBILITY WARNING ({inbreeding_pct:.2f}%)</h4>
                        <p style="color: #ffedd5; margin: 0;">This pair shares distant ancestors. Proceed with caution if genetic alternatives are unavailable.</p>
                    </div>
                """, unsafe_allow_html=True)
                
            st.write("**Shared Ancestor Pedigree Path Details:**")
            st.dataframe(
                df_kinship.rename(columns={
                    "shared_ancestor_id": "Ancestor ID",
                    "shared_ancestor_name": "Ancestor Name",
                    "female_side_gen": "Generations back (Mother)",
                    "male_side_gen": "Generations back (Father)",
                    "degree_of_relationship": "Total Degree Steps",
                    "kinship_contribution": "F Coefficient Contribution"
                }).style.format({"F Coefficient Contribution": "{:.4f}"}),
                use_container_width=True,
                hide_index=True
            )

        # Render visual pedigree tree
        render_pedigree_visualizer(female_id, male_id)

# ==========================================
# TAB 3: OUTBREAK SURVEILLANCE MONITOR
# ==========================================
with tab_outbreaks:
    st.markdown("### 📈 Epidemic Transmission Window Analytics")
    st.write("Using SQL Analytical Window functions (`LAG() OVER ...`), we calculate the time difference (in days) between consecutive positive DFTD diagnoses within each postcode to monitor disease velocity.")
    
    # Query outbreak monitor
    q_outbreak = """
        WITH PositiveDiagnoses AS (
            SELECT 
                hl.log_date,
                s.postcode,
                s.name AS sanctuary_name,
                d.devil_id,
                d.name AS devil_name,
                st.strain_name,
                LAG(hl.log_date) OVER (PARTITION BY s.postcode ORDER BY hl.log_date) AS prev_positive_date
            FROM health_logs hl
            INNER JOIN devils d ON hl.devil_id = d.devil_id
            INNER JOIN sanctuaries s ON d.current_sanctuary_id = s.sanctuary_id
            INNER JOIN strains st ON hl.detected_strain_id = st.strain_id
            WHERE hl.pcr_result = 'Positive' AND st.strain_name IN ('DFT1', 'DFT2')
        ),
        DiagnosisIntervals AS (
            SELECT 
                log_date,
                postcode,
                sanctuary_name,
                devil_id,
                devil_name,
                strain_name,
                prev_positive_date,
                DATEDIFF(log_date, prev_positive_date) AS days_since_last_case
            FROM PositiveDiagnoses
        ),
        IntervalTrends AS (
            SELECT
                log_date,
                postcode,
                sanctuary_name,
                devil_id,
                devil_name,
                strain_name,
                days_since_last_case,
                AVG(days_since_last_case) OVER (PARTITION BY postcode ORDER BY log_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg_interval
            FROM DiagnosisIntervals
            WHERE days_since_last_case IS NOT NULL
        )
        SELECT 
            log_date,
            postcode,
            sanctuary_name,
            devil_id,
            devil_name,
            strain_name,
            days_since_last_case,
            ROUND(moving_avg_interval, 1) AS moving_avg_interval_days,
            CASE 
                WHEN days_since_last_case < moving_avg_interval THEN '⚠️ ACCELERATING OUTBREAK'
                ELSE 'STABLE'
            END AS biosecurity_status
        FROM IntervalTrends
        ORDER BY postcode, log_date DESC
    """
    
    df_outbreak_raw = run_query(q_outbreak)
    
    # Summary of accelerating postcodes
    accelerating = df_outbreak_raw[df_outbreak_raw['biosecurity_status'].str.contains('ACCELERATING')]
    accelerating_summary = accelerating.groupby(['postcode', 'sanctuary_name']).size().reset_index(name='Recent Accelerating Tests')
    
    c_alert, c_table = st.columns([1, 2])
    
    with c_alert:
        st.markdown("#### Outbreak Alert Panel")
        if not accelerating_summary.empty:
            for s in accelerating_summary.itertuples():
                st.error(f"🚨 **Accelerating Infection Rate: {s.sanctuary_name} (Postcode: {s.postcode})**\nTime interval between consecutive positive cases is shrinking!")
        else:
            st.success("✅ No postcodes currently showing accelerating transmission intervals.")
            
        # Grouped summary of regions
        st.markdown("#### Diagnostic Case Rates (Postcode Grouped)")
        st.dataframe(
            df_outbreak_raw.groupby('postcode').agg(
                cases=('devil_id', 'count'),
                avg_interval=('days_since_last_case', 'mean')
            ).rename(columns={"cases": "Total Cases Logged", "avg_interval": "Avg Transmission Interval (days)"})
            .style.format({"Avg Transmission Interval (days)": "{:.1f}"}),
            use_container_width=True
        )
        
    with c_table:
        st.markdown("#### Trapping Event Logs & Transmission Status")
        st.dataframe(
            df_outbreak_raw.rename(columns={
                "log_date": "Log Date",
                "postcode": "Postcode",
                "sanctuary_name": "Sanctuary Location",
                "devil_id": "Devil ID",
                "devil_name": "Name",
                "strain_name": "Strain",
                "days_since_last_case": "Days Since Prev Case",
                "moving_avg_interval_days": "Moving Avg Interval (days)",
                "biosecurity_status": "Outbreak Velocity Status"
            }),
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# TAB 4: BIOSECURITY TRANSFER GUARD
# ==========================================
with tab_biosecurity:
    st.markdown("### 🛡️ Sanctuary Biosecurity Guard & Transfer Manager")
    st.write("Demonstrate the database trigger in action. Attempting to transfer a devil to a designated clean insurance zone (e.g. Maria Island, Bonorong, Devils@Cradle) will query the devil's latest health log. If positive for DFTD, the database trigger natively aborts the update and throws a custom exception.")
    
    # Retrieve living devils and their current location
    q_transfer_devils = """
        SELECT 
            d.devil_id, 
            d.name, 
            s.name AS current_sanctuary,
            s.sanctuary_id,
            -- Subquery to get latest health status
            (SELECT strain_name FROM strains WHERE strain_id = hl.detected_strain_id) AS latest_status,
            (SELECT pcr_result FROM health_logs hl WHERE hl.devil_id = d.devil_id ORDER BY hl.log_date DESC, hl.log_id DESC LIMIT 1) AS latest_pcr
        FROM devils d
        INNER JOIN sanctuaries s ON d.current_sanctuary_id = s.sanctuary_id
        LEFT JOIN health_logs hl ON hl.devil_id = d.devil_id
        WHERE d.status = 'Alive'
        GROUP BY d.devil_id
    """
    df_transfers = run_query(q_transfer_devils)
    
    # Setup selection
    devil_choices = [
        f"#{row.devil_id} - {row.name} (Current: {row.current_sanctuary} | Status: {row.latest_status} [{row.latest_pcr}])"
        for row in df_transfers.itertuples()
    ]
    
    selected_devil_str = st.selectbox("Select Devil to Transfer:", devil_choices)
    selected_devil_id = int(selected_devil_str.split(" - ")[0].replace("#", ""))
    selected_devil_info = df_transfers[df_transfers['devil_id'] == selected_devil_id].iloc[0]
    
    # Retrieve sanctuaries list
    q_all_sanc = "SELECT sanctuary_id, name, postcode, is_clean_zone FROM sanctuaries"
    df_all_sanc = run_query(q_all_sanc)
    
    sanc_choices = [
        f"#{row.sanctuary_id} - {row.name} (Postcode: {row.postcode} | {'🔒 CLEAN INSURANCE ZONE' if row.is_clean_zone else '🔓 GENERAL AREA'})"
        for row in df_all_sanc.itertuples()
    ]
    
    selected_sanc_str = st.selectbox("Select Destination Sanctuary:", sanc_choices)
    selected_sanc_id = int(selected_sanc_str.split(" - ")[0].replace("#", ""))
    selected_sanc_info = df_all_sanc[df_all_sanc['sanctuary_id'] == selected_sanc_id].iloc[0]
    
    # Run the transaction
    if st.button("Execute Transfer Transaction"):
        st.markdown("#### execution logs")
        
        # Check if same sanctuary
        if selected_devil_info.sanctuary_id == selected_sanc_id:
            st.warning("Animal is already located in the selected sanctuary.")
        else:
            # Connect and attempt update
            conn = get_connection()
            cursor = conn.cursor()
            
            try:
                st.info(f"Initiating SQL transfer statement: `UPDATE devils SET current_sanctuary_id = {selected_sanc_id} WHERE devil_id = {selected_devil_id}`")
                
                # Try executing the update
                sql = translate_query("UPDATE devils SET current_sanctuary_id = %s WHERE devil_id = %s")
                cursor.execute(sql, (selected_sanc_id, selected_devil_id))
                conn.commit()
                
                st.success("🎉 **TRANSFER SUCCESSFUL**")
                # Clear query cache to reflect changes immediately
                st.cache_data.clear()
                st.markdown(f"Devil **#{selected_devil_id} ({selected_devil_info['name']})** has been safely transferred to **{selected_sanc_info['name']}**.")
            except Exception as e:
                # Capture the custom fail-safe error code from the trigger
                err_msg = str(e)
                if "Biosecurity Breach" in err_msg or "trigger" in err_msg.lower() or "fail" in err_msg.lower() or "abort" in err_msg.lower():
                    st.markdown(f"""
                        <div style="background-color: #7f1d1d; border: 1px solid #dc2626; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;">
                            <h4 style="color: #fca5a5; margin: 0 0 0.5rem 0;">🚫 BIOSECURITY TRANSFER BLOCK (DATABASE REJECTION)</h4>
                            <p style="color: #fca5a5; font-family: monospace; font-size: 0.95rem; margin-bottom: 0.5rem;">{err_msg}</p>
                            <p style="color: #f87171; margin: 0; font-size: 0.9rem;">
                                <strong>Trigger Alert:</strong> The database engine intercepted the transaction natively. The animal's latest health diagnosis is <strong>{selected_devil_info.latest_status} ({selected_devil_info.latest_pcr})</strong>, violating the strict biosecurity quarantine policy of the clean zone <strong>{selected_sanc_info['name']}</strong>.
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Database Error: {err_msg}")
            finally:
                cursor.close()
                conn.close()

# ==========================================
# TAB 5: INDIVIDUAL PROFILE LOOKUP
# ==========================================
with tab_profile:
    st.markdown("### 😈 Tasmanian Devil Clinical & Weight Profile")
    st.write("Search for any monitored devil to view their full pedigree information, clinical history log, and weight wasting analysis compared to a healthy reference population.")
    
    search_query = st.text_input("🔍 Search Devil by ID or Name:", placeholder="Enter ID (e.g. 7024) or Name (e.g. Teresa)")
    
    if search_query:
        conn = get_connection()
        cursor = conn.cursor()
        if search_query.isdigit():
            sql = "SELECT devil_id, name, sex, status, current_sanctuary_id FROM devils WHERE devil_id = %s"
            params = (int(search_query),)
        else:
            sql = "SELECT devil_id, name, sex, status, current_sanctuary_id FROM devils WHERE name LIKE %s LIMIT 15"
            params = (f"%{search_query}%",)
            
        sql = translate_query(sql)
        cursor.execute(sql, params)
        matches = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not matches:
            st.warning("No devils found matching that query.")
        else:
            options = [f"#{m[0]} - {m[1]} ({m[2]} | {m[3]})" for m in matches]
            selected_option = st.selectbox("Select devil to view:", options)
            selected_id = int(selected_option.split(" - ")[0].replace("#", ""))
            
            # Fetch complete profile data
            q_profile = """
                SELECT 
                    d.devil_id, d.name, d.sex, d.birth_date, d.status, d.mhc_allele_1, d.mhc_allele_2,
                    s.name AS sanctuary_name, s.postcode, s.is_clean_zone,
                    d.mother_id, d.father_id,
                    m.name AS mother_name, f.name AS father_name
                FROM devils d
                INNER JOIN sanctuaries s ON d.current_sanctuary_id = s.sanctuary_id
                LEFT JOIN devils m ON d.mother_id = m.devil_id
                LEFT JOIN devils f ON d.father_id = f.devil_id
                WHERE d.devil_id = %s
            """
            df_prof = run_query(q_profile, params=(selected_id,))
            
            if not df_prof.empty:
                prof = df_prof.iloc[0]
                
                # Display layout columns
                col_info, col_chart = st.columns([1, 2])
                
                with col_info:
                    st.markdown("#### 📋 Demographics & Pedigree")
                    
                    status_badge = '<span class="status-badge badge-clean">Alive</span>' if prof['status'] == 'Alive' else '<span class="status-badge badge-threat">Deceased</span>'
                    zone_badge = '<span class="status-badge badge-clean">🔒 Clean Zone</span>' if prof['is_clean_zone'] else '<span class="status-badge badge-threat">🔓 General Area</span>'
                    
                    st.markdown(f"""
                        <div style="background-color: #161b22; border: 1px solid #30363d; padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;">
                            <h3 style="color: #f3e8ff; margin: 0 0 0.5rem 0;">{prof['name']}</h3>
                            <p style="margin: 0.2rem 0;"><strong>Devil ID:</strong> #{prof['devil_id']}</p>
                            <p style="margin: 0.2rem 0;"><strong>Sex:</strong> {"Female ♀️" if prof['sex'] == 'F' else "Male ♂️"}</p>
                            <p style="margin: 0.2rem 0;"><strong>Status:</strong> {status_badge}</p>
                            <p style="margin: 0.2rem 0;"><strong>Birth Date:</strong> {prof['birth_date']}</p>
                            <p style="margin: 0.2rem 0;"><strong>MHC Haplotype:</strong> <span style="color: #c084fc; font-weight: bold;">{prof['mhc_allele_1']} | {prof['mhc_allele_2']}</span></p>
                            <p style="margin: 0.2rem 0;"><strong>Current Location:</strong> {prof['sanctuary_name']} (Postcode: {prof['postcode']})</p>
                            <p style="margin: 0.2rem 0;"><strong>Biosecurity Class:</strong> {zone_badge}</p>
                            <hr style="border: 0; border-top: 1px solid #30363d; margin: 1rem 0;" />
                            <p style="margin: 0.2rem 0;"><strong>Mother:</strong> {f"#{prof['mother_id']} - {prof['mother_name']}" if prof['mother_id'] else "Wild Born (Unknown)"}</p>
                            <p style="margin: 0.2rem 0;"><strong>Father:</strong> {f"#{prof['father_id']} - {prof['father_name']}" if prof['father_id'] else "Wild Born (Unknown)"}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Fetch latest health details
                    q_latest_health = """
                        SELECT hl.log_date, hl.weight, hl.bite_scars, hl.pcr_result, s.strain_name, hl.notes
                        FROM health_logs hl
                        INNER JOIN strains s ON hl.detected_strain_id = s.strain_id
                        WHERE hl.devil_id = %s
                        ORDER BY hl.log_date DESC, hl.log_id DESC
                        LIMIT 1
                    """
                    df_hl_latest = run_query(q_latest_health, params=(selected_id,))
                    if not df_hl_latest.empty:
                        hl_l = df_hl_latest.iloc[0]
                        health_class = "badge-clean" if hl_l['strain_name'] == 'Healthy' else "badge-threat"
                        st.markdown(f"""
                            <div style="background-color: #161b22; border: 1px solid #30363d; padding: 1.5rem; border-radius: 12px;">
                                <h4 style="color: #fca5a5; margin: 0 0 0.5rem 0;">🩺 Latest Clinical Diagnostic</h4>
                                <p style="margin: 0.2rem 0;"><strong>Last Checked:</strong> {hl_l['log_date']}</p>
                                <p style="margin: 0.2rem 0;"><strong>Status:</strong> <span class="status-badge {health_class}">{hl_l['strain_name']} [{hl_l['pcr_result']}]</span></p>
                                <p style="margin: 0.2rem 0;"><strong>Weight:</strong> {hl_l['weight']} kg</p>
                                <p style="margin: 0.2rem 0;"><strong>Bite Scars:</strong> {hl_l['bite_scars']}</p>
                                <p style="margin: 0.4rem 0 0 0; font-size: 0.9rem; font-style: italic; color: #8b949e;">" {hl_l['notes']} "</p>
                            </div>
                        """, unsafe_allow_html=True)
                
                with col_chart:
                    st.markdown("#### 📈 Weight Wasting & Growth Trajectory Analysis")
                    
                    fig, ax = plt.subplots(figsize=(10, 5))
                    fig.patch.set_facecolor('#0d0f12')
                    ax.set_facecolor('#161b22')
                    
                    df_logs = run_query("""
                        SELECT hl.log_date, hl.weight, hl.pcr_result, s.strain_name,
                               (julianday(hl.log_date) - julianday(d.birth_date)) / 365.25 AS age_years
                        FROM health_logs hl
                        INNER JOIN devils d ON hl.devil_id = d.devil_id
                        INNER JOIN strains s ON hl.detected_strain_id = s.strain_id
                        WHERE hl.devil_id = %s
                        ORDER BY hl.log_date
                    """, params=(selected_id,))
                    
                    ages_ref = np.linspace(0.5, 6.0, 100)
                    if prof['sex'] == 'F':
                        y_min = np.where(ages_ref < 1.5, 1.5 + (ages_ref/1.5)*3.5, 5.0)
                        y_max = np.where(ages_ref < 1.5, 4.5 + (ages_ref/1.5)*4.5, 9.0)
                    else:
                        y_min = np.where(ages_ref < 1.5, 1.5 + (ages_ref/1.5)*6.5, 8.0)
                        y_max = np.where(ages_ref < 1.5, 4.5 + (ages_ref/1.5)*9.5, 14.0)
                        
                    ax.fill_between(ages_ref, y_min, y_max, color='#10b981', alpha=0.08, label='Healthy Reference Range')
                    
                    if not df_logs.empty:
                        ax.plot(df_logs['age_years'], df_logs['weight'], color='#c084fc', linewidth=3, marker='o', label=f"{prof['name']}'s Growth Curve")
                        
                        colors_points = []
                        for row in df_logs.itertuples():
                            if row.strain_name != 'Healthy' and row.pcr_result == 'Positive':
                                colors_points.append('#ef4444')
                            elif row.pcr_result == 'Inconclusive':
                                colors_points.append('#f59e0b')
                            else:
                                colors_points.append('#10b981')
                        
                        ax.scatter(df_logs['age_years'], df_logs['weight'], c=colors_points, s=80, zorder=5)
                        
                    ax.set_xlabel("Age (Years)", color='#e2e8f0', fontsize=12)
                    ax.set_ylabel("Weight (kg)", color='#e2e8f0', fontsize=12)
                    ax.tick_params(colors='#8b949e')
                    ax.spines['bottom'].set_color('#30363d')
                    ax.spines['left'].set_color('#30363d')
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.grid(axis='both', linestyle='--', alpha=0.1)
                    ax.legend(facecolor='#161b22', edgecolor='#30363d', labelcolor='#e2e8f0')
                    st.pyplot(fig)
                    
                    st.markdown("---")
                    st.markdown("#### 📜 Clinical Timeline Event Logs")
                    
                    timeline_html = "<div class='timeline'>"
                    for log in df_logs.itertuples():
                        badge_color = "#059669" if log.strain_name == 'Healthy' else "#dc2626"
                        badge_text = f"{log.strain_name} [{log.pcr_result}]"
                        
                        timeline_html += f"""
                            <div class="timeline-item">
                                <div class="timeline-date">{log.log_date} (Age {log.age_years:.1f} yr)</div>
                                <div class="timeline-content">
                                    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 5px;">
                                        <span class="timeline-badge" style="background-color: {badge_color};">{badge_text}</span>
                                        <span style="font-size: 0.85rem; color: #8b949e;">Weight: <strong>{log.weight} kg</strong> | Bite Scars: <strong>{log.bite_scars}</strong></span>
                                    </div>
                                    <div style="font-size: 0.9rem; color: #d1d5db;">{log.notes}</div>
                                </div>
                            </div>
                        """
                    timeline_html += "</div>"
                    st.markdown(timeline_html, unsafe_allow_html=True)
