import requests
from bs4 import BeautifulSoup
import re
import json
from collections import defaultdict
from database import DatabaseConnection
from duckduckgo_search import DDGS
import time

class MarketAnalyzer:
    def __init__(self):
        self.db = DatabaseConnection()
        self.tech_cache = {}
        self.salary_cache = {}

    def search_technologies(self, query):
        """Search for technologies related to the query"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{query} technologies", max_results=5))
                technologies = set()

                for result in results:
                    try:
                        response = requests.get(result['href'], timeout=10)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        text = ' '.join([p.get_text() for p in soup.find_all('p')]).lower()

                        # Extract technology names
                        tech_pattern = re.compile(
                            r'\b(react|angular|vue\.?js|node\.?js|django|flask|spring|rails|express|laravel|asp\.?net|ruby|php|python|java|javascript|typescript|go|rust|kotlin|swift|flutter|react native|aws|azure|gcp|firebase|heroku|mongodb|mysql|postgresql|redis|graphql|rest api|oauth|kubernetes|docker|jenkins|github actions|circle ci|tensorflow|pytorch|scikit-learn)\b'
                        )
                        found_techs = tech_pattern.findall(text)
                        technologies.update(found_techs)

                    except Exception:
                        continue

                return list(technologies)
        except Exception as e:
            print(f"Technology search error: {e}")
            return []

    def get_tech_salary(self, technology):
        """Get current salary data for a technology"""
        if technology in self.salary_cache:
            return self.salary_cache[technology]

        # Define default salaries based on technology category
        tech_category = self._determine_tech_category(technology)

        # Base salaries per category (annual)
        category_salaries = {
            "Frontend": {"low": 70000, "median": 95000, "high": 130000},
            "Backend": {"low": 80000, "median": 110000, "high": 150000},
            "Database": {"low": 85000, "median": 115000, "high": 145000},
            "Cloud": {"low": 90000, "median": 125000, "high": 160000},
            "Mobile": {"low": 85000, "median": 120000, "high": 155000},
            "Data": {"low": 95000, "median": 130000, "high": 170000},
            "Other": {"low": 75000, "median": 100000, "high": 135000}
        }

        # Get base salary for category
        base_salary = category_salaries.get(tech_category, category_salaries["Other"])

        # Adjust based on technology popularity (simplified)
        popular_techs = ["react", "node.js", "python", "aws", "docker"]
        if any(t in technology.lower() for t in popular_techs):
            base_salary = {k: v * 1.1 for k, v in base_salary.items()}

        # Store annual salary
        self.salary_cache[technology] = base_salary
        return base_salary

    def get_tech_analysis(self, tech_names):
        """Get comprehensive analysis of technologies"""
        tech_data = {}

        for tech in tech_names:
            if tech in self.tech_cache:
                tech_data[tech] = self.tech_cache[tech]
                continue

            # Get salary data - ensure it's properly formatted (annual figures)
            salary_data = self.get_tech_salary(tech)

            # Get technology category and description
            category = self._determine_tech_category(tech)
            description = self._get_tech_description(tech)

            # Get market position and trends - ensure robust data retrieval
            market_position = self._get_detailed_market_position(tech)

            # Get competitors and merits
            competitors, merits = self._get_tech_comparison(tech)

            tech_data[tech] = {
                'name': tech,
                'category': category,
                'description': description,
                'salary_data': salary_data,
                'market_position': market_position,
                'competitors': competitors,
                'merits': merits,
                'last_updated': time.time()
            }

            self.tech_cache[tech] = tech_data[tech]

        return tech_data

    def _get_detailed_market_position(self, tech):
        """Get detailed market position and trends for a technology with improved reliability"""
        try:
            # Try multiple search queries to increase chances of getting relevant data
            search_queries = [
                f"{tech} technology market position 2024",
                f"{tech} developer demand trends",
                f"{tech} technology adoption rate",
                f"state of {tech} technology 2024"
            ]
            
            all_results = []
            with DDGS() as ddgs:
                for query in search_queries:
                    results = list(ddgs.text(query, max_results=2))
                    all_results.extend(results)
                    if len(all_results) >= 3:
                        break
                
                position_data = []
                for result in all_results[:3]:  # Use top 3 results
                    try:
                        response = requests.get(result['href'], timeout=10)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        paragraphs = soup.find_all('p')
                        
                        # Extract paragraphs containing tech name and market-related terms
                        for p in paragraphs:
                            text = p.get_text()
                            if tech.lower() in text.lower() and any(term in text.lower() for term in 
                                                                  ["market", "adoption", "trend", "popular", "demand", "industry"]):
                                position_data.append(text)
                                break  # Take first relevant paragraph per result
                    except:
                        continue
                
                if position_data:
                    # Use the most informative paragraph (typically the longest)
                    best_paragraph = max(position_data, key=len)
                    # Trim to reasonable length
                    return best_paragraph[:300] + '...' if len(best_paragraph) > 300 else best_paragraph
                else:
                    # Fallback with analysis based on category
                    category = self._determine_tech_category(tech)
                    return f"{tech} is an established technology in the {category} space with steady market adoption. It continues to be relevant in 2024 for software development projects."
        except Exception as e:
            print(f"Error getting detailed market position for {tech}: {e}")
            return f"{tech} is currently used in modern software development with stable market adoption."

    def _determine_tech_category(self, tech):
        """Determine technology category"""
        tech_lower = tech.lower()
        if 'react' in tech_lower or 'angular' in tech_lower or 'vue' in tech_lower:
            return 'Frontend'
        elif 'node' in tech_lower or 'django' in tech_lower or 'flask' in tech_lower:
            return 'Backend'
        elif 'mysql' in tech_lower or 'postgres' in tech_lower or 'mongodb' in tech_lower:
            return 'Database'
        elif 'aws' in tech_lower or 'azure' in tech_lower or 'gcp' in tech_lower:
            return 'Cloud'
        elif 'flutter' in tech_lower or 'swift' in tech_lower or 'kotlin' in tech_lower:
            return 'Mobile'
        elif 'tensorflow' in tech_lower or 'pytorch' in tech_lower or 'scikit' in tech_lower:
            return 'Data'
        else:
            return 'Other'

    def _get_tech_description(self, tech):
        """Get technology description from web"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"What is {tech} technology", max_results=2))
                if results:
                    response = requests.get(results[0]['href'], timeout=10)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    paragraphs = [p.get_text() for p in soup.find_all('p')]
                    for p in paragraphs:
                        if tech.lower() in p.lower() and len(p) > 50:
                            return p[:250] + '...' if len(p) > 250 else p
            
            # Fallback descriptions for common technologies
            fallbacks = {
                "react": "React is a JavaScript library for building user interfaces, particularly single-page applications. It allows developers to create reusable UI components.",
                "node.js": "Node.js is a JavaScript runtime built on Chrome's V8 engine that allows execution of JavaScript code server-side.",
                "mongodb": "MongoDB is a NoSQL database that uses a document-oriented data model with flexible schema for storing data in JSON-like documents.",
                "python": "Python is a high-level, interpreted programming language known for its readability and versatility in web development, data science, and automation.",
                "aws": "Amazon Web Services (AWS) is a comprehensive cloud platform offering over 200 services from data centers globally."
            }
            
            for key, desc in fallbacks.items():
                if key in tech.lower():
                    return desc
        except:
            pass
            
        return f"{tech} is a technology used in modern software development projects."

    def _get_tech_comparison(self, tech):
        """Get technology competitors and merits"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{tech} vs other technologies pros and cons", max_results=3))
                competitors = set()
                merits = []

                for result in results:
                    try:
                        response = requests.get(result['href'], timeout=10)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        text = ' '.join([p.get_text() for p in soup.find_all('p')]).lower()

                        # Extract competitors
                        vs_pattern = re.compile(fr'{tech.lower()}\s+(?:vs|versus)\s+([a-z0-9\.]+)')
                        vs_matches = vs_pattern.findall(text)
                        competitors.update(vs_matches)

                        # Extract merits
                        merit_keywords = ['advantage', 'pro', 'benefit', 'strength']
                        sentences = text.split('.')
                        merits.extend([s.strip() for s in sentences 
                                       if any(kw in s for kw in merit_keywords) and tech.lower() in s])
                    except:
                        continue
                
                # Common competitors by category as fallback
                if not competitors:
                    category = self._determine_tech_category(tech)
                    fallback_competitors = {
                        "Frontend": ["Angular", "Vue.js", "Svelte"],
                        "Backend": ["Ruby on Rails", "Django", "Express.js"],
                        "Database": ["PostgreSQL", "MySQL", "Redis"],
                        "Cloud": ["Azure", "GCP", "IBM Cloud"],
                        "Mobile": ["React Native", "Flutter", "Native iOS/Android"],
                        "Data": ["scikit-learn", "R", "MATLAB"]
                    }
                    competitors = set(fallback_competitors.get(category, ["Other alternatives"]))
                
                # Common merits by category as fallback
                if not merits:
                    category = self._determine_tech_category(tech)
                    fallback_merits = {
                        "Frontend": [
                            "Offers a component-based architecture for reusable UI elements",
                            "Strong community support and extensive ecosystem of libraries",
                            "Excellent performance with virtual DOM implementation"
                        ],
                        "Backend": [
                            "Scalable architecture for handling concurrent requests",
                            "Rich ecosystem of libraries and frameworks",
                            "Strong performance characteristics for web applications"
                        ],
                        "Database": [
                            "Optimized for scalability and performance",
                            "Robust data model with strong consistency guarantees",
                            "Excellent tooling and administrative features"
                        ],
                        "Mobile": [
                            "Cross-platform compatibility reduces development time",
                            "Native-like performance on multiple devices",
                            "Shared codebase between platforms"
                        ]
                    }
                    merits = fallback_merits.get(category, [
                        f"Industry-standard solution in the {category} space",
                        "Strong performance characteristics",
                        "Reliable and well-tested in production environments"
                    ])

                return list(competitors)[:5], merits[:3]
        except Exception as e:
            print(f"Tech comparison error: {e}")
            return [], []