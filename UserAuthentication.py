import mysql.connector
from mysql.connector import Error
import re  # Import the regular expression module
from pwinput import pwinput
from databasePassword import database_password

def connect():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='task_manager',
            user='root',
            password=database_password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error connecting to the server:", e)
        return None

def create_user_table():
    db = connect()
    cursor = db.cursor()

    try:
        # Check if the users table was created
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        if 'users' not in tables:
            # Creates the user table if it does not exist
            cursor.execute("CREATE TABLE IF NOT EXISTS users (\
                            id int NOT NULL AUTO_INCREMENT,\
                            username varchar(255) NOT NULL,\
                            password varchar(255) NOT NULL,\
                            email varchar(255) NOT NULL,\
                            phone_number varchar(20) NOT NULL,\
                            role varchar(255) NOT NULL,\
                            department varchar(255) NOT NULL ,\
                            PRIMARY KEY (id),\
                            UNIQUE KEY username (username),\
                            KEY idx_users_id_username_role (id,username,role)\
                            )")
            print("Table 'users' created successfully.")
        else:
            print("Table 'users' already exists.")

    except Error as e:
        print("Error creating user table:", e)

    finally:
        close_connection(db, cursor)
 
def close_connection(connection, cursor):
    if connection.is_connected():
        cursor.close()
        connection.close()

def authenticate(username, password):
    connection = connect()
    if not connection:
        return False

    try:
        cursor = connection.cursor()
        query = "SELECT username, role FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            print("Login successful!")
            # Unpack the retrieved data
            username, role = user
            return username, role  # Return both username and role if found

        else:
            print("Invalid username or password.")
            return False

    except Error as e:
        print("Error authenticating user:", e)
        return False

    finally:
        close_connection(connection, cursor)

def get_valid_username(cursor, username):
    while username_exists(cursor, username):
        print("Username already exists. Please choose another.")
        username = input('Enter a new username: ')
    return username

def get_valid_password():
    password = pwinput("Enter a new password: ")
    while not is_password_complex(password):
        print("Password must include at least 1 lowercase letter, 1 uppercase letter, 1 digit, and 1 special character.")
        password = input("Enter a new password: ")
    return password

def get_valid_email():
    email = input("Enter your email: ")
    while not is_valid_email(email):
        print("Invalid email format.")
        email = input("Enter your email: ")
    return email

def get_valid_phone_number():
    phone_number = input("Enter your phone number: ")
    while not is_valid_phone_number(phone_number):
        print("Invalid phone number format.")
        phone_number = input("Enter your phone number: ")
    return phone_number

def create_user(username, password, email, phone_number, role, department):
    connection = connect()
    if not connection:
        return False

    try:
        cursor = connection.cursor()

        while True:
            # Check if the username already exists
            if username_exists(cursor, username):
                print("Username already exists. Please choose another.")
                username = input('Enter a new username: ')
            else:
                break

        while True:
            # Check password complexity
            if not is_password_complex(password):
                print("Password must include at least 1 lowercase letter, 1 uppercase letter, 1 digit, and 1 special character.")
                password = input("Enter a new password: ")
            else:
                break  # Exit the loop if the password is complex

        # Validate email and phone number format (you can use regex)
        if not is_valid_email(email):
            print("Invalid email format.")
            return False

        if not is_valid_phone_number(phone_number):
            print("Invalid phone number format.")
            return False

        # If the username is unique and the password is complex, create a new user
        query = "INSERT INTO users (username, password, email, phone_number, role, department) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (username, password, email, phone_number, role, department))
        connection.commit()

        user_id = cursor.lastrowid  # Assuming the user ID is auto-incremented

        # Insert the user's ID and role into the respective department table
        if role != 'manager':
            query = f"INSERT INTO {department} (user_id, role) VALUES (%s, %s)"
            cursor.execute(query, (user_id, role))
            connection.commit()

        print("User created successfully!")
        return True

    except Error as e:
        print("Error creating user:", e)
        return False

    finally:
        close_connection(connection, cursor)

def is_password_complex(password):
    # Check if the password contains at least 1 lowercase letter, 1 uppercase letter, 1 digit, and 1 special character
    regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&*!])[A-Za-z\d@#$%^&*!]+$'
    return re.match(regex, password) is not None

def username_exists(cursor, username):
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    return cursor.fetchone() is not None

def is_valid_email(email):
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_pattern, email) is not None

def is_valid_phone_number(phone_number):
    phone_pattern = r'^[0-9]{10}$'
    return re.match(phone_pattern, phone_number) is not None

def sign_up(cursor):
    while True:
        new_username = input("Enter a new username: ")
        new_username = get_valid_username(cursor, new_username)

        new_password = get_valid_password()

        new_email = get_valid_email()

        new_phone_number = get_valid_phone_number()

        print("Select a role:")
        print("1. Manager")  # Manager as the first role option
        print("2. Employee")
        role_choice = input("Enter your role choice (1-2): ")

        roles = ['manager', 'employee']
        role_index = int(role_choice) - 1

        if role_index in range(len(roles)):
            selected_role = roles[role_index]

            print("Select a department:")
            print("1. Sales")
            print("2. Marketing")
            print("3. HR")
            print("4. Finance")
            print("5. Operations")
            department_choice = input("Enter your department choice (1-5): ")

            departments = ['sales', 'marketing', 'hr', 'finance', 'operations']
            department_index = int(department_choice) - 1

            if department_index in range(len(departments)):
                selected_department = departments[department_index]
                if create_user(new_username, new_password, new_email, new_phone_number, selected_role, selected_department):
                    print("Welcome, your account has been created.")
                    return True
                else:
                    print("Account creation failed.")
            else:
                print("Invalid department choice. Please choose a number between 1 and 5.")
        else:
            print("Invalid role choice. Please choose either 1 or 2.")

