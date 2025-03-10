import dash
from dash import dcc, html
from layout import layout
from callbacks import *
import dash_bootstrap_components as dbc

app = dash.Dash(__name__,prevent_initial_callbacks="initial_duplicate",
                external_stylesheets=[dbc.themes.CYBORG])
app.layout = layout

# Add custom CSS for click propagation prevention
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* This prevents clicks on the modal content from closing the modal */
            .modal-content {
                pointer-events: auto;
            }
            .modal-overlay {
                pointer-events: auto;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script>
            // Add an event listener to prevent click propagation from modal content to overlay
            document.addEventListener('DOMContentLoaded', (event) => {
                const modalContent = document.querySelector('.modal-content');
                if (modalContent) {
                    modalContent.addEventListener('click', (e) => {
                        e.stopPropagation();
                    });
                }
            });
        </script>
    </body>
</html>
'''

register_callbacks(app)


if __name__ == '__main__':
    app.run_server(debug=False,host='0.0.0.0',port=8050)
