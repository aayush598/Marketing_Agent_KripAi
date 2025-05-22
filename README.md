# Marketing_Agent
# 🤖 AI-Powered Technology Stack Recommender

An intelligent system that provides comprehensive technology stack recommendations, optimal team composition, and detailed cost analysis based on project requirements, budget constraints, and timeline.

## 🌟 Features

- **Intelligent Project Analysis**: Uses Groq AI to analyze project requirements and extract key technical needs
- **Technology Stack Recommendations**: Suggests optimal frontend, backend, database, and infrastructure technologies
- **Team Composition Optimization**: Selects the best team members based on skills, expertise level, and availability
- **Real-time Market Analysis**: Fetches current salary data and technology trends from the web
- **Cost Estimation**: Provides detailed project cost breakdown including team costs and timeline factors
- **Implementation Roadmap**: Generates phase-by-phase development roadmap
- **Risk Analysis**: Analyzes market position and potential risks for recommended technologies
- **Caching System**: Stores recommendations in JSON database for faster retrieval

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Groq API Key (for AI analysis)
- Internet connection (for web scraping and market analysis)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-tech-recommender
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API key**
   - Update `config.py` with your Groq API key:
   ```python
   GROQ_API_KEY = "your_groq_api_key_here"
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:8501`

## 📁 Project Structure

```
ai-tech-recommender/
├── app.py                 # Streamlit web interface
├── recommender.py         # Main recommendation engine
├── groq_integration.py    # AI analysis using Groq API
├── market_analyzer.py     # Web scraping and market analysis
├── database.py           # Team data management and queries
├── database_utils.py     # JSON storage utilities
├── config.py             # Configuration and API keys
├── teams.json            # Team members database
├── requirements.txt      # Python dependencies
├── data/                 # JSON storage directory
│   ├── projects.json     # Cached projects
│   └── recommendations.json # Cached recommendations
└── README.md            # This file
```

## 🔧 Configuration

### API Keys

Update `config.py` with your API keys:

```python
GROQ_API_KEY = "your_groq_api_key_here"
```

### Team Database

The `teams.json` file contains information about available team members:

```json
{
  "teams": [
    {
      "id": 1,
      "name": "Frontend Team",
      "members": [
        {
          "id": 101,
          "name": "John Smith",
          "role": "Senior Frontend Developer",
          "skills": ["React", "TypeScript", "CSS"],
          "expertise_level": "Advanced",
          "availability": 80,
          "years_experience": 7,
          "remote_work": true
        }
      ]
    }
  ]
}
```

## 💡 Usage

### Web Interface

1. **Describe your project**: Enter detailed project requirements
2. **Set constraints**: Choose budget (tight/moderate/flexible) and timeline
3. **Select technologies** (optional): Choose specific technologies you want to use
4. **Generate recommendation**: Click the button to get comprehensive analysis

### Example Project Description

```
I need to build an e-commerce platform for small businesses. 
The platform should support:
- Product catalog management
- Shopping cart and checkout
- User authentication and profiles
- Payment processing (Stripe integration)
- Admin dashboard for inventory management
- Mobile-responsive design
- Expected to handle 1000+ concurrent users
- Need to integrate with existing accounting software
```

### Output Includes

- **Requirements Analysis**: Structured breakdown of project needs
- **Technology Stack**: Recommended technologies with justifications
- **Technology Analysis**: Market position, salary data, and competitive analysis
- **Team Composition**: Optimal team members with roles and expertise
- **Cost Estimation**: Detailed cost breakdown and factors
- **Implementation Roadmap**: Phase-by-phase development plan
- **Risk Analysis**: Market trends and potential challenges

## 🛠️ Core Components

### TechnologyRecommender (`recommender.py`)
- Main orchestrator that coordinates all analysis components
- Handles caching and data persistence
- Formats comprehensive output reports

### GroqAnalyzer (`groq_integration.py`)
- Uses Groq AI API for intelligent project analysis
- Generates technology stack recommendations
- Creates implementation roadmaps and risk assessments

### MarketAnalyzer (`market_analyzer.py`)
- Web scraping for real-time salary data
- Technology trend analysis using DuckDuckGo search
- Market position assessment and competitive analysis

### DatabaseConnection (`database.py`)
- Manages team member data and skills matching
- Optimal team composition algorithm
- Technology domain classification

## 📊 Algorithm Details

### Team Selection Algorithm

1. **Skill Matching**: Matches required technologies with team member skills
2. **Expertise Scoring**: Considers experience level and years of experience
3. **Domain Coverage**: Ensures all technology domains are covered
4. **Availability Optimization**: Factors in team member availability percentages
5. **Cost Optimization**: Balances expertise with budget constraints

### Cost Calculation

```python
# Base rates by expertise level (monthly)
base_rates = {
    "Beginner": $5,000,
    "Intermediate": $8,000,
    "Advanced": $12,000
}

# Factors affecting cost
- Team expertise factor
- Timeline urgency factor
- Project complexity factor
- Technology demand multiplier
```

## 🔍 Data Sources

- **Salary Data**: Web scraping from multiple job sites and salary databases
- **Technology Trends**: DuckDuckGo search results from tech publications
- **Market Analysis**: Real-time web scraping from technology blogs and news sites
- **Team Data**: JSON database with skills, availability, and experience

## 🚨 Error Handling

The system includes robust error handling for:
- API rate limits and timeouts
- Web scraping failures
- Missing team data
- Invalid project descriptions
- Network connectivity issues

## 📈 Performance Optimization

- **Caching**: Results cached in JSON files to avoid redundant API calls
- **Lazy Loading**: Market data fetched only when needed
- **Timeout Management**: Reasonable timeouts for web requests
- **Batch Processing**: Multiple searches conducted efficiently

## 🛡️ Security Considerations

- API keys stored in configuration files (not in code)
- Web scraping with respect for robots.txt
- Input validation for project descriptions
- Safe JSON parsing and error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Future Enhancements

- [ ] Integration with more AI models (OpenAI, Anthropic)
- [ ] Real-time team availability tracking
- [ ] Project template library
- [ ] Advanced cost optimization algorithms
- [ ] Integration with project management tools
- [ ] Multi-language support
- [ ] Docker containerization
- [ ] API endpoints for programmatic access

## 🐛 Known Issues

- Web scraping may occasionally fail due to site changes
- Groq API rate limits may affect response times
- Some technology salary data may be estimated rather than real-time

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Groq** for providing AI analysis capabilities
- **Streamlit** for the web interface framework
- **DuckDuckGo** for search API access
- **BeautifulSoup** for web scraping functionality

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

## 🔗 Links

- [Groq API Documentation](https://console.groq.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Project Demo](#) (Add your demo link here)

---

**Built with ❤️ by the AI Tech Recommender Team**
