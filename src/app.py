"""
This module initializes the Dash application and sets up routing for pages.
"""

import dash
from dash.dependencies import Input, Output
from dash import html, dcc
from src.pages.about import AboutPage
from src.pages.dashboard.layout import DashboardPage


def create_app():
    """
    Create and configure the Dash app.

    Returns:
        dash.Dash: Configured Dash app instance.
    """
    # Initialize the app
    app = dash.Dash(__name__, suppress_callback_exceptions=True)

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
        if pathname == '/dashboard':
            return DashboardPage()
        return html.H1('404 - Page not found', style={'textAlign': 'center'})

    return app


# # Uncomment to run the app
# if __name__ == '__main__':
#     app = create_app()
#     app.run_server(debug=True)
