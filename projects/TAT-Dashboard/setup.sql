-- ================================================================
--  TAT Dashboard — Run this ONCE in MySQL Workbench
--  Go to: File > Open SQL Script > select this file > click the
--  lightning bolt (Execute) button
-- ================================================================

CREATE DATABASE IF NOT EXISTS tat_dashboard
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE tat_dashboard;

CREATE TABLE IF NOT EXISTS tat_data (
    id                  INT AUTO_INCREMENT PRIMARY KEY,

    -- Week identifier (date of first record in that upload, YYYY-MM-DD)
    week_id             VARCHAR(20)     NOT NULL,

    -- Core fields from your Excel file
    req_number          VARCHAR(100),
    site_name           VARCHAR(100),
    department          VARCHAR(100),
    test_name           VARCHAR(255),
    entry_datetime      DATETIME,
    verify_datetime     DATETIME,
    tat_status          VARCHAR(10),        -- 'Pass' or 'Fail'
    tat_minutes         DECIMAL(10, 2),     -- TAT converted to minutes
    target_tat_minutes  DECIMAL(10, 2),     -- Target TAT in minutes

    -- Audit
    uploaded_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes for fast filtering
    INDEX idx_week_id   (week_id),
    INDEX idx_site      (site_name),
    INDEX idx_dept      (department),
    INDEX idx_status    (tat_status),
    INDEX idx_entry     (entry_datetime)
);

-- Confirm it worked
SELECT 'Database and table created successfully!' AS Status;
