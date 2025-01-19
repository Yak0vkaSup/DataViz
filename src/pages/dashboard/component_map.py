import os
from dash import html, dcc, Input, Output, callback
from src.utils.config import DATA_DIR

def MapComponent():
    """
    Layout for the interactive map component.
    """
    return html.Div(
        children=[
            html.H2('Interactive Map: Zoom on Departments and Communes'),
            html.Iframe(
                id='map',  # The iframe to display the map
                srcDoc='',  # Initially empty, will be updated dynamically
                width='100%',
                height='600'
            ),
            dcc.Store(id='selected-location'),  # Store for selected location data
        ],
        className='map-component'
    )

# Callback to dynamically update the map
@callback(
    Output('map', 'srcDoc'),  # Update the iframe's content
    Input('selected-location', 'data'),  # Trigger when the location changes
)
def update_map(selected_location):

    base_path = os.path.abspath(DATA_DIR)
    """
    Callback to update the displayed map based on selected location.
    """

    # Retrieve selected location details
    department_code = selected_location.get('department_code')
    commune_code = selected_location.get('commune_code')
    region = selected_location.get('region')

    # Determine which file to load based on the selection
    if department_code:
        file_path = os.path.join(base_path,'departements_maps',f'price_per_m2_per_department_{department_code}_choropleth_map.html'
        )
    elif region:
        file_path = os.path.join(base_path,
                                 'regions_maps',
                                 f'price_per_m2_{region.replace(" ", "_")}_choropleth_map.html'
        )
    else:
        # Default map for regions or no selection
        file_path = os.path.join(base_path,
                                 'payss_maps',
            'price_per_m2_region_choropleth_map.html'
        )

    # Check if the file exists
    if not os.path.exists(file_path):
        return f"<h4>No map available for the selected location: {department_code or commune_code}, for filepath {file_path}</h4>"

    # Load the HTML content of the map file
    with open(file_path, 'r', encoding='utf-8') as file:
        map_content = file.read()

    return map_content
