import pandas as pd
import world_bank_data as wb

class WBDIndicatorFetcher(object):

    def __init__(self):
        pass

    def construct_static_info(self):

        df_country_info = wb.get_countries()
        df_country_info = df_country_info[df_country_info.region !='Aggregates']

        from meteostat import Stations

        ## fetch the number of weather stations for each country.
        df_country_info['num_of_weather_station'] = df_country_info.apply(
            lambda r: Stations().region(r['iso2Code']).count() ,axis=1
            )
        ## fetch the land area for each country.
        df_country_info = fetch_countries_indicator(
                df_country_info,
                indicator = 'AG.LND.TOTL.K2',
                col_name = 'land_area_sq_km',
                spec_year = '2018'
                )

        self.df_country_info = df_country_info
        self.country_codes = df_country_info.index


    def construct_panel_data(self, start_year = 1980, end_year = 2020):

        ## construct panel data
        self.start_year = start_year
        self.end_year = end_year

        self.df_country_ts = pd.DataFrame(
            index = pd.MultiIndex.from_product(
                [
                    self.country_codes ,
                    pd.date_range(start = str(start_year), end = str(end_year),freq ='Y').to_period('Y').astype(str)
                ]
            )
        )
        self.df_country_ts.index.names = ['Country', 'Year']


    def fetch_countries_indicator_ts(
        self, indicator, col_name):
        '''
            add one more indicator to the df_country_ts
        '''

        for country in self.country_codes:
            df_country_ts.loc[country, col_name] = wb.get_series(
                indicator, country = country, simplify_index = True
                ).loc[self.start_year:self.end_year].values


    def fetch_countries_indicator(
        self, indicator, col_name, spec_year):
        '''

        '''
        self.df_country_info[col_name] = wb.get_series(
                indicator, country = country, date = spec_year, simplify_index = True,
                id_or_value = 'id'
                )


    def fetch_countries_indicators(self, indicator_maps):
        '''

        '''

        for indicator, col_name in indicator_maps.items():

            self.df_country_ts[col_name] = wb.get_series(
                        indicator, simplify_index = True, id_or_value = 'id'
                    ).reset_index(level =0).loc[np.arange(self.start_year, self.end_year).astype(str)] \
                    .set_index('Country',append =True).reorder_levels([1, 0], axis=0).sort_index()



#%%

wbd = WBDIndicatorFetcher()
wbd.construct_static_info()
wbd.df_country_info

# df_country_info.to_csv('Peru-MDA-Ship/data/dim_all_country_static_info.csv')
#%%
indicator_maps = {
    'SP.POP.TOTL' : 'total_population',
    'SP.URB.TOTL.IN.ZS' : 'urban_pop_ratio',
    'AG.LND.FRST.ZS' : 'forest_area_ratio',
    'NY.GDP.MKTP.KD.ZG': 'gdp_growth_rate',
    'NY.GDP.MKTP.CD': 'gdp_growth_usd',
    'EN.ATM.CO2E.KT': 'co2_emission_kt',
    'AG.LND.AGRI.ZS': 'agri_land_ratio'
}

wbd.construct_panel_data()
wbd.fetch_countries_indicators(indicator_maps)

wbd.df_country_ts
#%%
