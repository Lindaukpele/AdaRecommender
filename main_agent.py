from agent_model import build_and_save_model, load_model, recommend_agents

# Load the preprocessed model
model_data = load_model()

# Example usage
author_genres = ["Fantasy", "Sci-Fi"]
author_location = "New York"
recommendations = recommend_agents(model_data, author_genres, author_location, top_n=2)

print(recommendations[["name", "location", "genres", "similarity_score"]])