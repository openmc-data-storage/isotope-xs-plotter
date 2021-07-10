from os import link
from typing import Text
import dash
from dash.dependencies import Input, Output
from dash_html_components.Label import Label
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import json
# import time

# start = time.process_time()
df = pd.read_hdf("all_indexes.h5", "/data/d1")
# print('time to read index', time.process_time() - start)

downloaded_xs_data={}

app = dash.Dash(__name__, prevent_initial_callbacks=True)
app.title = 'XSPlot'

# added to allow Gunicorn access to Dash Flask as discussed here
# https://ldnicolasmay.medium.com/deploying-a-free-dash-open-source-app-from-a-docker-container-with-gunicorn-3f426b5fd5df
server = app.server

app.layout = html.Div([
    # guide on plotly html https://dash.plotly.com/dash-html-components
    html.H1(
        'XSPlot - Nuclear interaction cross section plotter',
        # style={'font-family': 'Times New Roman, Times, serif'},
        # style={'font-family': 'Georgia, serif'},
        # style={'fontColor': 'blue'}
        ),
    html.H3('Filter and search for cross sections to get started'),
    html.Iframe(
        src="https://ghbtns.com/github-btn.html?user=openmc-data-storage&repo=xsplot.com&type=star&count=true&size=large",
        width="170",
        height="30",
        title="GitHub",
        style={'border':0, 'scrolling':"0"}
    ),
    # html.Text("Contribute, raise feature requests or report issues"),
    # html.A("here", href='https://github.com/openmc-data-storage/xsplot.com', target="_blank"),
    # dcc.Link('Contribute, raise feature requests or report issues here', href=''),
    html.H2(
        'Hint! When filtering in numeric columns use operators. For example =3',
        style={'color': 'red'}
    ),

    dash_table.DataTable(
        # style_cell={'fontSize':20, 'font-family':'sans-serif'}
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        editable=False,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        # column_selectable="single",
        row_selectable="multi",
        row_deletable=False,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=15,
    ),
    html.Div(
        id='datatable-interactivity-container'
    ),
    html.Title('xsplot.com nuclear cross section plotting'),
    html.H5('X axis scale'),
    dcc.RadioItems(
        options=[
            {'label': 'log', 'value': 'log'},
            {'label': 'linear', 'value': 'linear'}
        ],
        value='log',
        id='xaxis_scale',
        labelStyle={'display': 'inline-block'},
        ),
    html.H5('Y axis scale'),
    dcc.RadioItems(
        options=[
            {'label': 'log', 'value': 'log'},
            {'label': 'linear', 'value': 'linear'}
        ],
        value='log',
        id='yaxis_scale',
        labelStyle={'display': 'inline-block'},
        ),
    html.Button("Download Plotted Data", id="btn_txt"),
    dcc.Download(id="download-text-index")
    ])
    # RangeSlider for energy units
    # Download

@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]

def get_uuid_from_row(row):
    atomic_symbol = row['Atomic symbol'].to_string(index=False)
    # print('atomic_symbol', atomic_symbol)
    mass_number = row['Mass number'].to_string(index=False)
    # print('mass_number', mass_number)
    library = row['Library'].to_string(index=False)
    # print('library', library)
    incident_particle_symbol = 'n'
    # print('incident_particle_symbol', incident_particle_symbol)
    reaction = row['MT reaction number'].to_string(index=False)
    # print('reaction', reaction)
    reaction_description = row['Reaction products'].to_string(index=False)
    
    if library == 'TENDL-2019':
        temperature = '294K'
    else:
        temperature = '300K' # FENDL 3.1d

    uuid = '_'.join([
        atomic_symbol,
        mass_number,
        library, 
        incident_particle_symbol,
        str(int(reaction)),
        str(temperature)]
    )
    return uuid

@app.callback(
    Output('datatable-interactivity-container', "children"),
    [
    #  Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "selected_rows"),
     Input('xaxis_scale', 'value'),
     Input('yaxis_scale', 'value')
     ])
def update_graphs(selected_rows, xaxis_scale, yaxis_scale):
    # When the table is first rendered, `derived_virtual_data` and
    # `selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if selected_rows is None:
        selected_rows = []

    # dff = df if rows is None else pd.DataFrame(rows)
    global downloaded_xs_data
    # print('selected_rows', selected_rows)

    if len(downloaded_xs_data) > 0:
        # print('setting all to plot=False')
        for entry in selected_rows:
    #     # for entry in range(0 , 15):
    #         row = df.iloc[[entry]]
    #         uuid = get_uuid_from_row(row)
            if entry in downloaded_xs_data.keys():
                downloaded_xs_data[entry]['plot'] = False

    for entry in selected_rows:
        row = df.iloc[[entry]]

        uuid = get_uuid_from_row(row)
        library = row['Library'].to_string().split()[1]

        fn = library+'_json/'+uuid+'.json'
        # print('filename loading', fn)
        with open(fn) as json_file:
            xs = json.load(json_file)

        xs['plot'] = True
        xs['legend'] = '{}{} (n,{}) {}'.format(
            xs['Atomic symbol'],
            xs['Mass number'],
            xs['Reaction products'],
            xs['Library'],
        )
        
        downloaded_xs_data[entry] = xs

    all_x_y_data = []
    for k, v in downloaded_xs_data.items():
        # print('    plotting ', k)
        # print("downloaded_xs_data[k]['plot']", downloaded_xs_data[k]['plot'].array[0])
        # print("downloaded_xs_data[k]['plot']", type(downloaded_xs_data[k]['plot'].array[0]))
        # if downloaded_xs_data[k]['plot'].array[0] == True:
            # print('got here')
        # print('        found plot=True', k)
        # print('uuid is ', downloaded_xs_data[k]['uuid'].array[0])
        # print('uuid is ', type(downloaded_xs_data[k]['uuid'].array[0]))
        if k in selected_rows:
            print(downloaded_xs_data[k]['legend'])
            all_x_y_data.append(
                {
                    "y": downloaded_xs_data[k]["cross section"],
                    "x": downloaded_xs_data[k]['energy'],
                    "type": "scatter",
                    "name": downloaded_xs_data[k]['legend']
                    # "marker": {"color": colors},
                    }
                )

    # print('xaxis_scale', xaxis_scale)
    # print('yaxis_scale', yaxis_scale)
    if len(selected_rows) == 0:
        return html.H1('Select cross sections in the table above to start plotting')
    return [
        dcc.Graph(
            # config=dict(modeBarButtonsToAdd=['sendDataToCloud']),
            config=dict(showSendToCloud=True),
            figure={
                "data": all_x_y_data,
                "layout": {
                    "xaxis": {
                        "title": {"text": 'Energy'},
                        "type": xaxis_scale
                    },
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": 'Cross Section'},
                        "type": yaxis_scale
                    },
                    "showlegend": True
                    # "height": 250,
                    # "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
    ]


# could work with tigger detection
# @app.callback(Output("download-text-index", "data"), [Input("btn_txt", "n_clicks"), Input('datatable-interactivity', "selected_rows")])
# def func(n_clicks, selected_rows):
    # trigger_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

@app.callback(Output("download-text-index", "data"), Input("btn_txt", "n_clicks"))
def func(n_clicks):

    global downloaded_xs_data

    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    else:
        if len(downloaded_xs_data>0):
            return dict(
                content=json.dumps(downloaded_xs_data, indent=2),
                filename="xsplot_download.json")

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
    # app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
