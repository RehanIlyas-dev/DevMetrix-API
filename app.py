import streamlit as st
import requests


st.set_page_config(page_title="Salary Analytics Dashboard", layout="wide")

BASE_URL = "http://127.0.0.1:8000"

st.sidebar.header("Filters")
st.sidebar.selectbox('Select Country', ['United States', 'India', 'Germany', 'Canada', 'United Kingdom'], key='country')
st.sidebar.selectbox('Select Programming Language', ['Python', 'JavaScript', 'Java', 'C#', 'C++'], key='language')
st.sidebar.slider('Minimum Years of Experience', 0, 20, 5, key='experience')


st.title('EDA Salary Analytics Dashboard') 
button =  st.button('Fetch Salary Analytics', key='fetch_button')

if button:
    country = st.session_state.country
    language = st.session_state.language
    experience = st.session_state.experience

    response = requests.get(f"{BASE_URL}/analytics/salary", params={
        "country": country,
        "language": language,
        "experience": experience
    })

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

payload = {
    "countries": [st.session_state.country],
    "languages": [st.session_state.language],
    'min_salary': 0,
    'limit': 10,
}

response = requests.post(f"{BASE_URL}/analytics/cohort", json=payload)

if response.status_code == 200:
    data = response.json()
    records = data.get('results', [])
    if records:
       st.write(f"Showing top {len(records)} out of {data.get('count', 0)} total developers:")
       st.dataframe(records)
    else:
        st.warning("No records found for the selected filters.")
else:
    st.error(f"Error fetching cohort data: {response.status_code} - {response.text}")
    
