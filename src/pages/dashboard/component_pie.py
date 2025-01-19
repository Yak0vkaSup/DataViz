import pandas as pd
from dash import dcc, html, Input, Output, callback
from src.utils.config import DATA_DIR, load_region_dept_commune_map
import os

DATA_FILE = os.path.join(DATA_DIR, 'full.pkl')
data = pd.read_pickle(DATA_FILE)
map = load_region_dept_commune_map()

# Layout for the pie chart
def PieComponent():
    return html.Div(
        children=[
            html.H2('Pie Chart of Type Local'),
            dcc.Graph(
                id='type-local-pie-chart',
                config={'displayModeBar': False},  # Hides the mode bar for a cleaner look
                style={'height': '400px', 'width': '100%'},  # Adjust height and width
            ),
        ],
        className='pie-chart-container',  # Add a class for styling
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
    region = selected_location.get('region')
    department_code = selected_location.get('department_code')
    department = selected_location.get('department')
    commune_code = selected_location.get('commune_code')
    commune = selected_location.get('commune')

    title = ''
    # Filter data for the selected location
    if commune_code:
        filtered_data = data[
            (data['code_commune'] == commune_code)
        ]
        title = f'Type Local Distribution for Commune {commune}'
    elif department_code:
        filtered_data = data[
            (data['code_departement'] == department_code)
        ]
        title = f'Type Local Distribution for Department {department}'
    else:
        departments = map[region]['departments']
        department_codes = [dept_info['code'] for dept_info in departments.values()]
        filtered_data = data[
            (data['code_departement'].isin(department_codes))
        ]
        title = f'Type Local Distribution for Region {region}'

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
            'title': title,
            'height': 400,
            'margin': {'l': 10, 'r': 10, 't': 50, 'b': 10},
        }
    }
    return figure