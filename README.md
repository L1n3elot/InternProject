# InternProject
Steps to begin running any project phase:
1. Open the command prompt and paste myfirstproject\Scripts\activate to activate the virtual environment.
2. If needed, type cd and the path to where the files are located.

# How to run the project
1. Paste the API key next to GEMINI_API_KEY in env. file
1. Execute the AI Scoring layer by pasting in python AI_scoring.py
2. It will prompt you to enter a job title and again after that
3. After entering the job titles, you will see a task based on the job title, the AI response, and the number of tokens used
4. Enter whether or not you would like to override the scores and reason codes. If yes, it will prompt you to enter each change. If no, it will return None and will save the results
6. The same prompt will continue to appear until the loop finishes
