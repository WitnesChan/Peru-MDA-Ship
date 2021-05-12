import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_predict
from statsmodels.tsa.seasonal import STL, seasonal_decompose
from statsmodels.tsa.stattools import adfuller, kpss


def adf_test(timeseries):
    print ('Results of Dickey-Fuller Test:')
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
       dfoutput['Critical Value (%s)'%key] = value
    print (dfoutput)

def kpss_test(timeseries):
    print ('Results of KPSS Test:')
    kpsstest = kpss(timeseries, regression='c', nlags="auto")
    kpss_output = pd.Series(kpsstest[0:3], index=['Test Statistic','p-value','Lags Used'])
    for key,value in kpsstest[3].items():
        kpss_output['Critical Value (%s)'%key] = value
    print (kpss_output)

def hp_filter_decomp(df_ts):

    # Hodrick-Prescott Filter
    hw_cycle, hw_trend = sm.tsa.filters.hpfilter(df_ts)
    hw_year_decomp = df_ts.copy()
    hw_year_decomp['cycle'] = hw_cycle
    hw_year_decomp['trend'] = hw_trend
    hw_year_decomp.plot()

    for y in range(1980, 2020):
        plt.axvline(x = str(y), linestyle='--', c ='black', alpha = 0.2)

    plt.legend()

def stl_decomp(df_ts, period = 5, plot_seasonal = True):
    stl = STL(df_ts, period = period)
    res = stl.fit()
    seasonal, trend, resid = res.seasonal, res.trend, res.resid
    estimated = seasonal + trend

    plt.figure(figsize=(13,7))
    df_ts.plot()
    trend.plot()
    estimated.plot(label ='estimated')
    if(plot_seasonal):
        seasonal.plot()
    plt.legend()

os.chdir('/Users/witnes/Workspace/MDA/Peru-MDA-Ship')

# %%

df_country_ts_dim = pd.read_csv('data/dim_all_country_info.csv',
    index_col = ['country', 'year']
    )



# %%
## Frequency
df_hwd_ts = df_country_ts_dim.groupby(['year'])['HWN'].sum()
stl_decomp(df_ts= df_hwd_ts, period = 4)
# %%
## Duration (Total days of Heat Waves)

df_hwf_ts = df_country_ts_dim.groupby(['year'])['HWF'].sum()
stl_decomp(df_ts= df_hwf_ts, period = 4)

# %%
## Duration (Longest days of Heat Waves)
df_hwd_ts = df_country_ts_dim.groupby(['year'])['HWD'].max()
stl_decomp(df_ts= df_hwd_ts, period = 4)
# %%
## Intensity (Hottest day of hottest yearly event)
df_hwa_ts = df_country_ts_dim.groupby(['year'])['HWA'].max()
stl_decomp(df_ts= df_hwa_ts, period = 4, plot_seasonal = False)

# %%
## Intensity (average magnitude of all yearly heat waves)
df_hwm_ts = df_country_ts_dim.groupby(['year'])['HWM'].max()
stl_decomp(df_ts= df_hwa_ts, period = 4, plot_seasonal = False)

# %%
df_country_ts_dim.info()
# %%

obs_start = '1980-01'
obs_end = '2020-01'

df_ts_month = pd.merge(
    left = pd.DataFrame(
        index = pd.date_range(start= obs_start, end = obs_end, freq='M').to_period('M')
    ),
    right = df_heat_wave[df_heat_wave.Continent.isin(['Asia', 'Europe'])]\
        .groupby('start_year_month')['ISO'].count().rename('num_of_heat_waves'),
    how = 'left',
    left_index = True, right_index= True
).fillna(0)

df_ts_year = pd.merge(
    left = pd.DataFrame(
        index = pd.date_range(start= obs_start, end = obs_end, freq='Y').to_period('Y').astype(str)
    ),
    right = df_heat_wave[df_heat_wave.Continent.isin(['Asia', 'Europe'])]\
        .groupby(df_heat_wave['Year'].astype(str))['ISO'].count()\
        .rename('num_of_heat_waves'),
    how = 'left',
    left_index = True, right_index= True
).fillna(0)

df_ts_month.plot()
df_ts_year.plot()

for y in range(1980, 2020):
    plt.axvline(x = str(y), linestyle='--', c ='black', alpha = 0.2)

# %%

sm.graphics.tsa.plot_pacf(trend.subtract(trend.shift(1) ,axis=0).dropna(), lags=80)
#sm.graphics.tsa.plot_acf(trend.subtract(trend.shift(1) ,axis=0).dropna(), lags=10)

# %%

arma_mod = ARIMA(endog = trend, order = (5,1,0))
arma_res = arma_mod.fit()

arma_res.summary()

plot_predict(arma_res,start='2000', end ='2020')
