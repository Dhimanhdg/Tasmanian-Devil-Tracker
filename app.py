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
    </style>
""", unsafe_allow_html=True)

# Ensure .env is loaded
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)

# Retrieve configuration
def get_db_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 3306)),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "root"),
        "database": os.getenv("DB_NAME", "devil_tracker")
    }

def test_db_connection(config):
    """Test connection without database name first, to check access permissions."""
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
    """Retrieve connection to devil_tracker database."""
    cfg = get_db_config()
    return mysql.connector.connect(**cfg)

# Title Header
st.markdown("""
    <div class='title-container'>
        <h1 class='title-text'>Save the Tasmanian Devil</h1>
        <p class='subtitle-text'>Disease Transmission Tracking, Pedigree Kinship Analysis & Biosecurity Control Center</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Credentials & Setup Management
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/ea/Tasmanian_devil_port_arthur.jpg", caption="Sarcophilus harrisii", use_container_width=True)
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
        
        Please make sure:
        1. Your local MySQL server is running on port `{config['port']}`.
        2. The user credentials entered in the sidebar are correct.
        3. You have set up a password in the sidebar if required.
        
        Once connected, you will be able to initialize the database schema and populate it with simulated data.
    """)
    
    st.markdown("### 🚀 Database Initialization & Setup Wizard")
    if st.button("Initialize & Populate Database (~50k rows)", type="primary"):
        with st.status("Initializing Database...", expanded=True) as status:
            try:
                status.write("Checking schema.sql...")
                import data_factory
                status.write("Running schema.sql scripts on MySQL server...")
                data_factory.init_schema()
                
                status.write("Inserting base strains & sanctuaries...")
                conn = get_connection()
                data_factory.populate_static_data(conn)
                
                status.write("Generating demographic cohorts & health histories (~50,000 rows)...")
                data_factory.generate_demographics(conn)
                conn.close()
                
                status.update(label="Database Populated Successfully!", state="complete")
                st.success("Success! Please refresh or interact with the app.")
                st.rerun()
            except Exception as ex:
                status.update(label="Setup Failed!", state="error")
                st.error(f"Error during initialization: {ex}")
    st.stop()

# If connected, check if database and tables exist
try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    cursor.close()
    conn.close()
except Error as e:
    st.warning("⚠️ **Database does not contain expected schema.**")
    st.markdown(f"Error: {e}")
    if st.button("Create Schema and Populate Data"):
        with st.status("Running Factory...", expanded=True) as status:
            import data_factory
            data_factory.init_schema()
            conn = get_connection()
            data_factory.populate_static_data(conn)
            data_factory.generate_demographics(conn)
            conn.close()
            st.success("Database populated!")
            st.rerun()
    st.stop()

# Navigation tabs
tab_overview, tab_breeding, tab_outbreaks, tab_biosecurity = st.tabs([
    "📊 Metapopulation Overview",
    "🧬 Breeding & Kinship Engine",
    "📈 Outbreak Surveillance Monitor",
    "🛡️ Biosecurity Transfer Guard"
])

# Utility to fetch query results into DataFrame
@st.cache_data(ttl=60)
def run_query(query, params=None):
    conn = get_connection()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

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
    
    # Layout with columns for charts
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
        fig, ax = plt.subplots(figsize=(8, 5))
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
        st.markdown("#### Sanctuary Capacity and Biosecurity Level")
        # Query sanctuary capacities and counts
        q_sanctuary_stats = """
            SELECT 
                s.name, 
                s.type,
                s.capacity,
                s.is_clean_zone,
                COUNT(d.devil_id) AS current_population
            FROM sanctuaries s
            LEFT JOIN devils d ON s.sanctuary_id = d.current_sanctuary_id AND d.status = 'Alive'
            GROUP BY s.sanctuary_id
        """
        df_sanc = run_query(q_sanctuary_stats)
        df_sanc['Fill Rate (%)'] = round((df_sanc['current_population'] / df_sanc['capacity']) * 100, 1)
        
        # Display as a beautiful table with formatted columns
        def highlight_clean(row):
            return ['background-color: #065f46; color: #d1fae5' if row.is_clean_zone else '' for _ in row]
            
        st.dataframe(
            df_sanc.style.apply(highlight_clean, axis=1)
                   .format({"capacity": "{:,}", "current_population": "{:,}", "Fill Rate (%)": "{:.1f}%"}),
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
                cursor.execute(
                    "UPDATE devils SET current_sanctuary_id = %s WHERE devil_id = %s",
                    (selected_sanc_id, selected_devil_id)
                )
                conn.commit()
                
                st.success("🎉 **TRANSFER SUCCESSFUL**")
                st.markdown(f"Devil **#{selected_devil_id} ({selected_devil_info['name']})** has been safely transferred to **{selected_sanc_info['name']}**.")
            except mysql.connector.Error as e:
                # Capture the custom fail-safe error code from the trigger
                st.markdown(f"""
                    <div style="background-color: #7f1d1d; border: 1px solid #dc2626; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;">
                        <h4 style="color: #fca5a5; margin: 0 0 0.5rem 0;">🚫 BIOSECURITY TRANSFER BLOCK (DATABASE REJECTION)</h4>
                        <p style="color: #fca5a5; font-family: monospace; font-size: 0.95rem; margin-bottom: 0.5rem;">{str(e)}</p>
                        <p style="color: #f87171; margin: 0; font-size: 0.9rem;">
                            <strong>Trigger Alert:</strong> The database engine intercepted the transaction natively. The animal's latest health diagnosis is <strong>{selected_devil_info.latest_status} ({selected_devil_info.latest_pcr})</strong>, violating the strict biosecurity quarantine policy of the clean zone <strong>{selected_sanc_info['name']}</strong>.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            finally:
                cursor.close()
                conn.close()
