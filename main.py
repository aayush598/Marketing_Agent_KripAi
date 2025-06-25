from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from recommender import TechnologyRecommender
from market_analyzer import MarketAnalyzer
from database import DatabaseConnection
from fastapi.middleware.cors import CORSMiddleware

# FastAPI app
app = FastAPI(
    title="AI Technology Stack Recommender API",
    description="Generate tech stack, team, cost & roadmap recommendations based on project description.",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ProjectInput(BaseModel):
    description: str
    budget: str = "moderate"
    timeline: str = "3-6 months"

class TechList(BaseModel):
    technologies: List[str]

class QueryInput(BaseModel):
    query: str

# Initialize components
recommender = TechnologyRecommender()
analyzer = MarketAnalyzer()
db = DatabaseConnection()

# Endpoints

@app.get("/health", tags=["Utility"])
def health_check():
    return {"status": "ok"}

@app.post("/generate", tags=["Recommendation"])
def generate_recommendation(project: ProjectInput):
    if not project.description.strip():
        raise HTTPException(status_code=400, detail="Project description cannot be empty.")
    
    result = recommender.get_structured_recommendations(
        project_description=project.description,
        budget_constraint=project.budget,
        timeline=project.timeline
    )
    return {"recommendation": result}

@app.get("/recommendation", tags=["Recommendation"])
def get_cached_recommendation(description: str, budget: str = "moderate", timeline: str = "3-6 months"):
    data = recommender.json_db.get_recommendation(description, budget, timeline)
    if not data:
        raise HTTPException(status_code=404, detail="No cached recommendation found for this input.")
    return data

@app.get("/teams/members", tags=["Team"])
def get_all_team_members():
    return db.fetch_team_members()

@app.post("/analyze/tech", tags=["Technology"])
def analyze_technologies(payload: TechList):
    return analyzer.get_tech_analysis(payload.technologies)

@app.post("/search/technologies", tags=["Technology"])
def search_technologies(query_input: QueryInput):
    return {"technologies": analyzer.search_technologies(query_input.query)}

@app.get("/salary", tags=["Technology"])
def get_salary_data(technology: str = Query(..., description="Technology name to fetch salary for")):
    salary = analyzer.get_tech_salary(technology)
    if not salary:
        raise HTTPException(status_code=404, detail="No salary data found.")
    return salary

@app.get("/roadmap", tags=["Planning"])
def generate_roadmap(
    description: str = Query(..., description="Project description"),
    stack: str = Query(..., description="Recommended technology stack"),
    timeline: str = Query("3-6 months", description="Project timeline")
):
    return {
        "roadmap": recommender.groq_analyzer.generate_implementation_roadmap(
            description, stack, timeline
        )
    }

@app.get("/market-position", tags=["Analysis"])
def get_market_position(
    technology: str = Query(..., description="Technology name"),
    context: Optional[str] = Query("", description="Project context (optional)")
):
    return {
        "market_analysis": recommender.groq_analyzer.analyze_market_position([technology], context)
    }
