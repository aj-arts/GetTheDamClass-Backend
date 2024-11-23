import mysql.connector

def create_tables():
    try:
        # Establish the database connection
        myDb = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="root",
            database="getthedamclass"
        )
        
        cursor = myDb.cursor()
        
        # SQL commands to create the tables
        create_users_table = """
        CREATE TABLE IF NOT EXISTS Users (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            EMAIL_ADDRESS VARCHAR(255) NOT NULL UNIQUE,
            HASHED_PIN VARCHAR(255) NOT NULL,
            SALT VARCHAR(255) NOT NULL,
            UNSUBSCRIBE VARCHAR(255) NOT NULL
        );
        """
        
        create_subscription_table = """
        CREATE TABLE IF NOT EXISTS Subscription (
            ID INT NOT NULL,
            CRN_NUMBER INT NOT NULL,
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
            COURSE_NAME VARCHAR(255) NOT NULL
        );
        """
        
        # Execute the SQL commands
        cursor.execute(create_users_table)
        cursor.execute(create_subscription_table)
        cursor.execute(create_crn_status_table)
        cursor.execute(create_course_name_table)
        
        # Commit the changes
        myDb.commit()
        print("Tables created successfully.")
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    finally:
        # Close the connection
        if myDb.is_connected():
            cursor.close()
            myDb.close()
            print("Database connection closed.")

if __name__ == "__main__":
    create_tables()