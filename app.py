from os import link
from typing import Text
import dash
from dash.dependencies import Input, Output
from dash_html_components.Label import Label
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from pandas import read_hdf
import json

df = read_hdf("all_indexes.h5", "/data/d1")

downloaded_xs_data = {}


app = dash.Dash(
    __name__,
    prevent_initial_callbacks=True,
    meta_tags=[
        # A description of the app, used by e.g.
        # search engines when displaying search results.
        {
            "name": "XSPlot neutron cross section plotter",
            "content": "Plot neutron cross sections",
            "keywords": "plot neutron nuclear cross section energy barns database plotter tendl",
        },
        # A tag that tells Internet Explorer (IE)
        # to use the latest renderer version available
        # to that browser (e.g. Edge)
        {"http-equiv": "X-UA-Compatible", "content": "IE=edge"},
        # A tag that tells the browser not to scale
        # desktop widths to fit mobile screens.
        # Sets the width of the viewport (browser)
        # to the width of the device, and the zoom level
        # (initial scale) to 1.
        #
        # Necessary for "true" mobile support.
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
    ],
)
app.title = "XSPlot neutron cross section plotter"
app.description = "Plot neutron cross sections. Nuclear data from the TENDL library."
# TODO add description, current google says Dash in description area
# https://github.com/plotly/dash/blob/1a40162dfce654b885e475ecb280d3cca9bff0a5/dash/dash.py#L193

# added to allow Gunicorn access to Dash Flask as discussed here
# https://ldnicolasmay.medium.com/deploying-a-free-dash-open-source-app-from-a-docker-container-with-gunicorn-3f426b5fd5df
server = app.server

