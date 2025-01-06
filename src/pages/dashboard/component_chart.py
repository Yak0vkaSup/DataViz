import pandas as pd
from dash import dcc, html, Input, Output, callback
from config import DATA_DIR
import os

# Load the preprocessed data
DATA_FILE = os.path.join(DATA_DIR, 'full_with_region.pkl')
data = pd.read_pickle(DATA_FILE)

# Layout for the chart with moving average slider
def ChartComponent():
    return html.Div(
        children=[
            html.H2('Price Movement Over Time with Moving Average'),
            dcc.Graph(id='price-movement-chart'),
            html.Div(
                children=[
                    html.Label('Moving Average Window:'),
                    dcc.Slider(
                        id='ma-slider',
                        min=7,
                        max=30,
                        step=1,
                        value=14,  # Default window size
                        marks={i: str(i) for i in range(7, 31, 5)},
                    )
                ],
                style={'marginTop': '20px'}
            ),
        ],
        className='chart-component'
    )

# Callback to update the chart
@callback(
    Output('price-movement-chart', 'figure'),
    [Input('selected-location', 'data'), Input('ma-slider', 'value')],
)
def update_chart(selected_location, ma_window):
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
        title = f"Price Movement for Commune {commune_code}"
    elif department_code:
        filtered_data = filtered_data[filtered_data['code_departement'] == department_code]
        title = f"Price Movement for Department {department_code}"
    elif region:
        filtered_data = filtered_data[filtered_data['region'] == region]
        title = f"Price Movement for Region {region}"
    else:
        title = "Price Movement"

    # Check for empty filtered data
    if filtered_data.empty:
        return {
            'data': [],
            'layout': {'title': 'No data available for the selected location.'}
        }

    # Prepare the data for the chart
    filtered_data['date_mutation'] = pd.to_datetime(filtered_data['date_mutation'])
    time_series = filtered_data.groupby('date_mutation')['price_per_m2'].mean().reset_index()

    # Create a new column with filled values for MA calculation
    all_dates = pd.date_range(start=time_series['date_mutation'].min(), end=time_series['date_mutation'].max())
    time_series_filled = time_series.set_index('date_mutation').reindex(all_dates, fill_value=0).reset_index()
    time_series_filled.columns = ['date_mutation', 'price_per_m2']
    time_series['price_per_m2_filled'] = time_series_filled['price_per_m2']

    # Add a moving average based on the filled column
    time_series['moving_average'] = time_series['price_per_m2_filled'].rolling(window=ma_window, min_periods=1).mean()

    # Create the figure
    figure = {
        'data': [
            {
                'x': time_series['date_mutation'],
                'y': time_series['price_per_m2'],
                'type': 'line',
                'name': 'Average Price per m²',
            },
            {
                'x': time_series['date_mutation'],
                'y': time_series['moving_average'],
                'type': 'line',
                'name': f'{ma_window}-Day Moving Average',
            }
        ],
        'layout': {
            'title': title,
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Average Price per m²'},
        }
    }
    return figure
