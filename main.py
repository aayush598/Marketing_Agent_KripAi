from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from recommender import TechnologyRecommender
from fastapi.middleware.cors import CORSMiddleware

# FastAPI app instance
app = FastAPI(
    title="AI Technology Stack Recommender API",
    description="Generate tech stack, team, cost & roadmap recommendations based on project description.",
    version="1.0.0"
)

# CORS for frontend usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schema for request body
class ProjectInput(BaseModel):
    description: str
    budget: str = "moderate"  # tight / moderate / flexible
    timeline: str = "3-6 months"

# Recommender instance
recommender = TechnologyRecommender()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/generate")
def generate_recommendation(project: ProjectInput):
    if not project.description.strip():
        raise HTTPException(status_code=400, detail="Project description cannot be empty.")
    
    result = recommender.get_structured_recommendations(
        project_description=project.description,
        budget_constraint=project.budget,
        timeline=project.timeline
    )
    return {"recommendation": result}

@app.get("/recommendation")
def get_cached_recommendation(description: str, budget: str = "moderate", timeline: str = "3-6 months"):
    db = recommender.json_db
    data = db.get_recommendation(description, budget, timeline)
    if not data:
        raise HTTPException(status_code=404, detail="No cached recommendation found for this input.")
    return data
