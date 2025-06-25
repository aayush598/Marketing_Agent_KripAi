from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Access environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SEARCH_DOMAINS = os.getenv("SEARCH_DOMAINS")
CLOUD_PROVIDERS = os.getenv("CLOUD_PROVIDERS")