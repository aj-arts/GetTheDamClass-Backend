import mysql.connector
from mysql.connector import Error
import argparse
from dotenv import load_dotenv
import os

load_dotenv()


def create_database_and_tables():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host="localhost",
            port= os.getenv("DATABASE_PORT"),
            user= os.getenv("DATABASE_USER"),
            password= os.getenv("DATABASE_PASSWORD"),
            database=os.getenv("DATABASE_NAME")
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Create a new database
            database_name = os.getenv("DATABASE_NAME") 
            create_database_query = f"CREATE DATABASE IF NOT EXISTS {database_name};"
            cursor.execute(create_database_query)
            print(f"Database '{database_name}' created or already exists.")

            # Use the created database
            use_database_query = f"USE {database_name};"
            cursor.execute(use_database_query)

            # Create tables in the new database

            #User table for 
            create_users_table = """
            CREATE TABLE IF NOT EXISTS Users (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                EMAIL_ADDRESS VARCHAR(255) NOT NULL UNIQUE,
                HASHED_PIN VARCHAR(255) NOT NULL
            );
            """

            create_subscription_table = """
            CREATE TABLE IF NOT EXISTS Subscription (
                ID INT NOT NULL,
                CRN_NUMBER INT NOT NULL,
                UNSUBSCRIBE CHAR(36) NOT NULL DEFAULT (UUID()),
                PRIMARY KEY (ID, CRN_NUMBER),
                FOREIGN KEY (ID) REFERENCES Users(ID) ON DELETE CASCADE
            );
            """

            create_crn_status_table = """
            CREATE TABLE IF NOT EXISTS CRN_Status (
                CRN_NUMBER INT PRIMARY KEY,
                VACANT BOOLEAN NOT NULL
            );
            """

            create_course_name_table = """
            CREATE TABLE IF NOT EXISTS Course_Name (
                CRN_NUMBER INT PRIMARY KEY,
                COURSE_NAME VARCHAR(255) NOT NULL,
                FOREIGN KEY (CRN_NUMBER) REFERENCES CRN_Status(CRN_NUMBER) ON DELETE CASCADE
            );
            """

            # Execute the table creation queries
            cursor.execute(create_users_table)
            print("Users table created successfully.")

            cursor.execute(create_subscription_table)
            print("Subscription table created successfully.")

            cursor.execute(create_crn_status_table)
            print("CRN_Status table created successfully.")

            cursor.execute(create_course_name_table)
            print("Course_Name table created successfully.")

            # Commit the changes
            connection.commit()

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

def insert_test_data():
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            port= os.getenv("DATABASE_PORT"),
            user= os.getenv("DATABASE_USER"),
            password= os.getenv("DATABASE_PASSWORD"),
            database=os.getenv("DATABASE_NAME")
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Insert test data into Users table
            cursor.execute("""
                INSERT INTO Users (EMAIL_ADDRESS, HASHED_PIN)
                VALUES
                ('john.doe@example.com', 'hashed_pin_1'),
                ('jane.smith@example.com', 'hashed_pin_2'),
                ('bob.johnson@example.com', 'hashed_pin_3'),
                ('alice.brown@example.com', 'hashed_pin_4');
            """)
            print("Test data inserted into Users table.")

            # Insert test data into CRN_Status table
            cursor.execute("""
                INSERT INTO CRN_Status (CRN_NUMBER, VACANT)
                VALUES
                (12345, TRUE),
                (23456, FALSE),
                (34567, TRUE),
                (45678, FALSE),
                (56789, TRUE);
            """)
            print("Test data inserted into CRN_Status table.")

            # Insert test data into Course_Name table
            cursor.execute("""
                INSERT INTO Course_Name (CRN_NUMBER, COURSE_NAME)
                VALUES
                (12345, 'Introduction to Programming'),
                (23456, 'Data Structures and Algorithms'),
                (34567, 'Database Management Systems'),
                (45678, 'Operating Systems'),
                (56789, 'Computer Networks');
            """)
            print("Test data inserted into Course_Name table.")

            # Insert test data into Subscription table
            cursor.execute("""
                INSERT INTO Subscription (ID, CRN_NUMBER)
                VALUES
                (1, 12345),
                (1, 23456),
                (2, 34567),
                (3, 45678),
                (4, 56789);
            """)
            print("Test data inserted into Subscription table.")

            # Commit the changes
            connection.commit()

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Create a database, tables, and optionally insert test data.")
    parser.add_argument('--insert-test-data', action='store_true', help="Insert test data into the tables.")
    args = parser.parse_args()

    # Create database and tables
    create_database_and_tables()

    # Insert test data if the argument is provided
    if args.insert_test_data:
        insert_test_data()
