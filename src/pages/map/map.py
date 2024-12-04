from dash import html
from dash import dcc

def MapComponent():
    return html.Div(
        children=[
            html.H2('Complex Component'),
            dcc.Input(
                id='input-box',
                type='text',
                placeholder='Select the region...',
                className='input'
            ),
            html.Button('Submit', id='button', className='button'),
            html.Div(id='output-container', className='output')
        ],
        className='complex-component'
    )