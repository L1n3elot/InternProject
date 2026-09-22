annual_salary = int(input("Enter employee fully-loaded annual cost ($) "))

# hours per task per week
weekly_hours_per_task = int(input("Enter estimated hours per task per week "))


human_cost = (annual_salary / 2080) * weekly_hours_per_task * 52

# Calculate AI cost per task: estimate token consumption per task run × current API rate per token

print(f"Total human cost: {human_cost:.2f}")