def manage_users():
    # if role != 'admin':
    #     print("You do not have permission to manage users.")
    #     return

    while True:
        print("\nUser Management:")
        print("1. View all users")
        print("2. Add a new user")
        print("3. Delete a user")
        print("4. Change user details")
        print("5. Go back")
        choice = input("Enter your choice: ")

        if choice == "1":
            view_all_users()
        elif choice == "2":
            connection = connect()
            cursor = connection.cursor()
            sign_up(cursor)
        elif choice == "3":
            delete_user()
        elif choice == "4":
            username_to_change = input("Enter the username you want to change details for: ")
            change_user_details(username_to_change)
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please enter a valid option.")

def view_all_users():
    connection = connect()
    if not connection:
        return

    try:
        cursor = connection.cursor()
        query = "SELECT id, username, email, phone_number, role, department FROM users"
        cursor.execute(query)
        users = cursor.fetchall()

        if users:
            headers = ["ID", "Username", "Email", "Phone Number", "Role", "Department"]
            format_string = "{:<5} {:<20} {:<25} {:<15} {:<15} {:<15}"  # Adjust spacing and alignment as needed

            print(format_string.format(*headers))
            print("-" * (5 + 20 + 25 + 15 + 15 + 15))

            for user in users:
                print(format_string.format(user[0], user[1], user[2], user[3], user[4], user[5]))  # Display each user with department info

    except Error as e:
        print("Error displaying all users:", e)

    finally:
        close_connection(connection, cursor)

def delete_user():
    connection = connect()
    if not connection:
        return

    try:
        cursor = connection.cursor()

        user_id = input("Enter the ID of the user to delete: ")

        # Fetch user details
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()

        if user:
            confirm_delete = input(f"Do you want to delete user '{user[1]}'? (yes/no): ").lower()

            if confirm_delete == "yes":
                # Delete from sales table
                delete_sales_query = "DELETE FROM sales WHERE user_id = %s"
                cursor.execute(delete_sales_query, (user_id,))
                connection.commit()

                # Delete from users table
                delete_user_query = "DELETE FROM users WHERE id = %s"
                cursor.execute(delete_user_query, (user_id,))
                connection.commit()

                print(f"User '{user[1]}' deleted successfully along with associated sales entries.")
            else:
                print("Deletion canceled.")
        else:
            print("User not found.")

    except Error as e:
        print("Error deleting user:", e)

    finally:
        close_connection(connection, cursor)



def change_user_details(username):
    connection = connect()
    if not connection:
        return

    try:
        cursor = connection.cursor()

        print("\nChange User Details:")
        print("1. Change username")
        print("2. Change password")
        print("3. Change email")
        print("4. Change phone number")
        print("5. Go Back")
        choice = input("Enter your choice: ")

        if choice == "1":
            # Code for changing the username (as provided in the previous segment)
            pass
        elif choice == "2":
            new_password = input("Enter the new password: ")
            confirm_password = input(f"Confirm new password: ")
            if new_password == confirm_password:
                update_query = "UPDATE users SET password = %s WHERE username = %s"
                cursor.execute(update_query, (new_password, username))
                connection.commit()
                print("Password updated successfully.")
            else:
                print("Passwords do not match. Password change canceled.")
        elif choice == "3":
            new_email = input("Enter the new email: ")
            update_query = "UPDATE users SET email = %s WHERE username = %s"
            cursor.execute(update_query, (new_email, username))
            connection.commit()
            print("Email updated successfully.")
        elif choice == "4":
            new_phone_number = input("Enter the new phone number: ")
            update_query = "UPDATE users SET phone_number = %s WHERE username = %s"
            cursor.execute(update_query, (new_phone_number, username))
            connection.commit()
            print("Phone number updated successfully.")
        elif choice == "5":
            return
        else:
            print("Invalid choice. Please enter a valid option.")

    except Error as e:
        print("Error changing user details:", e)

    finally:
        close_connection(connection, cursor)

def create_departments():
    departments = ['sales', 'marketing', 'hr', 'finance', 'operations']
    connection = connect()
    if not connection:
        return False

    try:
        cursor = connection.cursor()

        for department in departments:
            # Check if the department table already exists
            cursor.execute(f"SHOW TABLES LIKE '{department}'")
            existing_table = cursor.fetchone()

            if not existing_table:
                # Create the department table if it doesn't exist
                cursor.execute(f"CREATE TABLE {department} (\
                                user_id INT NOT NULL,\
                                role VARCHAR(255) NOT NULL,\
                                FOREIGN KEY (user_id) REFERENCES users(id))")

                print(f"{department.capitalize()} department table created successfully!")
            else:
                print(f"{department.capitalize()} department table already exists.")

        return True

    except Error as e:
        print("Error creating departments:", e)
        return False

    finally:
        close_connection(connection, cursor)