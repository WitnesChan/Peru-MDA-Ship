import os
import sys
src_path = os.path.join(os.getcwd(), 'Peru-MDA-Ship/code')

if src_path in sys.path:
    pass
else:
    sys.path.append(src_path)

import warnings
warnings.filterwarnings('ignore')

from datetime import datetime,date
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import math
sns.set(rc={'figure.figsize':(12,7)})
pd.set_option("display.max_rows", 300)
pd.set_option("display.max_columns", 30)

os.chdir('/Users/witnes/Workspace/MDA/Peru-MDA-Ship')
# %%
df_emdat = pd.read_excel(
    'data/emdat_public_2021_04_02.xlsx',
    engine = 'openpyxl'
    )
df_emdat['Year_10'] = (df_emdat.Year /10).astype(int) *10

# print all of disasters categories in this dataset.
print(df_emdat['Disaster Subtype'].unique())

print(df_emdat['Disaster Type'].unique())


# %%
sns.countplot(y = 'Disaster Type',  hue = 'Continent', data = df_emdat, orient = 'v')

# %%
sns.heatmap(
    pd.pivot_table(
        index = 'Year', columns = 'Disaster Subtype',
        values= 'ISO', aggfunc='count', fill_value= 0,
        data = df_emdat
    ).corr(),
    annot = True
)

# %%

pd.pivot_table(
    index = 'Year_10', columns = 'Disaster Subtype',
    values= 'ISO', aggfunc='count', fill_value= 0,
    data = df_emdat
).loc[1900:2010].plot(kind ='bar', stacked= True)


# %%

df_emdat.groupby(['Year'])['Disaster Subtype'].count().plot()

df_emdat.where(df_emdat['Disaster Subtype'] =='Heat wave'). \
    groupby(['Year'])['Disaster Subtype'].count().plot()

# %%

df_heat_wave = df_emdat[df_emdat['Disaster Subtype'] == 'Heat wave']

df_heat_wave.Country = df_heat_wave.Country.str.replace('\([a-zA-Z\s\']+\)', '').str.rstrip()
df_heat_wave.Country = df_heat_wave.Country.str.replace('United Kingdom of Great Britain and Northern Ireland', 'United Kingdom')

df_heat_wave['start_year_month'] = df_heat_wave[['Start Year', 'Start Month']].astype(int).apply(
    lambda r: datetime(r['Start Year'],r['Start Month'],1), axis =1
    ).dt.to_period('M')

df_heat_wave['Year_10'] = (df_heat_wave.Year /10).astype(int) *10

df_heat_wave.drop(columns = [
    'Origin', 'Aid Contribution', 'Local Time', 'River Basin', 'No Homeless',
    'Disaster Group', 'Disaster Type', 'Disaster Subtype','Associated Dis',
    'Associated Dis2', "Reconstruction Costs ('000 US$)", 'Appeal', 'OFDA Response',
    'Latitude', 'Longitude', 'Declaration', 'Dis Mag Scale', "Insured Damages ('000 US$)",],
    inplace = True)

#df_heat_wave.to_csv('Peru-MDA-Ship/data/heat_wave_records.csv')

# %%

# Aggregate counts of heat wave by Years to see the distribution.
# The events happened more frequently as years goes on.
df_heat_wave.groupby(['Year']).Country.count().plot(figsize = (13, 7), kind = 'bar')

# %%
sns.countplot(y = 'Year_10', hue ='Continent',orient= 'v', data = df_heat_wave[df_heat_wave.Year != 2020])


# %%

sns.countplot(y = 'Continent', hue ='Year_10',orient= 'v', data = df_heat_wave[df_heat_wave.Year != 2020])

# %% Occurence aggregated by Continent

sns.countplot(y = 'Continent', data = df_heat_wave)


# %%

df_agg_country = df_heat_wave.groupby(['Continent','Country']).Year.count().rename('Num of Heat Waves').reset_index() \
    .sort_values(by = ['Continent','Num of Heat Waves'], ascending =True).set_index('Continent')

plt.figure(figsize=(10,13))
i= 1

for continent in ['Asia', 'Europe']:
    ax = plt.subplot(2,1,i)
    df_agg_country.loc[continent].plot(x= 'Country',kind ='barh', ax =ax, figsize =(8,12))
    plt.title(continent)
    plt.ylabel('')
    ax.set_xlim([0,25])
    ax.get_legend().remove()
    i +=1

plt.figure(figsize=(10,13))

i= 1
for continent in ['Americas', 'Africa', 'Oceania']:

    ax = plt.subplot(3,1,i)
    df_agg_country.loc[continent].plot(x= 'Country',kind ='barh', ax =ax)
    plt.title(continent)
    plt.ylabel('')
    ax.set_xlim([0,25])
    ax.get_legend().remove()
    i +=1

# %%

df_heat_wave.groupby(['Continent','Country']).Year.count().rename('Num of Heat Waves').reset_index() \
    .sort_values(by = ['Continent','Num of Heat Waves'], ascending =True).set_index('Continent') \
    .loc[['Oceania', 'Africa', 'Americas', 'Europe', 'Asia']] \
    .plot(x = 'Country',figsize = (13, 10),kind ='barh')



# %% Aggregate by Country

df_sum_contyear = df_heat_wave.groupby(['Year_10','Continent']).agg(
    {
        'Seq': ['count'],
        'Total Deaths': ['sum']
    }
).reset_index()

df_sum_contyear.columns = ['Year', 'Continent', 'Count', 'Total Deaths']

# %% occurrence

sns.barplot(y="Count", x = 'Continent', hue="Year", palette= "husl",
            data=df_sum_contyear)



# %%
df_heat_wave.groupby(['Continent','Country'])['Total Deaths'].sum().sort_values(ascending =True)\
    .plot(figsize = (13, 10),kind ='barh')


# %%
df_heat_wave['lastdays'] = df_heat_wave.apply(
    lambda r:
        None if math.isnan(r['Start Day']) or math.isnan(r['End Day'])
        else (
            date(int(r['End Year']), int(r['End Month']), int(r['End Day']))
            - date(int(r['Start Year']), int(r['Start Month']), int(r['Start Day']))
        ).days,
    axis =1)


# %%
sns.distplot(
    df_heat_wave[df_heat_wave['lastdays'] != 376]['lastdays']
)
