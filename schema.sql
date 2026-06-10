-- Save the Tasmanian Devil Tracker
-- Database Schema DDL

CREATE DATABASE IF NOT EXISTS `devil_tracker`;
USE `devil_tracker`;

-- Drop tables in reverse order of dependencies to reset schema
DROP TABLE IF EXISTS `health_logs`;
DROP TABLE IF EXISTS `devils`;
DROP TABLE IF EXISTS `strains`;
DROP TABLE IF EXISTS `sanctuaries`;

-- 1. SANCTUARIES
CREATE TABLE IF NOT EXISTS `sanctuaries` (
    `sanctuary_id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `postcode` VARCHAR(10) NOT NULL,
    `type` ENUM('Wild Capture Zone', 'Captive Breeding Facility', 'Island Reserve') NOT NULL,
    `capacity` INT NOT NULL,
    `is_clean_zone` BOOLEAN NOT NULL DEFAULT FALSE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. STRAINS
CREATE TABLE IF NOT EXISTS `strains` (
    `strain_id` INT AUTO_INCREMENT PRIMARY KEY,
    `strain_name` VARCHAR(50) NOT NULL UNIQUE,
    `discovery_year` INT NULL,
    `description` TEXT NULL
) ENGINE=InnoDB;

-- 3. DEVILS
CREATE TABLE IF NOT EXISTS `devils` (
    `devil_id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL,
    `sex` ENUM('M', 'F') NOT NULL,
    `birth_date` DATE NOT NULL,
    `mother_id` INT NULL,
    `father_id` INT NULL,
    `current_sanctuary_id` INT NOT NULL,
    `status` ENUM('Alive', 'Deceased') NOT NULL DEFAULT 'Alive',
    `mhc_allele_1` VARCHAR(20) NULL,
    `mhc_allele_2` VARCHAR(20) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_devils_mother` FOREIGN KEY (`mother_id`) REFERENCES `devils` (`devil_id`) ON DELETE SET NULL,
    CONSTRAINT `fk_devils_father` FOREIGN KEY (`father_id`) REFERENCES `devils` (`devil_id`) ON DELETE SET NULL,
    CONSTRAINT `fk_devils_sanctuary` FOREIGN KEY (`current_sanctuary_id`) REFERENCES `sanctuaries` (`sanctuary_id`) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 4. HEALTH_LOGS
CREATE TABLE IF NOT EXISTS `health_logs` (
    `log_id` INT AUTO_INCREMENT PRIMARY KEY,
    `devil_id` INT NOT NULL,
    `log_date` DATE NOT NULL,
    `weight` DECIMAL(5, 2) NOT NULL,
    `detected_strain_id` INT NOT NULL,
    `bite_scars` INT NOT NULL DEFAULT 0,
    `pcr_result` ENUM('Positive', 'Negative', 'Inconclusive') NOT NULL,
    `notes` TEXT NULL,
    CONSTRAINT `fk_health_logs_devil` FOREIGN KEY (`devil_id`) REFERENCES `devils` (`devil_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_health_logs_strain` FOREIGN KEY (`detected_strain_id`) REFERENCES `strains` (`strain_id`) ON UPDATE CASCADE
) ENGINE=InnoDB;
