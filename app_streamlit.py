import streamlit as st
import requests
import pandas as pd

# Title
st.title("Literary Agent Recommender (via API)")

# Sidebar inputs
st.sidebar.header("Author Details")
genres_input = st.sidebar.text_input("Genres (comma-separated)", "Fantasy,Sci-Fi")
location_input = st.sidebar.text_input("Location", "New York")
top_n_input = st.sidebar.number_input("Number of Recommendations", min_value=1, max_value=10, value=3)

# Convert genres string to list
author_genres = [g.strip() for g in genres_input.split(",")]

# API endpoint
API_URL = "http://127.0.0.1:8000/recommend"

if st.button("Get Recommendations"):
    # Prepare request payload
    payload = {
        "genres": author_genres,
        "location": location_input,
        "top_n": top_n_input
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            recommendations = response.json()["recommendations"]
            if recommendations:
                df = pd.DataFrame(recommendations)
                st.subheader("Recommended Agents")
                st.dataframe(df)
            else:
                st.warning("No recommendations found.")
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {e}")