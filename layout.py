import dash
import dash_bootstrap_components as dbc
import sys

from dash import dcc, html,ctx,dash_table, callback_context
from dash.exceptions import PreventUpdate


tab_style = {
    'textAlign': 'center',
    'fontWeight': 'bold',
    'padding': '2px 4px',  # Reduced padding (vertical, horizontal)
    'fontSize': '14px',    # Smaller font size
    'height': '30px',      # Explicitly set height
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'center'
}
selected_tab_style = {
    'textAlign': 'center',
    'fontWeight': 'bold',
    'padding': '2px 4px',  # Reduced padding (vertical, horizontal)
    'fontSize': '14px',    # Smaller font size
    'height': '40px',      # Explicitly set height
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'center'
}
layout=html.Div([
    #Useful variables
    dcc.Store(id='store_values', storage_type='memory'),
    html.Div(id='check-column',style={'display':'none'},children='failed'),


    #Header
    html.Div([
        html.Button('≡', id='menu-button', n_clicks=0),
        html.Div([ 
            html.H2("Temporal Distortion")
        ], style={
            'alignItems': 'center',
            'flex': '1',
            'textAlign': 'center'  # Add this to center the text within the div
        }),
        html.Div([
            html.Button('?', id='help-button')
        ], style={'marginLeft': 'auto'})
        ],
        style={
        'display': 'flex',
        'alignItems': 'center',
        'padding': '0 15px',
        'width': '100%'  # Ensure the container takes full width
    }),
    #Notification
    dbc.Alert(
        f"",
        id="upload-notification",
        dismissable=True,
        is_open=False,
        duration=2000,  #milliseconds
        color="success"
    ),
    dbc.Alert(
        f"Wrong column name",
        id="wrong-column-notification",
        dismissable=True,
        is_open=False,
        duration=2000,  #milliseconds
        color="red"
    ),
    dbc.Alert(
        "File saved successfully!",
        id="save-notification",
        dismissable=True,
        is_open=False,
        duration=2000,  #milliseconds
        color="success"
    ),
    #Progress Bar
    html.Div([
    html.P("Processing anomalies:"),
    dbc.Progress(id="anomaly-progress", value=0, max=100, style={"width": "100%"})
    ], id="progress-container", style={"display": "none"}),

    dbc.Modal([
        dbc.ModalHeader(
            html.H4("Enter column names", className="mb-0"),
            close_button=True
        ),
        dbc.ModalBody([
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Enter the column name containing timestamps:", className="fw-bold"),
                    dbc.Input(
                        id="modal-date",
                        type="text",
                        className="mb-3",
                        value=''
                    ),
                    
                    dbc.Label("Enter the column name containing timeseries values:", className="fw-bold"),
                    dbc.Input(
                        id="modal-value",
                        type="text",
                        className="mb-3",
                        value=''
                    ),
                    
                    dbc.Label("Enter the column name containing anomalies (Leave empty if none):", className="fw-bold"),
                    dbc.Input(
                        id="modal-anomaly",
                        type="text",
                        className="mb-3",
                        value=''
                    ),
                ], width=16)
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button(
                "Cancel", 
                id="close-dialog-button", 
                color="secondary",
                className="me-2"
            ),
            dbc.Button(
                "Submit", 
                id="submit-dialog-button", 
                color="primary",
                n_clicks=0
            )
        ])
    ],id="modal", is_open=False, backdrop="static", size="md", centered=True, className="border-0 shadow"),
    #Main Content
    html.Div([
        #Side Pane
        html.Div([
            html.Div([
                html.Label("File Selection:"),
                dcc.Upload(id='file-selector',
                    children=html.Div([
                    'Upload',
                ]),
                style={
                    'float':'left',
                    'width': '90%',
                    'height': '30px',
                    'lineHeight': '30px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False  
                ),
                html.Strong("Click on the `upload` button to import a csv file"), 
                    ". Assumed structure:",
                html.Ul([
                    html.Li("- `timestamp` (\"%Y-%m-%d %H:%M:%S\")"),
                    html.Li("- `value`"),
                    html.Li("- `anomaly`(optional)")]),
                dcc.Checklist(
                    id='interpolate',
                    options=[{'label': 'Fill missing values in time series', 'value': 'yes'}],
                    value=['yes']
                ),
                html.Button("Download", id='save-button',
                    style={
                    'float':'left',
                    'width': '90%',
                    'height': '30px',
                    'lineHeight': '30px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                }),
                dcc.Download(id="download-dataframe-csv"),
            ],style={'margin':'10px 10px','padding': '10px','margin-bottom': '50px'}),

            #Collapsable statistics section
            html.Div([
                #Header
                html.Div(id='stats-state',style={'display':'none'},children='open'),
                html.Div([
                    html.Button("Statistics ▲", id="stats-collapse-button",
                        style={
                        'float':'left',
                        'width': '90%',
                        'height': '30px',
                        'lineHeight': '30px',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                        }
                    )
                ],),
                
                #Body
                html.Div([

                    html.Div(html.Strong("Uploaded file: "),id='upload-status',),
                    html.Div([html.Strong("Total Length of the time series: ")],id='total-len',),
                    html.Div([html.Strong("Number of anomalies labelled: ")],id='anomaly-len',),


                ],id="stats-content", style={
                    "padding": "10px",
                    'height':'200px',
                    'overflow':'auto',
                    'transition':'height 0.01s',
                    "backgroundColor": "#2c3e50",
                    'display':True
                    }),
            ], style={'margin-top': '20px',"margin": "15px 15px", "padding": "10px", "backgroundColor": "#34495e", "borderRadius": "5px"}),
                        

        ], id='side-pane', style={
            'width': '30%', 
            'minHeight': '100%',
            'transition': 'width 0.3s',
            'backgroundColor': '#2d3e50',
        }),

        #Main Content Area
        html.Div([

            #Tabs
            dcc.Tabs(id='tabs', value='tab-1', children=[
                dcc.Tab(label='Main', value='tab-1',style=tab_style,selected_style=selected_tab_style),
                dcc.Tab(label='Anomaly Injection', value='tab-2',style=tab_style,selected_style=selected_tab_style),
            ],  style={ 'width': '100%' },
        ),
        
            #Plot
            html.Div([
            dcc.Graph(
                id='main-plot',
                config={
                'displayModeBar': True,
                'scrollZoom': True,
                'displaylogo': False,  # This removes the Plotly logo
                'modeBarButtons': [['zoomIn2d', 'zoomOut2d','resetScale2d','pan2d','select2d']],
                'modeBarButtonsToRemove': ['toImage'],
                }
            ),
            ],id='graph-container',style={'margin':'10px','display':'none'}),

            html.Div(id='range-data', n_clicks=-2,style={'display': 'none'}),
            html.Div(id="alerts-container", children=[]),

            #Tab container
            html.Div([
                #Tab-1(Main)
                html.Div([
                    html.H2('Energy Anomaly Data Table',
                             style={'textAlign': 'center','float':'center','color': '#ffffff'}),
                    dash_table.DataTable(
                    id='table',
                    style_table={
                        'height': '400px',  # Fixed height
                        'overflowY': 'auto'  # Enable vertical scrolling
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'minWidth': '100px',
                        'width': '150px',
                        'maxWidth': '180px',
                        'whiteSpace': 'normal'  # Allow text wrapping
                    },
                    style_header={
                        'backgroundColor': '#2c3e50',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'position': 'sticky',  # Make header sticky while scrolling
                        'top': 0,
                        'zIndex': 999
                    },
                    style_data={
                        'backgroundColor': 'white',
                        'color': 'black'
                    },
                    style_data_conditional=[  # Add alternating row colors
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'black',
                            'color': 'white'
                        }
                    ],
                    fixed_rows={'headers': True},  # Keep header fixed when scrolling
                    sort_action='native',  # Enable sorting
                )

                ],id='tab-1-container',style={'display':'none'}),

                #Tab-2 (Anomaly Injection)
                html.Div([html.Button('Inject', id='inject-anomaly', n_clicks=0)],
                id='tab-2-container',style={'display':'none'}),

                #No data meesage
                html.H2("No data uploaded!",
                        style={'textAlign':'center','float':'center','color': "#ffffff",'padding':'5px'},
                        id='tab-no-data'),



            ],
                     id='tab-container',style={'height':'50%','float':'center'}),

        ],id='main-content', style={'width': '70%', 'float':'center','padding': '20px', 'transition': 'width 0.3s'}
        )
    ], style={'display':'flex'}),
    # Hidden div to store data
    html.Div(id='stored-data', style={'display': 'none'}),
    
    # Hidden div to track side pane state
    html.Div(id='side-pane-state', style={'display': 'none'}, children="open"),

    # Instructions modal overlay - note we're using a pattern here where clicking the overlay closes the modal
    html.Div([
        # Overlay that covers the entire screen and handles clicks to close
        html.Div(id='modal-overlay', className='modal-overlay', n_clicks=0, style={
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'width': '100vw',
            'height': '100vh',
            'backgroundColor': 'rgba(0, 0, 0, 0.5)',
            'zIndex': '1000',
            'display': 'none',
        }),
        
        # Modal content - we'll prevent it from triggering the overlay's click
        html.Div(className='modal-content', id='modal-content', style={
            'position': 'fixed',
            'top': '50%',
            'left': '50%',
            'transform': 'translate(-50%, -50%)',
            'backgroundColor': 'black',
            'padding': '20px',
            'borderRadius': '5px',
            'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
            'maxWidth': '800px',
            'width': '80%',
            'maxHeight': '80vh',
            'overflowY': 'auto',
            'zIndex': '1001',
            'display': 'none',
        }, children=[
            html.Ol([
                html.H3("Usage:", style={'borderBottom': '1px solid #ddd', 'paddingBottom': '10px'}),
                html.Strong("IMPORTANT: Click anywhere outside of the box to go out of the help menu"),
                html.Li([html.Strong("Press the `≡` icon to toggle the side panel ")]),
                html.Li([
                    html.Strong("Click on the `upload` button to import a csv file"), 
                    ". Assumed structure:",
                    html.Ul([
                        html.Li("- `timestamp` (\"%Y-%m-%d %H:%M:%S\")"),
                        html.Li("- `value`"),
                        html.Li("- `anomaly`(optional)")
                    ])
                ]),

                ])
            ])
    ], id='modal-container'),
])