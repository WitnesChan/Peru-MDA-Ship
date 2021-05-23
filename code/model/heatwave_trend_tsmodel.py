import os
import sys
os.chdir('/Users/witnes/Workspace/MDA/Peru-MDA-Ship')

import warnings
warnings.filterwarnings('ignore')
os.chdir('/Users/witnes/Workspace/MDA/Peru-MDA-Ship')

src_path = os.path.join(os.getcwd(), '/code')

if src_path not in sys.path:
    sys.path.append(os.getcwd() + '/code')

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from model.model_pipeline import ModelPipeline
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_predict
from statsmodels.tsa.seasonal import STL, seasonal_decompose
from statsmodels.tsa.stattools import adfuller, kpss

from sklearn.preprocessing import MinMaxScaler, StandardScaler


def stl_decomp(df_ts, period = 4):

    stl = STL(df_ts, period = period)
    res = stl.fit()
    seasonal, trend, resid = res.seasonal, res.trend, res.resid
    estimated = seasonal + trend

    return [trend, estimated]


class HeatwaveTrendTSModel(ModelPipeline):

    def __init__(self):

        self.hw_metrics = ['HWN','HWF','HWD','HWA', 'HWM']

        self.hw_trend_metrics = ['HWN_trend', 'HWF_trend','HWD_trend', 'HWA_trend', 'HWM_trend']

        self.hw_metric_title = {
            'HWN': 'HWN yearly number of heat waves',
            'HWF': 'HWF yearly sum of participating heat waves',
            'HWD': 'HWD length of the longest yearly event',
            'HWA': 'HWA hottest day of hottest yearly event',
            'HWM': 'HWM average magnitude of all yearly heat waves',
        }
    def refit_procedure(self, dataset, period = 4):

        self.__data_collect(dataset)

        self.__data_preprocess()

        self.__fit_model(period)

        self.__summary_model_fit()


    def predict_procedure(self, new_dataset):
        pass

    def __data_collect(self, dataset):

        self.dataset = dataset

    def __data_preprocess(self):


        self.dataset.loc[:, ['HWF','HWD','HWN']] = \
            self.dataset.loc[:, ['HWF','HWD','HWN']].fillna(0)

        self.dataset.loc[:, ['HWA', 'HWM']] = \
            self.dataset.loc[:, ['HWA', 'HWM']].fillna(20)

        self.dataset = self.dataset.groupby(['year']).agg(
            {
                'HWN': 'sum',
                'HWF': 'sum',
                'HWD': 'max',
                'HWA': 'max',
                'HWM': 'max'
            }
        )

    def __fit_model(self, period):

        for ind in self.hw_metrics :

            self.dataset['%s_trend'%ind], self.dataset['%s_estimated'%ind] = \
                stl_decomp(self.dataset[ind], period = period)


    def __summary_model_fit(self):


        self.dataset[self.hw_trend_metrics].plot(subplots =True, legend = True)

        pd.DataFrame(
            StandardScaler().fit_transform(self.dataset[self.hw_trend_metrics]),
            columns = self.hw_trend_metrics,
            index = self.dataset.index
        ).plot()

    def plot_estimated_metric(self, metric_name):

        plt.figure(figsize=(8,6))
        df_world_ts[[metric_name, '%s_trend'%metric_name, '%s_estimated'%metric_name]].plot(
            title = self.hw_metric_title[metric_name])
        plt.legend(loc= 'left upper')



if __name__ == '__main__':

    trd  = HeatwaveTrendTSModel()

    df_country_ts = pd.read_csv('data/dim_all_country_info.csv',
        index_col = ['country', 'year']
        )

    ## see the trend of heat wave in the whole world
    trd.refit_procedure(df_country_ts)

    trd.plot_estimated_metric('HWN')
    ## see the trend of heat wave in the belgium

    #trd.refit_procedure(df_country_ts.loc['BE'])
