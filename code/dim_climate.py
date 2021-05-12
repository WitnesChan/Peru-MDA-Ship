
from meteostat import Point, Daily, Stations
from datetime import datetime,date
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

sns.set(rc={'figure.figsize':(12,7)})
pd.set_option("display.max_rows", 300)
pd.set_option("display.max_columns", 30)


def fetch_country_daily_temperature(country, start_date, end_date, num_of_stations):

    stations = list(
        Stations().region(country).fetch(num_of_stations).index
        )
    if '02956' in stations:
        stations.remove('02956')
    if '68040' in stations:
        stations.remove('68040')
    if '68240' in stations:
        stations.remove('68240')
    if '68038' in stations:
        stations.remove('68038')
    if 'ZMUB0' in stations:
        stations.remove('ZMUB0')
    if '91737' in stations:
        stations.remove('91737')
    if 'KQRC0' in stations:
        stations.remove('KQRC0')

    df_temp_data = Daily(stations, start_date, end_date).fetch()

    df_temp_data['country'] = country
    return df_temp_data[['country','tmax','tmin','tavg','pres']]


def fetch_country_month_temperature(country, start_date, end_date, num_of_stations):

    stations = list(
        Stations().region(country).fetch(num_of_stations).index
        )

    df_temp_data = Daily(stations, start_date, end_date) \
        .normalize().aggregate('1M').fetch()

    return df_temp_data


def fetch_countries_daily_temperature():

    df_country_info = pd.read_csv(
        'Peru-MDA-Ship/data/dim_all_country_static_info.csv',
        index_col = 'id')

    df_temp_data = pd.DataFrame(
        columns = ['country','tmax','tmin','tavg','pres']
        )
    df_temp_data.index.names = ['date']

    for con in df_country_info.index:

        df_temp_data = df_temp_data.append(
            fetch_country_daily_temperature(
                df_country_info.loc[con]['iso2Code'],
                datetime(1980, 1, 1), datetime(2019, 12, 1),
                df_country_info.loc[con]['num_of_weather_station']
            )
        )
        print(con)

    df_temp_data.index = pd.MultiIndex.from_arrays(
        [
            df_temp_data.index.map(
                lambda r : r[0] if type(r) == tuple else None
                ),

            df_temp_data.index.map(
                lambda r : r[1] if type(r) == tuple else r
                )
        ],
        names = ['station_id', 'date']
    )

    return df_temp_data

#%%

df_temp_data = pd.read_csv('Peru-MDA-Ship/data/dim_temp_data_1980_2019.csv')

df_temp_data['date'] = pd.to_datetime(df_temp_data.date)

df_temp_data['year'] = df_temp_data.date.dt.year

df_temp_data['tmax'] = df_temp_data.tmax.apply(lambda r: r if r <= 50 else None) \
    .fillna(method = 'ffill')

df_temp_data['tavg'] = df_temp_data.tavg.apply(lambda r: r if r <= 50 else None) \
    .fillna(method = 'ffill')

df_temp_day_coun = df_temp_data.groupby(['country', 'year','date']).agg({
    'tmax': 'max',
    'tmin': 'min',
    'tavg': 'mean',
    'pres': 'max'
})

# df_temp_day_coun.to_csv('Peru-MDA-Ship/data/dim_temp_country_day_1980_2019.csv')
df_temp_day_coun = pd.read_csv(
    'Peru-MDA-Ship/data/dim_temp_country_day_1980_2019.csv',
    )
df_temp_day_coun['date'] = pd.to_datetime(df_temp_day_coun.date)
df_temp_day_coun = df_temp_day_coun.set_index(['country','year','date'])

## calculate the 85 percentile threshold

df_temp_day_coun_ma15 = \
    df_temp_day_coun.groupby('country')[['tmax','tmin']].rolling(15).mean().droplevel(0)

df_temp_threshold = df_temp_day_coun_ma15.groupby(
    ['country', 'year']
).quantile(0.85).rename(columns = {'tmin': 'tmin_thres', 'tmax': 'tmax_thres'})

df_temp_threshold['tmax_thres'] = df_temp_threshold.apply(
    lambda r: 32 if r['tmax_thres'] <= 32 else r['tmax_thres'], axis =1
)

df_temp_day_coun_thres = pd.merge(
    df_temp_day_coun, df_temp_threshold,
    left_index = True,
    right_index = True
)


## calculate EHF (Excess Heat Factor)
avg_last_3 = df_temp_day_coun['tavg'].copy()

for i in range(1, 3):
    avg_last_3 += df_temp_day_coun.groupby(['country'])['tavg'].shift(-i)

