from google import genai
from pydantic import BaseModel, Field
from typing import Literal
import json
import sqlite3
import string
import time
import hashlib
import task_search
import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values


load_dotenv() 

# Read the json file
with open("config.json", "r") as jsonfile:
    data = json.load(jsonfile)
    print("Read successful\n")
   
def format_filename(a, b, c):
    filename = '*'.join([a, b, c])
    hash_object = hashlib.sha256(filename.encode('utf-8'))  
    hex_dig = hash_object.hexdigest()

    return hex_dig

def file_cache(filename):
    print("The file already exists. Here was the result:" + '\n')
    try:
        with open(filename, 'r') as file:
            json_data = json.load(file)
        
        json_data["metadata"]["cache hits"] = json_data["metadata"].get("cache hits", 0) + 1
        
              
        with open(filename, "w") as f:
            json.dump(json_data, f, indent=4)
                  
        print('Task text: ', json_data['task text'])
        print('\nresponse: ', json_data['raw response'])
        print('date created: ', json_data['date created'])
        print('prompt version: ', json_data['prompt version'])
        print('Task text: ', json_data['task text'])
        
        return json_data 
    except json.JSONDecodeError as e:
        print("Invalid JSON syntax:", e)

class Results(BaseModel):
    automation_feasibility_score: int = Field(ge=1, le=5, description="automation feasibility score from 1-5")
    quality_confidence_score: int = Field(ge=1, le=5, description="quality confidence score from 1-5")
    retention_reason_code: Literal["capability",  "capacity",  "regulatory",  "accountability", "judgment", "not_retained"] = Field(description="the retention reason code, but if automation feasibility is 5, return not_retained")
    justification: str = Field(description="a one-sentence justification, under 40 words")


