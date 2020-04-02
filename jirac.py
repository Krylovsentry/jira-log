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
        config.get("Settings", "brazil_team")
    ]

if __name__ == "__main__":
    path = "settings.ini"
    [jira_server, project, user_name, password, team, cis_team, brazil_team] = crud_config(path)

    # initialize jira api
    jira_options = {'server': jira_server}
    jira = JIRA(options=jira_options, basic_auth=(user_name, password))

    for user in str(cis_team).split(','):
        issues = jira.search_issues(f'assignee = {user} AND resolution = Unresolved and type in (Bug, Defect) and status in (Open)')
        if issues.total < 2:
            lead_issues = jira.search_issues(f'assignee = {user_name} AND resolution = Unresolved and type in (Bug, Defect) and status in (Open) ORDER BY priority DESC')
            jira.assign_issue(lead_issues.next(), user)
            jira.assign_issue(lead_issues.next(), user)
