from email.message import EmailMessage
import ssl
import smtplib
import datetime
from CreateTask import save_tasks


def edit_task_assignment(task):
    try:
        new_assigned_to = input("Enter the new assigned user: ")
        if not new_assigned_to.strip():  # Check if the input is empty
            raise ValueError("Assigned user cannot be empty.")
        print("Task assignment edited successfully.")
        return (task[0], task[1], task[2], new_assigned_to, task[4])
    except ValueError as e:
        print(f"Error: {e}. Task assignment not changed.")
        return task

def edit_due_date(task):
    try:
        new_due_date_str = input("Enter the new due date (YYYY-MM-DD): ")
        if new_due_date_str.lower() == 'n/a': # to allow user to indicate that a task does not have a specific due date
            return (task[0], task[1], task[2], task[3], 'N/A')
        
        if not new_due_date_str.strip():  # Check if the input is empty
            raise ValueError("Due date cannot be empty.")

        new_due_date = datetime.datetime.strptime(new_due_date_str, '%Y-%m-%d').date()
        print("Due date successfully changed.")

        if new_due_date < datetime.date.today():
            raise ValueError("Due date cannot be before today. Due date not changed.")

        return (task[0], task[1], task[2], task[3], new_due_date)
    except ValueError as e:
        print(f"Error: {e} Due date not changed.")
        return task

def edit_task_details(tasks):
    task_id = input("Enter the task ID to edit: ")
    task_id = int(task_id) if task_id.isdigit() else None

    if task_id is not None and any(task[0] == task_id for task in tasks):
        for i, task in enumerate(tasks):
            if task[0] == task_id:
                print(f"Editing Task {task_id}: {task[1]}")
                print("1. Edit task assigned to")
                print("2. Edit due date")
                edit_choice = input("Enter your choice: ")

                if edit_choice == "1":
                    tasks[i] = edit_task_assignment(task)
                elif edit_choice == "2":
                    tasks[i] = edit_due_date(task)
                else:
                    print("Invalid choice. No changes were made.")

                save_tasks(tasks)
                break
    else:
        print("Invalid task ID. Please enter a valid task ID.")

def send_email(subject, body, receiver_email):
    # Sender's email credentials
    email_sender = 'pctemporaryemailfortesting@gmail.com'
    email_password = 'rlke kfcg qhbd ezht'

    # Create an EmailMessage object
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = receiver_email
    em['subject'] = subject
    em.set_content(body)

    # Create an SSL context for secure connection
    context = ssl.create_default_context()

    # Connect to the SMTP server and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        # Login to the email account
        smtp.login(email_sender, email_password)

        # Send the email
        smtp.sendmail(email_sender, receiver_email, em.as_string())

# Function to send email to the user when the admins assigns a new task
def send_assignment_email(receiver_email, task_description, due_date):
    subject = "Task Assignment"
    body = f"You have been assigned a new task:\n\nTask Description: {task_description}\nDue Date: {due_date}"
    
    try:
        send_email(subject, body, receiver_email)
        print(f"Email notification sent to {receiver_email} for the assigned task.")
    except Exception as e:
        print(f"Error sending email notification: {e}")

