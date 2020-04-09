class JiraProxy(object):
    def __init__(self, jira, team, lead, component, project):
        self.jira = jira
        self.team = team
        self.lead = lead
        self.component = component
        self.project = project

    def issues_resolved(self, user, type_of_issue):
        return self.jira.search_issues(
            f'status changed by {user} AND resolutiondate >= startOfWeek(-14d) AND resolutiondate < endOfWeek(-7d) '
            f'and type in ({type_of_issue})')

    def create_issue(self, summary):
        issue_dict = {
            'project': self.project,
            'summary': summary,
            'description': summary,
            'issuetype': {'name': 'Defect'},
            'components': [{'name': self.component}],
            'assignee': {'name': self.lead},
            'customfield_10014': {'id': '10010'}
        }
        self.jira.create_issue(fields=issue_dict)

    def team_assign(self, count=2):
        for user in str(self.team).split(','):
            issues = self.jira.search_issues(
                f'assignee = {user} AND resolution = Unresolved and type in (Bug, Defect) and status in (Open)')
            if issues.total < count:
                lead_issues = self.jira.search_issues(
                    f'assignee = {self.lead} AND resolution = Unresolved and type in (Bug, Defect) and status in (Open) ORDER BY priority DESC')
                self.jira.assign_issue(lead_issues.next(), user)
                self.jira.assign_issue(lead_issues.next(), user)

    def time_logged(self):
        pass

    def count_velocity(self):
        # | time logged * (2 / count of tasks + 1 / bugs)
        # || original estimate / logged on ticket
        pass
