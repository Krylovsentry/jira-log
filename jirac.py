import configparser
import os

from jira import JIRA


def create_config(path):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "jira_server", "jira server")
    config.set("Settings", "project", "project name")
    config.set("Settings", "user_name", "your username")
    config.set("Settings", "password", "your password")
    config.set("Settings", "team", "team assignie codes")

    with open(path, "w") as config_file:
        config.write(config_file)


def crud_config(path):
    if not os.path.exists(path):
        create_config(path)
    config = configparser.ConfigParser()
    config.read(path)

    return [
        config.get("Settings", "jira_server"),
        config.get("Settings", "project"),
        config.get("Settings", "user_name"),
        config.get("Settings", "password"),
        config.get("Settings", "team"),
        config.get("Settings", "cis_team"),
        config.get("Settings", "brazil_team"),
        config.get("Settings", "component")
    ]


def team_assign(jira, lead, team, count=2):
    for user in str(team).split(','):
        issues = jira.search_issues(
            f'assignee = {user} AND resolution = Unresolved and type in (Bug, Defect) and status in (Open)')
        if issues.total < count:
            lead_issues = jira.search_issues(
                f'assignee = {lead} AND resolution = Unresolved and type in (Bug, Defect) and status in (Open) ORDER BY priority DESC')
            jira.assign_issue(lead_issues.next(), user)
            jira.assign_issue(lead_issues.next(), user)


def create_issue(jira, project, summary, component, lead):
    issue_dict = {
        'project': project,
        'summary': summary,
        'description': summary,
        'issuetype': {'name': 'Defect'},
        'components': [{'name': component}],
        'assignee': {'name': lead},
        'customfield_10014': {'id': '10010'}
    }
    jira.create_issue(fields=issue_dict)


def issues_resolved(jira, user, type):
    return jira.search_issues(
        f'status changed by {user} AND resolutiondate >= startOfWeek(-14d) AND resolutiondate < endOfWeek(-7d) and type in ({type})')


def time_logged():
    pass


def count_velocity():
    # | time logged * (2 / count of tasks + 1 / bugs)
    # || original estimate / logged on ticket
    pass

if __name__ == "__main__":
    path = "settings.ini"
    [jira_server, project, user_name, password, team, cis_team, brazil_team, component] = crud_config(path)

    # initialize jira api
    jira_options = {'server': jira_server}
    jira = JIRA(options=jira_options, basic_auth=(user_name, password))
    team_assign(jira, user_name, cis_team, 2)

    # create_issue(jira, project, 'Test issue', component, user_name)
