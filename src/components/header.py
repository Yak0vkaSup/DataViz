from dash import html
from dash import dcc

def Header():
    return html.Header(
        children=[
            html.H1('Dashboard for quant finance', className='header-title'),
        ],
        className='header'
    )