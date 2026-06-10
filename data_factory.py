import os
import random
import datetime
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
import mysql.connector
# pyrefly: ignore [missing-import]
from faker import Faker

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path, override=True)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dhiman@650")
DB_NAME = os.getenv("DB_NAME", "devil_tracker")

fake = Faker()
Faker.seed(42)
random.seed(42)

USE_SQLITE = os.getenv("USE_SQLITE", "False").lower() == "true"

def get_db_connection(include_db=True):
    """Establish a connection to MySQL, falling back to SQLite if it fails."""
    global USE_SQLITE
    if USE_SQLITE:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "devil_tracker.db")
        conn = sqlite3.connect(db_path)
        # Enable foreign keys in SQLite
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
        
    try:
        load_dotenv(dotenv_path, override=True)
        db_host = os.getenv("DB_HOST", "127.0.0.1")
        db_port = int(os.getenv("DB_PORT", 3306))
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "dhiman@650")
        db_name = os.getenv("DB_NAME", "devil_tracker")
        
        config = {
            "host": db_host,
            "port": db_port,
            "user": db_user,
            "password": db_password,
            "autocommit": True
        }
        if include_db:
            config["database"] = db_name
        return mysql.connector.connect(**config)
    except Exception as e:
        print(f"MySQL connection failed: {e}. Falling back to SQLite...")
        USE_SQLITE = True
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "devil_tracker.db")
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

def db_execute(cursor, sql, params=None):
    """Execute a single query, translating placeholder formatting for SQLite if needed."""
    if USE_SQLITE:
        sql = sql.replace("%s", "?")
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)

def db_executemany(cursor, sql, params):
    """Execute batch insert queries, translating placeholder formatting for SQLite if needed."""
    if USE_SQLITE:
        sql = sql.replace("%s", "?")
    cursor.executemany(sql, params)

def init_schema():
    """Execute schema script to initialize the database structure."""
    global USE_SQLITE
    print("Connecting to database to initialize schema...")
    conn = get_db_connection(include_db=False)
    cursor = conn.cursor()
    
    if USE_SQLITE:
        print("Executing schema_sqlite.sql...")
        schema_path = os.path.join(os.path.dirname(__file__), "schema_sqlite.sql")
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        cursor.executescript(schema_sql)
        conn.commit()
    else:
        # Read MySQL schema file
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r") as f:
            schema_sql = f.read()
            
        print("Executing schema.sql statements on MySQL...")
        for statement in schema_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)
                
        # Also initialize the biosecurity trigger for MySQL
        print("Creating biosecurity trigger...")
        cursor.execute("DROP TRIGGER IF EXISTS before_devil_transfer")
        
        trigger_sql = """
        CREATE TRIGGER before_devil_transfer
        BEFORE UPDATE ON devils
        FOR EACH ROW
        BEGIN
            DECLARE new_is_clean BOOLEAN;
            DECLARE latest_strain_id INT;
            DECLARE latest_pcr VARCHAR(20);
            
            -- Check if the destination sanctuary is a clean zone
            SELECT is_clean_zone INTO new_is_clean
            FROM sanctuaries
            WHERE sanctuary_id = NEW.current_sanctuary_id;
            
            -- Only perform biosecurity checks if the location is changing
            IF NEW.current_sanctuary_id <> OLD.current_sanctuary_id THEN
                -- Check if target sanctuary is a clean zone
                IF new_is_clean = TRUE THEN
                    -- Get the latest health log for the devil being moved
                    SELECT detected_strain_id, pcr_result INTO latest_strain_id, latest_pcr
                    FROM health_logs
                    WHERE devil_id = NEW.devil_id
                    ORDER BY log_date DESC, log_id DESC
                    LIMIT 1;
                    
                    -- If the latest log is positive for any disease strain (DFT1/DFT2), abort the transfer
                    IF latest_strain_id <> 1 OR latest_pcr = 'Positive' THEN
                        SIGNAL SQLSTATE '45000'
                        SET MESSAGE_TEXT = 'Biosecurity Breach: Cannot transfer DFTD-positive or symptomatic animal to a clean insurance sanctuary.';
                    END IF;
                END IF;
            END IF;
        END
        """
        cursor.execute(trigger_sql)
            
    cursor.close()
    conn.close()
    print("Schema initialized successfully.")

