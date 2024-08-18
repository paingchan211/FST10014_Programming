from mysql.connector import Error
from UserAuthentication import connect, close_connection
import mysql.connector
from databasePassword import database_password

# Function that will run only if it is the first time to run the program
def connect_first_time(): # doesn't contain database yet in the mysql.connector.connect()
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=database_password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error connecting to the server:", e)
        return None

def exit_program():
    print("Exiting program.")
    exit()

def create_database():
    mydb = connect_first_time()
    mycursor = mydb.cursor()
    # Check if the database was created
    mycursor.execute("SHOW DATABASES")
    databases = [db[0] for db in mycursor.fetchall()]
    if 'task_manager' not in databases:
        print("Database 'task_manager' created successfully.")
    # Creates database if it doesn't exist
    mycursor.execute("CREATE DATABASE IF NOT EXISTS task_manager") 

def create_task_table():
    mydb = connect()
    mycursor = mydb.cursor()
    # Check if the tasks table was created
    mycursor.execute("SHOW TABLES")
    tables = [table[0] for table in mycursor.fetchall()]
    if 'tasks' not in tables:
        print("Table 'tasks' created successfully.")
    # Creates a table if it does not exist
    mycursor.execute("CREATE TABLE IF NOT EXISTS tasks (\
                      id INT AUTO_INCREMENT PRIMARY KEY,\
                      description VARCHAR(255) NOT NULL, \
                      status ENUM('todo', 'done') NOT NULL, \
                      assigned_to VARCHAR(255) NOT NULL, \
                      due_date DATE)")

def task_menu(role):
    print("\nTask Management:")
    
    if role == "admin":
        print("1. List tasks")
        print("2. Assign task")
        print("3. Delete task")
        print("4. Mark task as done")
        print("5. Edit task details")
        print("6. Generate report")
        print("7. Manage users")
        print("8. Back")
        print("9. Quit")
    elif role == "manager":
        print("1. List Your tasks")
        print("2. Assign task")
        print("3. Delete task")
        print("4. Mark task as done")
        print("5. Edit task details")
        print("6. Generate report")
        print("7. View department tasks")
        print("8. Back")
        print("9. Quit")
    else:
        print("1. List Your tasks")
        print("2. Back")
        print("3. Quit")

def load_tasks():
    connection = connect()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        return tasks # returns a list of tuples e.g. [(1, 'buy milk', 'done' ,'user1'),(...)]
    except Error as e:
        print(f"Error: Unable to load tasks from the database. {e}")
        exit_program()
    finally: # will always works
        close_connection(connection, cursor)

def save_tasks(tasks):
    connection = connect()
    cursor = connection.cursor()

    try:
        cursor.execute("TRUNCATE tasks")
        for task in tasks:
            _, description, status, assigned_to, due_date = task
            cursor.execute("INSERT INTO tasks (description, status, assigned_to, due_date) \
                                VALUES (%s, %s, %s, %s)",
                                (description, status, assigned_to, due_date))
        connection.commit()
    except Error as e:
        print(f"Error: Unable to save tasks to the database. {e}")
        exit_program()
    finally:
        close_connection(connection, cursor)