import configparser
import json
import os

import matplotlib.pyplot as plt
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

    with open('data.json', 'r') as f:
        prev_data = json.load(f)

    # initialize jira api
    jira_options = {'server': jira_server}
    jiraProxy = JiraProxy(
        JIRA(options=jira_options, basic_auth=(user_name, password)),
        str(team).split(',') + str(brazil_team).split(','), user_name, component, project, jira_server,
        prev_data['median']
    )

    bugs = prev_data['bugs']
    bugs.append(jiraProxy.count_of_bugs())
    for user in str(team).split(',') + str(brazil_team).split(','):
        bug_temp = []
        week = []
        for j in range(len(bugs)):
            bug_temp.append(bugs[j][user])
            week.append(j)
        plt.plot(week, bug_temp, label=str(user))
    plt.legend()
    plt.title('Bugs')
    plt.show()

    tasks = prev_data['tasks']

    tasks.append(jiraProxy.count_velocity_on_tasks())
    for user in str(team).split(',') + str(brazil_team).split(','):
        tasks_temp = []
        week = []
        for j in range(len(bugs)):
            tasks_temp.append(tasks[j][user] if user in tasks[j].keys() else 0)
            week.append(j)
        plt.plot(week, tasks_temp, label=str(user))
    plt.legend()
    plt.title('Tasks')
    plt.show()

    data = {'tasks': tasks, 'bugs': bugs, 'median': jiraProxy.get_median()}
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)
