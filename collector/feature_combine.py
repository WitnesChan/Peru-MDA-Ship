import os
import sys
from os import path

src_path = os.path.join(os.getcwd(), '/code')

if src_path not in sys.path:
    sys.path.append(os.getcwd() + '/code')

from collector.dim_world_bank import WBDIndicatorFetcher
from collector.dim_climate import generate_heat_wave_by_temp

def build_feature_data():

    start_year, end_year = 2020, 2020
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2020, 12, 1)

    feature_file = 'data/dim_all_country_info_%d_%d.csv'%(start_year, end_year)
    daily_country_weather_file = 'data/dim_temp_data_%d_%d.csv'%(start_year, end_year)

    # data from world bank
    indicator_maps = {
        'SP.POP.TOTL' : 'total_population',
        'SP.URB.TOTL.IN.ZS' : 'urban_pop_ratio',
        'AG.LND.FRST.ZS' : 'forest_area_ratio',
        'NY.GDP.MKTP.KD.ZG': 'gdp_growth_rate',
        'NY.GDP.MKTP.CD': 'gdp_growth_usd',
        'EN.ATM.CO2E.KT': 'co2_emission_kt',
        'AG.LND.AGRI.ZS': 'agri_land_ratio',
        'EN.ATM.METH.KT.CE': 'methane_emission_kt',
        'AG.PRD.LVSK.XD': 'livestock_prod_ind',
        'AG.PRD.FOOD.XD': 'food_prod_ind'
    }


    wbd = WBDIndicatorFetcher()
    wbd.construct_static_info()
    wbd.construct_panel_data()
    wbd.fetch_countries_indicators(indicator_maps)

    df_country_ts = pd.merge(
        wbd.df_country_ts,
        wbd.df_country_info,
        left_index= True,
        right_index =True
    ).reset_index().set_index(['iso2Code', 'year'])

    df_country_ts.index.names = ['country', 'year']

    df_country_ts.index.set_levels(
         np.arange(start_year,end_year),1,
         inplace= True
    )

    # data from meteostat
    if ~path.exists():
        df_hw_gen = generate_heat_wave_by_temp(start_date, end_date)
    else:
        df_hw_gen = pd.read_csv(daily_country_weather_file)

    df_country_ts_dim = pd.merge(
        df_country_ts,
        df_hw_gen,
        left_index= True,
        right_index =True,
        how = 'left'
    )

    df_country_ts_dim = pd.read_csv(daily_country_weather_file)

    df_country_ts_dim[['tmp_mean', 'tmp_median']] = df_temp_day_coun.groupby(
            ['country', 'year']
        )['tavg'].agg(['mean', 'median']).rename(
            columns = {'mean':'temp_mean', 'median': 'temp_median'}
            )

    df_country_ts_dim.to_csv(feature_file)
