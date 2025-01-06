import pandas as pd
from dash import dcc, html, Input, Output, callback
from config import DATA_DIR, load_region_dept_commune_map
import os

DATA_FILE = os.path.join(DATA_DIR, 'full.pkl')
data = pd.read_pickle(DATA_FILE)
map = load_region_dept_commune_map()

# Layout for the pie chart
def PieComponent():
    return html.Div(
        children=[
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
    region = selected_location.get('region')
    department = selected_location.get('department')
    commune = selected_location.get('commune')

    department_code = selected_location.get('department_code')
    commune_code = selected_location.get('commune_code')
    region_code = selected_location.get('region_code')

    title = ''
    # Filter data for the selected location
    if commune_code:
        filtered_data = data[
            (data['code_commune'] == commune_code)
        ]
        title = f'Type Local Distribution for Commune {commune}, {commune_code}'
    elif department_code:
        filtered_data = data[
            (data['code_departement'] == department_code)
        ]
        title = f'Type Local Distribution for Departament {department}, {department_code}'
    else:
        departments = map[region]['departments']
        department_codes = [dept_info['code'] for dept_info in departments.values()]
        filtered_data = data[
            (data['code_departement'].isin(department_codes))
        ]
        title = f'Type Local Distribution for Region {region}, {region_code}'

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
        }
    }
    return figure

