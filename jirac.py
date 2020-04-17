import configparser
import os
import matplotlib

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
        config.get("Settings", "brazil_team"),
        config.get("Settings", "component")
    ]

if __name__ == "__main__":
    path = "settings.ini"
    [jira_server, project, user_name, password, team, brazil_team, component] = crud_config(path)

    # initialize jira api
    jira_options = {'server': jira_server}
    jiraProxy = JiraProxy(
        JIRA(options=jira_options, basic_auth=(user_name, password)),
        team, user_name, component, project, jira_server
    )

    tasks_velocity_2_weeks = jiraProxy.count_velocity_on_tasks()
    bugs_velocity_2_weeks = jiraProxy.count_of_bugs()
    tasks_velocity_3_weeks = jiraProxy.count_velocity_on_tasks(3, 4)
    bugs_velocity_3_weeks = jiraProxy.count_of_bugs(3, 4)
    tasks_velocity_4_weeks = jiraProxy.count_velocity_on_tasks(5, 6)
    bugs_velocity_4_weeks = jiraProxy.count_of_bugs(5, 6)
    tasks_velocity_5_weeks = jiraProxy.count_velocity_on_tasks(7, 8)
    bugs_velocity_5_weeks = jiraProxy.count_of_bugs(7, 8)
    tasks_velocity_6_weeks = jiraProxy.count_velocity_on_tasks(9, 10)
    bugs_velocity_6_weeks = jiraProxy.count_of_bugs(9, 10)
    tasks_velocity_7_weeks = jiraProxy.count_velocity_on_tasks(11, 12)
    bugs_velocity_7_weeks = jiraProxy.count_of_bugs(11, 12)
    tasks_velocity_8_weeks = jiraProxy.count_velocity_on_tasks(13, 14)
    bugs_velocity_8_weeks = jiraProxy.count_of_bugs(13, 14)
    print(tasks_velocity_2_weeks, bugs_velocity_2_weeks, tasks_velocity_3_weeks, bugs_velocity_3_weeks, tasks_velocity_4_weeks, bugs_velocity_4_weeks)


