from dash import html
from DataViz.src.components import Header, Footer, Navbar
from .component_chart import ChartComponent
from .component_pie import PieComponent
from .component_histogramme import HistogrammeComponent

def DashboardPage():
    return html.Div(
        children=[
            Header(),
            Navbar(),
            html.Main(
                children=[
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