components = [
    # guide on plotly html https://dash.plotly.com/dash-html-components
    html.Title("xsplot.com nuclear cross section plotting"),
    html.Iframe(
        src="https://ghbtns.com/github-btn.html?user=openmc-data-storage&repo=xsplot.com&type=star&count=true&size=large",
        width="170",
        height="30",
        title="GitHub",
        style={"border": 0, "scrolling": "0"},
    ),
    html.H1(
        "XSPlot - Neutron cross section plotter",
        # TODO find a nicer font
        # style={'font-family': 'Times New Roman, Times, serif'},
        # style={'font-family': 'Georgia, serif'},
        style={'text-align': 'center'}
    ),
    html.H3(
        "Filter and search the cross sections database and select neutron cross sections to plot",
        style={'text-align': 'center'}
    ),
    # html.H3('Powered by OpenMC, Plotly, Dash, Dash datatable, Flask, Gunicorn, Docker, GCloud, GitHub, Python, Arrow'),
    html.H4(
        'Hint! Column filtering uses "contains" logic. Filtering with  > < = are also supported. For example =56 would find entries equal to 56.',
        style={'text-align': 'center', "color": "red"},
    ),
    dash_table.DataTable(
        # style_cell={'fontSize':20, 'font-family':'sans-serif'}
        id="datatable-interactivity",
        columns=[
            {"name": i, "id": i, "selectable": True}
            for i in df.columns
            if i not in ["Temperature(K)", "Incident particle"]
        ],
        data=df.to_dict("records"),
        editable=False,
        filter_action="native",  # TODO change to equals instead of contains
        sort_action="native",
        sort_mode="multi",
        row_selectable="multi",
        row_deletable=False,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=15,
    ),
    html.Table(
        [
            html.Tr(
                [
                    html.Th(
                        html.Button(
                            "clear selection",
                            title="Clear all selected data. You can also temporarily hide plots by clicked them in the legend",
                            id="clear",
                        )
                    ),
                    html.Th(
                        dcc.RadioItems(
                            options=[
                                {"label": "log X axis", "value": "log"},
                                {"label": "linear X axis", "value": "linear"},
                            ],
                            value="log",
                            id="xaxis_scale",
                            labelStyle={"display": "inline-block"},
                        ),
                    ),
                ]
            ),
            html.Tr([html.Br()]),
            html.Tr(
                [
                    html.Th(
                        # html.H5('X axis scale'),
                        html.Button(
                            "Download Plotted Data",
                            title="Download a text file of the data in JSON format",
                            id="btn_download2",
                        )
                    ),
                    html.Th(
                        # html.H5('Y axis scale'),
                        dcc.RadioItems(
                            options=[
                                {"label": "log Y axis", "value": "log"},
                                {"label": "linear Y axis", "value": "linear"},
                            ],
                            value="log",
                            id="yaxis_scale",
                            # labelStyle={'display': 'inline-block'},
                        ),
                    ),
                ]
            ),
        ],
        style={"width": "100%"},
    ),
    # html.Br(),
    html.Br(),
    html.Div(id="datatable-interactivity-container"),
    # TODO move components to a table layout
    # https://dash.plotly.com/dash-html-components/td
    # https://dash.plotly.com/dash-html-components/tr
    # https://dash.plotly.com/dash-html-components/table
    # https://stackoverflow.com/questions/52213738/html-dash-table
    html.H5("X axis units"),
    dcc.Slider(
        min=0,
        max=4,
        marks={i: f"{s}" for i, s in enumerate(["μeV", "eV", "keV", "MeV", "GeV"])},
        value=1,
        id="x_axis_units",
    ),
    dcc.Download(id="download-text-index"),
    html.Br(),
    html.Div([
        html.Label('XSPlot is an open-source project powered by '),
        dcc.Link('OpenMC', href='https://docs.openmc.org/en/stable/'),
        html.Label(', '),
        dcc.Link(' Plotly', href='https://plotly.com/'),
        html.Label(', '),
        dcc.Link(' Dash', href='https://dash.plotly.com/'),
        html.Label(', '),
        dcc.Link(' Dash datatable', href='https://dash.plotly.com/datatable'),
        html.Label(', '),
        dcc.Link(' Flask', href='https://flask.palletsprojects.com/en/2.0.x/'),
        html.Label(', '),
        dcc.Link(' Gunicorn', href='https://gunicorn.org/'),
        html.Label(', '),
        dcc.Link(' Docker', href='https://www.docker.com'),
        html.Label(', '),
        dcc.Link(' GCloud', href='https://cloud.google.com'),
        html.Label(', '),
        dcc.Link(' Python', href='https://www.python.org/'),
        html.Label(' the with source code available on '),
        dcc.Link(' GitHub', href='https://github.com/openmc-data-storage/xsplot.com'),
    ],style={'text-align': 'center'}),
    html.Br(),
    html.Div([
        html.Label('Links to alternative cross section plotting websites: '),
        dcc.Link('NEA JANIS', href='https://www.oecd-nea.org/jcms/pl_39910/janis'),
        html.Label(', '),
        dcc.Link(' IAEA ENDF', href='https://www-nds.iaea.org/exfor/endf.htm'),
        html.Label(', '),
        dcc.Link(' NNDC Sigma', href='https://www.nndc.bnl.gov/sigma/'),
        html.Label(', '),
        dcc.Link(' Nuclear Data Center JAEA', href='https://wwwndc.jaea.go.jp/ENDF_Graph/'),
        html.Label(', '),
        dcc.Link('T2 LANL', href='https://t2.lanl.gov/nis/data/endf/index.html'),
    ],style={'text-align': 'center'}),
]


app.layout = html.Div(components)


@app.callback(
    Output("datatable-interactivity", "selected_rows"),
    Input("clear", "n_clicks"),
)
def clear(n_clicks):
    return []


@app.callback(
    Output("datatable-interactivity", "style_data_conditional"),
    [Input("datatable-interactivity", "selected_columns")],
)
def update_styles(selected_columns):
    return [
        {"if": {"column_id": i}, "background_color": "#D2F3FF"}
        for i in selected_columns
    ]


def get_uuid_from_row(row):
    atomic_symbol = row["Atomic symbol"].to_string(index=False)
    mass_number = row["Mass number"].to_string(index=False)
    library = row["Library"].to_string(index=False)
    incident_particle_symbol = "n"
    reaction = row["MT reaction number"].to_string(index=False)
    reaction_description = row["Reaction products"].to_string(index=False)

    if library == "TENDL-2019":
        temperature = "294K"
    else:
        temperature = "300K"  # FENDL 3.1d

    uuid = "_".join(
        [
            atomic_symbol,
            mass_number,
            library,
            incident_particle_symbol,
            str(int(reaction)),
            str(temperature),
        ]
    )
    return uuid


