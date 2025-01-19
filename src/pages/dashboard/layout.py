from dash import html
from .component_chart import ChartComponent
from .component_pie import PieComponent
from .component_histogramme import HistogrammeComponent
from .component_location import LocationComponent
from .component_map import MapComponent
from src.components import Header, Navbar, Footer

def DashboardPage():
    return html.Div(
        children=[
            Header(),
            Navbar(),
            html.Main(
                children=[
                    html.Div(
                        children=[
                            html.Div(MapComponent(), className='map-section'),
                            html.Div(
                                children=[
                                    PieComponent(),
                                    LocationComponent(),  # Le dropdown est maintenant sous le pie chart
                                ],
                                className='pie-and-dropdown-section',
                            ),
                        ],
                        className='map-and-pie-container',
                    ),
                    html.Div(
                        ChartComponent(),
                        className='dashboard-section chart-section',
                    ),
                    html.Div(
                        HistogrammeComponent(),
                        className='dashboard-section histogram-section',
                    ),
                ],
                className='main-content',
            ),
            Footer()
        ],
        className='dashboard-page',
    )
