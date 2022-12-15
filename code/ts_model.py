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



#%%

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



#%% Hodrick-Prescott Filter

hw_cycle, hw_trend = sm.tsa.filters.hpfilter(df_ts_year)
hw_year_decomp = df_ts_year.copy()
hw_year_decomp['hw_cycle'] = hw_cycle
hw_year_decomp['hw_trend'] = hw_trend


hw_year_decomp.plot()

for y in range(1980, 2020):
    plt.axvline(x = str(y), linestyle='--', c ='black', alpha = 0.2)

plt.legend()

#%%
trend.subtract(trend.shift(1) ,axis=0)
#%%
sm.graphics.tsa.plot_pacf(trend.subtract(trend.shift(1) ,axis=0).dropna(), lags=80)
#sm.graphics.tsa.plot_acf(trend.subtract(trend.shift(1) ,axis=0).dropna(), lags=10)

#%% Year
# stl = STL(df_ts_month, period =12, seasonal = 11)

stl = STL(df_ts_year, period = 3)
res = stl.fit()
seasonal, trend, resid = res.seasonal, res.trend, res.resid

plt.figure(figsize=(13,7))
df_ts_year.plot()
trend.plot()
seasonal.plot()
plt.legend()

#%% Month

stl = STL(df_ts_month, period =12)
res = stl.fit()
seasonal, trend, resid = res.seasonal, res.trend, res.resid

plt.figure(figsize=(13,7))
df_ts_month.plot()
trend.plot()
seasonal.plot()
plt.legend()

#%%
trend = df_ts_month.subtract(df_ts_month.shift(12), axis=0).dropna()

trend.plot()

#%% Stationarity and detrending (ADF/KPSS)¶

adf_test(trend)
kpss_test(trend)
kpss_test(trend.subtract(trend.shift(1)).dropna())

#%%

estimated = seasonal + trend

plt.figure(figsize=(14,7))
estimated.plot(label = 'estimated')
plt.plot(df_ts_year, label = 'real')
plt.legend()

#%%

# arma_mod = ARIMA(endog = df_overall_hw_by_year_.subtract(trend, axis =0), order = (3,0,0))
arma_mod = ARIMA(endog = trend, order = (5,1,0))
arma_res = arma_mod.fit()

arma_res.summary()


#%%
plot_predict(arma_res,start='2000', end ='2020')

#%%
# ax1 = (arma_res.predict() + trend).plot(figsize = (13, 7), label = 'estimated')

fig, ax = plt.subplots(figsize=(10,8))
fig = arma_res.predict().plot(ax=ax)
df_overall_hw_by_year_.rename(columns = {'ISO':'real'}).plot(ax =ax)
plt.legend()
