# Temporal Distortion

A web-based tool for interactive annotation of anomalies in time series data, built with Plotly Dash.

## Overview

Temporal Distortion allows researchers and analysts to upload time series data in CSV format, visualize it as an interactive plot, and manually label or correct anomaly annotations. Annotated data can be exported back to CSV for downstream use in machine learning pipelines or analysis workflows.

## Features

### Data Upload
- Upload any CSV file containing time series data via the sidebar upload button.
- Upon upload, a dialog prompts for the column names corresponding to timestamps, values, and (optionally) anomaly labels.
- Common column names (`timestamp`, `value`, `meter_reading`, `anomaly`, `outlier`, etc.) are detected automatically and pre-filled.
- If no anomaly column exists, one is created and initialized to zero.

### Visualization
- Time series data is rendered as an interactive Plotly line chart with a dark theme.
- Anomalies are overlaid as semi-transparent vertical red lines.
- A range slider below the chart allows navigation across large datasets.
- Crosshair spike lines display on hover for precise time inspection.
- Zoom, pan, and selection tools are available in the plot toolbar.

### Anomaly Annotation
Annotations can be modified in two ways:

**Point-level toggle:** Click any point on the plot to toggle its anomaly label between 0 and 1.

**Range-based operations:** Select a mode using the control buttons, then drag a horizontal selection on the plot to apply the operation to all points in the selected time range.
- **Mark** — sets all selected points as anomalies (label = 1).
- **Unmark** — removes anomaly labels from all selected points (label = 0).
- **Reset** — restores the original anomaly labels from the uploaded file for the selected range.

The active mode is highlighted in green and displayed below the control buttons.

### Data Export
- **CSV download:** The save button exports the current annotated data as a CSV file, preserving the original filename.
- **Plot screenshot:** Exports a high-resolution PNG image (1400x800, 2x scale) of the current plot, rendered via Kaleido.

### Modals and Panels
- **Data Table:** Displays the full dataset in a scrollable, sortable table. Reflects any annotation changes in real time.
- **Statistics:** Shows the uploaded filename, total number of data points, and current anomaly count.
- **Help:** In-app usage instructions with a link to the full user guide.

### Browser Safety
- A `beforeunload` warning is displayed if the user attempts to close or navigate away from the page after uploading data, preventing accidental data loss.
- Back-button navigation is also intercepted and requires confirmation.

## Input Format

The application expects a CSV file with the following structure:

| Column | Required | Accepted Names | Format |
|---|---|---|---|
| Timestamp | Yes | `timestamp`, `timestamps`, `date_time`, `datetime` | `%Y-%m-%d %H:%M:%S` |
| Value | Yes | `value`, `values`, `meter_reading`, `meter_readings` | Numeric |
| Anomaly | No | `anomaly`, `anomalies`, `outlier`, `outliers`, `fault`, `faults` | Binary (0 or 1) |

Column names not matching any of the above are entered manually in the dialog after upload.

## Tech Stack

- **[Dash](https://dash.plotly.com/)** — Python web framework for interactive data applications
- **[Plotly](https://plotly.com/python/)** — Interactive charting library
- **[Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)** — Bootstrap-themed UI components (Cyborg theme)
- **[Pandas](https://pandas.pydata.org/)** — Data loading and manipulation
- **[NumPy](https://numpy.org/)** — Numerical operations
- **[scikit-learn](https://scikit-learn.org/)** — Machine learning utilities
- **[Kaleido](https://github.com/plotly/Kaleido)** — Static image export for Plotly figures

## Local Setup

**Prerequisites:** Python 3.9 or later.

```bash
# Clone the repository
git clone https://github.com/<your-username>/temporal-distortion.git
cd temporal-distortion

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The application will be available at `http://localhost:8050`.

## Deployment (Vercel)

The repository includes a `vercel.json` configuration for deployment on Vercel.

1. Install the [Vercel CLI](https://vercel.com/docs/cli) and log in.
2. Run `vercel` from the project root and follow the prompts.

> **Note:** The screenshot export feature requires Kaleido, which depends on Chromium and may not be available in all serverless environments. All other features will work without it.

## Project Structure

```
temporal_distortion/
├── app.py           # Application entry point and custom HTML shell
├── layout.py        # Dash layout definition (components and modals)
├── callbacks.py     # All Dash callback logic (data processing, annotation, export)
├── requirements.txt # Python dependencies
└── vercel.json      # Vercel deployment configuration
```

## License

This project was developed at the Indian Institute of Science (IISc), Bangalore.
