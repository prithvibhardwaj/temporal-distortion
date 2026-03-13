import dash
from dash import dcc, html
from layout import layout
from callbacks import *
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, prevent_initial_callbacks="initial_duplicate",
                external_stylesheets=[dbc.themes.CYBORG])
app.layout = layout

# Add custom CSS for click propagation prevention and browser navigation warning
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Temporal Distortion</title>
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

            // Browser navigation warning functionality
            let dataUploaded = false;
            let hasUnsavedChanges = false;

            // Function to check if data has been uploaded
            function checkDataStatus() {
                // Check if there's data in the store or if graph is visible
                const graphContainer = document.getElementById('graph-container');
                if (graphContainer && graphContainer.style.display !== 'none') {
                    dataUploaded = true;
                } else {
                    dataUploaded = false;
                }
            }

            // Function to mark changes as made
            function markChanges() {
                hasUnsavedChanges = true;
            }

            // Function to clear the unsaved changes flag (when user saves)
            function clearChanges() {
                hasUnsavedChanges = false;
            }

            // Monitor for data uploads and changes
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'attributes' || mutation.type === 'childList') {
                        checkDataStatus();

                        // Check if anomaly data might have changed
                        if (mutation.target.id === 'main-plot' || 
                            mutation.target.closest('#main-plot')) {
                            markChanges();
                        }

                        // Clear changes flag when save notification appears
                        if (mutation.target.id === 'save-notification' && 
                            mutation.target.style.display !== 'none') {
                            clearChanges();
                        }
                    }
                });
            });

            // Start observing
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['style', 'class']
            });

            // Handle beforeunload event (refresh, close tab, navigate away)
            window.addEventListener('beforeunload', function(e) {
                if (dataUploaded || hasUnsavedChanges) {
                    const message = 'You have uploaded data that may be lost. Are you sure you want to leave?';
                    e.returnValue = message; // For older browsers
                    return message; // For modern browsers
                }
            });

            // Handle popstate event (back/forward button)
            window.addEventListener('popstate', function(e) {
                if (dataUploaded || hasUnsavedChanges) {
                    const confirmLeave = confirm('You have uploaded data that may be lost. Are you sure you want to go back?');
                    if (!confirmLeave) {
                        // Push the current state back to prevent navigation
                        history.pushState(null, null, window.location.pathname);
                    }
                }
            });

            // Push initial state to enable popstate detection
            history.pushState(null, null, window.location.pathname);

            // Additional event listeners for specific user actions that indicate changes
            document.addEventListener('click', function(e) {
                // Mark changes when user interacts with anomaly controls
                if (e.target.id === 'inject-anomaly' || 
                    e.target.id === 'remove-anomaly' || 
                    e.target.id === 'reset-anomaly') {
                    markChanges();
                }
            });

            // Listen for plot interactions
            document.addEventListener('plotly_click', function(e) {
                markChanges();
            });

            document.addEventListener('plotly_selected', function(e) {
                markChanges();
            });
        </script>
    </body>
</html>
'''

register_callbacks(app)
server = app.server  # Expose Flask server for WSGI deployment (Vercel, gunicorn)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)