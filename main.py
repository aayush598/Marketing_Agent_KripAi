from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from recommender import TechnologyRecommender
from market_analyzer import MarketAnalyzer
from database import DatabaseConnection
from fastapi.middleware.cors import CORSMiddleware
from mlops import MLOpsLogger
from sqlite_database import SQLiteDB
import time

# Initialize FastAPI
app = FastAPI(
    title="AI Technology Stack Recommender API",
    description="Generate tech stack, team, cost & roadmap recommendations with full logging and SQLite caching.",
    version="2.1.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
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

# Services
recommender = TechnologyRecommender()
analyzer = MarketAnalyzer()
db = DatabaseConnection()
sqlite_db = SQLiteDB()
logger = MLOpsLogger()

# Health check
@app.get("/health", tags=["Utility"])
def health_check():
    return {"status": "ok"}

# Generate recommendation (with caching and logging)
@app.post("/generate", tags=["Recommendation"])
def generate_recommendation(project: ProjectInput):
    logger.log_request("/generate", project.dict())

    if not project.description.strip():
        logger.log_error("Empty project description", "Description field was blank.")
        raise HTTPException(status_code=400, detail="Project description cannot be empty.")

    cached = sqlite_db.get_cached_recommendation(project.description, project.budget, project.timeline)
    if cached:
        logger.log_cache_hit("/generate", project.description)
        logger.log_recommendation(project.description, project.budget, project.timeline, 0, "cache")
        return {"recommendation": cached, "source": "cache"}

    start_time = time.time()
    try:
        result = recommender.get_structured_recommendations(
            project_description=project.description,
            budget_constraint=project.budget,
            timeline=project.timeline
        )
        latency = time.time() - start_time

        project_id = sqlite_db.save_project(project.description, project.budget, project.timeline)
        sqlite_db.save_recommendation(project_id, result)

        logger.log_recommendation(project.description, project.budget, project.timeline, latency, "generated")
        logger.log_response("/generate", {"recommendation": result[:500]}, latency)

        return {"recommendation": result, "source": "generated"}
    except Exception as e:
        logger.log_error("Exception in /generate", str(e))
        raise HTTPException(status_code=500, detail="Internal server error.")

# Get cached recommendation
@app.get("/recommendation", tags=["Recommendation"])
def get_cached_recommendation(description: str, budget: str = "moderate", timeline: str = "3-6 months"):
    logger.log_request("/recommendation", {
        "description": description,
        "budget": budget,
        "timeline": timeline
    })

    try:
        rec = sqlite_db.get_cached_recommendation(description, budget, timeline)
        if not rec:
            raise ValueError("No match found")
        logger.log_cache_hit("/recommendation", description)
        return {"recommendation": rec, "source": "cache"}
    except Exception as e:
        logger.log_error("Error in /recommendation", str(e))
        raise HTTPException(status_code=404, detail="No cached recommendation found.")

# List team members
@app.get("/teams/members", tags=["Team"])
def get_all_team_members():
    logger.log_request("/teams/members", {})
    try:
        result = db.fetch_team_members()
        logger.log_response("/teams/members", result, 0)
        return result
    except Exception as e:
        logger.log_error("Error in /teams/members", str(e))
        raise HTTPException(status_code=500, detail="Could not fetch team members.")

# Analyze tech
@app.post("/analyze/tech", tags=["Technology"])
def analyze_technologies(payload: TechList):
    logger.log_request("/analyze/tech", payload.dict())
    start_time = time.time()
    try:
        result = analyzer.get_tech_analysis(payload.technologies)
        logger.log_response("/analyze/tech", result, time.time() - start_time)
        return result
    except Exception as e:
        logger.log_error("Error in /analyze/tech", str(e))
        raise HTTPException(status_code=500, detail="Technology analysis failed.")

# Extract technologies from query
@app.post("/search/technologies", tags=["Technology"])
def search_technologies(query_input: QueryInput):
    logger.log_request("/search/technologies", query_input.dict())
    try:
        techs = analyzer.search_technologies(query_input.query)
        logger.log_response("/search/technologies", {"technologies": techs}, 0)
        return {"technologies": techs}
    except Exception as e:
        logger.log_error("Error in /search/technologies", str(e))
        raise HTTPException(status_code=500, detail="Technology extraction failed.")

# Get salary for one technology
@app.get("/salary", tags=["Technology"])
def get_salary_data(technology: str = Query(..., description="Technology name to fetch salary for")):
    logger.log_request("/salary", {"technology": technology})
    try:
        salary = analyzer.get_tech_salary(technology)
        if not salary:
            raise ValueError("Salary not found")
        logger.log_response("/salary", salary, 0)
        return salary
    except Exception as e:
        logger.log_error("Error in /salary", str(e))
        raise HTTPException(status_code=404, detail="No salary data found.")

# Generate roadmap
@app.get("/roadmap", tags=["Planning"])
def generate_roadmap(
    description: str = Query(...),
    stack: str = Query(...),
    timeline: str = Query("3-6 months")
):
    logger.log_request("/roadmap", {
        "description": description[:200],
        "stack": stack[:200],
        "timeline": timeline
    })

    try:
        roadmap = recommender.groq_analyzer.generate_implementation_roadmap(description, stack, timeline)
        logger.log_response("/roadmap", {"roadmap": roadmap[:500]}, 0)
        return {"roadmap": roadmap}
    except Exception as e:
        logger.log_error("Error in /roadmap", str(e))
        raise HTTPException(status_code=500, detail="Roadmap generation failed.")

# Market analysis for tech
@app.get("/market-position", tags=["Analysis"])
def get_market_position(
    technology: str = Query(...),
    context: Optional[str] = Query("")
):
    logger.log_request("/market-position", {
        "technology": technology,
        "context": context[:200]
    })

    try:
        result = recommender.groq_analyzer.analyze_market_position([technology], context)
        logger.log_response("/market-position", {"market_analysis": result[:500]}, 0)
        return {"market_analysis": result}
    except Exception as e:
        logger.log_error("Error in /market-position", str(e))
        raise HTTPException(status_code=500, detail="Market position analysis failed.")