def populate_static_data(conn):
    """Populate sanctuaries and strains tables."""
    cursor = conn.cursor()
    
    # Strains
    strains_data = [
        ("Healthy", None, "No active DFTD symptoms detected. General baseline health."),
        ("DFT1", 1996, "Devil Facial Tumor Disease Strain 1. Widespread across Tasmania since 1996."),
        ("DFT2", 2014, "Devil Facial Tumor Disease Strain 2. Discovered in 2014, geographically restricted to Channel region.")
    ]
    db_executemany(
        cursor,
        "INSERT INTO strains (strain_name, discovery_year, description) VALUES (%s, %s, %s)",
        strains_data
    )
    
    # Sanctuaries
    # Format: (name, postcode, type, capacity, is_clean_zone)
    sanctuaries_data = [
        # Clean sanctuaries (is_clean_zone = True)
        ("Maria Island Reserve", "7190", "Island Reserve", 500, True),
        ("Bonorong Wildlife Sanctuary", "7030", "Captive Breeding Facility", 300, True),
        ("Devils@Cradle", "7306", "Captive Breeding Facility", 250, True),
        
        # Channel / D'Entrecasteaux postcodes (DFT2 region)
        ("D'Entrecasteaux Channel Peninsula", "7112", "Wild Capture Zone", 800, False),
        ("Bruny Island Sanctuary", "7150", "Island Reserve", 600, False),
        ("Kettering Wild Reserve", "7155", "Wild Capture Zone", 400, False),
        
        # General Tasmanian locations (DFT1 and Healthy only)
        ("Mount William National Park", "7264", "Wild Capture Zone", 1000, False),
        ("Savage River National Park", "7321", "Wild Capture Zone", 1200, False),
        ("Freycinet Peninsula Zone", "7215", "Wild Capture Zone", 900, False),
        ("Tasmanian Devil Unzoo", "7179", "Captive Breeding Facility", 200, False)
    ]
    db_executemany(
        cursor,
        "INSERT INTO sanctuaries (name, postcode, type, capacity, is_clean_zone) VALUES (%s, %s, %s, %s, %s)",
        sanctuaries_data
    )
    
    conn.commit()
    cursor.close()
    print("Static data populated (Strains, Sanctuaries).")

