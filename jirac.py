import configparser
import os
from datetime import datetime, timedelta

from jira import JIRA

from jirap import JiraProxy


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
    config.set("Settings", "team", "team assignee codes")
    config.set("Settings", "components", "сomponent labels")

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
        config.get("Settings", "components")
    ]


if __name__ == "__main__":
    path = "settings.ini"
    [jira_server, project, user_name, password, team, components] = crud_config(path)

    # initialize jira api
    jira_options = {'server': jira_server}
    jiraProxy = JiraProxy(
        JIRA(options=jira_options, basic_auth=(user_name, password)),
        str(team).split(','), user_name, str(components).split(','), project, jira_server
    )

    # issues = jiraProxy.search_issues("filter = 5889579 and summary ~ 'UX' and resolution = Unresolved ")
    # print(issues)
    # jiraProxy.bulk_issue_update(issues, {'label': 'UI/UX'})
    # jiraProxy.check_un_estimate_tasks()
    jiraProxy.update_data(weeks=4, labels="'DS', 'Build'")
    jiraProxy.make_velocities()
    jiraProxy.make_velocities(False)
    # created_tickets = jiraProxy.get_medium_count_of_tickets_create(label='Release4.05', weeks=8, priority='Major')
    # # time_for_bugs = jiraProxy.get_medium_time_for_bugs('Release4.05', 4)
    # print(f"time for 1 bug: {time_for_bugs}")
    # print(f"created ticket median: {created_tickets}")
    # print(f"time for bugs: {created_tickets * time_for_bugs}")
