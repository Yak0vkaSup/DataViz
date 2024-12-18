import pandas as pd
from dash import dcc, html, Input, Output, callback
from DataViz.src.config import DATA_DIR
import os

# Load preprocessed data
DATA_FILE = os.path.join(DATA_DIR, 'full.pkl')
data = pd.read_pickle(DATA_FILE)

# Layout for the pie chart
def PieComponent():
    return html.Div(
        children=[
            html.H2('Pie Chart of Type Local'),
            dcc.Graph(id='type-local-pie-chart'),
        ],
    )

@callback(
    Output('type-local-pie-chart', 'figure'),
    Input('selected-location', 'data'),
)
def update_pie_chart(selected_location):
    if not selected_location:
        return {
            'data': [],
            'layout': {'title': 'No data available. Please select a location.'}
        }

    # Retrieve numeric codes for filtering
    region_code = selected_location.get('region_code')
    department_code = selected_location.get('department_code')
    commune_code = selected_location.get('commune_code')

    # Filter data for the selected location
    filtered_data = data[
        (data['code_commune'] == commune_code)
    ]
    print(filtered_data)
    print(commune_code)
    if filtered_data.empty:
        return {
            'data': [],
            'layout': {'title': f'No data available for Commune {commune_code}'}
        }

    # Create pie chart for 'type_local'
    pie_data = filtered_data['type_local'].value_counts()

    figure = {
        'data': [
            {
                'labels': pie_data.index,
                'values': pie_data.values,
                'type': 'pie',
                'name': 'Type Local Distribution',
            }
        ],
        'layout': {
            'title': f'Type Local Distribution for Commune {commune_code}',
        }
    }
    return figure