@app.callback(
    Output("datatable-interactivity-container", "children"),
    [
        Input("datatable-interactivity", "selected_rows"),
        Input("xaxis_scale", "value"),
        Input("yaxis_scale", "value"),
        Input("x_axis_units", "value"),
    ],
)
def update_graphs(selected_rows, xaxis_scale, yaxis_scale, x_axis_units):
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

    global downloaded_xs_data

    if len(downloaded_xs_data) > 0:
        for entry in selected_rows:
            if entry in downloaded_xs_data.keys():
                downloaded_xs_data[entry]["plot"] = False

    for entry in selected_rows:
        row = df.iloc[[entry]]

        uuid = get_uuid_from_row(row)
        library = row["Library"].to_string().split()[1]

        fn = library + "_json/" + uuid + ".json"
        # print('filename loading', fn)
        with open(fn) as json_file:
            xs = json.load(json_file)

        xs["plot"] = True
        xs["legend"] = "{}{} (n,{}) {}".format(
            xs["Atomic symbol"],
            xs["Mass number"],
            xs["Reaction products"],
            xs["Library"],
        )

        downloaded_xs_data[entry] = xs

    all_x_y_data = []

    x_axis_units_multiplier = {0: -3, 1: 0, 2: 3, 3: 6, 4: 9}
    for k, v in downloaded_xs_data.items():
        import math

        if k in selected_rows:

            multiplier = math.pow(10, -1 * x_axis_units_multiplier[x_axis_units])
            energy = [x * multiplier for x in downloaded_xs_data[k]["energy"]]

            all_x_y_data.append(
                {
                    "y": downloaded_xs_data[k]["cross section"],
                    "x": energy,
                    "type": "scatter",
                    "name": downloaded_xs_data[k]["legend"]
                    # "marker": {"color": colors},
                }
            )

    # previous website had more complex unit logic
    # https://github.com/Shimwell/database_GUI/blob/d670ca88feef8f41a0f20abd30bdb2a82cbab6bd/src/App.js#L305-L329
    x_axis_units_text = {0: "μeV", 1: "eV", 2: "keV", 3: "MeV", 4: "GeV"}

    energy_units = f"({x_axis_units_text[x_axis_units]})"
    xs_units = "(b)"

    if len(selected_rows) != 0:
        # return html.H1('Select cross sections in the table above to start plotting')
        return [
            dcc.Graph(
                config=dict(showSendToCloud=True),
                figure={
                    "data": all_x_y_data,
                    "layout": {
                        "margin": {"l": 3, "r": 2, "t": 15, "b": 60},
                        "xaxis": {
                            "title": {"text": f"Energy {energy_units}"},
                            "type": xaxis_scale,
                            "tickformat": ".1e",
                            "tickangle": 45,
                        },
                        "yaxis": {
                            "automargin": True,
                            "title": {"text": f"Cross Section {xs_units}"},
                            "type": yaxis_scale,
                            "tickformat": ".1e",
                        },
                        "showlegend": True
                        # "height": 250,
                        # "margin": {"t": 10, "l": 10, "r": 10},
                    },
                },
            )
        ]


# uses a trigger to identify the callback and if the button is used then jsonifys the selected data
@app.callback(
    Output("download-text-index", "data"),
    [
        Input("btn_download2", "n_clicks"),
        Input("datatable-interactivity", "selected_rows"),
    ],
)
def func2(n_clicks, selected_rows):
    trigger_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    global downloaded_xs_data

    if trigger_id == "btn_download2":
        if n_clicks is None:
            raise dash.exceptions.PreventUpdate
        else:
            if len(downloaded_xs_data) > 0:

                all_x_y_data = []
                for k, v in downloaded_xs_data.items():
                    if k in selected_rows:
                        print(downloaded_xs_data[k]["legend"])
                        all_x_y_data.append(downloaded_xs_data[k])

                return dict(
                    content=json.dumps(all_x_y_data, indent=2),
                    filename="xsplot_download.json",
                )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8080)