def score_task(task_text):
    # Calls the Gemini API
    client = genai.Client(api_key = os.getenv(data["environment_variable"]))
    prompt_version = "v1.3b"
    PROMPT_TEXT = """
You score occupational task statements for whether AI and robotics could replace the human performing them. Return only JSON matching the required schema.

AUTOMATION FEASIBILITY (1-5): how much of this task current, commercially available technology could perform without a human.
This is about coverage - how much of the task. Judge what is deployable today, not what is demonstrable in a lab.
1 = No current technology performs any meaningful part of it.
2 = A narrow slice can be automated under controlled conditions; the task as a whole still requires a human.
3 = A substantial portion can be automated, but a human must remain in the loop for the rest.
4 = Most of the task can be performed by deployed technology, with a human reviewing or handling exceptions.
5 = The complete task is performed by deployed technology with no human involvement in the ordinary case.
Score the task as written, not the occupation. Where the honest answer sits between two points, choose the lower.

QUALITY CONFIDENCE (1-5): if the automatable portion were performed by current technology, how close would the output come
to the standard a competent human meets? This is about standard - how good the result - not about how much is automatable.
1 = Well below standard. Output would need substantial human rework to be usable at all.
2 = Below standard. Usable for low-stakes instances only; errors frequent enough to require routine human checking.
3 = Comparable on routine cases, degrading noticeably on unusual or complex instances.
4 = Comparable to a competent human across the normal range of the task; failures rare and mostly detectable.
5 = At or above the human standard, edge cases included.
If feasibility is 1, quality is also 1 - there is no output to assess. Otherwise the two scales are independent.

RETENTION REASON CODE: why a human is retained. Exactly one.

If a human is retained because the law, licensure, certification, or binding standard requires a human to perform or sign off on, or any
licensed individual must be legally answerable for the outcome, skip the TIEBREAK and choose regulatory.

Start with this question: if the technology were good enough tomorrow, would a human still perform this task?

If NO - the human is there only because the machine cannot do the job - the code is capability.

If YES - something other than technical ability keeps the human in place - code that reason, using this order:
   regulatory = law, licensure or binding standard requires a human, irrespective of technical ability.
   accountability = someone must be answerable for the outcome; the machine could do it, a human must own it.
   judgment = the task requires weighing competing values or ambiguous context the organization has chosen not to delegate.
   capacity = the equipment or capital to deploy the technology at the needed scale does not exist or is not economic.

If the AUTOMATION FEASIBILITY score comes back a 5, meaning this task is completely automatable without any human involvement, always return the RETENTION REASON CODE
as the sentinel value, not_retained no matter what. If the reason code is not_retained, the AUTOMATION FEASIBILITY score must always come back a 5.

If the task is clear and non ambiguous as to deciding if it requires human accountability or judgement, then there is no need to trigger the TIEBREAK, so skip it.

TIEBREAK: accountability and judgment often both seem to apply. accountability = a human must answer for the outcome; the machine could make the call. judgment =
a human must make the call itself; the organization has reserved the decision. When both apply, choose accountability.

Do not default to capability because some part of the task is currently hard. Capability is for tasks where technical ability is the only thing keeping a human in the job.

JUSTIFICATION: one sentence, under 40 words, naming the specific constraint that drove the reason code. Do not restate the task.

EXAMPLES

Task: Read food order slips or receive verbal instructions as to food required by patron, and prepare and cook food according to instructions.
{"automation_feasibility_score": 2, "quality_confidence_score": 2, "retention_reason_code": "capability", "justification": "Order intake is automatable,
but preparation requires physical dexterity and sensory judgment that deployed systems cannot reliably provide across varied dishes."}

Task: Verify the accuracy of patient records and sign the completed chart.
{"automation_feasibility_score": 4, "quality_confidence_score": 4, "retention_reason_code": "regulatory", "justification": "Record
verification is technically automatable, but licensure rules require a credentialed clinician to attest to the chart."}

Task: Prepare or deliver reports or presentations of geospatial project information.
{"automation_feasibility_score": 4, "quality_confidence_score": 4, "retention_reason_code": "accountability", "justification": "Generative tools draft
geospatial reports efficiently, but a human must ultimately answer for the accuracy and strategic implications of the presentation."}

Task: Perform general office duties, such as filing, answering telephones, and handling routine correspondence.
{ "automation_feasibility_score": 4, "quality_confidence_score": 4, "retention_reason_code": "capacity", "justification": "Digital tools automate routine filing and correspondence,
but arranging full-scale administrative automation across fragmented legacy systems remains economically constrained." }

Task: Diagnose malfunctioning systems, apparatus, or components, using test equipment and hand tools to locate the cause of a breakdown and correct the problem.
{"automation_feasibility_score": 3, "quality_confidence_score": 3, "retention_reason_code": "judgment", "justification": "Diagnostic tools isolate known faults,
but evaluating ambiguous failure modes and choosing among competing repair strategies requires active decision-making during task execution."}
"""
    str_task = str(task_text)

    file_name = f"{format_filename(PROMPT_TEXT, data['model'], str_task)}.json"
    file_path = Path(file_name)
    
    if file_path.is_file():
        return file_cache(file_name)
    elif str_task.strip():
        
        print("\nSending to Gemini...")

        gen_config = {"temperature": 0}
        interaction = client.interactions.create(
            model=data['model'],
            input=PROMPT_TEXT + str_task,
            response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": Results.model_json_schema()
           },
            generation_config=gen_config
        )
        
        results_output = Results.model_validate_json(interaction.output_text)
        
        try:
            print('Task: ', task_text, '\n')
            print(results_output, '')
            print("Number of input tokens: ", interaction.usage.total_input_tokens, '')
            print("Number of output tokens: ", interaction.usage.total_output_tokens, '')
            print("Total number of tokens: ", interaction.usage.total_tokens, '')
            print("Creation date: ", interaction.created, '')
            print("temperature: ", gen_config['temperature'], '')
            
            output = json.loads(interaction.output_text)

            record = {}

            metadata = {"prompt text": PROMPT_TEXT,
                        "task text": str_task,
                        "model name": data['model'],
                        "raw response": interaction.output_text,
                        "input tokens": interaction.usage.total_input_tokens,
                        "output tokens": interaction.usage.total_output_tokens,
                        "total tokens": interaction.usage.total_tokens,
                        "date created": interaction.created,
                        "source": 'live call',
                        "parsed_ok": True,
                        "prompt version": prompt_version
                        }

            record['scores'] = output

            not_retained_invalid = record['scores']['retention_reason_code'] == 'not_retained' and not record['scores']['automation_feasibility_score'] == 5
            automation_feasibility_invalid = record['scores']['retention_reason_code'] != 'not_retained' and record['scores']['automation_feasibility_score'] == 5
            
  
            record['metadata'] = metadata
            if not_retained_invalid or automation_feasibility_invalid:
                record['metadata']['reason code/feasibility_score consistent?'] = False
            else:
                record['metadata']['reason code/feasibility_score consistent?'] = True

            json_str = json.dumps(record, indent=4)

            with open(file_name, "w") as f:
                f.write(json_str)
         
            return record
        except json.decoder.JSONDecodeError as e:
            record = {}
                
            metadata = {
                        "error message": str(e),
                        "prompt text": PROMPT_TEXT,
                        "task text": str_task,
                        "model name": data['model'],
                        "raw response": interaction.output_text,
                        "input tokens": interaction.usage.total_input_tokens,
                        "output tokens": interaction.usage.total_output_tokens,
                        "total tokens": interaction.usage.total_tokens,
                        "date created": interaction.created,
                        "source": 'live call',
                        "parsed_ok": False,
                        "prompt version": prompt_version
                        }
            record['scores'] = interaction.output_text
            record['metadata'] = metadata

            json_str = json.dumps(record, indent=4)
            with open(file_name, "w") as f:
                f.write(json_str)
            print("Invalid JSON syntax:", e)
       
            return record
    else:
        print("Input cannot be empty.")






