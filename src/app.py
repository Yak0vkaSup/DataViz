import dash
from dash.dependencies import Input, Output
from dash import html, dcc
from src.pages.about import AboutPage
from src.pages.dashboard.layout import DashboardPage

# Initialize the app
def create_app():
    # Initialize the app
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
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
            return AboutPage()
        elif pathname == '/dashboard':
            return DashboardPage()
        else:
            return html.H1('404 - Page not found', style={'textAlign': 'center'})
    return app


# # Run the app
# if __name__ == '__main__':
#     app = create_app()
#     app.run_server(debug=True)
