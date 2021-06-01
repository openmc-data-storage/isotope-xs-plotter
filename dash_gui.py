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
print(len(data))
df = pd.json_normalize(data[0])

# df = pd.read_json('TENDL-2019_json/TENDL-2019_index.json')

print(df)
downloaded_xs_data={}

app = dash.Dash(__name__)

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
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(
    Output('datatable-interactivity-container', "children"),
    [Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "derived_virtual_selected_rows")])
def update_graphs(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    # dff = df if rows is None else pd.DataFrame(rows)

    print(derived_virtual_selected_rows)

    for entry in derived_virtual_selected_rows:
        row = df.iloc[[entry]]
        print(row)

        atomic_symbol = str(row['Proton number / element']).split()[2]
        mass_number = str(int(row['Mass number']))
        library = row['Library'].to_string().split()[1] # not sure why the split is needed
        incident_particle_symbol = 'n'
        reaction = row['MT number / reaction products'].to_string().split()[1]
        
        if library == 'TENDL-2019':
            temperature = '294K'
        else:
            temperature = '300K' # FENDL 3.1d

        print('atomic_symbol',atomic_symbol)
        print('mass_number',mass_number)
        print('library',library)
        print('reaction',reaction)
    
        uuid = '_'.join([atomic_symbol, mass_number, library, 
                         incident_particle_symbol,
                         str(int(reaction)), str(temperature)])

        fn = library+'_json/'+uuid+'.json'
        print('filename loading', fn)
        xs = pd.read_json(fn)
        print(xs.keys())


        downloaded_xs_data[entry] = xs
    
    all_x_y_data = []
    for k, v in downloaded_xs_data.items():

        # print('entry', entry)
        all_x_y_data.append({"y": downloaded_xs_data[k]["cross section"],
                             "x": downloaded_xs_data[k]['energy'],
                             "type": "scatter",
                        # "marker": {"color": colors},
                             })
    
    return [
        dcc.Graph(
            figure={
                "data": all_x_y_data,
                "layout": {
                    "xaxis": {
                        "title": {"text": 'Energy'}
                    },
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": 'Cross Section'}
                    },
                    # "height": 250,
                    # "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        
    ]

if __name__ == '__main__':
    app.run_server(debug=True)