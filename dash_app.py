import webbrowser
from threading import Timer

import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime as dt

df = pd.read_csv('../20201225_012404.csv')
#---------------------------
#資料基本特性
Start_Date = df['成交日期'].iloc[0].split('-')
End_Date = df['成交日期'].iloc[-1].split('-')

Start_Date = [int(i) for i in Start_Date]
End_Date = [int(i) for i in End_Date]

#---------------------------
#APP介面

app = dash.Dash(external_stylesheets=[
    "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap-grid.min.css"],
    suppress_callback_exceptions=True
)

app.layout = html.Div([dbc.Row(
    [dbc.Col([
        dbc.Row([
            dbc.Col(dcc.DatePickerRange(
                                id='date-picker-range',
                                month_format='MMMM Y',
                                display_format='YYYY/M/D',
                                start_date=dt(Start_Date[0], Start_Date[1], Start_Date[2]),
                                end_date=dt(End_Date[0], End_Date[1], End_Date[2]),
                                initial_visible_month=dt(Start_Date[0], Start_Date[1], Start_Date[2]),
                                # style={
                                #     'width': '50%',
                                #     'height': '20px',
                                #     'lineHeight': '20px',
                                #     'borderWidth': '2px',
                                #     'borderRadius': '3px',
                                #     'textAlign': 'center',
                                #     'margin': '2px'
                                # }
                                ), style={'display': 'inline-block' }),
                dbc.Col(dcc.Dropdown(
                            id='approach',
                            options=[{'label': '選擇交易方式', 'value': 'All'}]+[
                                {'label': i, 'value': i} for i in df.交易方式.drop_duplicates()
                            ],
                            value='All',
                            multi=False
                        ), style={'display': 'inline-block' }),
                dbc.Col(dcc.Dropdown(
                            id='ticker',
                            options=[{'label': 'ticker', 'value': 'All'}]+[
                                {'label': i, 'value': i} for i in df.證券代號.drop_duplicates()
                            ],
                            value='All',
                            multi=True
                        ), style={'display': 'inline-block' }),

                # dcc.Dropdown(
                #             id='industry2',
                #             options=[{'label': 'All Sectors', 'value': 'All Sectors'}]+[
                #                 {'label': i, 'value': i} for i in df.證券代號.drop_duplicates()
                #             ],
                #             value='All Sectors',
                #             multi=True
                # ),
        ]                    
        ),
        dbc.Row(
            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                ),style={"width":"100%","height": "100vh", 'textAlign': 'center', 'margin': '5px'}
        )
        ]),

    dbc.Col(dbc.Col([
        
        dcc.Loading(
                id = "loading-icon1", 
                children=dcc.Graph(
                id='graph1', style={'width':'100%', 'height': '30vh','display': 'inline-block' }
                ),
                type="default"
            ),
        
        dcc.Loading(
                id = "loading-icon2", 
                children=dcc.Graph(
                id='graph2', style={'width':'100%', 'height': '30vh','display': 'inline-block' }
                ),
                type="default"
            ),
        
        dcc.Loading(
                id = "loading-icon3", 
                children=dcc.Graph(
                id='graph3', style={'width':'100%', 'height': '40vh','display': 'inline-block' }
                ),
                type="default"
            ),
    ]),align="right")
    ],
    )],style={"width":"100%","height": "100vh"}
    )






# dash_table.DataTable(
#     id='table',
#     columns=[{"name": i, "id": i} for i in df.columns],
#     data=df.to_dict('records'),
# )



#---------------------------










def open_browser():
    webbrowser.open_new('http://127.0.0.1:2000/')

if __name__ == "__main__":
    Timer(1, open_browser).start();
    app.run_server(port=2000,debug=True)