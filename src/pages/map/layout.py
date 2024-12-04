from dash import html
from src.components import Header, Footer, Navbar
from .map import MapComponent

def MapPage():
    return html.Div(
        children=[
            Header(),
            Navbar(),
            html.Main(
                children=[
                    MapComponent(),
                ],
                className='main-content'
            ),
            Footer()
        ],
        className='complex-page'
    )