import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = "models/gemini-2.0-flash"
    TEMPERATURE = 0.7
    TOP_P = 0.95
    TOP_K = 40

    # Add these for Jira
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")  # e.g., https://jira.enttxn.com
    JIRA_USERNAME = os.getenv("JIRA_USERNAME")
    JIRA_PAT = os.getenv("JIRA_PAT")  # or password if using basic auth

settings = Settings()
