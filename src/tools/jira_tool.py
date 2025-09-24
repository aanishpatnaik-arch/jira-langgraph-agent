from config.settings import settings
from jira import JIRA

def get_jira_client():
    # Create Jira client
    jira = JIRA(
        server=settings.JIRA_BASE_URL,
        basic_auth=(settings.JIRA_USERNAME, settings.JIRA_PAT)
    )
    return jira

def fetch_tickets_by_status(status: str = None):
    """
    Fetch tickets assigned to the current user.
    Optionally filter by status (e.g., "Closed", "In Progress").
    Returns a human-readable string.
    """
    jira = get_jira_client()
    jql = "assignee = currentUser()"
    if status:
        jql += f" AND status = '{status}'"
    jql += " ORDER BY updated DESC"

    issues = jira.search_issues(jql, maxResults=None)

    if not issues:
        return f"No tickets found for status '{status}'." if status else "No tickets assigned."

    # Format output in human-readable form
    output = []
    for i, issue in enumerate(issues, start=1):
        output.append(
            f"{i}. [{issue.key}] {issue.fields.summary} (Status: {issue.fields.status.name})"
        )

    return "\n".join(output)

def fetch_statuses():
    """
    Return all possible statuses in the Jira instance (lowercased)
    """
    jira = get_jira_client()
    return [s.name for s in jira.statuses()]
