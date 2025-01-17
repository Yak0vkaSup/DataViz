from dash import html

from .component_chart import ChartComponent
from .component_pie import PieComponent
from .component_histogramme import HistogrammeComponent
from .component_location import LocationComponent
from .component_map import MapComponent
from src.components import (Header, Navbar, Footer)


def DashboardPage():
    return html.Div(
        children=[
            Header(),
            Navbar(),
            html.Main(
                children=[
                    html.Div(
                        MapComponent(),
                        style={'width': '80vw', 'margin': '0 auto'},
                    ),
                    LocationComponent(),
                    html.Div(
                        PieComponent(),
                        style={'width': '80vw', 'margin': '0 auto'},  # Center and increase width
                    ),
                    html.Div(
                        ChartComponent(),
                        style={'width': '80vw', 'margin': '0 auto'},
                    ),
                    html.Div(
                        HistogrammeComponent(),
                        style={'width': '80vw', 'margin': '0 auto'},
                    ),
                ],
                className='main-content',
                style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'},  # Center align all components
            ),
            Footer()
        ],
        className='complex-page',
    )
