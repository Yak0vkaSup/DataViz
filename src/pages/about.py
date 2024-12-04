from dash import html
from src.components import Header, Footer, Navbar

def AboutPage():
    return html.Div(
        children=[
            Header(),
            Navbar(),
            html.Main(
                children=[
                    html.H2('About Us'),
                    html.P('Information about the company or application.'),
                ],
                className='main-content'
            ),
            Footer()
        ],
        className='about-page'
    )