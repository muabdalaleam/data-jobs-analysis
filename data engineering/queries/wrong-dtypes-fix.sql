-- ==========================Upwork===========================

CREATE OR REPLACE TABLE `data-jobs-analysis-db.data_jobs_analysis_db.upwork_profiles_temp`
AS
SELECT *,
  STRUCT(
    -- Collecting the numric data from the text data using REGEXP
    CASE
      WHEN LOWER(earnings_amount) LIKE '%k%' THEN CAST(REGEXP_REPLACE(earnings_amount, '[^0-9]', '') AS INT64) * 1000
      WHEN LOWER(earnings_amount) LIKE '%m%' THEN CAST(REGEXP_REPLACE(earnings_amount, '[^0-9]', '') AS INT64) * 1000000
      ELSE CAST(REGEXP_REPLACE(earnings_amount, '[^0-9]', '') AS INT64)
    END                                          AS earnings_amount_new,

    CAST(REPLACE(hour_rate, '$', '') AS FLOAT64) AS hour_rate_new
  ) AS new_columns

FROM `data-jobs-analysis-db.data_jobs_analysis_db.upwork_profiles`;

ALTER TABLE `data-jobs-analysis-db.data_jobs_analysis_db.upwork_profiles_temp`
  DROP COLUMN earnings_amount,
  DROP COLUMN hour_rate;

-- Copy data from temporary table to the main table with the desired schema
CREATE OR REPLACE TABLE `data-jobs-analysis-db.data_jobs_analysis_db.upwork_profiles`
AS
SELECT
  *,
  new_columns.earnings_amount_new AS earnings_amount_new,
  new_columns.hour_rate_new AS hour_rate_new
  
FROM `data-jobs-analysis-db.data_jobs_analysis_db.upwork_profiles_temp`;

-- Drop the temporary table
DROP TABLE `data-jobs-analysis-db.data_jobs_analysis_db.upwork_profiles_temp`;
-- ============================================================



-- ===========================Guru=============================
CREATE OR REPLACE TABLE `data-jobs-analysis-db.data_jobs_analysis_db.guru_profiles_temp`
AS
SELECT *,
  STRUCT(
    CAST(REGEXP_REPLACE(earnings_amount,        '[^0-9]', '') AS INT64)   AS earnings_amount_new,
    CAST(REGEXP_REPLACE(LEFT(hour_rate, 10),    '[^0-9]', '') AS FLOAT64) AS hour_rate_new,
    CAST(REGEXP_REPLACE(feedback,               '[^0-9]', '') AS FLOAT64) AS feedback_new
) AS new_columns

FROM `data-jobs-analysis-db.data_jobs_analysis_db.guru_profiles`;


ALTER TABLE `data-jobs-analysis-db.data_jobs_analysis_db.guru_profiles_temp`
  DROP COLUMN earnings_amount,
  DROP COLUMN hour_rate,
  DROP COLUMN feedback;

-- Copy data from temporary table to the main table with the desired schema
CREATE OR REPLACE TABLE `data-jobs-analysis-db.data_jobs_analysis_db.guru_profiles`
AS
SELECT
  *,
  new_columns.earnings_amount_new AS earnings_amount_new,
  new_columns.hour_rate_new AS hour_rate_new,
  new_columns.feedback_new AS feedback_new

FROM `data-jobs-analysis-db.data_jobs_analysis_db.guru_profiles_temp`;

-- Drop the temporary table
DROP TABLE `data-jobs-analysis-db.data_jobs_analysis_db.guru_profiles_temp`;
-- ===========================================================