
#### Agent Recommendation Based on Genres & Location

import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack
import joblib
import numpy as np
import warnings
warnings.filterwarnings('ignore')


df = pd.read_csv("literary_agents_location1.csv")
df.head(3)

# === Encode genres ===
mlb = MultiLabelBinarizer()
agent_genres = mlb.fit_transform(df["genres"])

# === Encode location ===
ohe = OneHotEncoder()
agent_locations = ohe.fit_transform(df[["location"]])


# === Combine features ===
agent_features = hstack([agent_genres, agent_locations])

def recommend_agents(author_genres, author_location, top_n=3):
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



# === Example usage ===
author_genres = ["Fantasy", "Sci-Fi"]
author_location = "New York"

recommendations = recommend_agents(author_genres, author_location, top_n=2)
print(recommendations[["name", "location", "genres", "similarity_score"]])




# Save all necessary components together
model_data = {
    "mlb": mlb,                    # MultiLabelBinarizer for genres
    "ohe": ohe,                    # OneHotEncoder for locations
    "agent_features": agent_features,  # sparse matrix with agent features
    "df": df                       # dataframe with agent info
}

joblib.dump(model_data, "agent_recommender_model.pkl")







