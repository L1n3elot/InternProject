import json
from google import genai
import anthropic
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv() 

# Read the json file
with open("config.json", "r") as jsonfile:
    data = json.load(jsonfile)
    print("Read successful\n")

def call_gemini():
    # Calls the Gemini API
    client = genai.Client(api_key = os.getenv(data["environment_variable"]))
    interaction = client.interactions.create(
        model=data['model'],
        input= ("In a structured JSON only response with no preamble and no code fences, give me the automation feasibility "
               "and quality confidence score from 1-5, the retention reason code (capability/capacity/regulatory/accountability/judgment),"
               "and a one-sentence justification regarding AI being able to replace a human for this task: " + input("Enter your task description: ")))
    print(interaction.output_text)
    print("Number of input tokens: ", interaction.usage.total_input_tokens, '')
    print("Number of output tokens: ", interaction.usage.total_output_tokens, '')
    print("Total number of tokens: ", interaction.usage.total_tokens, '')
    print("id: ", interaction.id, '\n')
        
    
    output = json.loads(interaction.output_text)
    
    output['input tokens'] = interaction.usage.total_input_tokens
    output['output tokens'] = interaction.usage.total_output_tokens
    output['total tokens'] = interaction.usage.total_tokens
    
    json_str = json.dumps(output, indent=4)
    with open(f"{interaction.id}.json", "w") as f:
        f.write(json_str)

    



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


