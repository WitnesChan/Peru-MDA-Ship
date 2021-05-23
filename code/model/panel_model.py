# Models for Panel Data

from datetime import datetime,date
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import statsmodels.api as sm

df_country_ts_dim = pd.read_csv('data/dim_all_country_info.csv', index_col = ['country', 'year'])

df_country_ts_dim['year'] = pd.Categorical(df_country_ts_dim['year.1'])

df_country_ts_dim['log_total_population'] = df_country_ts_dim['total_population'].apply(
    lambda r : np.log(r) if r > 0 else 0
)
df_country_ts_dim['log_gdp_growth_usd'] =  df_country_ts_dim['gdp_growth_usd'].apply(
    lambda r : np.log(r) if r > 0 else 0
)
df_country_ts_dim['log_land_area_sq_km'] =  df_country_ts_dim['land_area_sq_km'].apply(
    lambda r : np.log(r) if r > 0 else 0
)
df_country_ts_dim['log_co2_emission_kt'] =  df_country_ts_dim['co2_emission_kt'].apply(
    lambda r : np.log(r) if r > 0 else 0
)
df_country_ts_dim['log_methane_emission_kt'] =  df_country_ts_dim['methane_emission_kt'].apply(
    lambda r : np.log(r) if r > 0 else 0
)

df_country_ts_dim['temp_mean_l1'] = df_country_ts_dim.groupby(['country.1']).temp_mean.shift(1)
# add new lagged variable : the median tempeature of that that country in last year
df_country_ts_dim['temp_median_l1'] = df_country_ts_dim.groupby(['country.1']).temp_median.shift(1)
# add new lagged variable : 1 : heat wave happened in the last year, 0 :not happened in the last year
df_country_ts_dim['is_hw_happend_l1'] = df_country_ts_dim.groupby(['country.1']).is_hw_happend.shift(1) \
    .apply(lambda r: 1 if r else 0)
