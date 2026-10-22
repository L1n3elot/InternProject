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


def get_tasks(kwquery1):
    api_key = os.getenv("ONET_API_KEY")
    onet_ws = OnetWebService(api_key)

    vinfo = onet_ws.call('about')
    check_for_error(vinfo)
    print("Connected to O*NET Web Services version " + str(vinfo['api_version']))
    print("")

    
    kwresults1 = onet_ws.call('online/search',
                             ('keyword', kwquery1), ('end', 1))


    check_for_error(kwresults1)
    if ((not 'occupation' in kwresults1) or (0 == len(kwresults1['occupation']))):
        print("No relevant occupations were found.")
        print("")
    else:
        print("Task list for \"" + kwquery1 + "\":")
        for occ in kwresults1['occupation']:
            jobs = onet_ws.call('online/occupations/' + occ['code'] + '/details/tasks', ('end', 40))
            
            dict_jobs = dict(jobs)
            tasks1 = dict_jobs['task']
        
        print("")
    return tasks1
