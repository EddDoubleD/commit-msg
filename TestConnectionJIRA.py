import sys
import re
import codecs
from jira import JIRA
import requests
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

#Error message constant
NO_JIRA_TICKET_MESSAGE = \
'No Jira ticket present in the commit message. \
Please include the Jira ticket enclosed in brackets: [EXP-99999].'
INVALID_JIRA_TICKET_MESSAGE = \
'Proper Jira ticket syntax was found, but none were valid tickets. \
Please check the tickets and try again.'
TOO_MANY_JIRA_TICKETS_MESSAGE = \
'Only 1 Jira ticket is allowed per commit. Please commit only 1 change at a time.'
INVALID_ISSUE_TYPE_MESSAGE = \
'You may not commit against subtasks or task-splits. \
Please commit against the parent ticket.'
TASK_NOT_FOUND = \
'Task not found'
FIND_HELPER = 'FIND'

#Authentication constant
JIRA_URL = 'https://job-jira.otr.ru'
JIRA_USER = 'sulimov.dmitriy'
JIRA_PASSWORD = 'Gerbert94?'
#Jira pattern ticket
JIRA_TICKET_PATTERN = re.compile(r'(\w+?-{1,10}\d+)')
FIND_TICKET_PATTERN = re.compile(r'(SAM+?-{1.10}\d+)')

#Jira Exception class 
class JiraException(Exception):
	pass

def validMessage(msg, param):
	tickets = JIRA_TICKET_PATTERN.findall(msg)

	if not tickets:
		return NO_JIRA_TICKET_MESSAGE

	if len(tickets) > 1:
		return TOO_MANY_JIRA_TICKETS_MESSAGE

	if param == FIND_HELPER:
		return tickets[0]
	else:
		return None	

def getJiraSamTicket(msg):
	tickets = JIRA_TICKET_PATTERN.findall(msg)
	ticket = tickets[0]
	try:
		options = {'server': JIRA_URL, 'verify':False}
		jira = JIRA(options, basic_auth=(JIRA_USER, JIRA_PASSWORD))
	except:
		raise JiraException('Could not connect to the API, invalid username or password!') from None	
	try:
		issue = jira.issue(ticket)
	except:
		return TASK_NOT_FOUND		

	#Check subtask
	if issue.fields.issuetype.id == '5' or issue.fields.issuetype.id == '8':
		return INVALID_ISSUE_TYPE_MESSAGE
	
	#Link to refinement source
	return issue.fields.customfield_10227
	
#Test regular
def main():
	s = 'SAM-64104'
	errMsg = validMessage(s, None)
	if errMsg:
		print(errMsg)
		sys.exit(1)

	jira_ticket = validMessage(s, FIND_HELPER);	

	if jira_ticket == INVALID_ISSUE_TYPE_MESSAGE:
		print(INVALID_ISSUE_TYPE_MESSAGE)
		sys.exit(1)

	if getJiraSamTicket(jira_ticket) == TASK_NOT_FOUND:
		print('Task [' + jira_ticket + '] not found')
		sys.exit(1)

if __name__ == '__main__':
		main()	
