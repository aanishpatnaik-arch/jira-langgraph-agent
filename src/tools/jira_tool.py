from jira import JIRA
from config.settings import settings

def fetch_tickets():
    try:
        # Connect to Jira using official client with Basic Auth
        jira = JIRA(
            server="https://jira.enttxn.com",
            basic_auth=(settings.JIRA_USERNAME, settings.JIRA_PAT)  
            # JIRA_PAT = Personal Access Token or Password (if server allows)
        )

        # Fetch issues for the current user
        issues = jira.search_issues(
            'assignee = currentUser() ORDER BY updated DESC',
            maxResults=10,
            fields="key,summary,status"
        )

        if not issues:
            return "You have no assigned tickets."

        # Format response
        tickets = [
            {
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name
            }
            for issue in issues
        ]
        return f"Your assigned tickets: {tickets}"

    except Exception as e:
        return f"Error connecting to Jira: {e}"
