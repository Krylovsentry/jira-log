import json

import matplotlib.pyplot as plt


class JiraProxy(object):
    def __init__(self, jira, team, lead, component, project, jira_server, path='data.json'):
        with open(path, 'r') as f:
            self.prev_data = json.load(f)

        self.jira = jira
        self.team = team
        self.lead = lead
        self.component = component
        self.project = project
        self.jira_server = jira_server
        self.median = self.prev_data['median'] if 'median' in self.prev_data else 0

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
        for user in self.team.split(','):
            issues = self.jira.search_issues(
                f'assignee = {user} AND resolution = Unresolved and type in (Bug, Defect) and status in (Open)')
            if issues.total < count:
                lead_issues = self.jira.search_issues(
                    f'assignee = {self.lead} AND resolution = Unresolved and type in (Bug, Defect) and status in (Open) ORDER BY priority DESC')
                self.jira.assign_issue(lead_issues.next(), user)
                self.jira.assign_issue(lead_issues.next(), user)

    def time_logged(self, user, type_of_issue, other_conditions_with_and=""):
        return self.jira.search_issues(
            f'worklogAuthor = {user} AND (worklogDate >= startOfWeek(-14d) AND worklogDate <= endOfWeek(-14d)) and type in ({type_of_issue}) {other_conditions_with_and}'
        )

    def count_velocity_on_tasks(self, start_week=1, end_week=2):
        velocities = {}
        for user in self.team:
            issues = self.jira.search_issues(
                f'worklogAuthor = {user} AND (worklogDate >= startOfWeek(-{end_week * 7}d) AND worklogDate <= endOfWeek(-{start_week * 7}d)) and type in ("Dev Task") and (labels != "time-track" or labels is EMPTY )')

            velocity_temp = []
            for issue in issues:
                work_logs_unestimated = 0
                work_logs = self.jira.worklogs(issue)
                for work_log in work_logs:
                    if work_log.author.key == user:
                        work_logs_unestimated += work_log.timeSpentSeconds
                if issue.fields and issue.fields.timeoriginalestimate:
                    velocity = issue.fields.timeoriginalestimate / work_logs_unestimated * 100
                    velocity_temp.append(200 if velocity > 300 else velocity)
                else:
                    print(f'{self.jira_server}/browse/{issue}')

            if len(velocity_temp):
                velocities[user] = sum(velocity_temp) / len(velocity_temp)
        return velocities

    def count_of_bugs(self, start_week=1, end_week=2):
        bugs_count = {}
        for user in self.team:
            issues = self.jira.search_issues(
                f'status changed by {user} AND resolutiondate >= startOfWeek(-{end_week * 7}d) AND resolutiondate < endOfWeek(-{start_week * 7}d)')
            bugs_count[user] = len(issues)

        self.median = (sum(bugs_count.values()) + self.median) / (len(bugs_count) + 1)
        for key in bugs_count.keys():
            bugs_count[key] = bugs_count[key] / self.median * 100
        return bugs_count

    def update_data(self, path):
        bugs = self.prev_data['bugs'] if 'bugs' in self.prev_data else []
        bugs.append(self.count_of_bugs())

        tasks = self.prev_data['tasks'] if 'tasks' in self.prev_data else []
        tasks.append(self.count_velocity_on_tasks())

        data = {'tasks': tasks, 'bugs': bugs, 'median': self.get_median()}
        with open('data.json', 'w') as outfile:
            json.dump(data, outfile)

    def load_data(self, path='data.json'):
        with open(path, 'r') as f:
            self.prev_data = json.load(f)

    def make_velocities(self):
        self.load_data()
        bugs = self.prev_data['bugs']
        tasks = self.prev_data['tasks']
        for user in self.team:
            bug_temp = []
            week = []
            for j in range(len(bugs)):
                bug_temp.append(bugs[j][user])
                week.append(j)
            plt.plot(week, bug_temp, label=str(user))
        plt.legend()
        plt.title('Bugs')
        plt.show()

        for user in self.team:
            tasks_temp = []
            week = []
            for j in range(len(tasks)):
                tasks_temp.append(tasks[j][user] if user in tasks[j].keys() else 0)
                week.append(j)
            plt.plot(week, tasks_temp, label=str(user))
        plt.legend()
        plt.title('Tasks')
        plt.show()

    def get_median(self):
        return self.median
