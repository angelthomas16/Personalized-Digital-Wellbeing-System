USE hive_test;

CREATE EXTERNAL TABLE IF NOT EXISTS daily_wellbeing (
    record_id STRING,
    user_id STRING,
    record_date STRING,
    day_index INT,
    day_of_week STRING,
    is_weekend INT,
    daily_screen_time_hours DOUBLE,
    social_media_hours DOUBLE,
    gaming_hours DOUBLE,
    work_study_hours DOUBLE,
    sleep_hours DOUBLE,
    notifications_per_day DOUBLE,
    app_opens_per_day DOUBLE,
    physical_activity_minutes INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/ashlin/digital_wellbeing'
TBLPROPERTIES ('skip.header.line.count'='1');

SHOW TABLES;

DESCRIBE daily_wellbeing;

SELECT COUNT(*) AS total_records
FROM daily_wellbeing;

SELECT COUNT(DISTINCT user_id) AS total_users
FROM daily_wellbeing;

SELECT MIN(record_date) AS first_date,
       MAX(record_date) AS last_date
FROM daily_wellbeing;

SELECT
    ROUND(AVG(daily_screen_time_hours), 2) AS avg_screen_time,
    ROUND(AVG(social_media_hours), 2) AS avg_social_media,
    ROUND(AVG(gaming_hours), 2) AS avg_gaming,
    ROUND(AVG(sleep_hours), 2) AS avg_sleep,
    ROUND(AVG(physical_activity_minutes), 2) AS avg_activity
FROM daily_wellbeing;

SELECT
    CASE
        WHEN is_weekend = 1 THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(*) AS total_records,
    ROUND(AVG(daily_screen_time_hours), 2) AS avg_screen_time,
    ROUND(AVG(sleep_hours), 2) AS avg_sleep,
    ROUND(AVG(physical_activity_minutes), 2) AS avg_activity
FROM daily_wellbeing
GROUP BY is_weekend;

SELECT
    user_id,
    record_date,
    daily_screen_time_hours,
    sleep_hours
FROM daily_wellbeing
WHERE daily_screen_time_hours > 6
  AND sleep_hours < 6
ORDER BY daily_screen_time_hours DESC
LIMIT 20;
-- Personalised average screen time and sleep for each user
SELECT
    user_id,
    AVG(daily_screen_time_hours) AS personal_avg_screen_time,
    AVG(sleep_hours) AS personal_avg_sleep
FROM daily_wellbeing
GROUP BY user_id
LIMIT 10;
