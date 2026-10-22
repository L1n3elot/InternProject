#Add two input fields: employee fully-loaded annual cost ($) and estimated hours per task per week
#Calculate human cost per task: (annual salary ÷ 2080 hours) × hours per task per week × 52
#Calculate AI cost per task: estimate token consumption per task run × current API rate per token
#Build a cumulative savings table: tasks ranked by transition priority, running cost delta
#Add a residual view: total the tasks that stay with a human, grouped by reason code, and show what share of the role remains





annual_salary = int(input("Enter employee fully-loaded annual cost ($) "))

# hours per task per week
weekly_hours_per_task = int(input("Enter estimated hours per task per week "))


human_cost = (annual_salary / 2080) * weekly_hours_per_task * 52

# Calculate AI cost per task: estimate token consumption per task run × current API rate per token

print(f"Total human cost: {human_cost:.2f}")
