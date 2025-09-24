import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    JIRA_USERNAME = os.getenv("JIRA_USERNAME")   # your Jira username
    JIRA_PAT = os.getenv("JIRA_PAT")             # PAT or password
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = "models/gemini-2.0-flash"
    TEMPERATURE = 0.7

settings = Settings()
