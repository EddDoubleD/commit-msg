#!/usr/bin/python

import sys
import re
from jira import JIRA
import requests
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

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


JIRA_XMLRPC = 'https://job-jira.otr.ru'
JIRA_USER = 'YouLogIn'
JIRA_PASSWORD = 'YouPasswo'
JIRA_TICKET_PATTERN = re.compile(r'(\w+?-\d{5}?)')

class JiraException(Exception):
	pass

def check_message(message):
	tickets = JIRA_TICKET_PATTERN.findall(message)

	if not tickets:
		return NO_JIRA_TICKET_MESSAGE

	if len(tickets) > 1:
		return TOO_MANY_JIRA_TICKETS_MESSAGE    

	ticket = tickets[0]

	try:
		options = {'server': JIRA_XMLRPC, 'verify':False}
		jira = JIRA(options, basic_auth=(JIRA_USER, JIRA_PASSWORD))
		issue = jira.issue(ticket)
		# if issue is not None:	
		# 	if issue.fields.issuetype.id != 1 and issue.fields.issuetype.id != 10101:
		# 		return INVALID_ISSUE_TYPE_MESSAGE
	except:
		raise JiraException('Could not connect to the API, invalid username or password!') from None 			
			 
	return None	

def sam(message):
	tickets = JIRA_TICKET_PATTERN.findall(message)
	options = {'server': JIRA_XMLRPC, 'verify':False}
	jira = JIRA(options, basic_auth=(JIRA_USER, JIRA_PASSWORD))
	issue = jira.issue(tickets[0])
	print(issue)
	if issue is not None:
		if issue.fields.customfield_13900 is None:
			if issue.fields.customfield_10227 is not None:
				parent_issue = jira.issue(issue.fields.customfield_10227)
				if parent_issue.fields.customfield_10227 is None:
					samTask = parent_issue.fields.customfield_13400
				else:
					parent_issue = jira.issue(parent_issue.fields.customfield_10227)
					samTask = parent_issue.fields.customfield_13400	
			else:
				samTask = None
		else:
			parent_issue = jira.issue(issue.fields.customfield_13900) 
			samTask = parent_issue.fields.customfield_13400

	else:
		samTask = None
	return samTask

def main():
	if len(sys.argv) <= 1:
		print("Не заданы параметры")
	else:
		msg_file = open(sys.argv[1], 'r')
		msg = msg_file.read()
		err_msg = check_message(msg)
		if err_msg is None:
			samTask = sam(msg)	
			msg_file.close() 
			msg_file = open(sys.argv[1], 'a')
			if samTask is not None:
				msg_file.write(" /" + samTask)
			else:
				msg_file.write(" /SAM-NONE")		
			msg_file.close()
		else:
		 	print(err_msg)	

if __name__== "__main__" :
	main()