avg_last_3 = (avg_last_3/3).fillna(method = 'ffill')

avg_3_32 = df_temp_day_coun.groupby(['country'])['tavg'].shift(-3).copy()

for i in range(4, 33):
    avg_3_32 += df_temp_day_coun.groupby(['country'])['tavg'].shift(-i)

avg_3_32 = (avg_3_32/30).fillna(method = 'ffill')

EHI_accl = avg_last_3 - avg_3_32

df_EHI_sig = pd.merge(
    avg_last_3,
    df_temp_day_coun.groupby(['country','year'])['tavg'].quantile(0.95).rename('tavg95'),
    left_index = True,
    right_index =True
)

EHI_sig = avg_last_3 - df_EHI_sig.tavg95

df_EHF = pd.merge(
    EHI_accl.rename('EHI_accl'),
    EHI_sig.rename('EHI_sig'),
    left_index = True,
    right_index = True
)

df_EHF['EHI_accl'] = df_EHF.EHI_accl.apply(lambda r: r if r > 1 else 1)


# three threshold to filter out the heat wave events.
df_temp_day_coun['is_hw_ehf'] = df_EHF['EHI_accl'] * df_EHF['EHI_sig'] > 0

df_temp_day_coun['is_hw_ctx85'] = \
    df_temp_day_coun.tmax > (df_temp_day_coun_thres.tmax_thres +0.1)

df_temp_day_coun['is_hw_ctn85'] = \
    df_temp_day_coun.tmin > (df_temp_day_coun_thres.tmin_thres + 0.1)

df_thres_filter = df_temp_day_coun[
    df_temp_day_coun.is_hw_ctx85 & df_temp_day_coun.is_hw_ctn85
    & df_temp_day_coun.is_hw_ehf
    ].reset_index(level = 2)[['date','tmax']]

df_thres_filter['last_date'] = \
    df_thres_filter.groupby(['country', 'year'])['date'].shift(1)
df_thres_filter['next_date'] = \
    df_thres_filter.groupby(['country', 'year'])['date'].shift(-1)

df_thres_filter['start_flag'] = df_thres_filter.apply(lambda r:
        (r['date'] - r['last_date']).days > 1
    , axis = 1)
df_thres_filter['end_flag'] = df_thres_filter.apply(lambda r:
        (r['next_date'] - r['date']).days > 1
    , axis = 1)

df_thres_filter = df_thres_filter[
    (df_thres_filter.start_flag & ~df_thres_filter.end_flag) |
    (~df_thres_filter.start_flag & df_thres_filter.end_flag) &
    ~df_thres_filter.last_date.isna()
]

df_thres_filter['end_date'] = df_thres_filter.groupby(['country','year'])['date'].shift(-1)
df_thres_filter = df_thres_filter[df_thres_filter.start_flag]
df_thres_filter['duration'] = df_thres_filter.apply(lambda r: (r['end_date'] - r['date']).days, axis=1)
df_thres_filter = df_thres_filter[df_thres_filter.duration >=3]

df_thres_filter = \
    df_thres_filter.drop(columns = ['start_flag','end_flag', 'last_date', 'next_date'])

df_thres_filter['country_code'] = df_thres_filter.index.get_level_values(0)

df_temp_day_coun_ = df_temp_day_coun.reset_index(level =2).copy()

df_thres_filter[['avg_maximum_temp', 'maximum_temp']] = df_thres_filter.apply(
    lambda r :
        df_temp_day_coun_[
            df_temp_day_coun_.date.between(r['date'], r['end_date'])
            ].loc[r['country_code']]['tmax'].agg(['mean', 'max']), axis =1
            ).rename(columns = {'mean':'avg_maximum_temp', 'max': 'maximum_temp'})

df_hw_gen = df_thres_filter.groupby(['country', 'year']).agg(
    {
        'duration' : ['sum', 'max'],
        'date': 'nunique',
        'maximum_temp': 'max',
        'avg_maximum_temp': 'mean'
    }
)
df_hw_gen.columns = ['HWF','HWD','HWN','HWA','HWM']

# df_hw_gen.to_csv('data/dim_temp_gen_heat_wave.csv')

#%%%
df_country_ts_dim = pd.merge(
    df_country_ts,
    df_hw_gen,
    left_index= True,
    right_index =True,
    how = 'left'
)

df_country_ts_dim[['tmp_mean', 'tmp_median']] = \
    df_temp_day_coun.groupby(
        ['country', 'year']
    )['tavg'].agg(['mean', 'median']).rename(
        columns = {'mean':'temp_mean', 'median': 'temp_median'}
        )

#df_country_ts_dim.to_csv('data/dim_all_country_info.csv')
