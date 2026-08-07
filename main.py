from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import numpy as np

app = FastAPI(
    title="Stack Overflow Survey EDA API",
    description="Backend API exposing analytical endpoints over survey data",
    version="1.0.0"
)

# 1. LOAD DATASET (In-Memory Execution)
DATA_PATH = "cleaned_survey_data.csv"

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    df = pd.DataFrame({
        "Respondent_ID": [1, 2, 3, 4, 5],
        "Country": ["Pakistan", "Pakistan", "United States", "India", "Pakistan"],
        "LanguageHaveWorkedWith": ["Python;C++", "Python;SQL", "JavaScript;HTML", "Python;Java", "C++;SQL"],
        "ConvertedCompYearly": [65000.0, 80000.0, 120000.0, 45000.0, 55000.0],
        "YearsCodePro": [2, 5, 8, 3, 1]
    })


# 2. ENDPOINT 1: Dataset Overview / System Health

@app.get("/", tags=["Overview"])
def get_dataset_overview():
    """Returns high-level statistics about the loaded dataset."""
    return {
        "status": "online",
        "total_records": len(df),
        "columns": list(df.columns),
        "countries_available": df["Country"].dropna().unique().tolist()[:10]
    }


# 3. ENDPOINT 2: Filtered Salary Analytics (GET Request)

@app.get("/analytics/salary", tags=["Analytics"])
def get_salary_stats(
    # Query Parameters for filtering
    country: Optional[str] = Query(None, description="Filter by Country"),
    language: Optional[str] = Query(None, description="Filter by Programming Language"),
    min_years_exp: int = Query(0, ge=0, description="Minimum professional coding experience")
):
    temp_df = df.copy()

    if "YearsCodePro" in temp_df.columns:
        temp_df["YearsCodePro_num"] = pd.to_numeric(temp_df["YearsCodePro"], errors="coerce").fillna(0)
    else:
        temp_df["YearsCodePro_num"] = 0
    if "ConvertedCompYearly" in temp_df.columns:
        temp_df["Salary_num"] = pd.to_numeric(temp_df["ConvertedCompYearly"], errors="coerce")
    else:
        temp_df["Salary_num"] = np.nan

    # Apply Filters

    if country:
        temp_df = temp_df[
            temp_df["Country"].astype(str).str.strip().str.lower() == country.strip().lower()
        ]
    
    if language:
        temp_df = temp_df[
            temp_df["LanguageHaveWorkedWith"].astype(str).str.contains(language, case=False, na=False)
        ]
        
    temp_df = temp_df[temp_df["YearsCodePro_num"] >= min_years_exp]

    if temp_df.empty:
        raise HTTPException(status_code=404, detail="No developers match the specified criteria.")

    # Drop NaNs from salary series for clean metric calculation
    salary_series = temp_df["Salary_num"].dropna()

    if salary_series.empty:
        raise HTTPException(status_code=404, detail="Matching developers found, but no salary data is available for them.")

    return {
        "total_matches": int(len(temp_df)),
        "mean_salary": float(round(salary_series.mean(), 2)),
        "median_salary": float(round(salary_series.median(), 2)),
        "max_salary": float(salary_series.max()),
        "min_salary": float(salary_series.min())
    }

# 4. ENDPOINT 3: Custom Cohort Query (POST Request via Pydantic)

class CohortQuerySchema(BaseModel):
    countries: Optional[List[str]] = []
    languages: Optional[List[str]] = []
    min_salary: float = 0.0
    limit: int = 10

@app.post("/analytics/cohort", tags=["Analytics"])
def get_cohort_records(query: CohortQuerySchema):
    temp_df = df.copy()


    country_col = "Country" if "Country" in temp_df.columns else "country"
    lang_col = "LanguageHaveWorkedWith" if "LanguageHaveWorkedWith" in temp_df.columns else "language"
    salary_col = "ConvertedCompYearly" if "ConvertedCompYearly" in temp_df.columns else "salary"


    if query.countries and country_col in temp_df.columns:
        countries_lower = [c.strip().lower() for c in query.countries]
        temp_df = temp_df[
            temp_df[country_col].astype(str).str.strip().str.lower().isin(countries_lower)
        ]


    if query.languages and lang_col in temp_df.columns:
        pattern = "|".join([lang.strip() for lang in query.languages])
        temp_df = temp_df[
            temp_df[lang_col].astype(str).str.contains(pattern, case=False, na=False)
        ]


    if salary_col in temp_df.columns:
        temp_df[salary_col] = pd.to_numeric(temp_df[salary_col], errors="coerce").fillna(0)
        temp_df = temp_df[temp_df[salary_col] >= query.min_salary]

    if temp_df.empty:
        return {"count": 0, "results": []}

    sample_df = temp_df.head(query.limit).fillna("")
    
    return {
        "count": int(len(temp_df)),
        "results": sample_df.to_dict(orient="records")
    }