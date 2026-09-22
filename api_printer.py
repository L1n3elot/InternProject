from dotenv import load_dotenv
import os

load_dotenv()

onet_key= os.getenv("ONET_API_KEY")
gemini_key= os.getenv("GEMINI_API_KEY")

print("ONET_API_KEY: ", onet_key)
print("GEMINI_API_KEY: ", gemini_key)
