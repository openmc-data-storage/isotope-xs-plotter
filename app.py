from json import dumps, load

import dash
from dash.dependencies import Input, Output

from dash import html
from dash import dcc

# todo update imports dash_table
from dash import dash_table
from pandas import read_hdf

df = read_hdf("all_indexes.h5", "/data/d1")

downloaded_xs_data = {}


app = dash.Dash(
    __name__,
    prevent_initial_callbacks=True,
    meta_tags=[
        # A description of the app, used by e.g.
        # search engines when displaying search results.
        {"name": "title", "content": "XSPlot neutron cross section plotter"},
        {
            "name": "description",
            "content": "Online graph plotting tool for neutron cross sections from a range of nuclear data including TENDL ENDF",
        },
        {
            "name": "keywords",
            "keywords": "plot neutron nuclear cross section energy barns database plotter tendl endf",
        },
        {"name": "author", "content": "Jonathan Shimwell"},
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
app.title = "XSPlot \U0001f4c9 neutron cross section plotter \U0001f4c8"
app.description = "Plot neutron cross sections. Nuclear data from the TENDL library."
# TODO add description, current google says Dash in description area
# https://github.com/plotly/dash/blob/1a40162dfce654b885e475ecb280d3cca9bff0a5/dash/dash.py#L193

# added to allow Gunicorn access to Dash Flask as discussed here
# https://ldnicolasmay.medium.com/deploying-a-free-dash-open-source-app-from-a-docker-container-with-gunicorn-3f426b5fd5df
server = app.server

components = [
    # guide on plotly html https://dash.plotly.com/dash-html-components
    html.Title("xsplot.com isotope cross section plotting"),
    html.Iframe(
        src="https://ghbtns.com/github-btn.html?user=openmc-data-storage&repo=isotope-xs-plotter&type=star&count=true&size=large",
        width="170",
        height="30",
        title="GitHub",
        style={"border": 0, "scrolling": "0"},
    ),
    html.H1(
        "XSPlot - Neutron cross section plotter for isotopes",
        # TODO find a nicer font
        # style={'font-family': 'Times New Roman, Times, serif'},
        # style={'font-family': 'Georgia, serif'},
        style={"text-align": "center"},
    ),
    html.Div(
        html.Iframe(
            src="https://www.youtube.com/embed/aWXS9AqSkEk",
            width="560",
            height="315",
            title="Tutorial video",
            # style={},
            style={"text-align": "center", "border": 0, "scrolling": "0"},
        ),
        style={"text-align": "center"},
    ),
    html.Div(
        [
        html.H3(
            [
                "\U0001f50e Search the cross sections database using any of the table headings. \U0001f50d",
            ],
            style={'text-align': 'center'}
        ),
        html.H3(
            [
                "Make use of logical expressions to refine the database filtering \U0001f449 = < > "
                #  "Make use of \U0001f449 ", A("MT reaction number", href="https://t2.lanl.gov/nis/endf/mts.html"),
                # " or other table headings and then select neutron cross sections to plot. ",
                # "Use logical expressions = < > to perform advanced filtering."
            ],
            style={'text-align': 'center'}
        ),        
        html.H3(
            [
                "\U0000269b Make use of standard MT numbers to identify reactions \U0001f449 ",
                html.A("reaction descriptions \U0001f517",href="https://t2.lanl.gov/nis/endf/mts.html") ,
                # " or other table headings and then select neutron cross sections to plot. ",
                # "Use logical expressions = < > to perform advanced filtering."
            ],
            style={'text-align': 'center'}
        ),
        html.H3(
            [
                '\U0001f4c8 The plot should update automatically \U0001f389'
            ],
            style={'text-align': 'center'}
        ),
        html.H3(
            [
                '\U0001f4c9 Customise you graph and download your cross section data \U0001f4be'
            ],
            style={'text-align': 'center'}
        ),
        ]
    ),
    dash_table.DataTable(
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
        style_cell={'fontSize':16, 'font-family':'sans-serif'},
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
                    html.Th(
                        # html.H5("X axis range (comma delimitated)"),
                        html.Div(title='Enter both X lower and X upper limit to use, works best on linear X scale.', children=[
                            dcc.Input(
                                    id="x_lower_limit",
                                    type='text',
                                    placeholder='X axis lower limit in eV'
                            ),
                        ]),
                    ),
                    html.Th(
                        html.Div(title='Enter both X lower and X upper limit to use, works best on linear X scale.', children=[
                            dcc.Input(
                                    id="x_upper_limit",
                                    type='text',
                                    placeholder='X axis lower limit in eV'
                            ),
                        ]),
                    ),
                ]
            ),
            html.Tr([html.Br()]),
            html.Tr(
                [
                    html.Th(
                        html.Button(
                            "Download Plotted Data",
                            title="Download a text file of the data in JSON format",
                            id="btn_download2",
                        )
                    ),
                    html.Th(
                        dcc.RadioItems(
                            options=[
                                {"label": "log Y axis", "value": "log"},
                                {"label": "linear Y axis", "value": "linear"},
                            ],
                            value="log",
                            id="yaxis_scale",
                        ),
                    ),
                    # TODO add slider from SO
                    # https://stackoverflow.com/questions/61896144/dash-range-slider-with-input-on-each-side
                    html.Th(
                        html.Div(title='Enter both Y lower and Y upper limit to use, works best on linear Y scale.', children=[
                            dcc.Input(
                                    id="y_lower_limit",
                                    type='text',
                                    placeholder='Y axis lower limit in eV',
                            ),
                        ]),
                    ),
                    html.Th(
                        html.Div(title='Enter both Y lower and Y upper limit to use, works best on linear Y scale.', children=[
                            dcc.Input(
                                    id="y_upper_limit",
                                    type='text',
                                    placeholder='Y axis upper limit in eV'
                            ),
                        ]),
                    ),
                ]
            ),
        ],
        style={"width": "100%"},
    ),
    html.Br(),
    dcc.Loading(
        id="loading-1",
        type="default",
        children=html.Div(id="graph_container")
    ),
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
    html.Div(
        [
            html.Label("XSPlot is an open-source project powered by "),
            html.A("OpenMC", href="https://docs.openmc.org/en/stable/"),
            html.Label(", "),
            html.A(" Plotly", href="https://plotly.com/"),
            html.Label(", "),
            html.A(" Dash", href="https://dash.plotly.com/"),
            html.Label(", "),
            html.A(" Dash datatable", href="https://dash.plotly.com/datatable"),
            html.Label(", "),
            html.A(" Flask", href="https://flask.palletsprojects.com/en/2.0.x/"),
            html.Label(", "),
            html.A(" Gunicorn", href="https://gunicorn.org/"),
            html.Label(", "),
            html.A(" Docker", href="https://www.docker.com"),
            html.Label(", "),
            html.A(" GCloud", href="https://cloud.google.com"),
            html.Label(", "),
            html.A(" Python", href="https://www.python.org/"),
            html.Label(" with the source code available on "),
            html.A(" GitHub", href="https://github.com/openmc-data-storage"),
        ],
        style={"text-align": "center"},
    ),
    html.Br(),
    html.Div(
        [
            html.Label("Links to alternative cross section plotting websites: "),
            html.A("NEA JANIS", href="https://www.oecd-nea.org/jcms/pl_39910/janis"),
            html.Label(", "),
            html.A(" IAEA ENDF", href="https://www-nds.iaea.org/exfor/endf.htm"),
            html.Label(", "),
            html.A(" IAEA Libraries", href="https://nds.iaea.org/dataexplorer"),
            html.Label(", "),
            html.A(" NNDC Sigma", href="https://www.nndc.bnl.gov/sigma/"),
            html.Label(", "),
            html.A(
                " Nuclear Data Center JAEA",
                href="https://wwwndc.jaea.go.jp/ENDF_Graph/",
            ),
            html.Label(", "),
            html.A("T2 LANL", href="https://t2.lanl.gov/nis/data/endf/index.html"),
            html.Label(", "),
            html.A("Nuclear Data Center KAERI", href="https://atom.kaeri.re.kr"),
        ],
        style={"text-align": "center"},
    ),
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
    Output("graph_container", "children"),
    [
        Input("datatable-interactivity", "selected_rows"),
        Input("xaxis_scale", "value"),
        Input("yaxis_scale", "value"),
        Input("x_axis_units", "value"),
        Input("x_lower_limit", "value"),
        Input("x_upper_limit", "value"),
        Input("y_lower_limit", "value"),
        Input("y_upper_limit", "value"),
    ]
)
def update_graphs(
    selected_rows,
    xaxis_scale,
    yaxis_scale,
    x_axis_units,
    x_lower_limit,
    x_upper_limit,
    y_lower_limit,
    y_upper_limit,
):
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
        with open(fn) as json_file:
            xs = load(json_file)

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

    energy_units = f"[{x_axis_units_text[x_axis_units]}]"
    xs_units = "[barns]"


    if len(selected_rows) != 0:
        fig={
            "data": all_x_y_data,
            "layout": {
                "height":800,
                # "width":1600,
                "margin": {"l": 3, "r": 2, "t": 15, "b": 60},
                "xaxis": {
                    "title": {"text": f"Energy {energy_units}"},
                    "type": xaxis_scale,
                    "tickformat": ".1e",
                    "tickangle": 45,
                    "rangemode": 'nonnegative'
                },
                "yaxis": {
                    "automargin": True,
                    "title": {"text": f"Microscopic Cross Section {xs_units}"},
                    "type": yaxis_scale,
                    "tickformat": ".1e",
                },
                "showlegend": True,
                # "height": 250,
                # "margin": {"t": 10, "l": 10, "r": 10},
            },
        }

        if x_upper_limit is not None and x_lower_limit is not None:
            try:
                float_values = (float(x_lower_limit), float(x_upper_limit))
                fig["layout"]["xaxis"]["range"]=float_values
            except:
                fig["layout"]["xaxis"]["range"]=None
        else:
            fig["layout"]["xaxis"]["range"]=None

        if y_upper_limit is not None and y_lower_limit is not None:
            try:
                float_values = (float(y_lower_limit), float(y_upper_limit))
                fig["layout"]["yaxis"]["range"]=float_values
            except:
                fig["layout"]["yaxis"]["range"]=None
                
        else:
            fig["layout"]["yaxis"]["range"]=None


        return [
            dcc.Graph(
                # config=dict(showSendToCloud=True),
                figure=fig
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
                        all_x_y_data.append(downloaded_xs_data[k])

                return dict(
                    content=dumps(all_x_y_data, indent=2),
                    filename="xsplot_download.json",
                )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8080)
