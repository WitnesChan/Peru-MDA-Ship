# Models for Panel Data
from linearmodels.panel import PanelOLS, RandomEffects, BetweenOLS, compare
'''
PanelOLS uses fixed effect (i.e., entity effects) to eliminate the entity specific components.
This is mathematically equivalent to including a dummy variable for each entity,
although the implementation does not do this for performance reasons.
'''
from datetime import datetime,date
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import statsmodels.api as sm



df_country_ts_dim = pd.read_csv('data/dim_all_country_info.csv')
df_country_ts_dim = df_country_ts_dim.set_index( ['country', 'year'], drop =False)
df_country_ts_dim['year'] = pd.Categorical(df_country_ts_dim.year)

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
#%%
df_country_ts_dim.columns

# df_country_ts_dim.to_csv('data/dim_all_country_info.csv')

#%%
sns.scatterplot(x = 'log_methane_emission_kt', y = 'log_co2_emission_kt', data = df_country_ts_dim)
#%%
exog_vars = ['gdp_growth_rate','forest_area_ratio', 'is_hw_happend_l1', 'temp_median_l1',
        'temp_mean_l1', 'log_co2_emission_kt', 'incomeLevel', 'num_of_weather_station']

exog = sm.add_constant(df_country_ts_dim[exog_vars])

mod = BetweenOLS(
    dependent = df_country_ts_dim.HWM,
    exog = exog,
    check_rank=False,
    )
mod.res = mod.fit()
mod.res
#%%


fix_mod = PanelOLS(
        dependent = df_country_ts_dim.HWM,
        exog = exog,
        entity_effects = True, check_rank=False, drop_absorbed=True

        )
fix_res = fix_mod.fit(cov_type='clustered', cluster_entity=True)
print(fix_res)


#%%
