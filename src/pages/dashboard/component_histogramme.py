from dash import html
from dash import dcc

def HistogrammeComponent():
    return html.Div(
        children=[
            html.H2('Histogramme'),
            dcc.Input(
                id='input-box',
                type='text',
                placeholder='Enter something...',
                className='input'
            ),
            html.Button('Submit', id='button', className='button'),
            html.Div(id='output-container', className='output')
        ],
        className='histogramme-component'
    )