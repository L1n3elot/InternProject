#!python3
from OnetWebService import OnetWebService
import sys

# importing module and functions for environment variables
import os
from dotenv import load_dotenv, dotenv_values 

# loading variables from .env file
load_dotenv() 
def get_api(prompt):
    result = ''
    while (len(result) == 0):
        result = input(prompt + ': ').strip()
    return result

def check_for_error(service_result):
    if 'error' in service_result:
        sys.exit(service_result['error'])

api_key = os.getenv("ONET_API_KEY")
onet_ws = OnetWebService(api_key)

vinfo = onet_ws.call('about')
check_for_error(vinfo)
print("Connected to O*NET Web Services version " + str(vinfo['api_version']))
print("")

kwquery = get_api('Enter a job title')
kwresults = onet_ws.call('online/search',
                         ('keyword', kwquery), ('end', 1))


check_for_error(kwresults)
if (not 'occupation' in kwresults) or (0 == len(kwresults['occupation'])):
    print("No relevant occupations were found.")
    print("")
else:
    print("Task list for \"" + kwquery + "\":")
    for occ in kwresults['occupation']:
    	jobs = onet_ws.call('online/occupations/' + occ['code'] + '/details/tasks', ('end', 40))
    	
    	dict_jobs = dict(jobs)
    	tasks = dict_jobs['task']
    	for t in tasks:
            print(t, '\n')
    print("There are", len(tasks), "tasks")
    
    print("")
