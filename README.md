# InternProject
Steps to begin running any project phase:
1. Open the command prompt and paste myfirstproject\Scripts\activate to activate the virtual environment.
2. If needed, type cd and the path to where the files are located.

# For running Phase 1
The project will tell the user to enter a job title. Once a title is entered, it will print a list of no more than 40 detailed tasks for that job.

1. Execute the task search by typing python task_search.py
2. It will then prompt you to enter a job title
3. Enter any job title and it will print a list of tasks

# For running Phase 2
1. Execute the AI Scoring layer by typing python cash_test.py
2. It will then prompt you to enter a task description
3. Enter any job description and it will give you a structured JSON response with scores, the number of input tokens used, number of output, tokens, total tokens, and teh creation date, along with caching the data in a json file if it doesnt already exist
