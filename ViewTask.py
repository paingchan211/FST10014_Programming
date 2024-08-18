from datetime import datetime, date
import time
from CreateTask import save_tasks
from AssignTask import send_assignment_email
from mysql.connector import Error
from UserAuthentication import connect, close_connection

# Function to display tasks based on user's role
def display_tasks(tasks, username, role):
    tasks_for_user = []
    for task in tasks:
        if role == "admin" or task[3] == username:
            tasks_for_user.append(task)

    all_done = all(task[2] == "done" for task in tasks_for_user)

    if all_done and role != "admin":
        print("Great job. You have no tasks for now.")
        return

    headers = ["Task ID", "Status", "Description", "Assigned To", "Due Date"]
    format_string = "{:<10} {:<10} {:<30} {:<20} {:<12}" # < is used to left-align the columns

    print(format_string.format(*headers)) # * is used to unpack headers which is a list of strings
    print("-" * (10 + 10 + 30 + 20 + 12))

    for task in tasks_for_user:
        if isinstance(task[4], date):
            formatted_due_date = task[4].strftime('%Y-%m-%d')
        else:
            formatted_due_date = task[4] if task[4] and task[4] != 'N/A' else "N/A"

        print(format_string.format(task[0], task[2], task[1], task[3], formatted_due_date))

def add_task(tasks):
    description = input("Enter task description: ")
    assigned_to = input("Assign task to (username): ")
    due_date_str = input("Enter due date (YYYY-MM-DD): ")

    try:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    # Fetch the email of the assigned user
    assigned_user_email = get_user_email(assigned_to)

    if assigned_user_email:
        task_id = len(tasks) + 1
        new_task = (task_id, description, "todo", assigned_to, due_date.strftime('%Y-%m-%d'))
        tasks.append(new_task)
        save_tasks(tasks)
        time.sleep(1)
        print("\n******************** Task added successfully. ********************\n")

        # Notify the assigned user via email
        send_assignment_email(assigned_user_email, description, due_date)
    else:
        print("Assigned user not found. Task not added.")

def get_user_email(username):
    connection = connect()
    if not connection:
        return None

    try:
        cursor = connection.cursor()
        query = "SELECT email FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the email if found

    except Error as e:
        print("Error retrieving user email:", e)

    finally:
        close_connection(connection, cursor)
    return None

def delete_task(tasks):
    task_id = input("Enter the task ID to delete: ")

    matching_tasks = []
    for task in tasks:
        if str(task[0]) == task_id:
            matching_tasks.append(task)

    if matching_tasks:
        confirm_delete_task(matching_tasks, tasks, task_id)
    else:
        print("Invalid task ID. Please enter a valid task ID.")

def confirm_delete_task(matching_tasks, tasks, task_id):
    task_to_delete = matching_tasks[0]

    print(f"Task ID: {task_to_delete[0]}")
    print(f"Description: {task_to_delete[1]}")
    print(f"Status: {task_to_delete[2]}")
    print(f"Assigned to: {task_to_delete[3]}")
    print(f"Due Date: {task_to_delete[4]}")

    confirm_delete = input("Do you want to delete this task? (yes/no): ").lower()
    
    if confirm_delete == "yes":
        tasks.remove(task_to_delete)
        save_tasks(tasks)
        print(f"Task {task_id} deleted successfully.")
    else:
        print("Task deletion canceled.")

#Function to mark tasks as done
def mark_tasks(tasks, username, role):
    while True:
        task_id = input("Enter the task ID to mark as done: ")
        task_id = int(task_id) if task_id.isdigit() else None

        if task_id is not None and any(task[0] == task_id for task in tasks):
            for i, task in enumerate(tasks):
                if task[0] == task_id:
                    tasks[i] = (task[0], task[1], "done", task[3], task[4])
                    save_tasks(tasks)
                    print("Task marked as done........\n")
                    time.sleep(1)
                    display_tasks(tasks, username, role)
            break
        else:
            print("Invalid task ID. Please enter a valid task ID.")

from datetime import datetime

from datetime import datetime

def view_department_tasks(username, role):
    if role == 'manager':
        connection = connect()
        if not connection:
            return

        try:
            cursor = connection.cursor()

            # Assuming there's a 'department' field in the users table
            query = f"SELECT u.username, t.description, t.due_date FROM tasks t \
                     JOIN users u ON t.id = u.id \
                     WHERE u.username = %s"
            cursor.execute(query, (username,))
            tasks = cursor.fetchall()

            if tasks:
                print("{:<20} {:<25} {:<15}".format("Username", "Task Description", "Due Date"))
                for task in tasks:
                    formatted_date = task[2].strftime('%Y-%m-%d')  # Format date here
                    print("{:<20} {:<25} {:<15}".format(task[0], task[1], formatted_date))
            else:
                print("No tasks found for this department.")

        except Error as e:
            print("Error fetching department tasks:", e)

        finally:
            close_connection(connection, cursor)
    else:
        print("You do not have permission to access this function.")

