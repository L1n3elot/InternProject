import pandas as pd
import sqlite3

#Add two input fields
annual_salary = float(input("Enter employee fully-loaded annual cost ($) "))

weekly_hours_per_task = float(input("Enter estimated hours per task per week "))

conn = sqlite3.connect('results.sqlite')

API_rate_per_token = 2.80 / 1000000

#Build a cumulative savings table: tasks ranked by importance_score, running cost delta
df = pd.read_sql("""
    SELECT task_text, importance_score, retention_reason_code, input_tokens, output_tokens 
    FROM records ORDER BY importance_score
""", conn)
conn.close()

#Calculate human cost per task
df["human_cost"] = (annual_salary / 2080) * weekly_hours_per_task * 52

#Calculate AI cost per task
df["ai_cost"] = (df["input_tokens"] + df["output_tokens"]) * API_rate_per_token

# cumulative savings table
df["savings"] = df["human_cost"] - df["ai_cost"]
df["cumulative_savings"] = df["savings"].cumsum()

print("\n=== COST COMPARISON TABLE ===")
print(df[["task_text", "importance_score", "human_cost", "ai_cost", "savings", "cumulative_savings"]])
print(f"\nTotal Human Cost: ${df['human_cost'].sum():,.2f}")
print(f"Total AI Cost:    ${df['ai_cost'].sum():,.2f}")
print(f"Total Savings:    ${df['savings'].sum():,.2f}")

# Add a residual view: total the tasks that stay with a human, grouped by reason code, and show what share of the role remains
retained = df[df["retention_reason_code"] != "not_retained"]
residual = retained.groupby("retention_reason_code")["human_cost"].agg(task_count="count", total_human_cost="sum")
percent_retained = (len(retained) / len(df)) * 100

print(f"\n=== RESIDUAL VIEW ({percent_retained:.1f}% Role Retained) ===")
print(residual)








