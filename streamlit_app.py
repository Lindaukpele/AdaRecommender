import streamlit as st
import requests

import warnings
warnings.filterwarnings("ignore")

st.title("Agent Recommender")

genres_input = st.text_input("Enter book genres (comma separated):")
location_input = st.text_input("Enter author location:")
top_n = st.number_input("Number of recommendations", min_value=1, max_value=10, value=3)

if st.button("Recommend Agents"):
    if not genres_input or not location_input:
        st.warning("Please enter both genres and location.")
    else:
        genres_list = [g.strip() for g in genres_input.split(",")]
        payload = {
            "genres": genres_list,
            "location": location_input,
            "top_n": top_n
        }
        
        try:
            response = requests.post("http://localhost:8000/recommend", json=payload)
            if response.status_code == 200:
                recs = response.json()["recommendations"]
                st.write("Top recommended agents:")
                for r in recs:
                    st.write(f"- {r['agent_name']} (Score: {r['similarity_score']:.3f})")
            else:
                st.error(f"API error: {response.status_code}")
        except Exception as e:
            st.error(f"Request failed: {e}")







