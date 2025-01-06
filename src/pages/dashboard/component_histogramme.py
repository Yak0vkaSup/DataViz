import pandas as pd
from dash import dcc, html, Input, Output, callback
from config import DATA_DIR
import os

# Load the preprocessed data
DATA_FILE = os.path.join(DATA_DIR, 'full_with_region.pkl')
data = pd.read_pickle(DATA_FILE)

# Layout for the histogram
def HistogrammeComponent():
    return html.Div(
        children=[
            html.H2('Price per Square Meter Distribution'),
            dcc.Graph(id='price-histogram'),
        ],
        className='histogramme-component'
    )

# Callback to update the histogram
@callback(
    Output('price-histogram', 'figure'),
    Input('selected-location', 'data'),
)
def update_histogram(selected_location):
    # Default filtering: no data available
    if not selected_location:
        return {
            'data': [],
            'layout': {'title': 'No data available. Please select a location.'}
        }

    # Retrieve selected location filters
    region = selected_location.get('region')
    department_code = selected_location.get('department_code')
    commune_code = selected_location.get('commune_code')

    # Filter data dynamically
    filtered_data = data.copy()
    if commune_code:
        filtered_data = filtered_data[filtered_data['code_commune'] == commune_code]
        title = f"Price Distribution for Commune {commune_code}"
    elif department_code:
        filtered_data = filtered_data[filtered_data['code_departement'] == department_code]
        title = f"Price Distribution for Department {department_code}"
    elif region:
        filtered_data = filtered_data[filtered_data['region'] == region]
        title = f"Price Distribution for Region {region}"
    else:
        title = "Price Distribution"

    # Check for empty filtered data
    if filtered_data.empty:
        return {
            'data': [],
            'layout': {'title': 'No data available for the selected location.'}
        }

    # Create histogram bins (e.g., 0–1,000, 1,000–2,000, etc.)
    bins = range(0, 15000, 500)  # From 0 to 20,000 in 1,000 increments
    filtered_data['price_bin'] = pd.cut(filtered_data['price_per_m2'], bins=bins)

    # Count the number of properties in each bin
    histogram_data = filtered_data['price_bin'].value_counts().sort_index()
    bin_labels = [f"{int(interval.left)}–{int(interval.right)}" for interval in histogram_data.index]

    # Create the histogram figure
    figure = {
        'data': [
            {
                'x': bin_labels,
                'y': histogram_data.values,
                'type': 'bar',
                'name': 'Price Distribution',
            }
        ],
        'layout': {
            'title': title,
            'xaxis': {'title': 'Price per Square Meter (€)', 'automargin': True},
            'yaxis': {'title': 'Number of Properties'},
            'bargap': 0.2,  # Add spacing between bars
        },
    }
    return figure
