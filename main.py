from jira import JIRA

jira_options = {'server': 'https://tms.netcracker.com/'}
jira = JIRA(options=jira_options, basic_auth=('', ''))

jql = 'assignee = currentUser() AND resolution = Unresolved order by updated DESC'
issues_list = jira.search_issues(jql)
jira.add_worklog('', timeSpent='2h')
