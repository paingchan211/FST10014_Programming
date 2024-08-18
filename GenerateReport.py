import datetime
from datetime import date, datetime

# Function to calculate the number of completed tasks
def count_completed_tasks(tasks):
    return sum(1 for task in tasks if task[2] == "done")

# Function to calculate the number of uncompleted tasks
def count_uncompleted_tasks(tasks):
    return sum(1 for task in tasks if task[2] == "todo")

# Function to generate and display the report of finished and unfinished tasks
def generate_and_display_report(tasks):
    done_tasks = count_completed_tasks(tasks)
    not_done_tasks = count_uncompleted_tasks(tasks)

    print(f"\nFinished Tasks: {done_tasks}")
    print(f"Unfinished Tasks: {not_done_tasks}")

# Calculate and print the percentage of completed tasks
def percentage_completed(tasks):
    total_tasks = len(tasks)
    completed_tasks = 0

    for task in tasks:
        if task[2] == "done":
            completed_tasks += 1

    if total_tasks > 0:
        percentage = (completed_tasks / total_tasks) * 100
    else:
        percentage = 0

    print(f"Percentage of Completed Tasks: {percentage:.2f}%")

# Find tasks due soon within a specified threshold of days
def tasks_due_soon(tasks, days_threshold=7):
    current_date = date.today()
    due_soon_tasks = []

    for task in tasks:
        if task[2] == "todo" and task[4] is not None:
            # Ensure that task[4] is already a datetime.date object
            if not isinstance(task[4], date):
                raise ValueError("Task due date must be a datetime.date object")

            # Calculate the days until the task is due
            days_until_due = (task[4] - current_date).days

            # Check if the task is due within the threshold
            if days_until_due <= days_threshold:
                due_soon_tasks.append(task)

    return due_soon_tasks
