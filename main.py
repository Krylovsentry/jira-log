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
    config.set("Settings", "username", "your username")
    config.set("Settings", "password", "your password")

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
        config.get("Settings", "password")
    ]


if __name__ == "__main__":
    path = "settings.ini"
    [jira_server, project, user_name, password] = crud_config(path)

    jira_options = {'server': jira_server}
    jira = JIRA(options=jira_options, basic_auth=(user_name, password))

    print('Some')

    # jql = 'assignee = currentUser() AND resolution = Unresolved order by updated DESC'
    # issues_list = jira.search_issues(jql)
    # jira.add_worklog('', timeSpent='2h')
