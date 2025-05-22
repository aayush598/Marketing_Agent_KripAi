from groq import Groq
from config import GROQ_API_KEY

class GroqAnalyzer:
    def __init__(self):
        try:
            # Initialize client with minimal configuration
            self.client = Groq(
                api_key=GROQ_API_KEY,
                # Explicitly set timeout and other optional parameters
                timeout=30.0,
            )
        except TypeError as e:
            # Fallback to simpler initialization if the above fails
            self.client = Groq(api_key=GROQ_API_KEY)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Groq client: {e}")

    def analyze_project_requirements(self, project_description):
        """Analyze project requirements to extract key details."""
        try:
            completion = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{
                    "role": "user",
                    "content": f"""Analyze this project description and extract the following key requirements in a structured format:
                    
                    Project Description:
                    {project_description}
                    
                    Provide output in this exact structure:
                    
                    ### 1. Project Overview
                    - Primary goal: [clear statement of main objective]
                    - Target users: [list of user types]
                    - Key success metrics: [3-5 measurable outcomes]
                    
                    ### 2. Functional Requirements
                    - [List 5-7 core functional requirements]
                    
                    ### 3. Technical Requirements
                    - Performance: [specific requirements]
                    - Scalability: [expected growth]
                    - Security: [specific needs]
                    - Integrations: [external systems]
                    
                    ### 4. Constraints
                    - Budget: [any mentioned constraints]
                    - Timeline: [key milestones]
                    - Team: [any specific team requirements]
                    
                    Be concise but comprehensive. Use bullet points for clarity."""
                }],
                temperature=0.5,
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return "Requirements analysis failed"
    
    def suggest_technology_stack(self, project_requirements, budget_constraint, timeline):
        """Suggest appropriate technology stack based on project requirements."""
        try:
            completion = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{
                    "role": "user",
                    "content": f"""Based on these project requirements, suggest an optimal technology stack in this exact format:
                    
                    Requirements:
                    {project_requirements}
                    
                    Budget Constraint: {budget_constraint}
                    Timeline: {timeline}
                    
                    ### Recommended Technology Stack
                    
                    #### 1. Frontend
                    - Primary Framework: [recommendation with version]
                    - State Management: [solution]
                    - UI Components: [library]
                    - Testing: [framework]
                    
                    #### 2. Backend
                    - Language: [recommendation]
                    - Framework: [specific version]
                    - API Architecture: [REST/GraphQL/etc]
                    - Authentication: [solution]
                    
                    #### 3. Database
                    - Primary Database: [recommendation]
                    - ORM/Driver: [tool]
                    - Caching: [solution]
                    
                    #### 4. DevOps & Infrastructure
                    - Hosting: [provider]
                    - CI/CD: [pipeline]
                    - Monitoring: [tools]
                    - Containerization: [solution]
                    
                    #### 5. Additional Components
                    - Analytics: [tools]
                    - Error Tracking: [service]
                    - Payment: [processor]
                    
                    For each recommendation, include a 1-sentence justification considering budget and timeline."""
                }],
                temperature=0.7,
                max_tokens=1536,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return "Technology stack suggestion failed"
    
    def generate_implementation_roadmap(self, project_description, technology_stack, timeline):
        """Generate an implementation roadmap for the project."""
        try:
            completion = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{
                    "role": "user",
                    "content": f"""Create a detailed implementation roadmap in this exact format:
                    
                    Project Description:
                    {project_description}
                    
                    Technology Stack:
                    {technology_stack}
                    
                    Timeline: {timeline}
                    
                    ### Implementation Roadmap
                    
                    #### 1. Planning Phase (Weeks 1-2)
                    - [Task 1]
                    - [Task 2]
                    - Deliverables: [list]
                    
                    #### 2. Core Development (Weeks 3-8)
                    - Frontend: [tasks]
                    - Backend: [tasks]
                    - Deliverables: [list]
                    
                    #### 3. Testing & QA (Weeks 9-10)
                    - Unit Tests: [coverage goal]
                    - Integration Tests: [scope]
                    - Deliverables: [list]
                    
                    #### 4. Deployment & Launch (Week 11-12)
                    - Infrastructure Setup: [tasks]
                    - CI/CD Pipeline: [steps]
                    - Deliverables: [list]
                    
                    #### 5. Post-Launch (Ongoing)
                    - Monitoring: [setup]
                    - Maintenance: [plan]
                    
                    Include realistic time estimates for each phase based on the timeline."""
                }],
                temperature=0.7,
                max_tokens=1536,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return "Roadmap generation failed"
    
    def analyze_market_position(self, technologies, project_description):
        """Analyze market position and trends for the recommended technologies."""
        try:
            completion = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{
                    "role": "user",
                    "content": f"""Analyze the market position for these technologies in this exact format:
                    
                    Technologies: {', '.join(technologies)}
                    
                    Project Context:
                    {project_description}
                    
                    ### Market Analysis
                    
                    #### 1. Technology Trends
                    - Adoption Rates: [analysis]
                    - Future Outlook: [projections]
                    
                    #### 2. Hiring Landscape
                    - Talent Availability: [assessment]
                    - Salary Ranges: [data]
                    
                    #### 3. Competitive Analysis
                    - Strengths: [compared to alternatives]
                    - Weaknesses: [potential risks]
                    
                    #### 4. Recommendations
                    - Long-term Viability: [assessment]
                    - Risk Mitigation: [strategies]
                    
                    Provide concise, data-driven insights for each section."""
                }],
                temperature=0.7,
                max_tokens=1536,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return "Market analysis failed"