#!python3
from OnetWebService import OnetWebService
import sys
import json
import os
# importing necessary functions from dotenv library

from dotenv import load_dotenv, dotenv_values 

# loading variables from .env file
load_dotenv() 

# read JSON input
input = json.load(sys.stdin)

# initialize Web Services and results objects
onet_ws = OnetWebService(os.getenv("ONET_API_KEY"))
max_results = max(1, input['config']['max_results'])
output = { 'output': [] }

# call keyword search for each input query
for q in input['queries']:
    res = []
    kwresults = onet_ws.call('online/search',
                             ('keyword', q),
                             ('end', max_results))
    if ('occupation' in kwresults) and (0 < len(kwresults['occupation'])):
        for occ in kwresults['occupation']:
            res.append({ 'code': occ['code'], 'title': occ['title'] })
    output['output'].append({ 'query': q, 'results': res })

json.dump(output, sys.stdout, indent=2, sort_keys=True)
