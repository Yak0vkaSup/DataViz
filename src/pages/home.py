from dash import html
from components import Header, Footer, Navbar

def HomePage():
    return html.Div(
        children=[
            Header(),
            Navbar(),
            html.Main(
                children=[
                    html.H2('Welcome to the Home Page'),
                    html.P('This is the main content area of the home page.'),
                ],
                className='main-content'
            ),
            Footer()
        ],
        className='home-page'
    )