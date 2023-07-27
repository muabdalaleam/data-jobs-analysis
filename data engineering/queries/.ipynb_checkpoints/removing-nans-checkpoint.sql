SELECT *,
       IFNULL(reqierd_credential, 'Not Specified') AS reqierd_credential_1,
       CASE
          WHEN (LOWER(describtion) LIKE '%remote%' OR 
                LOWER(describtion) LIKE '%from home%') AND
               (location_type != 'TELECOMMUTE') THEN 'Remote'

          WHEN (LOWER(describtion) LIKE '%hybrid%') OR
               (location_type = 'TELECOMMUTE') THEN 'Hybrid'

          WHEN (LOWER(describtion) LIKE '%office%') OR
               (LOWER(describtion) LIKE '%in-person%') OR 
               (LOWER(describtion) LIKE '%in-person%') THEN 'From office'
         ELSE 'Remote' -- We will set the Non-Specified locaion type to Remote

       END AS location_type_1
FROM `data-jobs-analysis-db.data_jobs_analysis_db.linkedin_jobs`
WHERE (describtion IS NOT NULL)
LIMIT 500;
