import sys
import os
import pandas as pd
import numpy as np
import seaborn as sns

import warnings
warnings.filterwarnings('ignore')
import boto3

# from heatwave_binarymodel import HeatwaveBinaryModel

from heatwave_trend_tsmodel import HeatwaveTrendTSModel

sns.set(rc={'figure.figsize':(13,8)})


def read_from_s3_bucket(data_object_name):

    s3 = boto3.resource(
        service_name='s3',
        region_name='eu-central-1',
        aws_access_key_id='AKIATJJR2V5V27JPS7JA',
        aws_secret_access_key='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'
    )

    data_response = s3.Bucket('s3groupperu').Object(data_object_name).get()['Body']

    return data_response

#%%

data_object_name = 'dim_all_country_info.csv'

hwb = HeatwaveBinaryModel('svc')

# run the refitting procedure
df_smp = pd.read_csv(read_from_s3_bucket(data_object_name), index_col=[0,1])

hwb.refit_procedure(df_smp, random_state = 24)

# persist the model if you want
hwb.dump_model()

# run the predict procedure

print(hwb.predict_procedure(df_smp.iloc[100:2003]))

#%%
trd  = HeatwaveTrendTSModel()

df_country_ts = pd.read_csv('data/dim_all_country_info.csv',
    index_col = ['country', 'year']
    )

## see the trend of heat wave in the whole world
trd.refit_procedure(df_country_ts)

trd.plot_estimated_metric('HWN')
#%%


trd.dataset
