import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from .send_email import send_verify
from flask import render_template
import os
from dotenv import find_dotenv, load_dotenv
import uuid



dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
host_arg = os.getenv("host_arg")
user_arg = os.getenv("user_arg")
passwd_arg = os.getenv("passwd_arg")
database_arg = os.getenv("database_arg")


def store_in_db(**kwargs):
    try:
        email = kwargs["email"]
        fname = kwargs["fname"]
        fname=fname.capitalize()
        password = kwargs["password"]
        db = mysql.connector.connect(
            host=host_arg,
            user=user_arg,
            passwd=passwd_arg,
            database=database_arg
        )
        token = generate_unique_token()
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        sql = "INSERT INTO user_data (email, password, first_name, verified, total_api_calls, token) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (email, hashed_password, fname, "false", 0, token)
        mycursor = db.cursor()
        mycursor.execute(sql, val)
        db.commit()
        mycursor.close()
        db.close()
        
    except mysql.connector.Error as err:
        print("Error:", err)
        if err == f"Error: 1062 (23000): Duplicate entry {email} for key 'user_data.email'":
            return render_template("login_signup.html", display="sign_up", alert="An account already exists with this email.")

def get_id_by_email(email):
    try:
        global host_arg, user_arg, passwd_arg, database_arg

        # Connect to the database
        mydb = mysql.connector.connect(
            host=host_arg,
            user=user_arg,
            passwd=passwd_arg,
            database=database_arg
        )

        mycursor = mydb.cursor()

        # Prepare and execute the SQL query
        sql = "SELECT id FROM user_data WHERE email = %s"
        val = (email,)  # Note the comma to create a tuple
        mycursor.execute(sql, val)

        result = mycursor.fetchone()

        mycursor.close()
        mydb.close()

        if result:
            return result[0]  # Return the first column of the result (ID)
        else:
            return None  # Email not found
    except mysql.connector.Error as err:
        print("MySQL Error:", err)
        return None

def check_user_login(email, password):
    try:
        # Ensure global variables are correctly set
        global host_arg, user_arg, passwd_arg, database_arg

        # Connect to the database
        mydb = mysql.connector.connect(
            host=host_arg,
            user=user_arg,
            passwd=passwd_arg,
            database=database_arg
        )

        # Create a cursor
        mycursor = mydb.cursor()

        # Prepare and execute the SQL query
        sql = "SELECT password FROM user_data WHERE email = %s"
        val = (email,)  # Ensure the value is a tuple
        mycursor.execute(sql, val)  # Pass the parameter as a tuple

        # Fetch the result
        result = mycursor.fetchone()

        # Close cursor and database connection
        mycursor.close()
        mydb.close()

        if result:
            hashed_password = result[0]
            if check_password_hash(hashed_password, password):
                return True
            else:
                return False
        else:
            return False
    except mysql.connector.Error as err:
        # Print error message if there's a database error
        print("MySQL Error:", err)
        return False


