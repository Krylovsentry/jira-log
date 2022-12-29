import configparser
import os
import uvicorn
from fastapi import FastAPI
from jira import JIRA
from pydantic import BaseModel
from typing import Optional, List

from jirap import JiraProxy


class Ticket(BaseModel):
    summary: str
    description: Optional[str] = None
    externalKey: Optional[str] = None
    environment: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[List] = None


def create_config(path):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "jira_server", "jira server")
    config.set("Settings", "jira_server_external", "jira external server")
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
        config.get("Settings", "jira_server_external"),
        config.get("Settings", "project"),
        config.get("Settings", "user_name"),
        config.get("Settings", "password"),
        config.get("Settings", "team"),
        config.get("Settings", "components")
    ]


path = "settings.ini"
[jira_server, jira_server_external, project, user_name, password, team, components] = crud_config(path)
# initialize jira api
jira_options = {'server': jira_server}
jiraProxy = JiraProxy(
    JIRA(options=jira_options, basic_auth=(user_name, password)),
    str(team).split(','), user_name, str(components).split(','), project, jira_server
)

jira_options = {'server': jira_server_external}

jiraExternalProxy = JiraProxy(
    JIRA(options=jira_options, basic_auth=(user_name, password)),
    str(team).split(','), user_name, str(components).split(','), project, jira_server
)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/tickets/external/{ticket_number}", tags=["PSUP JIRA"])
async def get_ticket_external(ticket_number: str):
    ticket = jiraExternalProxy.get_ticket(ticket_number)
    return {
        'externalKey': ticket.key,
        'description': ticket.fields.description + ' ' + ticket.fields.customfield_21220,
        'summary': ticket.fields.summary,
        'environment': ticket.fields.environment,
        'priority': ticket.fields.priority.name,
        'labels': ticket.fields.labels
    }

@app.get("/tickets/external/{ticket_number}/clone", tags=["PSUP JIRA"])
async def clone_ticket_external(ticket_number: str):
    ticket = jiraExternalProxy.get_ticket(ticket_number)
    createdIssue = jiraProxy.create_issue('[' + ticket.key + ']' + ticket.fields.summary, ticket.fields.description + ' ' + ticket.fields.customfield_21220,
                                          priority=ticket.fields.priority.name,
                                          environment=ticket.fields.environment or '', labels=ticket.fields.labels)
    return createdIssue.key



@app.get("/tickets/{ticket_number}")
async def get_ticket(ticket_number: str):
    return {
        "ticket": jiraProxy.get_ticket(ticket_number)
    }


@app.post("/tickets/")
async def create_ticket(ticket: Ticket):
    createdIssue = jiraProxy.create_issue('[' + ticket.externalKey + ']' + ticket.summary, ticket.description,
                                          priority=ticket.priority,
                                          environment=ticket.environment or '', labels=ticket.labels)
    return createdIssue.key


@app.post("/tickets/{ticket_number}/link")
async def link_tickets(ticket_number: str, ticket_numbers):
    for el in ticket_numbers.split(','):
        jiraProxy.create_issue_link_impl(ticket_number, el)\

@app.post("/tickets/rft")
async def tickets_to_rft(ticket_numbers):
    for ticket_number in ticket_numbers.split(','):
        jiraProxy.issue_to_rft(ticket_number)

@app.post("/tickets/close")
async def tickets_to_close(ticket_numbers):
    for ticket_number in ticket_numbers.split(','):
        jiraProxy.issue_to_close(ticket_number)



@app.get("/tickets/")
async def get_tickets(searchQuery: str = ''):
    tickets = jiraProxy.search_issues(searchQuery)
    return {"tickets": ','.join([x.key for x in tickets])}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)