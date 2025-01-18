from dash import dcc, html, Input, Output, callback
from src.utils.config import load_region_dept_commune_map

# Load the JSON map
region_dept_commune_map = load_region_dept_commune_map()


# Extract region options
region_options = [{'label': region, 'value': region} for region in region_dept_commune_map.keys()]

# Layout for the dropdowns
def LocationComponent():
    default_region = region_options[0]['value']  # Use the first region as default
    return html.Div(
        children=[
            html.H2('Select Region, Department, and Commune'),
            dcc.Dropdown(
                id='region-dropdown',
                options=region_options,
                value=default_region,
                placeholder='Select a Region',
            ),
            dcc.Dropdown(
                id='department-dropdown',
                placeholder='Select a Department',
            ),
            dcc.Dropdown(
                id='commune-dropdown',
                placeholder='Select a Commune',
            ),
            dcc.Store(id='selected-location', data={}),  # Store for selected values
            html.Div(id='output-container'),
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
    Output('output-container', 'children'),
    Input('region-dropdown', 'value'),
    Input('department-dropdown', 'value'),
    Input('commune-dropdown', 'value'),
)
def save_selected_values(region, department, commune):
    if not region:
        return {}, 'Please select a region.'

    # Initialize the selected data
    selected_data = {'region': region, 'region_code': None, 'department': None, 'department_code': None, 'commune': None, 'commune_code': None}

    # Retrieve region code
    region_code = region_dept_commune_map[region]['code']
    selected_data['region_code'] = region_code

    # Retrieve department code (if a department is selected)
    if department:
        department_info = region_dept_commune_map[region]['departments'].get(department, {})
        department_code = department_info.get('code')
        selected_data['department'] = department
        selected_data['department_code'] = department_code

    # Retrieve commune code (if a commune is selected)
    if commune and department:
        commune_info = next(
            (c for c in region_dept_commune_map[region]['departments'][department]['communes'] if c['name'] == commune),
            None
        )
        commune_code = commune_info['code'] if commune_info else None
        selected_data['commune'] = commune
        selected_data['commune_code'] = commune_code

    # Debugging print statements
    print(f"Region: {region}, Region Code: {region_code}")
    print(f"Department: {department}, Department Code: {selected_data['department_code']}")
    print(f"Commune: {commune}, Commune Code: {selected_data['commune_code']}")

    # Prepare display text
    display_text = f"Selected: Region = {region}"
    if department:
        display_text += f", Department = {department}"
    if commune:
        display_text += f", Commune = {commune}"

    return selected_data, display_text


