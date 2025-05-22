# database_utils.py - JSON Storage Version
import json
from pathlib import Path
from datetime import datetime
import hashlib
import os

class JSONDatabase:
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.projects_file = self.data_dir / "projects.json"
        self.recommendations_file = self.data_dir / "recommendations.json"
        self._initialize_storage()

    def _initialize_storage(self):
        """Create data directory and files if they don't exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize projects file if it doesn't exist
        if not self.projects_file.exists():
            with open(self.projects_file, 'w') as f:
                json.dump({"projects": []}, f)
        
        # Initialize recommendations file if it doesn't exist
        if not self.recommendations_file.exists():
            with open(self.recommendations_file, 'w') as f:
                json.dump({"recommendations": []}, f)

    def _get_project_hash(self, project_description):
        """Generate a unique hash for the project description"""
        return hashlib.sha256(project_description.encode()).hexdigest()

    def save_recommendation(self, project_description, budget_constraint, timeline, recommendation_data):
        """Save recommendation to JSON files"""
        try:
            project_hash = self._get_project_hash(project_description)
            
            # Load existing data
            with open(self.projects_file, 'r') as f:
                projects_data = json.load(f)
            
            with open(self.recommendations_file, 'r') as f:
                recommendations_data = json.load(f)
            
            # Find or create project
            project = next((p for p in projects_data["projects"] if p["project_hash"] == project_hash), None)
            if not project:
                project = {
                    "id": len(projects_data["projects"]) + 1,
                    "project_description": project_description,
                    "project_hash": project_hash,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                projects_data["projects"].append(project)
            else:
                project["updated_at"] = datetime.now().isoformat()
            
            # Prepare recommendation
            recommendation = {
                "project_id": project["id"],
                "budget_constraint": budget_constraint,
                "timeline": timeline,
                "requirements_analysis": recommendation_data.get('requirements_analysis'),
                "tech_stack": recommendation_data.get('tech_stack'),
                "tech_analysis": recommendation_data.get('tech_analysis'),
                "team_composition": recommendation_data.get('team_composition', []),
                "cost_estimation": recommendation_data.get('cost_estimation', {}),
                "roadmap": recommendation_data.get('roadmap'),
                "risk_analysis": recommendation_data.get('risk_analysis'),
                "created_at": datetime.now().isoformat()
            }
            
            # Check if recommendation already exists
            existing_rec = next(
                (r for r in recommendations_data["recommendations"] 
                 if r["project_id"] == project["id"] 
                 and r["budget_constraint"] == budget_constraint 
                 and r["timeline"] == timeline),
                None
            )
            
            if existing_rec:
                # Update existing recommendation
                existing_rec.update(recommendation)
            else:
                # Add new recommendation
                recommendations_data["recommendations"].append(recommendation)
            
            # Save data back to files
            with open(self.projects_file, 'w') as f:
                json.dump(projects_data, f, indent=2)
            
            with open(self.recommendations_file, 'w') as f:
                json.dump(recommendations_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving recommendation: {e}")
            return False

    def get_recommendation(self, project_description, budget_constraint, timeline):
        """Retrieve recommendation from JSON files"""
        try:
            project_hash = self._get_project_hash(project_description)
            
            # Load projects data
            with open(self.projects_file, 'r') as f:
                projects_data = json.load(f)
            
            # Find project
            project = next((p for p in projects_data["projects"] if p["project_hash"] == project_hash), None)
            if not project:
                return None
            
            # Load recommendations data
            with open(self.recommendations_file, 'r') as f:
                recommendations_data = json.load(f)
            
            # Find matching recommendation
            recommendation = next(
                (r for r in recommendations_data["recommendations"] 
                 if r["project_id"] == project["id"] 
                 and r["budget_constraint"] == budget_constraint 
                 and r["timeline"] == timeline),
                None
            )
            
            if recommendation:
                # Convert team_composition and cost_estimation to proper format if they're strings
                if isinstance(recommendation.get('team_composition'), str):
                    recommendation['team_composition'] = json.loads(recommendation['team_composition'])
                if isinstance(recommendation.get('cost_estimation'), str):
                    recommendation['cost_estimation'] = json.loads(recommendation['cost_estimation'])
                
                return recommendation
            
            return None
        except Exception as e:
            print(f"Error retrieving recommendation: {e}")
            return None

    def close(self):
        """No connection to close in JSON storage"""
        pass