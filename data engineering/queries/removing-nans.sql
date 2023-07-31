-- ============================LinkedIn============================
UPDATE `data-jobs-analysis-db.data_jobs_analysis_db.linkedin_jobs`
SET
  reqierd_credential = IFNULL(reqierd_credential, 'Not Specified'),
  location_type = CASE
                   WHEN (LOWER(describtion) LIKE '%remote%' OR 
                         LOWER(describtion) LIKE '%from home%') AND
                        (location_type != 'TELECOMMUTE') THEN 'Remote'

                   WHEN (LOWER(describtion) LIKE '%hybrid%') OR
                        (location_type = 'TELECOMMUTE') THEN 'Hybrid'

                   WHEN (LOWER(describtion) LIKE '%office%') OR
                        (LOWER(describtion) LIKE '%in-person%') THEN 'From office'

                   ELSE 'Remote' -- We will set the Non-Specified location type to Remote
                 END
WHERE describtion IS NOT NULL OR describtion IS NULL;


DELETE FROM `data-jobs-analysis-db.data_jobs_analysis_db.linkedin_jobs`
WHERE describtion IS NULL;
-- ================================================================

-- ==============================Guru==============================
UPDATE `data-jobs-analysis-db.data_jobs_analysis_db.guru_profiles`
SET
  feedback = IFNULL(feedback, '0%'),
  earnings_amount = CASE
                     WHEN (earnings_amount IS NULL) OR 
                          (earnings_amount = 'ID Verified') OR
                          (earnings_amount = 'Past Earnings') THEN '0'
                     ELSE earnings_amount
                    END
WHERE name IS NOT NULL;
-- ================================================================

