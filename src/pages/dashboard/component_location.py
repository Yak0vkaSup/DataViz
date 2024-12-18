from dash import dcc, html, Input, Output, callback
from DataViz.src.config import load_region_dept_commune_map

# Load the JSON map
region_dept_commune_map = load_region_dept_commune_map()

# Extract region options
region_options = [{'label': region, 'value': region} for region in region_dept_commune_map.keys()]

# Layout for the dropdowns
def LocationComponent():
    return html.Div(
        children=[
            html.H2('Select Region, Department, and Commune'),
            dcc.Dropdown(
                id='region-dropdown',
                options=region_options,
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
    # Get departments for the selected region
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
    if not region or not department or not commune:
        return {}, 'Please select a region, department, and commune.'

    # Retrieve codes from the JSON map
    region_code = region_dept_commune_map[region]['code']
    department_code = region_dept_commune_map[region]['departments'][department]['code']
    commune_info = next(
        (c for c in region_dept_commune_map[region]['departments'][department]['communes'] if c['name'] == commune),
        None
    )
    commune_code = commune_info['code'] if commune_info else None

    # Debugging print statements
    print(f"Region: {region}, Region Code: {region_code}")
    print(f"Department: {department}, Department Code: {department_code}")
    print(f"Commune: {commune}, Commune Code: {commune_code}")

    # Save selected data in Store
    selected_data = {
        'region': region,
        'region_code': region_code,
        'department': department,
        'department_code': department_code,
        'commune': commune,
        'commune_code': commune_code,
    }
    display_text = f"Selected: Region = {region}, Department = {department}, Commune = {commune}"
    return selected_data, display_text

