-- Save the Tasmanian Devil Tracker
-- Advanced SQL Programming Showcase

USE `devil_tracker`;

-- =====================================================================
-- A. The Kinship & Inbreeding Prevention Engine
-- =====================================================================
-- Walks back 3 generations to find shared ancestors and degree of kinship
-- between a target female (mother candidate) and male (father candidate).
-- Example targets: @female_id = 2050, @male_id = 2088

-- To run this, define variables (or replace placeholders in application)
SET @female_id = 2500;
SET @male_id = 2501;

WITH RECURSIVE Ancestry AS (
    -- Anchor member: Start with both candidate parents
    SELECT 
        devil_id, 
        mother_id, 
        father_id, 
        name,
        0 AS generation,
        devil_id AS lineage_start
    FROM devils
    WHERE devil_id IN (@female_id, @male_id)
    
    UNION ALL
    
    -- Recursive member: Walk back through lineage
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
-- Find overlapping ancestors
SELECT 
    a.devil_id AS shared_ancestor_id,
    a.name AS shared_ancestor_name,
    a.generation AS female_side_gen,
    b.generation AS male_side_gen,
    (a.generation + b.generation) AS degree_of_relationship,
    -- Simple Kinship Coefficient approximation: sum(0.5 ^ (gen_female + gen_male + 1))
    POWER(0.5, a.generation + b.generation + 1) AS inbreeding_risk_contribution
FROM Ancestry a
INNER JOIN Ancestry b ON a.devil_id = b.devil_id
WHERE a.lineage_start = @female_id 
  AND b.lineage_start = @male_id;


-- =====================================================================
-- B. The Outbreak Surveillance Monitor
-- =====================================================================
-- Analyzes positive cases grouped by regional postcode, calculates intervals in days,
-- and flags postcodes where the disease transmission interval is rapidly shrinking.

WITH PositiveDiagnoses AS (
    SELECT 
        hl.log_date,
        s.postcode,
        s.name AS sanctuary_name,
        d.devil_id,
        d.name AS devil_name,
        st.strain_name,
        -- Get the previous diagnosis date in the same postcode region
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
        -- Get a moving average of the last 3 case intervals to establish regional transmission pace
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
ORDER BY postcode, log_date DESC;


-- =====================================================================
-- C. The Sanctuary Biosecurity Guard (Trigger)
-- =====================================================================
-- Halts updates that transfer infected animals into clean sanctuaries.

DROP TRIGGER IF EXISTS before_devil_transfer;

DELIMITER //

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
END //

DELIMITER ;
