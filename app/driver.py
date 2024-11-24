import mysql.connector
from mysql.connector import pooling
import bcrypt
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Database connection pool
db_config = {
    "host": os.getenv("DATABASE_HOST"),
    "port": os.getenv("DATABASE_PORT"),
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "database": os.getenv("DATABASE_NAME")
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    pool_reset_session=True,
    **db_config
)

# Database utility function
def get_db_connection():
    return connection_pool.get_connection()

# Functions
def valid(email, pin):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT HASHED_PIN FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
        result = cursor.fetchone()
        return bcrypt.checkpw(pin.encode(), result[0].encode()) if result else False
    except Exception as e:
        print(f"Error validating user: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def addUser(email, pin):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed = bcrypt.hashpw(pin.encode(), bcrypt.gensalt())
        cursor.execute("INSERT IGNORE INTO Users (EMAIL_ADDRESS, HASHED_PIN) VALUES (%s, %s)", (email, hashed.decode()))
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()

def linkCRN(CRN, email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
        result = cursor.fetchone()
        if result:
            cursor.execute("INSERT IGNORE INTO Subscription (ID, CRN_NUMBER) VALUES (%s, %s)", (result[0], CRN))
            conn.commit()
            return True
        return False
    finally:
        cursor.close()
        conn.close()

def unlinkCRN(CRN, email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
        result = cursor.fetchone()
        if result:
            cursor.execute("DELETE FROM Subscription WHERE ID = %s AND CRN_NUMBER = %s", (result[0], CRN))
            conn.commit()
            return cursor.rowcount > 0
        return False
    finally:
        cursor.close()
        conn.close()

def getCRNsByUser(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
        result = cursor.fetchone()
        if not result:
            return []
        cursor.execute("SELECT CRN_NUMBER FROM Subscription WHERE ID = %s", (result[0],))
        crns = cursor.fetchall()
        return [crn[0] for crn in crns]
    finally:
        cursor.close()
        conn.close()

def delSubscription(subsubToken):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Subscription WHERE UNSUBSCRIBE = %s", (subsubToken,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def getUniqueCRNs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT CRN_NUMBER FROM Subscription")
        results = cursor.fetchall()
        return [crn[0] for crn in results]
    finally:
        cursor.close()
        conn.close()

def getUsersByCRN(CRN):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT u.EMAIL_ADDRESS FROM Users u JOIN Subscription s ON u.ID = s.ID WHERE s.CRN_NUMBER = %s", (CRN,))
        results = cursor.fetchall()
        return [user[0] for user in results]
    finally:
        cursor.close()
        conn.close()

def getUnsubValue(email, CRN):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
        result = cursor.fetchone()
        if not result:
            return False
        cursor.execute("SELECT UNSUBSCRIBE FROM Subscription WHERE ID = %s AND CRN_NUMBER = %s", (result[0], CRN))
        result = cursor.fetchone()
        return result[0] if result else False
    finally:
        cursor.close()
        conn.close()

def purgeUnusedCRNs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CRN_Status WHERE CRN_NUMBER NOT IN (SELECT CRN_NUMBER FROM Subscription)")
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()

def purgeUnusedUsers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE ID NOT IN (SELECT ID FROM Subscription)")
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()

def deleteUser(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def wasVacant(crn):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT VACANT FROM CRN_Status WHERE CRN_NUMBER = %s", (crn,))
        result = cursor.fetchone()
        return result[0] if result else False
    finally:
        cursor.close()
        conn.close()

def setWasVacant(crn, vacant):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO CRN_Status (CRN_NUMBER, VACANT) VALUES (%s, %s) ON DUPLICATE KEY UPDATE VACANT = %s", (crn, vacant, vacant))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def setCourseNameDB(crn, name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Course_Name (CRN_NUMBER, COURSE_NAME) VALUES (%s, %s) ON DUPLICATE KEY UPDATE COURSE_NAME = %s", (crn, name, name))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def getCourseNameDB(crn):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COURSE_NAME FROM Course_Name WHERE CRN_NUMBER = %s", (crn,))
        result = cursor.fetchone()
        return result[0] if result else False
    finally:
        cursor.close()
        conn.close()

def userExists(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
        result = cursor.fetchone()
        return result is not None
    finally:
        cursor.close()
        conn.close()

def subExists(email, CRN):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
        result = cursor.fetchone()
        if not result:
            return False
        cursor.execute("SELECT ID FROM Subscription WHERE ID = %s AND CRN_NUMBER = %s", (result[0], CRN))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()
