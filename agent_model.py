import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack
import joblib
import numpy as np
import os
import time
import warnings
warnings.filterwarnings('ignore')

# === Step 1: Auto rebuild function, updates file as csv file changes ===
def build_model_if_needed(csv_path="literary_agents_location1.csv", model_path="agent_recommender_model.pkl"):
    """Builds model if CSV is newer than saved model or model does not exist."""
    
    csv_time = os.path.getmtime(csv_path)
    if os.path.exists(model_path):
        model_time = os.path.getmtime(model_path)
    else:
        model_time = 0

    if csv_time > model_time:
        print("CSV updated. Rebuilding model...")
        build_and_save_model(csv_path, model_path)
    else:
        print("Model is up-to-date.")
    
    return load_model(model_path)

def build_and_save_model(csv_path="literary_agents_location1.csv", model_path="agent_recommender_model.pkl"):
    # Load data
    df = pd.read_csv(csv_path)

    # Encode genres
    mlb = MultiLabelBinarizer()
    agent_genres = mlb.fit_transform(df["genres"])

    # Encode location
    ohe = OneHotEncoder()
    agent_locations = ohe.fit_transform(df[["location"]])

    # Combine features
    agent_features = hstack([agent_genres, agent_locations])

    # Save all necessary components
    model_data = {
        "mlb": mlb,
        "ohe": ohe,
        "agent_features": agent_features,
        "df": df
    }

    joblib.dump(model_data, model_path)
    print(f"Model saved to {model_path}")


def load_model(model_path="agent_recommender_model.pkl"):
    return joblib.load(model_path)


def recommend_agents(model_data, author_genres, author_location, top_n=3):
    mlb = model_data["mlb"]
    ohe = model_data["ohe"]
    agent_features = model_data["agent_features"]
    df = model_data["df"]

    # Encode author's genres and location
    author_genres_vec = mlb.transform([author_genres])
    author_location_vec = ohe.transform([[author_location]])

    # Combine author features
    author_features = hstack([author_genres_vec, author_location_vec])

    # Calculate cosine similarity
    similarity = cosine_similarity(author_features, agent_features).flatten()

    # Get top N indices
    top_indices = np.argsort(similarity)[::-1][:top_n]

    # Prepare recommendations
    recommendations = df.iloc[top_indices].copy()
    recommendations["similarity_score"] = similarity[top_indices]

    return recommendations