def load_db(tasks, res, db_name, job_name):
    
    file = 'task_list1.json'
    
    with open(file, "w") as f:
        json.dump([tasks], f, indent=4)
        
    print('Reading from file:\n')
    with open(file, "r") as jsonfile:
        data1 = json.load(jsonfile)[0]
        print("Read successful\n")
        

    
    with sqlite3.connect(db_name) as conn:

        cursor = conn.cursor()

        CREATE_TABLE = '''
CREATE TABLE IF NOT EXISTS records (task_id INT PRIMARY KEY, job_title TEXT, 
task_text TEXT, automation_feasibility_score INT, quality_confidence_score INT, retention_reason_code TEXT,
justification TEXT, model_name TEXT, run_date TEXT, input_tokens INT, output_tokens INT, prompt_version TEXT, importance_score INT, override_feasibility INT, override_confidence INT, override_reason TEXT, override_by TEXT,
UNIQUE(task_id, prompt_version, model_name))
'''

        cursor.execute(CREATE_TABLE)

        json_get = []

        
        # Loop through the records and tasks
        user_input = input('Override scores and reasons? (Y for yes, N for no, 0 to stop) ')

        if user_input.strip() == '0' or user_input.strip().lower() == 'o':
            return 'STOP'
        
        if user_input.upper() == 'Y' or user_input.upper() == 'YES':
            override_feas = input('Enter feasibility score correction (or Enter to skip) ')
            override_conf = input('Enter quality confidence score correction (or Enter to skip) ')
            override_reas = input('Enter retention reason code correction (or Enter to skip) ')
            overrider = input('Enter the name of the overrider (or Enter to skip) ')

            override_feasibility = int(override_feas) if override_feas.strip() else None
            override_confidence = int(override_conf) if override_conf.strip() else None
            override_reason = override_reas if override_reas.strip() else None
            override_by = overrider if overrider.strip() else None

            sql_row = (data1.get("id"), job_name, data1.get("title"), res['scores']['automation_feasibility_score'], res['scores']['quality_confidence_score'],
                                                                res['scores']['retention_reason_code'], res['scores']['justification'], res['metadata']['model name'],
                                                                        res['metadata']['date created'], data1.get('importance'), res['metadata']['input tokens'], res['metadata']['output tokens'], res['metadata']['prompt version'],
                                                                        override_feasibility, override_confidence, override_reason, override_by)
        else:

            sql_row = (data1.get("id"), job_name, data1.get("title"), res['scores']['automation_feasibility_score'], res['scores']['quality_confidence_score'],
                                                                res['scores']['retention_reason_code'], res['scores']['justification'], res['metadata']['model name'],
                                                                        res['metadata']['date created'], data1.get('importance'), res['metadata']['input tokens'], res['metadata']['output tokens'], res['metadata']['prompt version'],
                                                                        None, None, None, None)
                
        json_get.append(sql_row)
        cursor.executemany('''INSERT OR REPLACE INTO records (task_id, job_title, task_text, automation_feasibility_score, quality_confidence_score, retention_reason_code,
                            justification, model_name, run_date, importance_score, input_tokens, output_tokens, prompt_version, override_feasibility, override_confidence, override_reason, override_by)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', json_get)

        conn.commit()

        cursor.execute('SELECT * FROM records')
        result = cursor.fetchone()
         
    print("Saving task")
    
    

    conn.close()
    return result






def call_gemini_retry(task_id, task_text, max_retries=3, delay=5):
    for attempt in range(max_retries):
        try:
            result = score_task(task_text)
            return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for task ID {task_id}: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"All {max_retries} attempts failed for task ID {task_id}.")
                return None
            
    
def override_existing_rows(db_name):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM records')
        rows = cursor.fetchall()

        if not rows:
            print("No existing rows found in the database.")
            return

        for row in rows:
            task_id, job_title, task_text, automation_feasibility_score, quality_confidence_score, retention_reason_code, justification, model_name, run_date, input_tokens, output_tokens, prompt_version, importance_score, override_feasibility, override_confidence, override_reason, override_by = row
            
            print(f"\nTask ID: {task_id}")
            print(f"Job Title: {job_title}")
            print(f"Task Text: {task_text}")
            print(f"Automation Feasibility Score: {automation_feasibility_score}")
            print(f"Quality Confidence Score: {quality_confidence_score}")
            print(f"Retention Reason Code: {retention_reason_code}")
            print(f"Justification: {justification}")
            print(f"Model Name: {model_name}")
            print(f"Run Date: {run_date}")
            print(f"Input Tokens: {input_tokens}")
            print(f"Output Tokens: {output_tokens}")
            print(f"Prompt Version: {prompt_version}")
            print(f"Importance Score: {importance_score}")
            print(f"Override Feasibility: {override_feasibility}")
            print(f"Override Confidence: {override_confidence}")
            print(f"Override Reason: {override_reason}")
            print(f"Override By: {override_by}")

                  
                
            user_input = input('\nOverride scores and reasons? (Y for yes, N for no, 0 to stop) ')

            if user_input.strip() == '0' or user_input.strip().lower() == 'o':
                return 'STOP'

            if user_input.upper() == 'Y' or user_input.upper() == 'YES':
                override_feas = input('Enter feasibility score correction (or Enter to skip) ')
                override_conf = input('Enter quality confidence score correction (or Enter to skip) ')
                override_reas = input('Enter retention reason code correction (or Enter to skip) ')
                overrider = input('Enter the name of the overrider (or Enter to skip) ')

                override_feasibility = int(override_feas) if override_feas.strip() else None
                override_confidence = int(override_conf) if override_conf.strip() else None
                override_reason = override_reas if override_reas.strip() else None
                override_by = overrider if overrider.strip() else None

                cursor.execute('''UPDATE records SET 
                                  override_feasibility = ?, 
                                  override_confidence = ?, 
                                  override_reason = ?, 
                                  override_by = ? 
                                  WHERE task_id = ? AND prompt_version = ? AND model_name = ?''',
                               (override_feasibility, override_confidence, override_reason, override_by, task_id, prompt_version, model_name))
                
                conn.commit()
                print(f"Updated overrides for Task ID {task_id}.")
            else:
                print(f"No changes made for Task ID {task_id}.")

    conn.close()
    print("Finished processing overrides.")
    


def main():

    try:
        user_input = input('Are you adding tasks or overriding existing tasks? (A for adding, O for overriding) ')

        if user_input.upper() == 'O' or user_input.upper() == 'OVERRIDE':
            sql_filename = f"results.sqlite"
            stop_signal = override_existing_rows(sql_filename)
            if stop_signal == 'STOP':
                print('The program has stopped')
                return
        else:
            job1 = task_search.get_api('Enter a job title')
            
            # task list for the job title
            model_task1 = task_search.get_tasks(job1)

            job2 = task_search.get_api('Enter another job title')
            
            # task list for the other job title
            model_task2 = task_search.get_tasks(job2)

            
            # saves the tasks, scores and reasons to file

            sql_filename = f"results.sqlite"
            
            for task_list, job_name in [(model_task1, job1), (model_task2, job2)]:
                for task in task_list:
                    result = call_gemini_retry(task.get("id"), task.get("title"))
                    if result is not None:
                        stop_signal = load_db(task, result, sql_filename, job_name)
                        if stop_signal == 'STOP':
                            print('The program has stopped')
                            return
                    else:
                        print(f"Failed to score task ID {task.get('id')}. Skipping.")
    except Exception as e:
        print('An Error occured: ' + e)
        
            
if __name__ == "__main__":
    main()

































    


