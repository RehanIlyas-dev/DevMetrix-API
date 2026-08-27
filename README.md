# DevMetrix

A FastAPI + Streamlit project for developer-market analytics (EDA) over the Stack Overflow Developer Survey. It exposes analytics endpoints for querying salary statistics and developer cohorts, plus a Streamlit dashboard frontend.

## Features

- **FastAPI backend** (`backend/main.py`)
  - `GET /` – dataset overview / system health
  - `GET /analytics/salary` – filter by country, programming language, and minimum years of experience to get salary statistics (mean, median, min, max)
  - `POST /analytics/cohort` — build a custom developer cohort by countries, languages, and minimum salary
  - `GET /analytics/salary-distribution` — get cleaned salary values (1K–300K) for a country, used to build charts
- **Streamlit dashboard** (`frontend/app.py`) — interactive UI for the salary and cohort endpoints
- **Visual analytics** — the dashboard includes an interactive Plotly salary distribution histogram and a native Streamlit bar chart for the top experience levels

## Dataset

The project expects a `cleaned_survey_data.csv` file in `data/`. Place your own survey data there. If the file is missing, the API falls back to a small built-in sample dataset so the server still runs.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

Start the API server:

```bash
uvicorn backend.main:app --reload
```

- Interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check / overview: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

In a second terminal, launch the dashboard:

```bash
streamlit run frontend/app.py
```

The dashboard points at `http://127.0.0.1:8000` by default (see `BASE_URL` in `frontend/app.py`).

## Example API Calls

```bash
curl "http://127.0.0.1:8000/analytics/salary?country=Pakistan&language=Python&min_years_exp=2"
```

```bash
curl -X POST "http://127.0.0.1:8000/analytics/cohort" \
  -H "Content-Type: application/json" \
  -d '{"countries": ["Pakistan", "India"], "languages": ["Python"], "min_salary": 50000, "limit": 10}'
```

```bash
curl "http://127.0.0.1:8000/analytics/salary-distribution?country=Pakistan"
```

## Running with Docker

Build and run the backend in a container:

```bash
docker build -f Dockerfile.fastapi -t devmetrix-api .
docker run -d -p 8000:8000 --name devmetrix-api devmetrix-api
```

Then access [http://localhost:8000/docs](http://localhost:8000/docs).

## Project Structure

```
.
├── backend/
│   └── main.py            # FastAPI API — analytics endpoints
├── frontend/
│   └── app.py            # Streamlit dashboard
├── data/
│   └── cleaned_survey_data.csv  # Survey dataset
├── Dockerfile.fastapi    # Docker image for the backend
├── requirements.txt      # Python dependencies
└── README.md
```
