# recommender.py (updated to use JSONDatabase)
import json
import re
from market_analyzer import MarketAnalyzer
from groq_integration import GroqAnalyzer
from database import DatabaseConnection
from database_utils import JSONDatabase

class TechnologyRecommender:
    def __init__(self):
        self.groq_analyzer = GroqAnalyzer()
        self.market_analyzer = MarketAnalyzer()
        self.db = DatabaseConnection()
        self.json_db = JSONDatabase()  # Changed from MySQLDatabase to JSONDatabase
    
    def get_structured_recommendations(self, project_description, budget_constraint="moderate", timeline="3-6 months"):
        """Generate structured recommendations with consistent output format"""
        # First check if we have this recommendation in the database
        cached_recommendation = self.json_db.get_recommendation(
            project_description, 
            budget_constraint, 
            timeline
        )
        
        if cached_recommendation:
            return self._format_output_from_db(cached_recommendation, budget_constraint, timeline)
        
        # If not in database, generate new recommendation
        # Step 1: Analyze project requirements
        requirements_analysis = self.groq_analyzer.analyze_project_requirements(project_description)
        
        # Step 2: Identify required technologies
        required_techs = self._identify_required_technologies(project_description)
        
        # Step 3: Get detailed technology analysis from market
        tech_analysis = self.market_analyzer.get_tech_analysis(required_techs)
        
        # Step 4: Select optimal team based on requirements and constraints
        team_selection = self.db.fetch_optimal_team_composition(required_techs, budget_constraint)
        
        # Step 5: Generate technology stack recommendation
        tech_stack = self.groq_analyzer.suggest_technology_stack(
            requirements_analysis, 
            budget_constraint, 
            timeline
        )
        
        # Step 6: Generate cost estimation
        cost_estimation = self._calculate_project_cost(team_selection.get('team', []), timeline)
        
        # Step 7: Generate implementation roadmap
        roadmap = self.groq_analyzer.generate_implementation_roadmap(
            project_description,
            tech_stack,
            timeline
        )
        
        # Step 8: Generate risk analysis
        risk_analysis = self.groq_analyzer.analyze_market_position(required_techs, project_description)
        
        # Save to database
        recommendation_data = {
            'requirements_analysis': requirements_analysis,
            'tech_stack': tech_stack,
            'tech_analysis': tech_analysis,
            'team_composition': team_selection.get('team', []),
            'cost_estimation': cost_estimation,
            'roadmap': roadmap,
            'risk_analysis': risk_analysis
        }
        self.json_db.save_recommendation(
            project_description,
            budget_constraint,
            timeline,
            recommendation_data
        )
        
        # Format the standardized output
        return self._format_output(
            project_description,
            requirements_analysis,
            tech_stack,
            tech_analysis,
            team_selection.get('team', []),
            cost_estimation,
            roadmap,
            risk_analysis,
            budget_constraint,
            timeline
        )

    def _format_output_from_db(self, db_data, budget_constraint, timeline):
        """Format database data into the same output structure"""
        return self._format_output(
            "Cached Project Description",  # We don't store the original in the recommendations table
            db_data['requirements_analysis'],
            db_data['tech_stack'],
            json.loads(db_data['tech_analysis']) if isinstance(db_data['tech_analysis'], str) else db_data['tech_analysis'],
            db_data['team_composition'],
            db_data['cost_estimation'],
            db_data['roadmap'],
            db_data['risk_analysis'],
            budget_constraint,
            timeline
        )

    def _identify_required_technologies(self, project_description):
        """Identify required technologies from project description"""
        techs = set()
        
        # Extract technology names from description
        tech_pattern = re.compile(
            r'\b(react|angular|vue\.?js|node\.?js|django|flask|spring|rails|express|laravel|asp\.?net|ruby|php|python|java|javascript|typescript|go|rust|kotlin|swift|flutter|react native|aws|azure|gcp|firebase|heroku|mongodb|mysql|postgresql|redis|graphql|rest api|oauth|kubernetes|docker|jenkins|github actions|circle ci|tensorflow|pytorch|scikit-learn)\b',
            re.IGNORECASE
        )
        found_techs = tech_pattern.findall(project_description.lower())
        techs.update(found_techs)
        
        # Extract required technologies from explicit statements
        required_pattern = re.compile(r'required technologies?:?\s*(.*?)(?:\.|$)', re.IGNORECASE)
        required_match = required_pattern.search(project_description)
        if required_match:
            req_techs = [t.strip() for t in required_match.group(1).split(',')]
            techs.update(req_techs)
        
        # Search for additional technologies
        additional_techs = self.market_analyzer.search_technologies(project_description)
        techs.update(additional_techs)
        
        # Extract technologies mentioned in requirements analysis
        req_tech_pattern = re.compile(r'\b(react|angular|vue\.?js|node\.?js|django|flask|spring|rails|express|laravel|asp\.?net|ruby|php|python|java|javascript|typescript|go|rust|kotlin|swift|flutter|react native|aws|azure|gcp|firebase|heroku|mongodb|mysql|postgresql|redis|graphql|rest api|oauth|kubernetes|docker|jenkins|github actions|circle ci|tensorflow|pytorch|scikit-learn)\b', 
            re.IGNORECASE)
        
        # If no technologies found, add some default ones based on project description
        if not techs:
            if 'web' in project_description.lower():
                techs.update(['react', 'node.js', 'mongodb'])
            elif 'mobile' in project_description.lower():
                techs.update(['react native', 'node.js', 'mongodb'])
            elif 'data' in project_description.lower():
                techs.update(['python', 'tensorflow', 'postgresql'])
            else:
                techs.update(['react', 'node.js', 'mongodb'])
        
        # Remove empty strings and normalize technology names
        techs = [tech for tech in techs if tech and isinstance(tech, str)]
        return list(techs)

    def _calculate_project_cost(self, team_selection, timeline):
        """Calculate project cost based on project requirements and team composition"""
        timeline_months = self._convert_timeline_to_months(timeline)
        
        if not team_selection:
            return {
                'total_cost': 0,
                'monthly_burn_rate': 0,
                'breakdown': [],
                'timeline_months': timeline_months,
                'cost_factors': {
                    'team_expertise_factor': 1.0,
                    'timeline_factor': 1.0,
                    'complexity_factor': 1.0
                }
            }
        
        # Define base rates per expertise level (monthly)
        base_rates = {
            "Beginner": 5000,
            "Intermediate": 8000,
            "Advanced": 12000
        }
        
        cost_breakdown = []
        total_cost = 0
        
        # Calculate expertise factor
        expertise_counts = {"Beginner": 0, "Intermediate": 0, "Advanced": 0}
        
        for member in team_selection:
            # Use get() method to safely access expertise_level with a default value
            expertise_level = member.get('expertise_level', 'Intermediate')
            expertise_counts[expertise_level] += 1
            
            base_rate = base_rates.get(expertise_level, 8000)
            # Use get() method to safely access availability with a default value
            availability_percentage = member.get('availability', 100)
            monthly_cost = base_rate * (availability_percentage / 100)
            member_cost = monthly_cost * timeline_months
            total_cost += member_cost
            
            cost_breakdown.append({
                'name': member.get('name', member.get('role', 'Team Member')),
                'role': member.get('role', 'Developer'),
                'expertise_level': expertise_level,
                'monthly_cost': monthly_cost,
                'total_cost': member_cost,
                'monthly_hours': member.get('monthly_hours', 160 * availability_percentage / 100),
                'hourly_rate': monthly_cost / (member.get('monthly_hours', 160 * availability_percentage / 100)),
                'technologies': member.get('technologies', member.get('matched_skills', []))
            })
        
        monthly_burn_rate = total_cost / timeline_months if timeline_months > 0 else 0
        
        # Calculate cost factors for detailed explanation
        team_expertise_factor = (expertise_counts["Advanced"] * 1.2 + 
                                expertise_counts["Intermediate"] * 1.0 + 
                                expertise_counts["Beginner"] * 0.8) / max(sum(expertise_counts.values()), 1)
        
        timeline_factor = {
            2: 1.2,    # Short timeline (1-3 months)
            4.5: 1.0,  # Standard timeline (3-6 months)
            9: 0.9,    # Extended timeline (6-12 months)
            15: 0.8    # Long-term timeline (12+ months)
        }.get(timeline_months, 1.0)
        
        # Calculate project complexity factor based on technologies
        unique_techs = set()
        for member in cost_breakdown:
            unique_techs.update(member['technologies'])
        
        complexity_factor = min(1.0 + (len(unique_techs) * 0.05), 1.5)
        
        return {
            'total_cost': total_cost,
            'monthly_burn_rate': monthly_burn_rate,
            'breakdown': cost_breakdown,
            'timeline_months': timeline_months,
            'cost_factors': {
                'team_expertise_factor': team_expertise_factor,
                'timeline_factor': timeline_factor,
                'complexity_factor': complexity_factor,
                'team_size': len(cost_breakdown),
                'unique_technologies': len(unique_techs)
            }
        }

    def _convert_timeline_to_months(self, timeline):
        """Convert timeline string to months"""
        if "1-3" in timeline:
            return 2
        elif "3-6" in timeline:
            return 4.5
        elif "6-12" in timeline:
            return 9
        else:  # 12+ months
            return 15

    def _format_output(self, project_desc, requirements, tech_stack, tech_analysis, team, costs, roadmap, risks, budget, timeline):
        """Format all data into standardized output structure"""
        output = f"""
# TECHNOLOGY STACK RECOMMENDATION REPORT

## 1. PROJECT OVERVIEW
**Description:** {project_desc}

**Budget Constraint:** {budget}
**Timeline:** {timeline}

## 2. REQUIREMENTS ANALYSIS
{requirements}

## 3. RECOMMENDED TECHNOLOGY STACK
{tech_stack}

## 4. TECHNOLOGY ANALYSIS
"""
        for tech, analysis in tech_analysis.items():
            # Ensure salary data is properly formatted
            if isinstance(analysis.get('salary_data', {}), dict):
                low_salary = analysis['salary_data'].get('low', 0)
                high_salary = analysis['salary_data'].get('high', 0)
                salary_range = f"${low_salary:,.0f} - ${high_salary:,.0f}"
            else:
                salary_range = "Data not available"
                
            # Get market position or indicate it's being retrieved
            market_position = analysis.get('market_position', '')
            if not market_position or market_position == "Market data not available":
                market_position = "Currently retrieving market position data..."
            
            output += f"""
### {tech}
- **Category:** {analysis.get('category', 'N/A')}
- **Description:** {analysis.get('description', 'N/A')}
- **Market Position:** {market_position}
- **Salary Range (Annual):** {salary_range}
"""
            if analysis.get('competitors'):
                output += "- **Competitors:** " + ", ".join(analysis['competitors']) + "\n"
            if analysis.get('merits'):
                output += "- **Key Advantages:**\n"
                for merit in analysis['merits']:
                    output += f"  - {merit}\n"

        output += f"""
## 5. TEAM COMPOSITION
**Total Team Members:** {len(team)}
**Project Duration:** {costs['timeline_months']} months
"""
        for member in team:
            # Use get() method to safely access member attributes with default values
            output += f"""
### {member.get('name', 'Team Member')} ({member.get('role', 'Developer')})
- **Expertise Level:** {member.get('expertise_level', 'N/A')}
- **Availability:** {member.get('availability', 'N/A')}%
- **Technologies:** {', '.join(member.get('technologies', []))}
"""
        
        # Enhanced cost estimation section with detailed breakdown
        output += f"""
## 6. COST ESTIMATION
**Total Project Cost:** ${costs['total_cost']:,.2f}
**Monthly Team Cost:** ${costs['monthly_burn_rate']:,.2f}

### Cost Breakdown Factors:
- **Team Size:** {costs['cost_factors']['team_size']} members
- **Project Duration:** {costs['timeline_months']} months
- **Team Expertise Level Factor:** {costs['cost_factors']['team_expertise_factor']:.2f} (higher values indicate more senior team)
- **Timeline Factor:** {costs['cost_factors']['timeline_factor']:.2f} (projects with shorter timelines typically cost more per month)
- **Project Complexity Factor:** {costs['cost_factors']['complexity_factor']:.2f} (based on {costs['cost_factors']['unique_technologies']} unique technologies)

### Cost Calculation:
The total cost is calculated by multiplying the monthly team cost by the project duration.
Monthly team cost represents the sum of all team members' compensation based on their expertise level,
availability, and the specific technologies they bring to the project.

## 7. IMPLEMENTATION ROADMAP
{roadmap}

## 8. RISK ANALYSIS
{risks}
"""
        return output