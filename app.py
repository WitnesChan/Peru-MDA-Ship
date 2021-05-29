from __future__ import absolute_import

import warnings
warnings.filterwarnings('ignore')

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import boto3
from plotly.subplots import make_subplots
import dash_table
import plotly.graph_objects as go

from heatwave_binarymodel import HeatwaveBinaryModel
from heatwave_trend_tsmodel import HeatwaveTrendTSModel

def read_from_s3_bucket(data_object_name):

    s3 = boto3.resource(
        service_name='s3',
        region_name='eu-central-1',
        aws_access_key_id='AKIATJJR2V5V27JPS7JA',
        aws_secret_access_key='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'
    )

    data_response = s3.Bucket('s3groupperu').Object(data_object_name).get()['Body']

    return data_response

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


df_smp = pd.read_csv(read_from_s3_bucket('data/dim_all_country_info.csv'), index_col=[0,1])


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Heatwave Event Research"),
                    html.H6("Cause and Effect Reporting"),
                ],
            )
        ],
    )

def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="heatwave-overview-tab",
                        label="Heatwave Overview",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="heatwave-trend-tab",
                        label="Heatwave Trend Spot",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="heatwave-binary-model-tab",
                        label="Binary Classification",
                        value="tab3",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    )
                ],
            )
        ],
    )

def build_hw_trend_spot_panel():

    df_country_code = pd.read_csv(
        read_from_s3_bucket('data/dim_all_country_static_info.csv')
        )[['iso2Code','name']].drop_duplicates()

    df_country_code = df_country_code[df_country_code.iso2Code.isin(
        df_smp['country.1'].drop_duplicates().values
    )]

    return  html.Div(children=[
        html.Label('Country Selection: '),
        dcc.Dropdown(
            id = 'country_select',
            options= df_country_code.rename(
                columns = { 'name':'label', 'iso2Code': 'value'}
                ).to_dict(orient='records'),

            value='BE'
        ),

        html.Div(
                children=[
                    html.Div(
                        children=[
                            html.H5("Heatwave indicators over years"),
                            dcc.Graph(id="trend_indicators")
                        ],
                        className="six columns pretty_container"
                    ),
                    html.Div(
                        children=[
                            html.H5("Heatwave scaled indicators over years"),
                            dcc.Graph(id="trend_scaled_indicators")
                        ],
                        className="six columns pretty_container"
                    ),
                ]
            ),
        html.Div(
            children = [
                html.Div(
                     dash_table.DataTable(
                        id='table_indcators_container',
                        data= None,
                        columns=[
                            {'id':'Year', 'name': 'Year'},
                            {'id': 'HWN_trend', 'name': 'HWN_trend'},
                            {'id': 'HWF_trend', 'name': 'HWF_trend'},
                            {'id': 'HWD_trend', 'name': 'HWD_trend'},
                            {'id': 'HWA_trend', 'name': 'HWA_trend'},
                            {'id': 'HWM_trend', 'name': 'HWM_trend'}
                        ],
                        style_header= {
                            "backgroundColor": "rgb(2,21,70)",
                            "color": "white",
                            "textAlign": "center",
                        },
                        style_data_conditional=[{"textAlign": "center"}],
                    ),
                    className="six columns pkcalc-results-table"
                ),
                html.Div(
                    children = [
                        html.H5("Heatwave Trend & Estimated Result"),
                        dcc.Graph(id="indicator_details_HWN"),
                        dcc.Graph(id="indicator_details_HWF"),
                        dcc.Graph(id="indicator_details_HWD"),
                        dcc.Graph(id="indicator_details_HWA"),
                        dcc.Graph(id="indicator_details_HWM")
                    ],
                    className="six columns pretty_container"
                )
            ]
        )

    ])

app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(
                    id="app-content",
                    children = [build_hw_trend_spot_panel()]
                ),
            ],
        )
    ],
)
# Callback function

@app.callback(
    [Output("app-content", "children")],
    [Input("app-tabs", "value")]
)
def render_tab_content(tab_switch):
    return build_hw_trend_spot_panel()

@app.callback(
    [Output('trend_indicators', 'figure'),
    Output('trend_scaled_indicators', 'figure'),
    Output('table_indcators_container', 'data'),
    Output('indicator_details_HWN', 'figure'),
    Output('indicator_details_HWF', 'figure'),
    Output('indicator_details_HWD', 'figure'),
    Output('indicator_details_HWA', 'figure'),
    Output('indicator_details_HWM', 'figure')],
    [Input('country_select', 'value')]
    )
def update_hw_trend_spot_panel(country_name):

    trd = HeatwaveTrendTSModel()
    trd.refit_procedure(df_smp.loc[country_name])
    fig_1 = make_subplots(
        rows=5, cols=1,
        shared_xaxes =True, x_title = 'Year'
        )

    fig_1.add_traces(
        [
            go.Bar(y = trd.dataset.HWN_trend, x = trd.dataset.index),
            go.Bar(y = trd.dataset.HWD_trend, x = trd.dataset.index),
            go.Bar(y = trd.dataset.HWF_trend, x = trd.dataset.index),
            go.Bar(y = trd.dataset.HWM_trend, x = trd.dataset.index),
            go.Bar(y = trd.dataset.HWA_trend, x = trd.dataset.index),
        ],
        rows=[1, 2, 3, 4, 5],
        cols=[1, 1, 1, 1, 1]
    )

    fig_1.update_layout(
        autosize=True, height=600,
        margin=dict(l=30,r=30,b=5,t=10,pad= 0.06)
    )

    scaled_trend_metrics=  trd.scaled_trend_metrics.stack().reset_index()
    scaled_trend_metrics.columns = ['year','indicator', 'value']

    fig_2 = px.line(scaled_trend_metrics, y = 'value', x= 'year', color = 'indicator')
    fig_2.update_layout(
        autosize=True, height=600,
        margin=dict(l=10,r=10,b=30,t=30)
    )

    tbl = trd.dataset[trd.hw_trend_metrics].apply(lambda r: round(r, 1)) \
        .reset_index(drop= False).rename(columns = {'year':'Year'}).to_dict('records')

    res  = []

    res.append(fig_1)
    res.append(fig_2)
    res.append(tbl)

    for m in trd.hw_metrics:

        detail_metric = \
        trd.dataset[['%s_trend'%m, '%s_trend'%m, '%s_estimated'%m]].stack().reset_index()
        detail_metric.columns = ['year','indicator', 'value']

        fig_m = px.line(detail_metric, y = 'value', x= 'year', color = 'indicator')
        fig_m.update_layout(autosize=True, height=225, margin=dict(l=10,r=10,b=30,t=30))
        res.append(fig_m)

    return res


if __name__ == '__main__':

    app.run_server(debug=True)
