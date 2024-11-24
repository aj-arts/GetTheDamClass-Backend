import mysql.connector
import bcrypt
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Database Connection 
# We have try catch as the flask server may start prior to the sql container being completly ready
def connect_to_db(attempts=5, delay=5):
    for attempt in range(attempts):
        try:
            myDb = mysql.connector.connect(
                host=os.getenv("DATABASE_HOST"),
                port=os.getenv("DATABASE_PORT"),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
                database=os.getenv("DATABASE_NAME")
            )
            return myDb
        except mysql.connector.Error as err:
            print(f"Attempt {attempt + 1} failed: {err}")
            if attempt < attempts - 1:
                time.sleep(delay)
            else:
                raise

myDb = connect_to_db()

cursor = myDb.cursor()

def valid(email, pin):
    cursor.execute("SELECT HASHED_PIN FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
    result = cursor.fetchone()
    if result is None:
        return False    

    return bcrypt.checkpw(pin.encode(), result[0].encode())


def addUser(email, pin):
    hashed = bcrypt.hashpw(pin.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO Users (EMAIL_ADDRESS, HASHED_PIN) VALUES (%s, %s)", (email, hashed.decode()))
    myDb.commit()
    return True

def linkCRN(CRN, email):
    cursor.execute("SELECT ID FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
    result = cursor.fetchone()
    if result is None:
        return False

    user_id = result[0]
    cursor.execute("INSERT INTO Subscription (ID, CRN_NUMBER) VALUES (%s, %s)", (user_id, CRN))
    myDb.commit()
    return True


def unlinkCRN(CRN, email):
    cursor.execute("SELECT ID FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
    result = cursor.fetchone()
    if result is None:
        return False

    user_id = result[0]
    cursor.execute("DELETE FROM Subscription WHERE ID = %s AND CRN_NUMBER = %s", (user_id, CRN))
    myDb.commit()
    if cursor.rowcount == 0:
        return False
    return True


def getCRNsByUser(email):
    cursor.execute("SELECT ID FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
    result = cursor.fetchone()
    if result is None:
        return []

    user_id = result[0]
    cursor.execute("SELECT CRN_NUMBER FROM Subscription WHERE ID = %s", (user_id,))
    crns = cursor.fetchall()

    return [crn[0] for crn in crns]


def delSubscription(subsubToken):
    cursor.execute("DELETE FROM Subscription WHERE UNSUBSCRIBE = %s", (subsubToken,))
    myDb.commit()
    if cursor.rowcount == 0:
        return False
    return True


def getUniqueCRNs():
    cursor.execute("SELECT DISTINCT CRN_NUMBER FROM Subscription")
    results = cursor.fetchall()
    return [{"CRN": crn, "COURSE_NAME": course_name} for crn, course_name in results]


def getUsersByCRN(CRN):
    cursor.execute("SELECT u.EMAIL_ADDRESS FROM Users u JOIN Subscription s ON u.ID = s.ID WHERE s.CRN_NUMBER = %s", (CRN,))
    results = cursor.fetchall()
    return [user[0] for user in results]


def getUnsubValue(email, CRN):
    cursor.execute("SELECT ID FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
    result = cursor.fetchone()
    if result is None:
        return False
    
    user_id = result[0]

    cursor.execute("SELECT UNSUBSCRIBE FROM Subscription WHERE ID = %s AND CRN_NUMBER = %s", (user_id, CRN))
    result = cursor.fetchone()
    if result is None:
        return False
    return result[0]

def purgeUnusedCRNs():
    cursor.execute("DELETE FROM CRN_Status WHERE CRN_NUMBER NOT IN (SELECT CRN_NUMBER FROM Subscription)")
    myDb.commit()
    return True

def purgeUnusedUsers():
    cursor.execute("DELETE FROM Users WHERE ID NOT IN (SELECT ID FROM Subscription)")
    myDb.commit()
    return True

def deleteUser(email):
    cursor.execute("DELETE FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
    myDb.commit()
    if cursor.rowcount == 0:
        return False
    return True

def wasVacant(crn):
    cursor.execute("SELECT VACANT FROM CRN_Status WHERE CRN_NUMBER = %s", (crn,))
    result = cursor.fetchone()
    if result is None:
        return False
    return result[0]

def setWasVacant(crn, vacant):
    cursor.execute("INSERT INTO CRN_Status (CRN_NUMBER, VACANT) VALUES (%s, %s) ON DUPLICATE KEY UPDATE VACANT = %s", (crn, vacant, vacant))
    myDb.commit()
    if cursor.rowcount == 0:
        return False
    return True

def setCourseNameDB(crn, name):
    cursor.execute("INSERT INTO Course_Name (CRN_NUMBER, COURSE_NAME) VALUES (%s, %s) ON DUPLICATE KEY UPDATE COURSE_NAME = %s", (crn, name, name))
    myDb.commit()
    if cursor.rowcount == 0:
        return False
    return True

def getCourseNameDB(crn):
    cursor.execute("SELECT COURSE_NAME FROM Course_Name WHERE CRN_NUMBER = %s", (crn,))
    result = cursor.fetchone()
    if result is None:
        return False
    return result[0]