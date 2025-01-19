from dash import html
from dash import dcc

def Navbar():
    return html.Nav(
        children=[
            html.Div(
                children=[
                    dcc.Link('About', href='/', className='nav-link'),
                    dcc.Link('Dashboard', href='/dashboard', className='nav-link'),
                ],
                className='nav-links-container',
            )
        ],
        className='navbar'
    )
