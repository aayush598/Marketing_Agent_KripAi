# database.py - Modified version

import json
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re
from duckduckgo_search import DDGS
from datetime import datetime
import time
from collections import defaultdict

class DatabaseConnection:
    def __init__(self):
        """Initialize database connection with JSON data"""
        self.data_dir = Path(__file__).parent / "data"
        self.teams = []
        self.domain_cache = {}  # Cache for domain data
        self.salary_cache = {}  # Cache for salary data
        self.trend_cache = {}   # Cache for market trend data
        self.load_data()

    def load_data(self):
        """Load data from JSON files"""
        try:
            # For testing purposes, let's check if teams.json exists in the current directory
            current_dir_file = Path.cwd() / "teams.json"
            if current_dir_file.exists():
                with open(current_dir_file, 'r') as f:
                    self.teams = json.load(f).get("teams", [])
                return
                
            # Create data directory if it doesn't exist
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Load teams data
            teams_file = self.data_dir / "teams.json"
            if teams_file.exists():
                with open(teams_file, 'r') as f:
                    self.teams = json.load(f).get("teams", [])
            else:
                # Fall back to looking for teams.json in the current directory
                current_dir = Path.cwd()
                for file in current_dir.glob("*.json"):
                    if file.name == "teams.json":
                        with open(file, 'r') as f:
                            self.teams = json.load(f).get("teams", [])
                        break
                if not self.teams:
                    print("Warning: teams.json not found in any location.")
        except Exception as e:
            print(f"Error loading data: {e}")

    def fetch_team_members(self):
        """Fetch all team members with their skills"""
        members = []
        for team in self.teams:
            for member in team["members"]:
                member_data = {
                    "id": member["id"],
                    "name": member["name"],
                    "role": member["role"],
                    "years_experience": member["years_experience"],
                    "availability_percentage": member["availability"],
                    "remote_work": member["remote_work"],
                    "expertise_level": member["expertise_level"],
                    "plus_points": member.get("plus_points", []),
                    "skills": member["skills"],
                    "team_name": team["name"]
                }
                members.append(member_data)
        return members
    
    def fetch_team_by_expertise(self, required_skills, min_expertise_level="Intermediate"):
        """Fetch team members who have expertise in the specified skills"""
        members = []
        expertise_levels = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
        req_level = expertise_levels.get(min_expertise_level, 2)
        
        if not required_skills:
            required_skills = []
        
        required_skills_lower = [skill.lower() if isinstance(skill, str) else "" for skill in required_skills]
        
        for team in self.teams:
            for member in team.get("members", []):
                member_level = expertise_levels.get(member.get("expertise_level", "Beginner"), 1)
                
                if member_level < req_level:
                    continue
                
                member_skills = member.get("skills", [])
                member_skills_lower = [skill.lower() if isinstance(skill, str) else "" for skill in member_skills]
                matched_skills = []
                
                for req_skill_lower in required_skills_lower:
                    for i, member_skill_lower in enumerate(member_skills_lower):
                        if req_skill_lower in member_skill_lower or member_skill_lower in req_skill_lower:
                            matched_skills.append(member_skills[i])
                            break
                
                if matched_skills:
                    skill_coverage = len(matched_skills) / len(required_skills) if required_skills else 0
                    expertise_score = member_level * (1 + min(member.get("years_experience", 0) * 0.1, 0.9))
                    specialization = len(matched_skills) / len(member_skills) if member_skills else 0
                    match_score = (skill_coverage * 0.5) + (expertise_score * 0.3) + (specialization * 0.2)
                    
                    member_data = {
                        "id": member["id"],
                        "name": member["name"],
                        "role": member["role"],
                        "team": team["name"],
                        "years_experience": member["years_experience"],
                        "availability_percentage": member["availability"],
                        "matched_skills": matched_skills,
                        "all_skills": member_skills,
                        "expertise_level": member["expertise_level"],
                        "plus_points": member.get("plus_points", []),
                        "match_score": match_score,
                        "skill_coverage": skill_coverage,
                        "expertise_score": expertise_score,
                        "specialization": specialization
                    }
                    members.append(member_data)
        
        members.sort(key=lambda x: x["match_score"], reverse=True)
        return members

    def fetch_technology_domains(self, technologies):
        """Dynamically determine technology domains using web search"""
        domains = {}
        
        for tech in technologies:
            if tech.lower() in self.domain_cache:
                domains[tech] = self.domain_cache[tech.lower()]
                continue
                
            try:
                with DDGS() as ddgs:
                    search_query = f"{tech} technology category 2024"
                    results = list(ddgs.text(search_query, max_results=3))
                    
                    if not results:
                        continue
                        
                    # Analyze results to determine domain
                    domain_counts = defaultdict(int)
                    for result in results:
                        try:
                            response = requests.get(result['href'], timeout=10)
                            soup = BeautifulSoup(response.text, 'html.parser')
                            text = ' '.join([p.get_text() for p in soup.find_all('p')]).lower()
                            
                            # Count domain mentions
                            if "frontend" in text or "ui" in text or "user interface" in text:
                                domain_counts["Frontend"] += 1
                            if "backend" in text or "server" in text or "api" in text:
                                domain_counts["Backend"] += 1
                            if "database" in text or "db" in text or "data storage" in text:
                                domain_counts["Database"] += 1
                            if "cloud" in text or "aws" in text or "azure" in text or "gcp" in text:
                                domain_counts["Cloud"] += 1
                            if "mobile" in text or "ios" in text or "android" in text:
                                domain_counts["Mobile"] += 1
                            if "data" in text or "ai" in text or "machine learning" in text:
                                domain_counts["Data"] += 1
                            if "devops" in text or "deployment" in text or "infrastructure" in text:
                                domain_counts["DevOps"] += 1
                        except:
                            continue
                    
                    if domain_counts:
                        detected_domain = max(domain_counts.items(), key=lambda x: x[1])[0]
                        domains[tech] = detected_domain
                        self.domain_cache[tech.lower()] = detected_domain
                    else:
                        domains[tech] = "Other"
            except Exception as e:
                print(f"Error detecting domain for {tech}: {e}")
                domains[tech] = "Other"
                
        return domains

    def get_tech_salary(self, technology):
        """Get current salary data for a technology from web search"""
        if technology in self.salary_cache:
            return self.salary_cache[technology]
            
        try:
            with DDGS() as ddgs:
                search_query = f"{technology} developer salary 2024"
                results = list(ddgs.text(search_query, max_results=3))
                
                salary_ranges = []
                for result in results:
                    try:
                        response = requests.get(result['href'], timeout=10)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        text = ' '.join([p.get_text() for p in soup.find_all('p')])
                        
                        # Extract salary ranges (multiple formats)
                        patterns = [
                            r'\$(\d{1,3}(?:,\d{3})*)\s*-\s*\$(\d{1,3}(?:,\d{3})*)',  # $70,000 - $120,000
                            r'\$(\d{1,3})k\s*-\s*\$(\d{1,3})k',                      # $70k - $120k
                            r'(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)',      # 70,000 - 120,000
                            r'(\d{1,3})k\s*-\s*(\d{1,3})k'                           # 70k - 120k
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, text)
                            for match in matches:
                                if len(match) == 2:
                                    try:
                                        low = int(match[0].replace(',', '')) if 'k' not in pattern else int(match[0]) * 1000
                                        high = int(match[1].replace(',', '')) if 'k' not in pattern else int(match[1]) * 1000
                                        salary_ranges.append((low, high))
                                    except:
                                        continue
                    except:
                        continue
                
                if salary_ranges:
                    # Calculate average range from found salaries
                    avg_low = sum(r[0] for r in salary_ranges) / len(salary_ranges)
                    avg_high = sum(r[1] for r in salary_ranges) / len(salary_ranges)
                    
                    salary_data = {
                        "low": int(avg_low),
                        "median": int((avg_low + avg_high) / 2),
                        "high": int(avg_high),
                        "currency": "USD",
                        "source": "web search",
                        "as_of": datetime.now().strftime("%Y-%m")
                    }
                    
                    self.salary_cache[technology] = salary_data
                    return salary_data
        except Exception as e:
            print(f"Error getting salary data for {technology}: {e}")
            
        # Fallback to domain-based estimation if web search fails
        domains = self.fetch_technology_domains({technology})
        domain = domains.get(technology, "Other")
        
        # Get base market rates from web search for the domain
        try:
            with DDGS() as ddgs:
                search_query = f"{domain} developer average salary 2024"
                results = list(ddgs.text(search_query, max_results=3))
                
                domain_salaries = []
                for result in results:
                    try:
                        response = requests.get(result['href'], timeout=10)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        text = ' '.join([p.get_text() for p in soup.find_all('p')])
                        
                        # Extract salary ranges
                        patterns = [
                            r'\$(\d{1,3}(?:,\d{3})*)\s*-\s*\$(\d{1,3}(?:,\d{3})*)',
                            r'\$(\d{1,3})k\s*-\s*\$(\d{1,3})k',
                            r'(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)',
                            r'(\d{1,3})k\s*-\s*(\d{1,3})k'
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, text)
                            for match in matches:
                                if len(match) == 2:
                                    try:
                                        low = int(match[0].replace(',', '')) if 'k' not in pattern else int(match[0]) * 1000
                                        high = int(match[1].replace(',', '')) if 'k' not in pattern else int(match[1]) * 1000
                                        domain_salaries.append((low, high))
                                    except:
                                        continue
                    except:
                        continue
                
                if domain_salaries:
                    avg_low = sum(r[0] for r in domain_salaries) / len(domain_salaries)
                    avg_high = sum(r[1] for r in domain_salaries) / len(domain_salaries)
                else:
                    # Default fallback if no domain salaries found
                    avg_low = 80000
                    avg_high = 120000
        except:
            avg_low = 80000
            avg_high = 120000
        
        # Adjust for technology demand
        high_demand_techs = ["react", "aws", "kubernetes", "python", "typescript", "ai", "machine learning"]
        if any(t in technology.lower() for t in high_demand_techs):
            avg_low *= 1.15
            avg_high *= 1.15
        
        salary_data = {
            "low": int(avg_low),
            "median": int((avg_low + avg_high) / 2),
            "high": int(avg_high),
            "currency": "USD",
            "source": "estimated",
            "as_of": datetime.now().strftime("%Y-%m")
        }
        
        self.salary_cache[technology] = salary_data
        return salary_data

    def get_market_position(self, technology):
        """Get market position data for a technology using web search"""
        if technology in self.trend_cache:
            return self.trend_cache[technology]
            
        try:
            with DDGS() as ddgs:
                search_query = f"{technology} technology market position 2024"
                results = list(ddgs.text(search_query, max_results=3))
                
                market_data = []
                for result in results:
                    try:
                        response = requests.get(result['href'], timeout=10)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        text = ' '.join([p.get_text() for p in soup.find_all('p')])
                        
                        # Extract relevant sentences
                        sentences = text.split('. ')
                        relevant = [s for s in sentences if technology.lower() in s.lower() and ("market" in s.lower() or "trend" in s.lower() or "adoption" in s.lower())]
                        market_data.extend(relevant)
                    except:
                        continue
                
                if market_data:
                    analysis = '. '.join(market_data[:3]) + '.'  # Take top 3 relevant sentences
                    self.trend_cache[technology] = analysis
                    return analysis
        except Exception as e:
            print(f"Error getting market position for {technology}: {e}")
        
        return f"Current market position analysis for {technology} is unavailable."

    def fetch_optimal_team_composition(self, required_technologies, budget_constraint="moderate", timeline="3-6 months"):
        """Build an optimal team composition based on project requirements"""
        if not required_technologies:
            required_technologies = ["React", "Node.js", "MongoDB"]
        
        # Determine project complexity based on number of technologies and domains
        tech_domains = self.fetch_technology_domains(required_technologies)
        unique_domains = len(set(tech_domains.values()))
        complexity = min(max(unique_domains, 1), 4)  # Scale 1-4
        
        # Calculate base team size based on complexity
        base_team_size = {
            1: 2,   # Simple project (1 domain)
            2: 3,   # Medium complexity
            3: 4,    # Complex
            4: 5     # Very complex
        }.get(complexity, 3)
        
        # Adjust team size based on budget
        budget_factors = {
            "tight": 0.8,
            "moderate": 1.0,
            "flexible": 1.2
        }
        budget_factor = budget_factors.get(budget_constraint.lower(), 1.0)
        
        # Adjust team size based on timeline
        timeline_factors = {
            "1-3 months": 1.2,    # Need more people for shorter timeline
            "3-6 months": 1.0,
            "6-12 months": 0.9,
            "12+ months": 0.8
        }
        timeline_factor = timeline_factors.get(timeline.lower(), 1.0)
        
        # Calculate final team size
        team_size = max(2, min(6, round(base_team_size * budget_factor * timeline_factor)))
        
        # Get all potential team members
        skilled_members = self.fetch_team_by_expertise(required_technologies)
        
        # Select team members ensuring domain coverage
        selected_team = []
        covered_domains = set()
        
        # First pass: ensure coverage of all required domains
        for domain in set(tech_domains.values()):
            if len(selected_team) >= team_size:
                break
                
            domain_techs = [t for t, d in tech_domains.items() if d == domain]
            domain_members = [m for m in skilled_members 
                             if any(skill in m["matched_skills"] for skill in domain_techs)
                             and m["id"] not in [tm["id"] for tm in selected_team]]
            
            if domain_members:
                best_match = max(domain_members, key=lambda x: x["match_score"])
                selected_team.append(best_match)
                covered_domains.add(domain)
        
        # Second pass: fill remaining slots with best overall matches
        remaining_slots = team_size - len(selected_team)
        if remaining_slots > 0:
            available_members = [m for m in skilled_members 
                                if m["id"] not in [tm["id"] for tm in selected_team]]
            available_members.sort(key=lambda x: x["match_score"], reverse=True)
            
            for member in available_members[:remaining_slots]:
                selected_team.append(member)
        
        # Calculate team costs based on market rates
        total_monthly_cost = 0
        for member in selected_team:
            # Get average salary for their primary skill
            primary_skill = member["matched_skills"][0] if member["matched_skills"] else ""
            if primary_skill:
                salary_data = self.get_tech_salary(primary_skill)
                hourly_rate = salary_data["median"] / 2000  # Convert annual to hourly
            else:
                hourly_rate = 50  # Default if no skill salary data
            
            # Calculate monthly cost based on availability
            monthly_hours = 160 * (member["availability_percentage"] / 100)
            member["monthly_cost"] = hourly_rate * monthly_hours
            total_monthly_cost += member["monthly_cost"]
        
        # Calculate project duration in months
        if "1-3" in timeline:
            duration = 2
        elif "3-6" in timeline:
            duration = 4.5
        elif "6-12" in timeline:
            duration = 9
        else:  # 12+ months
            duration = 12
        
        total_cost = total_monthly_cost * duration
        
        # Return simplified team information without individual rates
        simplified_team = []
        for member in selected_team:
            simplified_team.append({
                "name": member["name"],
                "role": member["role"],
                "expertise_level": member["expertise_level"],
                "availability": member["availability_percentage"],
                "technologies": member["matched_skills"],
                "experience": member["years_experience"],
                "strengths": member["plus_points"]
            })
        
        return {
            "team": simplified_team,
            "total_cost": total_cost,
            "monthly_cost": total_monthly_cost,
            "duration_months": duration
        }