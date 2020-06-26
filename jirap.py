import json
import math
import os

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
        self.dev_weight = self.prev_data['dev_weight'] if 'dev_weight' in self.prev_data else 1

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

    def load_data(self, path='data.json'):
        with open(path, 'r') as f:
            self.prev_data = json.load(f)

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

    def count_velocity_on_tasks(self, week=1):
        velocities = {}
        for user in self.team:
            issues = self.jira.search_issues(
                f'worklogAuthor = {user} AND (worklogDate >= startOfWeek(-{week * 7}d) AND worklogDate <= endOfWeek(-{week * 7}d)) and type in ("Dev Task") and (labels != "time-track" or labels is EMPTY )')

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

    def count_of_bugs(self, week=1):
        bugs_count = {}
        for user in self.team:
            issues = self.jira.search_issues(
                f'status changed by {user} AND resolutiondate >= startOfWeek(-{week * 7}d) AND resolutiondate < endOfWeek(-{week * 7}d)')
            if len(issues):
                bugs_count[user] = len(issues)

        self.median = ((sum(bugs_count.values()) / (len(bugs_count))) + self.median) / 2
        for key in bugs_count.keys():
            bugs_count[key] = bugs_count[key] / self.median * 100
        return bugs_count

    def check_un_estimate_tasks(self, week=1):
        for user in self.team:
            issues = self.jira.search_issues(
                f'worklogAuthor = {user} AND (worklogDate >= startOfWeek(-{week * 7}d) AND worklogDate <= endOfWeek(-{week * 7}d)) and type in ("Dev Task") and (labels != "time-track" or labels is EMPTY )')
            for issue in issues:
                if not (issue.fields and issue.fields.timeoriginalestimate):
                    print(f'{self.jira_server}/browse/{issue}')

    def count_of_tickets_created(self, label, week=1, ticket_type='Defect'):
        issues = self.jira.search_issues(
            f'type in ({ticket_type}) AND component in ("CPQ UI", UX, "Admin UI") AND labels in ({label}) AND (created >= startOfWeek(-{week}) and created <=endOfWeek(-{week}))')
        return len(issues)

    def update_data(self, path='data.json'):
        self.load_data()
        bugs = self.prev_data['bugs'] if 'bugs' in self.prev_data else []
        bugs.append(self.count_of_bugs())

        tasks = self.prev_data['tasks'] if 'tasks' in self.prev_data else []
        tasks.append(self.count_velocity_on_tasks())

        data = {'tasks': tasks, 'bugs': bugs, 'median': self.get_median()}
        with open(path, 'w') as outfile:
            json.dump(data, outfile)

    def make_velocities(self, team=True):
        self.load_data()
        bugs = self.prev_data['bugs']
        tasks = self.prev_data['tasks']
        fig = plt.figure()
        fig.set_figwidth(len(bugs) / 2)
        for user in self.team:
            bug_temp = []
            week = []
            for j in range(len(bugs)):
                bug_temp.append(bugs[j][user] if user in bugs[j] else None)
                week.append(j)
            for_mark = []
            filtered_bugs = list(filter(lambda x: x is not None, bug_temp))
            if len(filtered_bugs):
                bug_temp.append(self.forecast(filtered_bugs))
                for_mark = [len(week), len(week) - 1]
                week.append(len(week))

            plt.plot(week, bug_temp, '-D', label=str(user), markevery=for_mark)
            plt.xticks(week)
            if not team:
                plt.title(f'Bugs for {user}')
                if 'dev' not in os.listdir(os.getcwd()):
                    os.makedirs('dev')
                plt.savefig(f'dev/{user}-bugs.png')
                plt.show()
        if team:
            plt.legend()
            plt.title('Bugs')
            if 'team' not in os.listdir(os.getcwd()):
                os.makedirs('team')
            plt.savefig(f'team/team-bugs.png')
            plt.show()

        fig = plt.figure()
        fig.set_figwidth(len(tasks) / 2)
        for user in self.team:
            tasks_temp = []
            week = []
            for j in range(len(tasks)):
                current = tasks[j][user] if user in tasks[j].keys() else None
                tasks_temp.append(current)
                week.append(j)
            for_mark = []
            filtered_tasks = list(filter(lambda x: x is not None, tasks_temp))
            if len(filtered_tasks):
                tasks_temp.append(self.forecast(filtered_tasks))
                for_mark = [len(week), len(week) - 1]
                week.append(len(week))

            plt.plot(week, tasks_temp, '-D', label=str(user), markevery=for_mark)
            plt.xticks(week)
            if not team:
                self.dev_weight = (self.dev_weight + sum(filtered_tasks) / 100) / (len(filtered_tasks) + 1)
                plt.title(f'Tasks for {user}')
                if 'dev' not in os.listdir(os.getcwd()):
                    os.makedirs('dev')
                plt.savefig(f'dev/{user}-tasks.png')
                plt.show()
        if team:
            plt.legend()
            plt.title('Tasks')
            if 'team' not in os.listdir(os.getcwd()):
                os.makedirs('team')
            plt.savefig(f'team/team-tasks.png')
            plt.show()

    def get_median(self):
        return self.median

    def get_dev_weight(self):
        return self.dev_weight

    def get_time_for(self, label, ticket_type="Defect", weeks=4):
        time_spent = 0
        for user in self.team:
            issues = self.jira.search_issues(
                f'worklogAuthor = {user} AND (worklogDate >= startOfWeek({-7 * weeks}d) AND worklogDate <= endOfWeek({-7 * weeks}d)) and type in ({ticket_type}) and (labels = {label})')
            for issue in issues:
                work_logs = self.jira.worklogs(issue)
                for work_log in work_logs:
                    if work_log.author.key == user:
                        time_spent += work_log.timeSpentSeconds

        return time_spent / (weeks * 3600)

    def get_medium_time_for_bugs(self, label, weeks=1):
        temp = []
        for i in range(weeks):
            temp.append(self.get_time_for(label, weeks=i + 1))
        return sum(temp) / (weeks * self.get_median())

    def get_medium_count_of_tickets_create(self, label, weeks=1):
        temp = []
        for i in range(weeks):
            temp.append(self.count_of_tickets_created(label, week=i + 1))
        return sum(temp) / weeks

    def get_time_for_tasks_for_user(self, label, user, ticket_type="Defect", weeks=1):
        time_spent = 0
        issues = self.jira.search_issues(
            f'worklogAuthor = {user} AND (worklogDate >= startOfWeek({-7 * weeks}d) AND worklogDate <= endOfWeek({-7 * weeks}d)) and type in ({ticket_type}) and (labels = {label})')
        for issue in issues:
            work_logs = self.jira.worklogs(issue)
            for work_log in work_logs:
                if work_log.author.key == user:
                    time_spent += work_log.timeSpentSeconds

        return time_spent / weeks

    def forecast(self, values):
        mean = sum(values) / len(values)
        return math.sqrt(sum(map(lambda x: (x - mean) ** 2, values)) / len(values))
