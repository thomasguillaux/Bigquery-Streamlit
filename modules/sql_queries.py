"""
Define Parametric Standar SQL queries 
All queries are parametrized with year and state
"""

YEARS = list(range(1990, 2019, 1))

QUERY_POLLUTION = """
    SELECT
      pm10.year as year,
      pm10.month AS month,
      pm10.avg AS pm10,
      pm25_frm.avg AS pm25_frm,
      pm25_nonfrm.avg AS pm25_nonfrm,
      co.avg as co,
      so2.avg as so2,
      lead.avg AS lead
    FROM
      ( SELECT avg(arithmetic_mean) as avg, EXTRACT(MONTH FROM date_local) as month, EXTRACT(YEAR FROM date_local) as year
        FROM `bigquery-public-data.epa_historical_air_quality.pm10_daily_summary`
        WHERE state_name = '%(state)s' and EXTRACT(YEAR FROM date_local) = %(year)d
        GROUP BY year, month
      ) AS pm10
    JOIN
      ( SELECT avg(arithmetic_mean) as avg, EXTRACT(MONTH FROM date_local) as month, EXTRACT(YEAR FROM date_local) as year
        FROM `bigquery-public-data.epa_historical_air_quality.pm25_frm_daily_summary`
        WHERE state_name = '%(state)s' and EXTRACT(YEAR FROM date_local) = %(year)d
        GROUP BY year, month
      ) AS pm25_frm ON pm10.year = pm25_frm.year AND pm10.month = pm25_frm.month
    JOIN
      ( SELECT avg(arithmetic_mean) as avg, EXTRACT(MONTH FROM date_local) as month, EXTRACT(YEAR FROM date_local) as year
        FROM `bigquery-public-data.epa_historical_air_quality.pm25_nonfrm_daily_summary`
        WHERE state_name = '%(state)s' and EXTRACT(YEAR FROM date_local) = %(year)d
        GROUP BY year, month
      ) AS pm25_nonfrm ON pm10.year = pm25_nonfrm.year AND pm10.month = pm25_nonfrm.month
    JOIN
      ( SELECT avg(arithmetic_mean) * 100 as avg, EXTRACT(MONTH FROM date_local) as month, EXTRACT(YEAR FROM date_local) as year
        FROM `bigquery-public-data.epa_historical_air_quality.lead_daily_summary`
        WHERE state_name = '%(state)s' and EXTRACT(YEAR FROM date_local) = %(year)d
        GROUP BY year, month
      ) AS lead ON pm10.year = lead.year AND pm10.month = lead.month
    JOIN
      ( SELECT avg(arithmetic_mean) as avg, EXTRACT(MONTH FROM date_local) as month, EXTRACT(YEAR FROM date_local) as year
        FROM `bigquery-public-data.epa_historical_air_quality.voc_daily_summary`
        WHERE state_name = '%(state)s' and EXTRACT(YEAR FROM date_local) = %(year)d
        GROUP BY year, month
      ) AS co ON pm10.year = co.year AND pm10.month = co.month
    JOIN
      ( SELECT avg(arithmetic_mean) * 10 as avg, EXTRACT(MONTH FROM date_local) as month, EXTRACT(YEAR FROM date_local) as year
        FROM `bigquery-public-data.epa_historical_air_quality.so2_daily_summary`
        WHERE state_name = '%(state)s' and EXTRACT(YEAR FROM date_local) = %(year)d
        GROUP BY year, month
      ) AS so2 ON pm10.year = so2.year AND pm10.month = so2.month
    ORDER BY
      month
"""




QUERY_TEMPERATURE = """
    SELECT
      year,
      mo as month,
      da as day,
      MAX(max) as max_temp,
      MIN(min) as min_temp,
      AVG(temp) as avg_temp,
      state
    FROM
      `bigquery-public-data.noaa_gsod.gsod%(year)s` a
    JOIN
      `bigquery-public-data.noaa_gsod.stations` b
    ON
      a.stn=b.usaf
      AND a.wban=b.wban
    WHERE
      state IS NOT NULL
      AND max < 1000
      AND country = 'US'
      AND state = '%(state)s'
    GROUP BY
      year, month, day, state
    ORDER BY
      year, month, day, state
"""


QUERY_PRCP = """
    SELECT
      EXTRACT(YEAR FROM date) as year,
      EXTRACT(MONTH FROM date) as month,
      EXTRACT(DAY FROM date) as day,
      AVG(prcp) AS prcp
    FROM (
      SELECT
        date AS date,
        IF (element = 'PRCP', value/10, NULL) AS prcp
      FROM
        `bigquery-public-data.ghcn_d.ghcnd_%(year)s` AS weather
      JOIN
        `bigquery-public-data.ghcn_d.ghcnd_stations` as stations
      ON
        weather.id = stations.id
      WHERE
        stations.state = '%(state)s'
    )
    GROUP BY
      year, month, day
    ORDER BY
      year, month, day
"""


"""
Define States mapping
"""

STATES = (
    ('AK', 'Alaska'),
    ('AL', 'Alabama'),
    ('AZ', 'Arizona'),
    ('AR', 'Arkansas'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('CT', 'Connecticut'),
    ('DE', 'Delaware'),
    ('DC', 'District of Columbia'),
    ('FL', 'Florida'),
    ('GA', 'Georgia'),
    ('HI', 'Hawaii'),
    ('ID', 'Idaho'),
    ('IL', 'Illinois'),
    ('IN', 'Indiana'),
    ('IA', 'Iowa'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('LA', 'Louisiana'),
    ('ME', 'Maine'),
    ('MD', 'Maryland'),
    ('MA', 'Massachusetts'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MS', 'Mississippi'),
    ('MO', 'Missouri'),
    ('MT', 'Montana'),
    ('NE', 'Nebraska'),
    ('NV', 'Nevada'),
    ('NH', 'New Hampshire'),
    ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'),
    ('NY', 'New York'),
    ('NC', 'North Carolina'),
    ('ND', 'North Dakota'),
    ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),
    ('OR', 'Oregon'),
    ('PA', 'Pennsylvania'),
    ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'),
    ('SD', 'South Dakota'),
    ('TN', 'Tennessee'),
    ('TX', 'Texas'),
    ('UT', 'Utah'),
    ('VT', 'Vermont'),
    ('VA', 'Virginia'),
    ('WA', 'Washington'),
    ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'),
    ('WY', 'Wyoming'),
)

NAMES = [v for (k, v) in STATES]
CODE_TO_NAMES = {k: v for (k, v) in STATES}
NAMES_TO_CODES = {v: k for (k, v) in STATES}