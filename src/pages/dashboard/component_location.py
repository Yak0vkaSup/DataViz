from dash import dcc, html, Input, Output, callback
from config import load_region_dept_commune_map

region_dept_commune_map = load_region_dept_commune_map()

region_options = [{'label': region, 'value': region} for region in region_dept_commune_map.keys()]
local_type_options = [
    {'label': 'Maison', 'value': 'Maison'},
    {'label': 'Dépendance', 'value': 'Dépendance'},
    {'label': 'Appartement', 'value': 'Appartement'},
    {'label': 'Local industriel, commercial ou assimilé', 'value': 'Local industriel. commercial ou assimilé'}
]

def LocationComponent():
    default_region = region_options[0]['value']  # Use the first region as default
    dropdown_style = {
        'width': '400px',
        'marginBottom': '15px',
    }
    return html.Div(
        children=[
            html.H2('Select location', style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='region-dropdown',
                options=region_options,
                value=default_region,
                placeholder='Select a Region',
                style=dropdown_style,
            ),
            dcc.Dropdown(
                id='department-dropdown',
                placeholder='Select a Department',
                style=dropdown_style,
            ),
            dcc.Dropdown(
                id='commune-dropdown',
                placeholder='Select a Commune',
                style=dropdown_style,
            ),
            dcc.Dropdown(
                id='local-type-dropdown',
                options=local_type_options,
                placeholder='Select a Local Type',
                style=dropdown_style,
            ),
            dcc.Store(id='selected-location', data={}),
        ]
    )

# Callbacks for dynamic dropdowns
@callback(
    Output('department-dropdown', 'options'),
    Output('department-dropdown', 'value'),
    Input('region-dropdown', 'value'),
)
def update_departments(region):
    if region is None:
        return [], None
    departments = region_dept_commune_map[region]['departments']
    department_options = [{'label': dept, 'value': dept} for dept in departments.keys()]
    return department_options, None


@callback(
    Output('commune-dropdown', 'options'),
    Output('commune-dropdown', 'value'),
    Input('department-dropdown', 'value'),
    Input('region-dropdown', 'value'),
)
def update_communes(department, region):
    if region is None or department is None:
        return [], None

    # Get communes for the selected department
    communes = region_dept_commune_map[region]['departments'][department]['communes']
    commune_options = [{'label': commune['name'], 'value': commune['name']} for commune in communes]
    return commune_options, None


@callback(
    Output('selected-location', 'data'),
    Input('region-dropdown', 'value'),
    Input('department-dropdown', 'value'),
    Input('commune-dropdown', 'value'),
    Input('local-type-dropdown', 'value'),
)
def save_selected_values(region, department, commune, local_type):
    if not region:
        return {}

    selected_data = {
        'region': region,
        'region_code': None,
        'department': None,
        'department_code': None,
        'commune': None,
        'commune_code': None,
        'local_type': local_type
    }

    region_code = region_dept_commune_map[region]['code']
    selected_data['region_code'] = region_code

    if department:
        department_info = region_dept_commune_map[region]['departments'].get(department, {})
        department_code = department_info.get('code')
        selected_data['department'] = department
        selected_data['department_code'] = department_code

    if commune and department:
        commune_info = next(
            (c for c in region_dept_commune_map[region]['departments'][department]['communes'] if c['name'] == commune),
            None
        )
        commune_code = commune_info['code'] if commune_info else None
        selected_data['commune'] = commune
        selected_data['commune_code'] = commune_code

    print(f"Region: {region}, Region Code: {region_code}")
    print(f"Department: {department}, Department Code: {selected_data['department_code']}")
    print(f"Commune: {commune}, Commune Code: {selected_data['commune_code']}")
    print(f"Local Type: {local_type}")

    return selected_data

