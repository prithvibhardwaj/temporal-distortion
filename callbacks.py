import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import os
import dash_bootstrap_components as dbc
import base64
import io

from dash import Dash, dcc, html, ctx,dash_table
from dash.dependencies import Input,Output,State
from datetime import timedelta,datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import f1_score
from dash.exceptions import PreventUpdate


def register_callbacks(app):

    @app.callback(
            [Output('modal','is_open'),
             Output('modal-date','value'),
             Output('modal-value','value'),
             Output('modal-anomaly','value'),
            Output('check-column','children')
             ],
            [Input('file-selector','contents')],
            [State('file-selector','filename')]
    )
    def show_col_selector(content,n_file):
        if not(n_file and content):
            raise PreventUpdate
        if not n_file.endswith('csv'):
            raise PreventUpdate

        # store_values,selected_file,usecols,fig

        print("New file: ",n_file)
        selected_file=n_file
        content_type,content_string=content.split(',')
        decoded=base64.b64decode(content_string)
        decoded=decoded.decode('utf-8')
        df = pd.read_csv(io.StringIO(decoded))
        usecols=[]
        possible_t_columns=['timestamp','timestamps','date_time','datetime']
        for col in possible_t_columns:
            if col in df.columns:
                usecols.append(col)
        possible_e_columns=['values','value','meter_reading','meter_readings']
        for col in possible_e_columns:
            if col in df.columns:
                usecols.append(col)
                break
        if len(usecols)==1:
            usecols.append('')
        
        possible_a_columns=['anomaly','outlier','fault','anomalies','outliers','faults']
        for col in possible_a_columns:
            if col in df.columns:
                usecols.append(col)
                break
        if len(usecols)==2:
            usecols.append('')

        print(usecols)
        return [True],usecols[0],usecols[1],usecols[2],'failed'

    @app.callback(
            [Output('submit-dialog-button','n_clicks'),
             Output('modal','is_open',allow_duplicate=True)],
            [Input('close-dialog-button','n_clicks')]
    )
    def reset_submit_counter(n_clicks):
        return 0,False

    
    @app.callback(
            [
            Output('wrong-column-notification','is_open'),
            Output('wrong-column-notification','children'),
            Output('modal','is_open',allow_duplicate=True),
            Output('modal-anomaly','value',allow_duplicate=True),
            Output('check-column','children',allow_duplicate=True)
            ],
            [
            Input('submit-dialog-button','n_clicks'),
            ],
            [
            State('modal-date','value'),
            State('modal-value','value'),
            State('modal-anomaly','value'),
            State('file-selector','contents')
            ]
    )
    def column_sanity_check(n_clicks,date_col,value_col,anomaly_col,content):
        if n_clicks==0:
            raise PreventUpdate
        available=True
        content_type,content_string=content.split(',')
        decoded=base64.b64decode(content_string)
        decoded=decoded.decode('utf-8')

        df = pd.read_csv(io.StringIO(decoded))
        if anomaly_col=='': #Add a new anomaly col
            df['anomaly']=0
            anomaly_col='anomaly'

        usecols=[date_col,value_col,anomaly_col]
        for col in usecols:
            if not col in df.columns:
                available=False
                break
        mess="Column: "+col+" not in the dataframe"
        if not available:
            print(mess)
            style={'margin':'10px','display':"None"}
            return True,mess,True,anomaly_col,'failed'
        else:
            return False,mess,False,anomaly_col,'passed'

    @app.callback(
        [Output('main-plot','figure'),
         Output('upload-notification','is_open'),
         Output('upload-notification','children'),
         Output('graph-container','style'),
         Output('upload-status','children'),
         Output('store_values','data'),
         Output('tab-1-container','style'),
         Output('tab-2-container','style'),
         Output('tab-no-data','style'),
         Output('table','data'),
         Output('table','columns')],
        [Input('check-column','children'),],
        [State('interpolate','value'),State('modal-date','value'),
         State('modal-value','value'),State('modal-anomaly','value'),
        State('file-selector','filename'),
        State('file-selector','contents'),
        State('tabs','value')])
    def new_figure(column_checked,interpolate,date_col,value_col,anomaly_col,n_file,content,tab):
        if column_checked=='failed':
            print('column check failed')
            raise PreventUpdate
        print("new figure")
        if not n_file :
            raise PreventUpdate
        if not n_file.endswith('csv'):
            raise PreventUpdate
        
        if tab=='tab-1':
            style_1={'display':True}
            style_2={'display':'none'}
        elif tab=='tab-2':
            style_1={'display':'none'}
            style_2={'display':True}
        style_data={'display':'none'}


        data=dict()


        print("New file: ",n_file)
        selected_file=n_file

        content_type,content_string=content.split(',')
        decoded=base64.b64decode(content_string)
        decoded=decoded.decode('utf-8')

        df = pd.read_csv(io.StringIO(decoded))
        usecols=[date_col,value_col,anomaly_col]
        fig = go.Figure()
        fig.update_layout(
            hovermode='closest',
            hoverdistance=50,    # Maximum distance, in pixels, to look for data points
                        )

        # Validate limits
        x = pd.to_datetime(df[date_col]).values
        # Add main trace
        store_values=df[usecols].copy(deep=True)
        if interpolate:
            store_values[value_col]=store_values[value_col].ffill()
        store_values[date_col]=pd.to_datetime(store_values[date_col])
        store_values.reset_index(inplace=True,drop=True)
        fig.add_trace(go.Scatter(
            x=x,
            y=store_values[value_col].values,
            name=value_col,
            line=dict(color='gray'),
            hoverinfo='x+y'
        ))
        
        # Update layout
        fig.update_layout(
            plot_bgcolor='#2d3e50',
            paper_bgcolor='#2d3e50',
            xaxis=dict(
                rangeslider=dict(visible=True, thickness=0.1),
                showgrid=False,  # Turn off x-axis grid lines
                showline=True,
                showticklabels=True,  # Make x-axis tick labels visible
                tickfont=dict(color='white'),  # Make tick labels white for visibility
            ),
            yaxis=dict(
                showgrid=False,  # Turn off y-axis grid lines
                showticklabels=True,  # Make y-axis tick labels visible
                showline=True,
                tickfont=dict(color='white'),  # Make tick labels white for visibility
            ),
            margin=dict(l=0, r=0, t=20, b=0),
            showlegend=False,
            legend=dict(
                yanchor="top",
                y=1.0,
                xanchor="left",
                x=0.01
            ),
            yaxis_range=[min(store_values[value_col]), int(max(store_values[value_col])*1)],
            clickmode='event+select',
            dragmode='select',
            selectdirection='h',
            hovermode='closest',
            uirevision='same',
        )
        style={'display':True,'margin':'10px'}

        #add anomalies
        #Fortmat: '2016-04-14 03:00'
        f_mat='%Y-%m-%d %H:%M'
        anomalies=store_values[store_values[anomaly_col]==1]
        for Idx,click_x in zip(anomalies.index.values,anomalies[date_col].values):
            val=pd.to_datetime(click_x).strftime(f_mat)
            fig.add_vline(
                x=val,
                line_width=1,
                line_color="red",
                opacity=0.4,
                name=f'point_{Idx}'
            )

        #store_values
        data['filename']=selected_file
        data['fig']=pio.to_json(fig)
        data['df']= store_values.to_json(date_format='iso', orient='split')
        print(data.keys())
        columns=[{"name": i, "id": i} for i in store_values.columns]
        up_child=html.Strong(f"Uploaded file: {selected_file}")
        #fig,up_not,up_chil,graph_style,upload_status_children,store_data,tab_1_style,tab_2_style,tab_no_style,table_dta,table_columns
        return fig,True,f"File {selected_file} loaded successfully!",style,up_child,data,style_1,style_2,style_data,store_values.to_dict('records'),columns

    @app.callback(
        [Output('main-plot', 'figure', allow_duplicate=True),
         Output('table','data',allow_duplicate=True),
         Output('anomaly-len','children',allow_duplicate=True),
         Output('store_values','data',allow_duplicate=True)],
        [ Input('main-plot', 'selectedData'),
         Input('main-plot', 'clickData')],
        [State('store_values','data')],
        prevent_initial_call=True
    )
    def update_graph(selected_data,click_data,stored_data):
        store_values=pd.read_json(io.StringIO(stored_data['df']),orient='split')
        fig=pio.from_json(stored_data['fig'])

        # Handle selected data (box select)
        f_mat='%Y-%m-%d %H'
        date_col=store_values.columns.to_list()[0]
        anom_col=store_values.columns.to_list()[-1]
        if selected_data and 'range' in selected_data:
            print("box data= ",selected_data)
            start_x = selected_data['range']['x'][0]
            end_x = selected_data['range']['x'][1]
            print(start_x,end_x)
            start_x=pd.to_datetime(start_x)
            end_x=pd.to_datetime(end_x)
            print(start_x,end_x)
            print(type(start_x), type(end_x))
            if end_x<start_x:
                temp=end_x
                end_x=start_x
                start_x=temp

            while (start_x<=end_x):
                row=store_values.loc[store_values[date_col]==start_x.strftime(f_mat)]
                flag=row[anom_col].values[0]
                Idx=row.index.values[0]
                print(flag,Idx)
                if flag==0: #Add 
                    #Update the figure
                    fig.add_vline(
                        x=start_x.strftime(f_mat),
                        line_width=1,
                        line_color="red",
                        opacity=0.4,
                        name=f'point_{Idx}'
                    )
                    #Update the dataframe
                    store_values.loc[store_values[date_col]==start_x.strftime(f_mat),anom_col]=1
                elif flag==1:#Remove
                    name=f'point_{Idx}'
                    fig.layout.shapes = [trace for trace in fig.layout.shapes if trace.name !=name]
                    store_values.loc[store_values[date_col]==start_x.strftime(f_mat),anom_col]=0
                else:
                    raise ValueError("Unknown anomaly type!")
                print(type(start_x))
                start_x+=timedelta(hours=1)
                print(start_x)
            
    
        # Handle click data
        elif click_data:
            print('point data= ',click_data)
            click_x = click_data['points'][0]['x']
            click_x=pd.to_datetime(click_x).strftime(f_mat)
            row=store_values.loc[store_values[date_col]==click_x]
            flag=row[anom_col].values[0]
            Idx=row.index.values[0]
            print(flag,Idx)
            if flag==0: #Add
                fig.add_vline(
                    x=click_x,
                    line_width=1,
                    line_color="red",
                    opacity=0.4,
                    name=f'point_{Idx}'
                )
                store_values.loc[store_values[date_col]==click_x,anom_col]=1

            elif flag==1: #Remove
                name=f'point_{Idx}'
                fig.layout.shapes = [trace for trace in fig.layout.shapes if trace.name !=name]
                store_values.loc[store_values[date_col]==click_x,anom_col]=0

        #columns=[{"name": i, "id": i} for i in store_values.columns] 
        total_anomalies=sum(store_values[anom_col])
        anom=[html.Label(f'Number of anomalies: {total_anomalies}')]
        stored_data['fig']=pio.to_json(fig)
        stored_data['df']= store_values.to_json(date_format='iso', orient='split')

        return fig,store_values.to_dict('records'),anom,stored_data



    @app.callback(
            [
                Output('total-len','children'),
                Output('anomaly-len','children')
            ],
            [Input('store_values','data')],
            prevent_initial_call=True
    )
    def update_stats(stored_data):
        try:
            store_values=pd.read_json(io.StringIO(stored_data['df']),orient='split')
        except Exception:
            raise PreventUpdate
        anom_col=store_values.columns.to_list()[-1]
        anomalies=store_values[anom_col]
        t_len=len(anomalies)

        a_len=np.sum(anomalies.values==1)
        print('t_len= ',t_len,'a_len= ',a_len)
        t_return=[html.Strong(f"Total Length of the time series: {t_len} ")]
        a_return=[html.Strong(f"Number of anomalies labelled:{a_len} ")]
        return t_return,a_return



    @app.callback(
        [
        Output('stats-collapse-button','children'),
        Output('stats-content','style'),
        Output('stats-state','children'),
        ],
        [
        Input('stats-collapse-button','n_clicks')
        ],
        [State('stats-state','children')],
        prevent_initial_call=True,
    )
    def toggle_stats(clicks,state):
        print(state)
        if clicks==0:
            raise PreventUpdate
        if state=='open':
            stat_style={
                'height':'0px',
                'overflow':'hidden',
                'transition':'height 0.01s',
                "padding": "10px",
                'display':'none'
                }

            text="Statistics ▼"
            return text,stat_style,'closed'
        elif state=='closed':
            stat_style={
                "padding": "10px",
                'height':'200px',
                'overflow':'auto',
                'transition':'height 0.01s',
                "backgroundColor": "#2c3e50",
                'display':True
                }
            text="Statistics ▲"
            return text,stat_style,'open'

    @app.callback(
        [
        Output('side-pane','style'),
        Output('main-content','style'),
        Output('side-pane-state','children')
        ],
        [Input('menu-button','n_clicks')],
        [State('side-pane-state','children')]
    )
    def toggle_sidepane(n_clicks,children):
        if n_clicks:
            if children=='open':
                side_pane_style={
                    'width':'0%',
                    'transition':'width 0.5s',
                    'overflow':'hidden',
                    'backgroundColor': '#2d3e50',
                    'minHeight': 'calc(100vh - 60px)',
                }
                main_content_style={
                    'width':'100%',
                    'padding':'10px',

                }
                return side_pane_style,main_content_style,'closed'
            
            else:
                side_pane_style={
                    'width':'30%',
                    'transition': 'width 0.5s',
                    'backgroundColor': '#2d3e50',
                    'minHeight': 'calc(100vh - 60px)',
                }
                main_content_style={
                    'width':'70%',
                    'transition': 'width 0.5s'
                }
                return side_pane_style,main_content_style,'open'
        
        #Default setting (Initial load)
        side_pane_style={
            'width':'30%',
            'transition': 'width 0.5s',
            'backgroundColor': '#2d3e50',
            'minHeight': 'calc(100vh - 60px)',
        }
        main_content_style={
            'width':'70%',
            'transition': 'width 0.5s'
        }
        return side_pane_style,main_content_style,'open'
    
    @app.callback(
        [Output('tab-1-container','style',allow_duplicate=True),
         Output('tab-2-container','style',allow_duplicate=True),
         Output('tab-no-data','style',allow_duplicate=True) ],
        [Input('tabs','value'),
         ],
         [State('store_values','data')],
        prevent_initial_call=True
    )
    def toggle_tab(tab,data):
        print('toggle-tab')
        style_true={'display':True}
        style_none={'display':'none'}
        style_data={'textAlign':'center','float':'center','color': "#ffffff",'padding':'5px'}
        try:
            store_values=pd.read_json(io.StringIO(data['df']),orient='split')
            print('toggle tab store values: ',len(store_values))
        except Exception as err:
            print(err)
            return style_none,style_none,style_data
        if tab=='tab-1':
            print('tab-1')
            return style_true,style_none,style_none
        elif tab=='tab-2':
            print('tab-2')
            return style_none,style_true,style_none
    # Callback to toggle instructions modal
    @app.callback(
        [Output('modal-overlay', 'style'),
        Output('modal-content', 'style')],
        [Input('help-button', 'n_clicks'),
        Input('modal-overlay', 'n_clicks')],
        [State('modal-overlay', 'style'),
        State('modal-content', 'style')]
    )
    def toggle_modal(help_clicks, overlay_clicks, overlay_style, content_style):
        # Get the ID of the element that triggered the callback
        triggered_id = ctx.triggered_id if ctx.triggered else None
        
        # Create copies of the current styles to modify
        new_overlay_style = dict(overlay_style)
        new_content_style = dict(content_style)
        
        if triggered_id == 'help-button':
            # Show the modal when help button is clicked
            new_overlay_style['display'] = 'block'
            new_content_style['display'] = 'block'
        
        elif triggered_id == 'modal-overlay':
            # Hide the modal when overlay is clicked
            new_overlay_style['display'] = 'none'
            new_content_style['display'] = 'none'
        
        return new_overlay_style, new_content_style

    @app.callback(
        [
            Output('download-dataframe-csv','data'),
            Output('save-notification','is_open'),
        ],
        [
            Input('save-button','n_clicks')
        ],
        [
            State('store_values','data')
        ],
        prevent_initial_call=True
    )
    def download_file(n_clicks,data):
        if not ctx.triggered:
            raise PreventUpdate
        if n_clicks<=0:
            raise PreventUpdate
        try:
            store_values=pd.read_json(io.StringIO(data['df']),orient='split')
            selected_file=data['filename']
        except Exception as err:
            print(err)
        
        filename=selected_file
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id=='save-button':
            if len(store_values)==0:
                raise PreventUpdate
            print(filename)
            print('saved')
            return dcc.send_data_frame(store_values.to_csv, f"{filename}",index=False),True
        return None


