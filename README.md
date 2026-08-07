# EDA Analysis API

A FastAPI + Streamlit project for exploratory data analysis (EDA) over the Stack Overflow Developer Survey. It exposes analytics endpoints for querying salary statistics and developer cohorts, plus a Streamlit dashboard frontend.

## Features

- **FastAPI backend** (`main.py`)
  - `GET /` – dataset overview / system health
  - `GET /analytics/salary` – filter by country, programming language, and minimum years of experience to get salary statistics (mean, median, min, max)
  - `POST /analytics/cohort` — build a custom developer cohort by countries, languages, and minimum salary
- **Streamlit dashboard** (`app.py`) — interactive UI for the salary and cohort endpoints

## Dataset

The project expects a `cleaned_survey_data.csv` file at the project root. Place your own survey data there. If the file is missing, the API falls back to a small built-in sample dataset so the server still runs.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

Start the API server:

```bash
uvicorn main:app --reload
```

- Interactive API docs: <http://127.0.0.1:8000/docs>
- Health check / overview: <http://127.0.0.1:8000/>

In a second terminal, launch the dashboard:

```bash
streamlit run app.py
```

The dashboard points at `http://127.0.0.1:8000` by default (see `BASE_URL` in `app.py`).

## Example API Calls

```bash
curl "http://127.0.0.1:8000/analytics/salary?country=Pakistan&language=Python&min_years_exp=2"
```

```bash
curl -X POST "http://127.0.0.1:8000/analytics/cohort" \
  -H "Content-Type: application/json" \
  -d '{"countries": ["Pakistan", "India"], "languages": ["Python"], "min_salary": 50000, "limit": 10}'
```

## Project Structure

```
.
├── app.py               # Streamlit dashboard
├── main.py              # FastAPI backend
├── requirements.txt     # Python dependencies
└── cleaned_survey_data.csv  # Survey data (add your own; not tracked by git)
```