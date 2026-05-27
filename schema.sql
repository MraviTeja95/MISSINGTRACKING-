-- ============================================================
--  TraceNet – Missing Person Tracking & Crime Pattern Analysis
--  MySQL Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS missing_tracker_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE missing_tracker_db;

-- ── Missing Persons ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS missing_persons (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(120)  NOT NULL,
  age           INT           NOT NULL,
  photo         VARCHAR(255)  DEFAULT NULL COMMENT 'filename under static/uploads/',
  last_seen     VARCHAR(255)  NOT NULL,
  description   TEXT          DEFAULT NULL,
  contact       VARCHAR(120)  DEFAULT NULL,
  status        ENUM('missing','found') DEFAULT 'missing',
  date_reported DATETIME      DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_status (status),
  INDEX idx_date   (date_reported)
) ENGINE=InnoDB;

-- ── Crime Data ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS crime_data (
  id       INT AUTO_INCREMENT PRIMARY KEY,
  location VARCHAR(255) NOT NULL,
  type     VARCHAR(120) NOT NULL,
  severity TINYINT      DEFAULT 1 COMMENT '1=low … 5=high',
  date     DATETIME     DEFAULT CURRENT_TIMESTAMP,
  lat      DOUBLE       DEFAULT NULL,
  lng      DOUBLE       DEFAULT NULL,
  INDEX idx_location (location),
  INDEX idx_type     (type),
  INDEX idx_date     (date)
) ENGINE=InnoDB;

-- ── Sample Data (optional – also inserted automatically via seed_data.py) ─────
-- INSERT INTO crime_data (location, type, severity, date) VALUES
--   ('MG Road',      'Robbery', 4, NOW() - INTERVAL 10 DAY),
--   ('Koramangala',  'Assault', 3, NOW() - INTERVAL 5  DAY),
--   ('Whitefield',   'Theft',   2, NOW() - INTERVAL 2  DAY);
