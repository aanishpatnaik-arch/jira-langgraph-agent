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
    Fetch tickets assigned to, reported by, or mentioning the current user.
    Optionally filter by status (e.g., "Closed", "In Progress").
    Returns a human-readable string grouped by role.
    """
    jira = get_jira_client()
    current_user = jira.current_user()  # username (e.g., 'aanish_p')

    # Get full profile display name dynamically
    profile = jira.user(current_user)
    display_name = profile.displayName  # e.g., 'Aanish Patnaik'
    print(display_name)

    # JQL for assigned and reported
    status_clause = f" AND status = '{status}'" if status else ""
    assigned_jql = f"assignee = currentUser(){status_clause} ORDER BY updated DESC"
    reported_jql = f"reporter = currentUser(){status_clause} ORDER BY updated DESC"

    assigned_issues = jira.search_issues(assigned_jql, maxResults=None)
    reported_issues = jira.search_issues(reported_jql, maxResults=None)

    # Fetch all issues to check for mentions
    all_issues_jql = f'text ~ "{display_name}"{status_clause} ORDER BY updated DESC'  # no time range
    all_issues = jira.search_issues(all_issues_jql, maxResults=None)

    # Filter mentions strictly by display name in comment bodies
    mentioned_issues = []
    for issue in all_issues:
        # Skip if already assigned/reported
        if issue in assigned_issues or issue in reported_issues:
            continue
        comments = getattr(issue.fields, "comment", {}).comments or []
        for comment in comments:
            if f"@{display_name}" in comment.body:
                mentioned_issues.append(issue)
                break  # only add once per ticket

    # Helper to format issues
    def format_issues(issues):
        return [
            f"[{issue.key}] {issue.fields.summary} (Status: {issue.fields.status.name})"
            for issue in issues
        ]

    output_lines = []

    if assigned_issues:
        output_lines.append("🔹 Assigned to You:")
        output_lines.extend(f"  {i+1}. {line}" for i, line in enumerate(format_issues(assigned_issues)))

    if reported_issues:
        output_lines.append("\n🔹 Reported by You:")
        output_lines.extend(f"  {i+1}. {line}" for i, line in enumerate(format_issues(reported_issues)))

    if mentioned_issues:
        output_lines.append("\n🔹 You are Mentioned in:")
        output_lines.extend(f"  {i+1}. {line}" for i, line in enumerate(format_issues(mentioned_issues)))

    if not output_lines:
        return f"No tickets found for status '{status}'." if status else "No tickets found."

    return "\n".join(output_lines)

def fetch_statuses():
    """
    Return all possible statuses in the Jira instance (lowercased)
    """
    jira = get_jira_client()
    return [s.name for s in jira.statuses()]