def generate_demographics(conn=None):
    """Generate devils and health logs data."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    cursor = conn.cursor()
    
    # Get strains
    cursor.execute("SELECT strain_id, strain_name FROM strains")
    strains = {name: sid for (sid, name) in cursor.fetchall()}
    
    # Get sanctuaries
    cursor.execute("SELECT sanctuary_id, postcode, is_clean_zone FROM sanctuaries")
    sanctuaries = cursor.fetchall()
    cursor.close()
    
    # Lists for generation
    # Separate sanctuaries by characteristics
    clean_sanc_ids = [s[0] for s in sanctuaries if s[2]]
    channel_sanc_ids = [s[0] for s in sanctuaries if s[1] in ["7112", "7150", "7155"] and not s[2]]
    general_sanc_ids = [s[0] for s in sanctuaries if s[1] not in ["7112", "7150", "7155"] and not s[2]]
    
    all_sanc_ids = [s[0] for s in sanctuaries]
    
    # We will generate devils in 4 cohorts to establish parental links cleanly.
    # Cohort 1: Born 2010 - 2014 (unknown parents)
    # Cohort 2: Born 2015 - 2018 (parents from Cohort 1)
    # Cohort 3: Born 2019 - 2022 (parents from Cohort 1 & 2)
    # Cohort 4: Born 2023 - 2026 (parents from Cohort 2 & 3)
    
    devils_db = [] # List of dicts describing each devil: birth, death, infection, etc.
    
    cohort_dates = [
        (datetime.date(2010, 1, 1), datetime.date(2014, 12, 31)),
        (datetime.date(2015, 1, 1), datetime.date(2018, 12, 31)),
        (datetime.date(2019, 1, 1), datetime.date(2022, 12, 31)),
        (datetime.date(2023, 1, 1), datetime.date(2026, 4, 30))
    ]
    
    current_date = datetime.date(2026, 6, 10)
    
    # Track devils by cohort for parenting
    cohort_devils = {0: [], 1: [], 2: [], 3: []}
    
    # Total devils target: 9,000
    cohort_sizes = [2000, 2500, 2500, 2000]
    
    global_devil_id = 1
    
    for c_idx, (start_date, end_date) in enumerate(cohort_dates):
        size = cohort_sizes[c_idx]
        print(f"Generating Cohort {c_idx+1} ({size} devils)...")
        
        for _ in range(size):
            devil_id = global_devil_id
            global_devil_id += 1
            
            name = fake.first_name()
            sex = random.choice(["M", "F"])
            
            # Generate birth date
            days_between = (end_date - start_date).days
            birth_date = start_date + datetime.timedelta(days=random.randint(0, days_between))
            
            # Parent assignment
            mother_id = None
            father_id = None
            
            if c_idx > 0:
                # Determine candidate parents from previous cohorts
                parent_cohorts = []
                if c_idx == 1:
                    parent_cohorts = [0]
                elif c_idx == 2:
                    parent_cohorts = [0, 1]
                elif c_idx == 3:
                    parent_cohorts = [1, 2]
                
                candidates = []
                for pc in parent_cohorts:
                    candidates.extend(cohort_devils[pc])
                
                # Filter candidates by age (must be born at least 540 days / 1.5 years before)
                females = [d for d in candidates if d["sex"] == "F" and (birth_date - d["birth_date"]).days >= 540]
                males = [d for d in candidates if d["sex"] == "M" and (birth_date - d["birth_date"]).days >= 540]
                
                # 60% chance to assign parents if candidates exist
                if females and random.random() < 0.7:
                    mother_id = random.choice(females)["devil_id"]
                if males and random.random() < 0.7:
                    father_id = random.choice(males)["devil_id"]
            
            # Sanctuary assignment
            # 15% clean zones, 35% channel zones, 50% general zones
            r_val = random.random()
            if r_val < 0.15:
                sanctuary_id = random.choice(clean_sanc_ids)
            elif r_val < 0.50:
                sanctuary_id = random.choice(channel_sanc_ids)
            else:
                sanctuary_id = random.choice(general_sanc_ids)
            
            # Determine infection logic
            # Clean sanctuaries cannot have infections
            is_in_clean = sanctuary_id in clean_sanc_ids
            
            # Probability of getting infected over lifetime
            # Captive facilities in general have lower infection rate than wild zones
            # Wild zones have higher rate. Let's make average infection rate 30% for wild/non-clean
            is_infected = False
            infection_strain = "Healthy"
            infection_date = None
            
            if not is_in_clean and random.random() < 0.35:
                is_infected = True
                # Strains details:
                # DFT2 is only in Channel postcodes and only after 2014
                is_channel = sanctuary_id in channel_sanc_ids
                if is_channel and birth_date.year >= 2014 and random.random() < 0.5:
                    infection_strain = "DFT2"
                else:
                    # DFT1 is widespread since 1996, so anyone not in clean zone can get it
                    infection_strain = "DFT1"
                
                # Infection age: typically gets infected after reaching maturity (1.5 - 3 years old)
                infection_age_days = random.randint(540, 1000)
                infection_date = birth_date + datetime.timedelta(days=infection_age_days)
                
                # Make sure infection_date doesn't exceed current date (2026-06-10)
                if infection_date >= current_date:
                    # Not infected yet, or infection in future (reset to healthy)
                    is_infected = False
                    infection_strain = "Healthy"
                    infection_date = None
            
            # Life expectancy & Death date
            # Natural life expectancy: 4 to 6 years (1460 to 2190 days)
            natural_lifespan_days = random.randint(1460, 2190)
            death_date = birth_date + datetime.timedelta(days=natural_lifespan_days)
            
            if is_infected:
                # Infected devils die in 6 to 12 months after diagnosis/infection
                disease_survival_days = random.randint(180, 365)
                death_date = infection_date + datetime.timedelta(days=disease_survival_days)
            
            # Status determination
            # If death_date is before current date, devil is Deceased
            if death_date < current_date:
                status = "Deceased"
            else:
                status = "Alive"
                death_date = None # Still alive, no death date
                
            # MHC Allele generation based on genetic inheritance
            MHC_ALLELES = ["Saha-I*01", "Saha-I*02", "Saha-I*03", "Saha-I*04", "Saha-I*05", "Saha-I*06"]
            if mother_id:
                mhc_1 = random.choice([devils_db[mother_id - 1]["mhc_allele_1"], devils_db[mother_id - 1]["mhc_allele_2"]])
            else:
                mhc_1 = random.choice(MHC_ALLELES)
                
            if father_id:
                mhc_2 = random.choice([devils_db[father_id - 1]["mhc_allele_1"], devils_db[father_id - 1]["mhc_allele_2"]])
            else:
                mhc_2 = random.choice(MHC_ALLELES)
                
            devil_info = {
                "devil_id": devil_id,
                "name": name,
                "sex": sex,
                "birth_date": birth_date,
                "mother_id": mother_id,
                "father_id": father_id,
                "current_sanctuary_id": sanctuary_id,
                "status": status,
                "is_infected": is_infected,
                "infection_strain": infection_strain,
                "infection_date": infection_date,
                "death_date": death_date,
                "mhc_allele_1": mhc_1,
                "mhc_allele_2": mhc_2
            }
            
            cohort_devils[c_idx].append(devil_info)
            devils_db.append(devil_info)
            
    print("Devils metadata generated. Inserting devils into database...")
    
    # Bulk insert devils
    cursor = conn.cursor()
    insert_devil_sql = """
    INSERT INTO devils (devil_id, name, sex, birth_date, mother_id, father_id, current_sanctuary_id, status, mhc_allele_1, mhc_allele_2)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Prepare batch data
    devils_data = [
        (d["devil_id"], d["name"], d["sex"], d["birth_date"], d["mother_id"], d["father_id"], d["current_sanctuary_id"], d["status"], d["mhc_allele_1"], d["mhc_allele_2"])
        for d in devils_db
    ]
    
    # Insert in chunks of 2000
    chunk_size = 2000
    for i in range(0, len(devils_data), chunk_size):
        db_executemany(cursor, insert_devil_sql, devils_data[i:i+chunk_size])
    
    conn.commit()
    print(f"Successfully inserted {len(devils_db)} devils.")
    
    # Now generate Health Logs for all devils
    print("Generating Health Logs...")
    health_logs_data = []
    
    log_id_counter = 1
    
    for d in devils_db:
        # Determine log timeline
        # Start logging at 6 months of age, repeat every 180 days (6 months)
        log_start_date = d["birth_date"] + datetime.timedelta(days=180)
        log_end_date = d["death_date"] if d["death_date"] else current_date
        
        curr_log_date = log_start_date
        
        while curr_log_date <= log_end_date:
            # Determine weight based on age and sex
            age_days = (curr_log_date - d["birth_date"]).days
            
            # Check if this log date is after infection
            is_log_infected = d["is_infected"] and curr_log_date >= d["infection_date"]
            
            # Base weight calculation
            if age_days < 365: # Juvenile
                base_weight = random.uniform(1.5, 4.5)
            else: # Adult
                if d["sex"] == "F":
                    base_weight = random.uniform(5.0, 9.0)
                else:
                    base_weight = random.uniform(8.0, 14.0)
            
            # Wasting away effect from disease
            if is_log_infected:
                # How long has the devil been infected?
                infected_duration = (curr_log_date - d["infection_date"]).days
                # Weight drops up to 25% near death
                weight_loss_factor = min(0.25, (infected_duration / 365.0) * 0.25)
                base_weight = base_weight * (1.0 - weight_loss_factor)
                
            weight = round(base_weight, 2)
            
            # Strain and PCR
            if is_log_infected:
                detected_strain_id = strains[d["infection_strain"]]
                pcr_result = "Positive"
                # More bite scars if active/infected
                bite_scars = random.randint(2, 6)
                notes = f"DFTD symptoms visible. Lesions around face and neck. Tumor load severe."
            else:
                detected_strain_id = strains["Healthy"]
                # 98% Negative, 2% Inconclusive (simulating testing noise)
                pcr_result = "Negative" if random.random() < 0.98 else "Inconclusive"
                # Captive/clean zones have fewer bites
                is_clean = d["current_sanctuary_id"] in clean_sanc_ids
                bite_scars = random.randint(0, 1) if is_clean else random.randint(0, 3)
                notes = "Animal active, alert. No signs of facial tumors."
                
            health_logs_data.append((
                log_id_counter,
                d["devil_id"],
                curr_log_date,
                weight,
                detected_strain_id,
                bite_scars,
                pcr_result,
                notes
            ))
            log_id_counter += 1
            
            # Increment by 180 days for next log
            curr_log_date += datetime.timedelta(days=180)
            
        # Ensure we always add a log on the exact infection date if they are infected
        # (This makes tracing outbreak timestamps very clean for window functions)
        if d["is_infected"] and d["infection_date"] <= current_date:
            # Check if we already logged close to infection date, otherwise insert one
            # We can force a log at infection_date + 7 days as the first positive test
            test_date = d["infection_date"] + datetime.timedelta(days=7)
            if test_date <= current_date:
                # Check weight again
                if (test_date - d["birth_date"]).days < 365:
                    w = round(random.uniform(2.0, 4.0), 2)
                else:
                    w = round(random.uniform(5.0, 8.5) if d["sex"] == "F" else random.uniform(8.0, 13.0), 2)
                
                health_logs_data.append((
                    log_id_counter,
                    d["devil_id"],
                    test_date,
                    w,
                    strains[d["infection_strain"]],
                    random.randint(3, 5),
                    "Positive",
                    f"First positive diagnostic confirmation of {d['infection_strain']} via PCR."
                ))
                log_id_counter += 1
                
    print(f"Health logs metadata generated. Total logs: {len(health_logs_data)}")
    
    # Bulk insert health logs
    insert_log_sql = """
    INSERT INTO health_logs (log_id, devil_id, log_date, weight, detected_strain_id, bite_scars, pcr_result, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for i in range(0, len(health_logs_data), chunk_size):
        db_executemany(cursor, insert_log_sql, health_logs_data[i:i+chunk_size])
        
    conn.commit()
    cursor.close()
    print(f"Successfully inserted {len(health_logs_data)} health logs.")
    if close_conn:
        conn.close()
    print("Database populate complete!")
 
if __name__ == "__main__":
    init_schema()
    conn = get_db_connection()
    populate_static_data(conn)
    generate_demographics(conn)
    conn.close()
