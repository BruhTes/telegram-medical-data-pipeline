{{
  config(
    materialized='table',
    schema='marts'
  )
}}

WITH date_spine AS (
  SELECT 
    date_series::DATE as date_id
  FROM generate_series(
    '2024-01-01'::DATE,  -- Start date
    CURRENT_DATE + INTERVAL '1 year',  -- End date (1 year from now)
    '1 day'::INTERVAL
  ) as date_series
),

date_attributes AS (
  SELECT 
    date_id,
    -- Basic date attributes
    EXTRACT(YEAR FROM date_id) as year,
    EXTRACT(MONTH FROM date_id) as month,
    EXTRACT(DAY FROM date_id) as day,
    EXTRACT(DOW FROM date_id) as day_of_week,
    EXTRACT(DOY FROM date_id) as day_of_year,
    EXTRACT(WEEK FROM date_id) as week_of_year,
    EXTRACT(QUARTER FROM date_id) as quarter,
    
    -- Month names
    TO_CHAR(date_id, 'Month') as month_name,
    TO_CHAR(date_id, 'Mon') as month_name_short,
    
    -- Day names
    TO_CHAR(date_id, 'Day') as day_name,
    TO_CHAR(date_id, 'Dy') as day_name_short,
    
    -- Fiscal year (assuming fiscal year starts in July)
    CASE 
      WHEN EXTRACT(MONTH FROM date_id) >= 7 
      THEN EXTRACT(YEAR FROM date_id) + 1
      ELSE EXTRACT(YEAR FROM date_id)
    END as fiscal_year,
    
    -- Fiscal quarter
    CASE 
      WHEN EXTRACT(MONTH FROM date_id) IN (7, 8, 9) THEN 1
      WHEN EXTRACT(MONTH FROM date_id) IN (10, 11, 12) THEN 2
      WHEN EXTRACT(MONTH FROM date_id) IN (1, 2, 3) THEN 3
      WHEN EXTRACT(MONTH FROM date_id) IN (4, 5, 6) THEN 4
    END as fiscal_quarter,
    
    -- Business day indicator
    CASE 
      WHEN EXTRACT(DOW FROM date_id) IN (0, 6) THEN FALSE  -- Sunday = 0, Saturday = 6
      ELSE TRUE
    END as is_business_day,
    
    -- Weekend indicator
    CASE 
      WHEN EXTRACT(DOW FROM date_id) IN (0, 6) THEN TRUE
      ELSE FALSE
    END as is_weekend,
    
    -- Month end indicator
    CASE 
      WHEN date_id = (DATE_TRUNC('month', date_id) + INTERVAL '1 month - 1 day')::DATE 
      THEN TRUE
      ELSE FALSE
    END as is_month_end,
    
    -- Quarter end indicator
    CASE 
      WHEN date_id = (DATE_TRUNC('quarter', date_id) + INTERVAL '3 months - 1 day')::DATE
      THEN TRUE
      ELSE FALSE
    END as is_quarter_end,
    
    -- Year end indicator
    CASE 
      WHEN EXTRACT(MONTH FROM date_id) = 12 AND EXTRACT(DAY FROM date_id) = 31
      THEN TRUE
      ELSE FALSE
    END as is_year_end,
    
    -- Ethiopian calendar (approximate conversion)
    -- Note: This is a simplified conversion
    EXTRACT(YEAR FROM date_id) - 7 as ethiopian_year,
    
    -- Season (Northern Hemisphere)
    CASE 
      WHEN EXTRACT(MONTH FROM date_id) IN (12, 1, 2) THEN 'Winter'
      WHEN EXTRACT(MONTH FROM date_id) IN (3, 4, 5) THEN 'Spring'
      WHEN EXTRACT(MONTH FROM date_id) IN (6, 7, 8) THEN 'Summer'
      WHEN EXTRACT(MONTH FROM date_id) IN (9, 10, 11) THEN 'Fall'
    END as season,
    
    -- Current date indicators
    CASE 
      WHEN date_id = CURRENT_DATE THEN TRUE
      ELSE FALSE
    END as is_current_date,
    
    CASE 
      WHEN date_id = CURRENT_DATE - INTERVAL '1 day' THEN TRUE
      ELSE FALSE
    END as is_yesterday,
    
    CASE 
      WHEN date_id = CURRENT_DATE + INTERVAL '1 day' THEN TRUE
      ELSE FALSE
    END as is_tomorrow,
    
    -- Relative date indicators
    CASE 
      WHEN date_id >= CURRENT_DATE - INTERVAL '7 days' THEN TRUE
      ELSE FALSE
    END as is_last_7_days,
    
    CASE 
      WHEN date_id >= CURRENT_DATE - INTERVAL '30 days' THEN TRUE
      ELSE FALSE
    END as is_last_30_days,
    
    CASE 
      WHEN date_id >= CURRENT_DATE - INTERVAL '90 days' THEN TRUE
      ELSE FALSE
    END as is_last_90_days,
    
    CASE 
      WHEN date_id >= CURRENT_DATE - INTERVAL '1 year' THEN TRUE
      ELSE FALSE
    END as is_last_year
    
  FROM date_spine
)

SELECT 
  date_id,
  year,
  month,
  day,
  day_of_week,
  day_of_year,
  week_of_year,
  quarter,
  month_name,
  month_name_short,
  day_name,
  day_name_short,
  fiscal_year,
  fiscal_quarter,
  is_business_day,
  is_weekend,
  is_month_end,
  is_quarter_end,
  is_year_end,
  ethiopian_year,
  season,
  is_current_date,
  is_yesterday,
  is_tomorrow,
  is_last_7_days,
  is_last_30_days,
  is_last_90_days,
  is_last_year,
  CURRENT_TIMESTAMP as created_at
FROM date_attributes
ORDER BY date_id 