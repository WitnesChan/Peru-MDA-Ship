import os
import sys
src_path = os.path.join(os.getcwd(), 'Peru-MDA-Ship/code')

if src_path in sys.path:
    pass
else:
    sys.path.append(src_path)

import warnings
warnings.filterwarnings('ignore')


import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

sns.set()

#%%

df_emdat = pd.read_excel(
    'Peru-MDA-Ship/data/emdat_public_2021_04_02.xlsx',
    engine = 'openpyxl'
    )

#%%

print(df_emdat.head())

print(df_emdat.columns)

#%%

df_emdat['Disaster Subtype'].unique()

#%%

df_heat_wave = df_emdat[df_emdat['Disaster Subtype'] == 'Heat wave']

df_heat_wave.describe().T


#%%
df_heat_wave
