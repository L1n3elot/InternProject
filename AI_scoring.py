import json

# some JSON:
x =   ('{"task": "Read food order slips or receive verbal instructions as to food required by patron, and prepare and cook food according to instructions",'
        '"automation_feasibility_score": 2,'
        '"quality_confidence_score": 2,'
        '"retention_reason_code": "capability", '
        '"justification": "Current robotics and sensing lack the dexterity, adaptability, and multisensory judgment'
        '(texture, smell, visual doneness cues, real-time recipe adjustment) needed to reliably prepare varied dishes to order across unpredictable kitchen conditions."}')

# parse x:
y = json.loads(x)


import sqlite3
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('CREATE TABLE scores (task TEXT, automation_feasibility_score INTEGER, quality_confidence_score INTEGER, retention_reason_code TEXT, justification TEXT)')

cursor.execute("INSERT INTO scores  VALUES (?, ?, ?, ?, ?)",(y['task'], y['automation_feasibility_score'], y['quality_confidence_score'], y['retention_reason_code'], y['justification']))
conn.commit()

cursor.execute('SELECT * FROM scores')
result = cursor.fetchone()
print(f'task: {result[0]}\n\nautomation_feasibility_score: {result[1]}\n\nquality_confidence_score: {result[2]}\n\nretention_reason_code: {result[3]}\n\njustification: {result[4]}')

