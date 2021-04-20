from linearmodels.datasets import wage_panel
from linearmodels.panel import PooledOLS

from datetime import datetime,date
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

df_country_ts_dim = pd.read_csv('Peru-MDA-Ship/data/dim_all_country_info.csv')


df_country_ts_dim


#%%

exog_vars = ['total_population', 'urban_pop_ratio', 'forest_area_ratio',
       'agri_land_ratio', 'gdp_growth_rate', 'gdp_growth_usd',
       'Unemployment_ratio', 'co2_emission_kt', 'Year']
exog = sm.add_constant(df_country_ts[exog_vars])
mod = PooledOLS(df_country_ts.num_of_heat_waves, exog =exog, check_rank=False)
pooled_res = mod.fit()
print(pooled_res)


#%%

fam = sm.families.Poisson()
ind = sm.cov_struct.Exchangeable()


mod = smf.gee(formula =
    'num_of_heat_waves ~ alpha2_code + Year + total_population + urban_pop_ratio + forest_area_ratio + agri_land_ratio + gdp_growth_rate + gdp_growth_usd + Unemployment_ratio + co2_emission_kt + num_of_heat_waves',
    groups = 'alpha2_code',data = df_country_ts.reset_index(), cov_struct=ind, family=fam)

res = mod.fit()

print(res.summary())
