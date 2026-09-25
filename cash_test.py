import json
import string
from google import genai
import anthropic
import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values

load_dotenv() 

# Read the json file
with open("config.json", "r") as jsonfile:
    data = json.load(jsonfile)
    print("Read successful\n")
    
def format_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ','_') # I don't like spaces in filenames.
    return filename

def api_caller(filename):
    print("The file already exists. Here was the result:" + '\n')
    try:
        with open(filename, 'r') as file:
            json_data = json.load(file)
        json_data['number of times cached'] = json_data.get('number of times cached', 0) + 1
              
        json_str = json.dumps(json_data, indent=4)
              
        with open(filename, "w") as f:
            f.write(json_str)
                  
        print(json_data)
              
    except json.JSONDecodeError as e:
        print("Invalid JSON syntax:", e)


        
def call_gemini():
    # Calls the Gemini API
    client = genai.Client(api_key = os.getenv(data["environment_variable"]))
    task_description = input("Enter your task description: ")
    PROMPT_TEXT = ("In a structured JSON only response with no preamble and no code fences, give me the automation feasibility "
                       "and quality confidence score from 1-5, the retention reason code (capability/capacity/regulatory/accountability/judgment),"
                       "and a one-sentence justification regarding AI being able to replace a human for this task: ")
    PROMPT_VERSION = 'V1'
    
    file_name = f"{PROMPT_VERSION}_{data['model']}_{format_filename(task_description).lower()}.json"
    file_path = Path(file_name)
    
    if file_path.is_file():
        api_caller(file_name)
    elif task_description.strip():
        
        print("\nSending to Gemini...")
        interaction = client.interactions.create(
            model=data['model'],
            input= PROMPT_TEXT + task_description,
            generation_config={"temperature": 0
                }
            )
        print(interaction.output_text, '')
        print("Number of input tokens: ", interaction.usage.total_input_tokens, '')
        print("Number of output tokens: ", interaction.usage.total_output_tokens, '')
        print("Total number of tokens: ", interaction.usage.total_tokens, '')
        print("Creation date: ", interaction.created, '')
        print("temperature: ", interaction.generation_config, '')    
        try:
            output = json.loads(interaction.output_text)
             
            output['input tokens'] = interaction.usage.total_input_tokens
            output['output tokens'] = interaction.usage.total_output_tokens
            output['total tokens'] = interaction.usage.total_tokens
            output['date created'] = interaction.created
            output['source'] = 'live call'
            output['raw response'] = interaction.output_text
              
            json_str = json.dumps(output, indent=4)
            with open(file_name, "w") as f:
                f.write(json_str)
        except json.JSONDecodeError as e:
            print("Invalid JSON syntax:", e)
            
            
    else:
        print("Input cannot be empty.")
        
    
    



def call_anthropic():
    client = anthropic.Anthropic()
    task_description = input("Enter your task description: ")
    PROMPT_TEXT = ("In a structured JSON only response with no preamble and no code fences, give me the automation feasibility "
                       "and quality confidence score from 1-5, the retention reason code (capability/capacity/regulatory/accountability/judgment),"
                       "and a one-sentence justification regarding AI being able to replace a human for this task: ")
    PROMPT_VERSION = 'V1'
    
    file_name = f"{PROMPT_VERSION}_{data['model']}_{format_filename(task_description).lower()}.json"
    file_path = Path(file_name)
    
    if file_path.is_file():
        api_caller(file_name)
    elif task_description.strip():
         
        print("\nSending to Claude...")
        message = client.messages.create(
                 model=data['model'],
                 max_tokens=1024,
                 temperature=0,
                 messages=[{
                    "role": "user",
                    "content": (PROMPT_TEXT + task_description)
                  }]
            )
       
        for block in message.content:
            if block.type == "text":
                print(block.text)
        total_tokens = message.usage.input_tokens + message.usage.output_tokens
        print(f"Input Tokens Used: {message.usage.input_tokens}")
        print(f"Output Tokens Used: {message.usage.output_tokens}")
        print(f"Total Tokens:  {total_tokens}")
        print("temperature: ", message.temperature, '')
        try:
            output = json.loads(block.text)
                      
            output['input tokens'] = message.usage.input_tokens
            output['output tokens'] = message.usage.output_tokens
            output['total tokens'] = total_tokens
            output['date created'] = message.created_at
            output['source'] = 'live call'
            output['raw response'] = block.text
                        
            json_str = json.dumps(output, indent=4)
            with open(file_name, "w") as f:
                f.write(json_str)
        except json.JSONDecodeError as e:
            print("Invalid JSON syntax:", e)
    else:
        print("Input cannot be empty.")


if data['provider'].lower() == "gemini":
    call_gemini()
elif data['provider'].lower() == "claude" or data['provider'].lower() == "anthropic":
    call_anthropic()


