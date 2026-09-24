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

def call_gemini():
    # Calls the Gemini API
    client = genai.Client(api_key = os.getenv(data["environment_variable"]))
    user_prompt = input("Enter your task description: ")
    file_path = Path(f"{format_filename(user_prompt)}.json")
    if file_path.is_file():
            print("The file already exists. Here was the result:" + '\n')

            with open(f"{format_filename(user_prompt)}.json", 'r') as file:
                json_data = json.load(file)
            print(json_data)  
    else:
        if user_prompt.strip():
            print("\nSending to Gemini...")
            interaction = client.interactions.create(
                model=data['model'],
                input= ("In a structured JSON only response with no preamble and no code fences, give me the automation feasibility "
                       "and quality confidence score from 1-5, the retention reason code (capability/capacity/regulatory/accountability/judgment),"
                       "and a one-sentence justification regarding AI being able to replace a human for this task: " + user_prompt))
            print(interaction.output_text, '')
            print("Number of input tokens: ", interaction.usage.total_input_tokens, '')
            print("Number of output tokens: ", interaction.usage.total_output_tokens, '')
            print("Total number of tokens: ", interaction.usage.total_tokens, '')
            print("Creation date: ", interaction.created, '\n')
                
            
            output = json.loads(interaction.output_text)
            
            output['input tokens'] = interaction.usage.total_input_tokens
            output['output tokens'] = interaction.usage.total_output_tokens
            output['total tokens'] = interaction.usage.total_tokens
            output['date created'] = interaction.created
            
            json_str = json.dumps(output, indent=4)
            with open(f"{format_filename(user_prompt)}.json", "w") as f:
                f.write(json_str)
            
        else:
            print("Input cannot be empty.")
    



def call_anthropic():
    client = anthropic.Anthropic()

    message = client.messages.create(
      model=data['model'],
      max_tokens=1024,
      messages=[{
        "role": "user",
        "content": ("In a structured JSON only response with no preamble and no code fences, give me the automation feasibility "
               "and quality confidence score from 1-5, the retention reason code (capability/capacity/regulatory/accountability/judgment),"
               "and a one-sentence justification regarding AI being able to replace a human for this task: " + input("Enter your task description: "))
      }]
    )
    for block in message.content:
        if block.type == "text":
            print(block.text)
    myJSON = json.dumps(block.text)

    with open("output_anthropic.json", "w") as jsonfile:
        jsonfile.write(myJSON)
        print("Write successful")


if data['provider'].lower() == "gemini":
    call_gemini()
elif data['provider'].lower() == "claude" or data['provider'].lower() == "anthropic":
    call_anthropic()


