import configparser
import os

from argparse import ArgumentParser
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
    config.set("Settings", "component", "сomponent label")

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
        config.get("Settings", "component")
    ]


if __name__ == "__main__":
    path = "settings.ini"
    [jira_server, project, user_name, password, team, component] = crud_config(path)

    # initialize jira api
    jira_options = {'server': jira_server}
    jiraProxy = JiraProxy(
        JIRA(options=jira_options, basic_auth=(user_name, password)),
        str(team).split(','), user_name, component, project, jira_server
    )

    parser = ArgumentParser()
    parser.add_argument("-u", "--update",
                        help="update data from previous week",
                        default=False)
    parser.add_argument("-v", "--velocities",
                        default=None,
                        help="make velocities graphics for team or for every person")

    args = parser.parse_args()
    if args.update:
        jiraProxy.update_data()
    elif args.velocities is not None:
        jiraProxy.make_velocities(args.velocities)
