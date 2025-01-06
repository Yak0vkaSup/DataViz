from dash import html
from dash import dcc

def Navbar():
    link_style = {
        'margin': '0 15px',
        'textDecoration': 'none',
        'color': '#007bff',
        'fontWeight': 'bold',
        'transition': 'color 0.3s ease',
    }

    nav_style = {
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'padding': '1rem',
    }

    return html.Nav(
        children=[
            dcc.Link('Home', href='/', style=link_style),
            dcc.Link('About', href='/about', style=link_style),
            dcc.Link('Dashboard', href='/dashboard', style=link_style),
        ],
        style=nav_style
    )
