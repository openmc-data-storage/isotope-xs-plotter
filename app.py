import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import json

# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

f = open('TENDL-2019_json/TENDL-2019_index.json')
data = json.load(f)
# print('number of entries', len(data))
df = pd.json_normalize(data)

# df = pd.read_json('TENDL-2019_json/TENDL-2019_index.json')

# print(df)
downloaded_xs_data={}

app = dash.Dash(__name__)

# added to allow Gunicorn access to Dash Flask as discussed here
# https://ldnicolasmay.medium.com/deploying-a-free-dash-open-source-app-from-a-docker-container-with-gunicorn-3f426b5fd5df
server = app.server

app.layout = html.Div([
    dash_table.DataTable(
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
        page_current= 0,
        page_size= 15,
    ),
    html.Div(id='datatable-interactivity-container')
])

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
    atomic_symbol = str(row['Proton number / element']).split()[2]
    mass_number = str(int(row['Mass number']))
    library = row['Library'].to_string().split()[1] # not sure why the split is needed
    incident_particle_symbol = 'n'
    reaction = row['MT number / reaction products'].to_string().split()[1]
    reaction_description = row['MT number / reaction products'].to_string().split()[0]
    
    if library == 'TENDL-2019':
        temperature = '294K'
    else:
        temperature = '300K' # FENDL 3.1d

    # print('atomic_symbol',atomic_symbol)
    # print('mass_number',mass_number)
    # print('library',library)
    # print('reaction',reaction)

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
    [Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "selected_rows")])
def update_graphs(rows, selected_rows):
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
        # print('    ', row)
        # print('    adding ', entry)


        uuid = get_uuid_from_row(row)
        library = row['Library'].to_string().split()[1]

        fn = library+'_json/'+uuid+'.json'
        # print('filename loading', fn)
        xs = pd.read_json(fn)
        # print(xs.keys())

        # xs['uuid'] = uuid
        xs['plot'] = True
        xs['legend'] = uuid
        # xs['legend'] = '_'.join([
        #     mass_number,
        #     atomic_symbol,
        #     reaction_description,
        #     library]
        # )
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
            all_x_y_data.append(
                {
                    "y": downloaded_xs_data[k]["cross section"],
                    "x": downloaded_xs_data[k]['energy'],
                    "type": "scatter",
                    "name": downloaded_xs_data[k]['legend']
                    # "marker": {"color": colors},
                    }
                )

    return [
        dcc.Graph(
            figure={
                "data": all_x_y_data,
                "layout": {
                    "xaxis": {
                        "title": {"text": 'Energy'},
                        "type": 'linear'
                    },
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": 'Cross Section'},
                        "type": 'log'
                    },
                    # "height": 250,
                    # "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
    ]


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
    # app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
