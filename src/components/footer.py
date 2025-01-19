from dash import html

def Footer():
    return html.Footer(
        children=[
            html.P('© 2024 PVE project github.com/yak0vkaSup'),
        ],
        className='footer'
    )