def get_user_fname(user_id):
    try:
        global host_arg
        global user_arg
        global passwd_arg
        global database_arg
        mydb = mysql.connector.connect(
            host=host_arg,
            user=user_arg,
            passwd=passwd_arg,
            database=database_arg
        )

        mycursor = mydb.cursor()
        sql = "SELECT first_name FROM user_data WHERE id = %s"
        val = (user_id,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        mycursor.close()
        mydb.close()
        if result:
            return result[0]  # Return the first column of the result (ID)
        else:
            return None  # name not found
    except mysql.connector.Error as err:
        print("Error:", err)
        return None
    
def get_verify_status(user_id):
    try:
        global host_arg
        global user_arg
        global passwd_arg
        global database_arg
        mydb = mysql.connector.connect(
            host=host_arg,
            user=user_arg,
            passwd=passwd_arg,
            database=database_arg
        )

        mycursor = mydb.cursor()
        sql = "SELECT verified FROM user_data WHERE id = %s"
        val = (user_id,)  # Add a comma to make it a tuple
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        mycursor.close()
        mydb.close()
        if result:
            return result[0]  # Return the first column of the result (verified status)
        else:
            return None  # ID not found
    except mysql.connector.Error as err:
        print("Error:", err)
        return None


def verify_status(user_id):
    try:
        global host_arg
        global user_arg
        global passwd_arg
        global database_arg
        mydb = mysql.connector.connect(
            host=host_arg,
            user=user_arg,
            passwd=passwd_arg,
            database=database_arg
        )

        mycursor = mydb.cursor()
        sql = "UPDATE user_data SET verified = true WHERE id = %s"
        val = (user_id,)
        mycursor.execute(sql, val)
        mydb.commit()  # Commit the transaction to make the changes permanent
        mycursor.close()
        mydb.close()
        return None 
    except mysql.connector.Error as err:
        print("Error:", err)
        return None

def change_password(email, password):
    try:
        global host_arg, user_arg, passwd_arg, database_arg
        
        # Connect to the MySQL database
        mydb = mysql.connector.connect(
            host=host_arg,
            user=user_arg,
            passwd=passwd_arg,
            database=database_arg
        )
        print(email,password , "email and password")
        # Generate hashed password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Create a cursor
        mycursor = mydb.cursor()
        
        # Update the password in the user_data table
        sql = "UPDATE user_data SET password = %s WHERE email = %s"
        val = (hashed_password, email)
        mycursor.execute(sql, val,)
        
        # Commit the transaction to make the changes permanent
        mydb.commit()
        
        # Close cursor and database connection
        mycursor.close()
        mydb.close()
        print("password changed")
        return None
    except mysql.connector.Error as err:
        print("MySQL Error:", err)
        return None


def update_total_api_call(user_id):
    try:
        global host_arg, user_arg, passwd_arg, database_arg
        mydb = mysql.connector.connect(
            host=host_arg,
            user=user_arg,
            passwd=passwd_arg,
            database=database_arg
        )

        mycursor = mydb.cursor()

        # Update total_api_calls column by incrementing its value by 1
        sql = "UPDATE user_data SET total_api_calls = total_api_calls + 1 WHERE id = %s"
        val = (user_id,)
        mycursor.execute(sql, val)

        mydb.commit()  # Commit the transaction to make the changes permanent
        mycursor.close()
        mydb.close()
    except mysql.connector.Error as err:
        print("Error:", err)


def generate_unique_token():
    while True:
        # Generate a UUID token
        token = str(uuid.uuid4())
        # Check if the token already exists in the database
        if not token_exists_in_database(token):
            return token

def token_exists_in_database(token):
    # Connect to your MySQL database
    # Replace 'your_database' with your actual database name and provide host, user, and password
    connection = mysql.connector.connect(
            host=host_arg,
            user=user_arg,
            passwd=passwd_arg,
            database=database_arg
    )

    # Create a cursor
    cursor = connection.cursor()

    # Check if the token exists in the database
    sql = "SELECT COUNT(*) FROM user_data WHERE token = %s"
    cursor.execute(sql, (token,))
    count = cursor.fetchone()[0]

    # Close cursor and connection
    cursor.close()
    connection.close()

    # Return True if token exists, False otherwise
    return count > 0


def get_token_by_user_id(user_id):
    try:
        # Connect to your MySQL database
        connection = mysql.connector.connect(
            host=host_arg,
            user=user_arg,
            passwd=passwd_arg,
            database=database_arg
        )

        # Create a cursor
        cursor = connection.cursor()

        # Retrieve the token from the database based on the user_id
        sql = "SELECT token FROM user_data WHERE id = %s"
        cursor.execute(sql, (user_id,))  # Pass user_id as a tuple
        token = cursor.fetchone()[0]  # Fetch the token from the query result

        # Close cursor and connection
        cursor.close()
        connection.close()

        return token

    except mysql.connector.Error as err:
        print("MySQL Error:", err)
        return None

def update_token(user_id):
    try:
        # Generate a new unique token
        new_token = generate_unique_token()

        # Connect to your MySQL database
        # Replace 'your_database' with your actual database name and provide host, user, and password
        connection = mysql.connector.connect(
            host=host_arg,
            user=user_arg,
            passwd=passwd_arg,
            database=database_arg
        )

        # Create a cursor
        cursor = connection.cursor()

        # Update the token in the database for the given user_id
        sql = "UPDATE user_data SET token = %s WHERE id = %s"
        cursor.execute(sql, (new_token, user_id))

        # Commit the transaction
        connection.commit()

        # Close cursor and connection
        cursor.close()
        connection.close()

        print(new_token,"new token")

    except mysql.connector.Error as err:
        print("MySQL Error:", err)