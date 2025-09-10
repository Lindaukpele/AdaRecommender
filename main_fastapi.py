
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent_model import build_model_if_needed, recommend_agents

app = FastAPI(title="Literary Agent Recommender")

# Automatically build or load the model
model_data = build_model_if_needed("literary_agents_location1.csv", "agent_recommender_model.pkl")

class AuthorRequest(BaseModel):
    genres: list[str]
    location: str
    top_n: int = 3

@app.get("/")
def root():
    return {"message": "Welcome to the Literary Agent Recommender API"}

@app.post("/recommend")
def recommend(author: AuthorRequest):
    try:
        recommendations = recommend_agents(
            model_data, 
            author.genres, 
            author.location, 
            top_n=author.top_n
        )
        result = recommendations[["name", "location", "genres", "similarity_score"]].to_dict(orient="records")
        return {"recommendations": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))