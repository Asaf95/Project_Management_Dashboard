""" constants  for App"""
import pandas as pd

DATA_TABLE_COLUMNS = [
    {
        "id": "Task",
        "name": "Task",
    },
    {
        "id": "Duration",
        "name": "Days",
        "type": "numeric",
    },
    {"id": "Resource", "name": "Resource", "presentation": "dropdown"},
    {"id": "Start", "name": "Start", "type": "datetime"},
    {"id": "Finish", "name": "End", "type": "datetime", "editable": False},
]

DATA_TABLE_STYLE = {
    "style_data_conditional": [
        {"if": {"column_id": "Finish"}, "backgroundColor": "#eee"}
    ],
    "style_header": {
        "color": "white",
        "backgroundColor": "#799DBF",
        "fontWeight": "bold",
    },
    "css": [
        {"selector": ".Select-value", "rule": "padding-right: 22px"},  # makes space for the dropdown caret
        {"selector": ".dropdown", "rule": "position: static"}  # makes dropdown visible
    ]
}

# Default new row for datatable
new_task_line = {
    "Task": "",
    "Start": "2016-01-01",
    "Duration": 0,
    "Resource": "A",
    "Finish": "2016-01-01",
}
df_new_task_line = pd.DataFrame(new_task_line, index=[0])
