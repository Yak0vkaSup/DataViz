from dash import html

def Component1():
    return html.Div(
        children=[
            html.H2('Component 1'),
            html.P('This is an example of a reusable component.')
        ],
        className='component1'
    )