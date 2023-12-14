interaction_query = """
WITH num_engaged_days AS (
    SELECT DISTINCT
    p.maker_guid,
    (TO_CHAR(DATE_TRUNC('month', p.dvce_created_tstamp), 'YYYY-MM')) AS engaged_month,
    COUNT(DISTINCT (TO_CHAR(DATE_TRUNC('day', p.dvce_created_tstamp), 'DD'))) AS engaged_days  
    FROM dwh.dbt_reporting.platform_events p
    GROUP BY p.maker_guid, (TO_CHAR(DATE_TRUNC('month', p.dvce_created_tstamp), 'YYYY-MM'))
)

SELECT 
    m.maker_id,
    acct.account_id,
    (TO_CHAR(DATE_TRUNC('month', a.day_date), 'YYYY-MM')) AS engaged_month,
    ned.engaged_days,
    a.total_engaged_time_in_s / 60 AS total_engaged_time_in_m,
    a.num_unique_interactions,
    a.generic_active_maker,
    a.results_active_maker,
    acct.total_account_arr
FROM "dwh"."dbt_reporting"."active_makers" AS a
LEFT JOIN dwh.dbt_reporting.makers AS m ON a.maker_guid = m.maker_guid
LEFT JOIN dwh.dbt_reporting.accounts AS acct ON acct.account_id = m.account_id
LEFT JOIN num_engaged_days AS ned ON ned.maker_guid = a.maker_guid AND ned.engaged_month = (TO_CHAR(DATE_TRUNC('month', a.day_date), 'YYYY-MM'))

WHERE (TO_CHAR(DATE_TRUNC('month', a.day_date), 'YYYY-MM')) >= '2022-10'
AND LAST_DAY(a.day_date) = a.day_date
AND num_unique_interactions IS NOT NULL
AND total_engaged_time_in_s IS NOT NULL
AND (NOT m.is_attest OR m.is_attest IS NULL)
AND m.has_ever_subscribed = 'true'
AND (acct.account_type <> 'Churned Customer' OR (acct.account_type = 'Churned Customer' AND 
(TO_CHAR(DATE_TRUNC('month', acct.churned_date), 'YYYY-MM')) <= ned.engaged_month))
"""


survey_query = """
WITH survey_count_day AS (
    SELECT DISTINCT
    maker_id,
    (TO_CHAR(DATE_TRUNC('day', purchase_time), 'YYYY-MM-DD')) AS purchase_day,
    COUNT(*) AS daily_total_survey
    FROM dwh.dbt_reporting.surveys
    WHERE status NOT IN ('archived', 'deleted', 'draft') 
    AND purchase_time > '2022-01-01'
    GROUP BY maker_id, (TO_CHAR(DATE_TRUNC('day', purchase_time), 'YYYY-MM-DD'))
),

survey_count_month AS (
    SELECT DISTINCT
    maker_id,
    (TO_CHAR(DATE_TRUNC('month', DATE(purchase_day)), 'YYYY-MM')) AS purchase_month,
    COUNT(*) AS num_days_survey, 
    SUM(daily_total_survey) AS monthly_total_survey
    FROM survey_count_day
    GROUP BY maker_id, (TO_CHAR(DATE_TRUNC('month', DATE(purchase_day)), 'YYYY-MM'))
)

SELECT DISTINCT
    m.maker_id,
    acct.account_id,
    scm.purchase_month,
    scm.num_days_survey,
    scm.monthly_total_survey,
    scd.purchase_day,
    (TO_CHAR(DATE_TRUNC('year', DATE(scd.purchase_day)), 'YYYY')) AS purchase_year,
    acct.total_account_arr
FROM dwh.dbt_reporting.makers m
LEFT JOIN dwh.dbt_reporting.accounts AS acct ON acct.account_id = m.account_id
LEFT JOIN survey_count_day scd ON m.maker_id = scd.maker_id
LEFT JOIN survey_count_month scm ON m.maker_id = scm.maker_id AND (TO_CHAR(DATE_TRUNC('month', DATE(scd.purchase_day)), 'YYYY-MM')) = scm.purchase_month
WHERE scm.purchase_month >= '2022-01'
AND (NOT m.is_attest OR m.is_attest IS NULL)
AND m.has_ever_subscribed = 'true'
AND (acct.account_type <> 'Churned Customer' OR (acct.account_type = 'Churned Customer' AND 
(TO_CHAR(DATE_TRUNC('month', acct.churned_date), 'YYYY-MM')) <= scm.purchase_month))
"""