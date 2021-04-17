
from meteostat import Point, Daily, Stations


def fetch_country_temperature(country, start_date, end_date, num_of_stations):

    stations = list(
        Stations().region(country).fetch(num_of_stations).index
        )

    df_temp_data = Daily(stations, start_date, end_date).fetch()

    return df_temp_data[['tavg','tmin','tmax',]]


df_country_info = pd.read_csv(
    'Peru-MDA-Ship/data/dim_country_static_info.csv',
    index_col = 'alpha3_code')


df_pak_temp =fetch_country_temperature(
    df_country_info.loc['BEL']['alpha2_code'],
    datetime(2014, 1, 1), datetime(2015, 11, 1),
    df_country_info.loc['BEL']['num_of_weather_station']
)

df_pak_temp.groupby('time')[['tmax','tmin','tavg']].max().plot()
