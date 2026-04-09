# EduMetrics Student Analytics

A Streamlit dashboard for student performance analytics using class data from `data/students.csv`.

## Project Overview

`EduMetrics` provides a visually rich analytics interface for inspecting student scores, attendance, study habits, department comparisons, and risk profiling.

## Key Features

- Interactive Streamlit dashboard with multiple pages:
  - Overview metrics and summary cards
  - Charts for score distribution, grade distribution, attendance vs performance, department trends, gender performance, and correlations
  - Top 10 performers and at-risk student listings
  - Searchable student table with filters for department, grade, and pass/fail status

- Analysis logic separated into `analysis.py`:
  - data loading and preprocessing
  - score and grade calculations
  - chart generation with Plotly
  - summary and table helpers

## Files

- `app.py` — main Streamlit application
- `analysis.py` — data processing and chart helper functions
- `requirements.txt` — Python dependencies
- `data/students.csv` — student dataset used by the app
- `templates/index.html` — optional HTML template content (if used)
- `style.css` — custom styling (if used)

## Requirements

- Python 3.8+
- Streamlit
- pandas
- numpy
- plotly
- statsmodels

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Locally

From the project root:

```bash
streamlit run app.py
```

Then open the local URL displayed in the terminal.

## Notes

- The app reads student records from `data/students.csv` and computes average scores, grades, pass/fail status, and performance bands automatically.
- Modify the CSV dataset to update the dashboard with new student data.
