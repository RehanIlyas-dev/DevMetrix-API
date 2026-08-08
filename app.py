import streamlit as st
import requests
import plotly.express as px
import os

st.set_page_config(page_title="Salary Analytics Dashboard", layout="wide")

BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
if BASE_URL and not BASE_URL.startswith(("http://", "https://")):
    BASE_URL = "https://" + BASE_URL
if not os.getenv("BACKEND_URL"):
    st.sidebar.warning("BACKEND_URL not set — using local fallback. Set it in Streamlit Cloud Settings → Secrets → BACKEND_URL")

st.sidebar.header("Filters")
st.sidebar.selectbox('Select Country', ['United States of America', 'Germany', 'United Kingdom of Great Britain and Northern Ireland', 'France', 'Canada', 'India', 'Netherlands', 'Italy', 'Brazil', 'Australia', 'Poland', 'Spain', 'Ukraine', 'Sweden', 'Switzerland'], key='country')
st.sidebar.selectbox('Select Programming Language', ['Python', 'JavaScript', 'Java', 'C#', 'C++'], key='language')
st.sidebar.slider('Minimum Years of Experience', 0, 20, 5, key='experience')


st.title('DevMetrix Salary Analytics Dashboard')

try:
    health = requests.get(f"{BASE_URL}/", timeout=10)
    backend_ok = health.status_code == 200
except requests.exceptions.RequestException:
    backend_ok = False

if not backend_ok:
    st.error(f"Cannot reach backend at {BASE_URL}. Check BACKEND_URL (Streamlit Cloud → Settings → Secrets) or ensure Railway is deployed.")

button =  st.button('Fetch Salary Analytics', key='fetch_button')

if button:
    country = st.session_state.country
    language = st.session_state.language
    experience = st.session_state.experience

    try:
        response = requests.get(f"{BASE_URL}/analytics/salary", params={
            "country": country,
            "language": language,
            "min_years_exp": experience
        }, timeout=10)
    except requests.exceptions.RequestException:
        st.error(f"Could not reach the backend at {BASE_URL}. Is the API running?")
    else:
        if response.status_code == 200:
            data = response.json()

            col1, col2, col3 = st.columns(3)
            with col1:
                mean_salary = data.get('mean_salary', 'N/A')
            with col2:
                median_salary = data.get('median_salary', 'N/A')
            with col3:
                total_matches = data.get('total_matches', 'N/A')

            st.metric(label="Mean Salary", value=f"${mean_salary}")
            st.metric(label="Median Salary", value=f"${median_salary}")
            st.metric(label="Total Matches", value=total_matches)
        else:
            st.error(f"Error fetching data: {response.status_code} - {response.text}")
        
st.subheader('Developer Cohort Analytics')

records = None
if button:
    payload = {
        "countries": [st.session_state.country],
        "languages": [st.session_state.language],
        'min_salary': 0,
        'limit': 10,
    }

    try:
        cohort_response = requests.post(f"{BASE_URL}/analytics/cohort", json=payload, timeout=10)
    except requests.exceptions.RequestException:
        st.error(f"Could not reach the backend at {BASE_URL}. Is the API running?")
    else:
        if cohort_response.status_code == 200:
            data = cohort_response.json()
            records = data.get('results', [])
            if records:
                st.write(f"Showing top {len(records)} out of {data.get('count', 0)} total developers:")
                st.dataframe(records)
            else:
                st.warning("No records found for the selected filters.")
        else:
            st.error(f"Error fetching cohort data: {cohort_response.status_code} - {cohort_response.text}")
    
st.write("---")
st.subheader("📊 Visual Analytics")

# Create two columns for side-by-side charts
col_chart1, col_chart2 = st.columns(2)

# --- CHART 1: Salary Distribution Histogram ---
with col_chart1:
    st.markdown("### Salary Distribution")

    # Fetch salary data from backend
    try:
        sal_response = requests.get(
            f"{BASE_URL}/analytics/salary-distribution",
            params={"country": st.session_state.country},
            timeout=10,
        )
    except requests.exceptions.RequestException:
        st.error("Failed to reach backend for salary distribution.")
        sal_response = None

    if sal_response and sal_response.status_code == 200:
        sal_data = sal_response.json().get("salaries", [])

        if sal_data:
            # Create interactive Plotly Histogram
            fig_hist = px.histogram(
                x=sal_data,
                nbins=30,
                title=f"Salary Range in {st.session_state.country}",
                labels={"x": "Yearly Compensation ($USD)", "y": "Count"},
                color_discrete_sequence=["#00CC96"],
            )
            # Render chart in Streamlit
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.warning("No salary data available for this selection.")
    else:
        st.error("Failed to load salary distribution.")


# --- CHART 2: Native Streamlit Bar Chart (Quick & Simple) ---
with col_chart2:
    st.markdown("### Top Experience Levels")

    # If your cohort dataframe/records are already fetched in app.py:
    if records:
        # Convert records to Pandas DataFrame directly inside Streamlit
        import pandas as pd

        df_cohort = pd.DataFrame(records)

        exp_col = (
            "YearsCodePro"
            if "YearsCodePro" in df_cohort.columns
            else "experience"
        )

        if exp_col in df_cohort.columns:
            exp_counts = df_cohort[exp_col].value_counts().head(10)

            # Native Streamlit bar chart (No extra library needed!)
            st.bar_chart(exp_counts)
        else:
            st.info("Experience column not present in cohort sample.")
    else:
        st.info("Fetch cohort records above to view experience breakdown.")
