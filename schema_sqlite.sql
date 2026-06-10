-- Save the Tasmanian Devil Tracker
-- SQLite Schema DDL (Fallback Mode)

-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS health_logs;
DROP TABLE IF EXISTS devils;
DROP TABLE IF EXISTS strains;
DROP TABLE IF EXISTS sanctuaries;

-- 1. SANCTUARIES
CREATE TABLE IF NOT EXISTS sanctuaries (
    sanctuary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    postcode TEXT NOT NULL,
    type TEXT CHECK(type IN ('Wild Capture Zone', 'Captive Breeding Facility', 'Island Reserve')) NOT NULL,
    capacity INTEGER NOT NULL,
    is_clean_zone INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. STRAINS
CREATE TABLE IF NOT EXISTS strains (
    strain_id INTEGER PRIMARY KEY AUTOINCREMENT,
    strain_name TEXT NOT NULL UNIQUE,
    discovery_year INTEGER NULL,
    description TEXT NULL
);

-- 3. DEVILS
CREATE TABLE IF NOT EXISTS devils (
    devil_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sex TEXT CHECK(sex IN ('M', 'F')) NOT NULL,
    birth_date TEXT NOT NULL,
    mother_id INTEGER NULL,
    father_id INTEGER NULL,
    current_sanctuary_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('Alive', 'Deceased')) NOT NULL DEFAULT 'Alive',
    mhc_allele_1 TEXT NULL,
    mhc_allele_2 TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mother_id) REFERENCES devils (devil_id) ON DELETE SET NULL,
    FOREIGN KEY (father_id) REFERENCES devils (devil_id) ON DELETE SET NULL,
    FOREIGN KEY (current_sanctuary_id) REFERENCES sanctuaries (sanctuary_id) ON UPDATE CASCADE
);

-- 4. HEALTH_LOGS
CREATE TABLE IF NOT EXISTS health_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    devil_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    weight REAL NOT NULL,
    detected_strain_id INTEGER NOT NULL,
    bite_scars INTEGER NOT NULL DEFAULT 0,
    pcr_result TEXT CHECK(pcr_result IN ('Positive', 'Negative', 'Inconclusive')) NOT NULL,
    notes TEXT NULL,
    FOREIGN KEY (devil_id) REFERENCES devils (devil_id) ON DELETE CASCADE,
    FOREIGN KEY (detected_strain_id) REFERENCES strains (strain_id) ON UPDATE CASCADE
);

-- 5. BIOSECURITY TRIGGER (SQLite native)
CREATE TRIGGER IF NOT EXISTS before_devil_transfer
BEFORE UPDATE OF current_sanctuary_id ON devils
FOR EACH ROW
WHEN NEW.current_sanctuary_id <> OLD.current_sanctuary_id
BEGIN
    SELECT RAISE(ABORT, 'Biosecurity Breach: Cannot transfer DFTD-positive or symptomatic animal to a clean insurance sanctuary.')
    WHERE (SELECT is_clean_zone FROM sanctuaries WHERE sanctuary_id = NEW.current_sanctuary_id) = 1
      AND (
          SELECT (detected_strain_id <> 1 OR pcr_result = 'Positive')
          FROM health_logs 
          WHERE devil_id = NEW.devil_id
          ORDER BY log_date DESC, log_id DESC
          LIMIT 1
      ) = 1;
END;
