from CreateTask import create_database, create_task_table, load_tasks, task_menu
from ViewTask import display_tasks, add_task, delete_task, mark_tasks, view_department_tasks
from AssignTask import edit_task_details
from GenerateReport import generate_and_display_report, percentage_completed, tasks_due_soon
from UserAuthentication import create_user_table,authenticate, connect
from pwinput import pwinput
from UserAuthentication import close_connection, manage_users, create_departments
from mysql.connector import Error

def display_menu():
    print("\n******************")
    print("Enter your choice:")
    print("******************")
    print("1. Login")
    print("2. Exit")
    choice = input("")
    return choice

def login():
    counter = 0
    while counter < 3: # Allows only 3 maximum attempt
        username_input = input("Enter your username: ")
        password_input = pwinput("Enter your password: ")

        result = authenticate(username_input, password_input)
        if result:
            username, role = result
            print("Welcome,", username)
            print("Your role is:", role)  # Display the role of the user
            return username, role
        else:
            print("Authentication failed.")
        counter += 1

def exit_program():
    print("Exiting program.")
    exit()

def create_default_admin_user():
    connection = connect()
    if not connection:
        return False

    try:
        cursor = connection.cursor()

        # Check if the 'admin' user already exists
        query = "SELECT * FROM users WHERE username = 'admin'"
        cursor.execute(query)
        admin_exists = cursor.fetchone()

        if not admin_exists:
            default_admin_username = 'admin'
            default_admin_password = 'pA1@'
            default_admin_email = 'admin@gmail.com'
            default_admin_phone = '1234567890'
            default_admin_role = 'admin'
            default_admin_department = 'null'

            # Create the default admin user
            query = "INSERT INTO users (username, password, email, phone_number, role, department) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (default_admin_username, default_admin_password, default_admin_email, default_admin_phone, default_admin_role, default_admin_department))
            connection.commit()
            print("Default admin user created as it does not exist!")
            return True

        else:
            print("Default admin user already exists.")
            return False

    except Error as e:
        print("Error creating default admin user:", e)
        return False

    finally:
        close_connection(connection, cursor)

def main():
    create_database()
    create_user_table()
    create_task_table()
    create_departments() # Create 5 departments - 'sales', 'marketing', 'hr', 'finance', 'operations'

    # Create default admin user if it doesn't exist
    create_default_admin_user()

    while True:
        choice = display_menu()

        if choice == '1':
            # Login
            username, role = login()
            break

        elif choice == '2':
            # Exit
            exit_program()
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3.")

    if not username:
        return

    tasks = load_tasks()

    while True:
        task_menu(role)

        choice = input("Enter your choice: ")

        if choice == "1":
            print()
            display_tasks(tasks, username, role)
        elif (role == "admin" or role == "manager") and choice in ("2", "3", "4", "5", "6", "7","8"):
            if choice == "2":
                add_task(tasks)
            elif choice == "3":
                display_tasks(tasks, username, role)
                delete_task(tasks)
            elif choice == "4":
                print()
                display_tasks(tasks, username, role)
                mark_tasks(tasks, username, role)
            elif choice == "5":
                display_tasks(tasks, username, role)
                edit_task_details(tasks)
            elif choice == "6":
                generate_and_display_report(tasks)
                percentage_completed(tasks)
                tasks_due_soon(tasks)
            elif choice == "7" and role == "admin":
                manage_users()
            elif choice == "7" and role == "manager":
                view_department_tasks(username,role)
            elif choice == "8":
                main()
                print()
        elif choice in ("2", "3", "9"):
            if choice == "2":
                main()
            else:
                mydb = connect()
                mydb.close()

                print("Thank you. Hope to see you again")
                exit_program()
        else:
            print("Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()