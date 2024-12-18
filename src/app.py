import dash
from dash.dependencies import Input, Output
from dash import html, dcc
from DataViz.src.pages.home import HomePage
from .pages.about import AboutPage
from .pages.dashboard.layout import DashboardPage

# Initialize the app
app = dash.Dash(__name__)
server = app.server  # For deploying to a server

# Define the app layout
app.layout = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ]
)

# Update page content based on the URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return HomePage()
    elif pathname == '/about':
        return AboutPage()
    elif pathname == '/dashboard':
        return DashboardPage()
    else:
        return html.H1('404 - Page not found', style={'textAlign': 'center'})

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
