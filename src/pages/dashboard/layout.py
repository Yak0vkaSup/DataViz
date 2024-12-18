from dash import html
from components import Header, Footer, Navbar
from .component_chart import ChartComponent
from .component_pie import PieComponent
from .component_histogramme import HistogrammeComponent
from .component_location import LocationComponent
def DashboardPage():
    return html.Div(
        children=[
            Header(),
            Navbar(),
            html.Main(
                children=[
                    LocationComponent(),
                    ChartComponent(),
                    PieComponent(),
                    HistogrammeComponent(),
                ],
                className='main-content'
            ),
            Footer()
        ],
        className='complex-page'
    )