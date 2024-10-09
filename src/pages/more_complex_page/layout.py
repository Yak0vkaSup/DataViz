from dash import html
from DataViz.src.components import Header, Footer, Navbar
from .page_specific_component import ComplexComponent

def ComplexPage():
    return html.Div(
        children=[
            Header(),
            Navbar(),
            html.Main(
                children=[
                    ComplexComponent(),
                ],
                className='main-content'
            ),
            Footer()
        ],
        className='complex-page'
    )