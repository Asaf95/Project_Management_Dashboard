import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, html, dcc, Input, Output, dash_table, ctx
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import const

Resource_Color_values = px.colors.qualitative.Alphabet  # @TODO: ADD MORE COLORS TO THE CHARTS and make them all use the same for each resource


def __get_default_table() -> pd.DataFrame:
    return pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/GanttChart.csv"
    )


def add_finish_column(timeline_df: pd.DataFrame) -> pd.DataFrame:
    """
    This function is creates 'Finish' column which is a required column for timeline chart.
    """
    timeline_df["Start"] = pd.to_datetime(timeline_df["Start"])
    timeline_df["Duration"] = timeline_df["Duration"].astype(int)
    timeline_df["Finish"] = timeline_df["Start"] + pd.to_timedelta(timeline_df["Duration"], unit="D")
    timeline_df["Start"] = pd.to_datetime(timeline_df["Start"]).dt.date
    timeline_df["Finish"] = pd.to_datetime(timeline_df["Finish"]).dt.date
    return timeline_df


app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.SPACELAB],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True,
)

app.layout = dbc.Container(
    [
        html.H1("Project Time Line", className="bg-primary text-white p-1 text-center"),
        dbc.Button("Add task", n_clicks=0, id="add-row-btn", size="sm"),
        dash_table.DataTable(
            id="user-datatable",
            sort_action="native",
            columns=const.DATA_TABLE_COLUMNS,
            data=__get_default_table().to_dict("records"),
            editable=True,
            dropdown={
                "Resource": {
                    "clearable": False,
                    "options": [
                        {"label": i, "value": i} for i in ["A", "B", "C", "D"]
                    ],
                },
            },
            css=const.DATA_TABLE_STYLE.get("css"),
            page_size=10,
            row_deletable=True,
            style_data_conditional=const.DATA_TABLE_STYLE.get("style_data_conditional"),
            style_header=const.DATA_TABLE_STYLE.get("style_header"),
        ),
        dcc.Graph(id="gantt-graph"),
        dcc.Graph(id="pie-graph"),
    ],
    fluid=True,
)


def update_datatable(user_datatable):
    # if user deleted all rows, return the default table:
    if not user_datatable:
        updated_table = const.df_new_task_line

    # if button clicked, then add a row
    elif ctx.triggered_id == "add-row-btn":
        updated_table = pd.concat([pd.DataFrame(user_datatable), const.df_new_task_line])

    else:
        updated_table = pd.DataFrame(user_datatable)
    return add_finish_column(updated_table)


def create_gantt_chart(updated_table_as_df) -> px:
    gantt_fig = px.timeline(updated_table_as_df, x_start="Start", x_end="Finish", y="Task", color="Resource",
                            title='Project Plan Gantt Chart')
    # https://stackoverflow.com/questions/63559119/how-to-specify-color-for-elements-in-plotly-gannt-chart
    gantt_fig.update_layout(
        title_x=0.5,
        font=dict(size=16),
        yaxis=dict(title="Task", automargin=True, autorange="reversed", categoryorder="array",
                   categoryarray=updated_table_as_df["Task"]),  # sorting gantt according to datatable
        xaxis=dict(title=""))

    gantt_fig.update_traces(width=0.7)
    return gantt_fig


def create_kpi_charts(updated_table_as_df) -> px:
    df_for_kpi = updated_table_as_df[['Resource', 'Duration']].groupby(['Resource']).agg(
        nunique=('Resource', 'count'), sum=('Duration', 'sum'),
    ).reset_index()  # Using pandas methods on the datatable to create KPI's
    kpi_charts = make_subplots(1, 2, specs=[[{'type': 'domain'}, {'type': 'domain'}]],
                               subplot_titles=['Number of tasks that use the Resource',  # @TODO change names of titles
                                               'Number of tasks that use the Resource'])
    kpi_charts.add_trace(go.Pie(labels=df_for_kpi['Resource'].tolist(), values=df_for_kpi['sum'].tolist(), ), 1, 1)
    kpi_charts.add_trace(
        go.Pie(labels=df_for_kpi['Resource'].tolist(), values=df_for_kpi['nunique'].tolist()), 1,
        2)
    # kpi_charts.update_traces(marker=dict(colors=px.colors.qualitative.Alphabet))
    kpi_charts.update_layout(

        # paper_bgcolor="#DDE6EF",
        font=dict(
            size=20,
            color="#104870"),
    )
    return kpi_charts


@app.callback(
    Output("user-datatable", "data"),
    Output("gantt-graph", "figure"),
    Output("pie-graph", "figure"),
    Input("user-datatable", "derived_virtual_data"),
    Input("add-row-btn", "n_clicks"),
)
def update_table_and_figure(user_datatable: None or list, _) -> (list, dict):
    """
    This callback function returns the timeline chart and the updated datatable for the main app layout
    """
    updated_table_as_df = update_datatable(user_datatable)
    gantt_chart = create_gantt_chart(updated_table_as_df)
    kpi_charts = create_kpi_charts(updated_table_as_df)
    return updated_table_as_df.to_dict("records"), gantt_chart, kpi_charts


if __name__ == "__main__":
    app.run_server(debug=True)
