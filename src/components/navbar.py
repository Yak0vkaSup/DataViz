from dash import html
from dash import dcc

def Navbar():
    return html.Nav(
        children=[
            dcc.Link('Home', href='/', className='nav-link'),
            dcc.Link('Map', href='/map', className='nav-link'),
            dcc.Link('About', href='/about', className='nav-link'),
            dcc.Link('Dashboard', href='/dashboard', className='nav-link'),
        ],
        className='navbar'
    )