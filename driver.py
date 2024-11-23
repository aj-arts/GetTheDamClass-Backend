import mysql.connector
import bcrypt

# Database Connection
myDb = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="root",
    database="getthedamclass"
)

cursor = myDb.cursor()

def valid(email, pin):
    cursor.execute("SELECT SALT, HASHED_PIN FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
    result = cursor.fetchone()
    if result is None:
        return False

    salt, hashed_pin = result
    hashed = bcrypt.hashpw(pin.encode(), salt.encode())
    return hashed == hashed_pin.encode()


def addUser(email, pin):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pin.encode(), salt)
    cursor.execute("INSERT INTO Users (EMAIL_ADDRESS, HASHED_PIN, SALT) VALUES (%s, %s, %s)", (email, hashed.decode(), salt.decode()))
    myDb.commit()
    return True


def linkCRN(CRN, email):
    cursor.execute("SELECT ID FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
    result = cursor.fetchone()
    if result is None:
        return False

    user_id = result[0]
    cursor.execute("INSERT INTO Subscription (USER_ID, CRN) VALUES (%s, %s)", (user_id, CRN))
    myDb.commit()
    return True


def unlinkCRN(CRN, email):
    cursor.execute("SELECT ID FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
    result = cursor.fetchone()
    if result is None:
        return False

    user_id = result[0]
    cursor.execute("DELETE FROM Subscription WHERE USER_ID = %s AND CRN = %s", (user_id, CRN))
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
    cursor.execute("SELECT CRN FROM Subscription WHERE USER_ID = %s", (user_id,))
    crns = cursor.fetchall()
    return [crn[0] for crn in crns]


def delUser(unsubEmail):
    cursor.execute("DELETE FROM Users WHERE EMAIL_ADDRESS = %s", (unsubEmail,))
    myDb.commit()
    if cursor.rowcount == 0:
        return False
    return True


def getUniqueCRNs():
    cursor.execute("SELECT DISTINCT CRN, COURSE_NAME FROM Subscription")
    results = cursor.fetchall()
    return [{"CRN": crn, "COURSE_NAME": course_name} for crn, course_name in results]


def getUsersByCRN(CRN):
    cursor.execute("SELECT u.EMAIL_ADDRESS FROM Users u JOIN Subscription s ON u.ID = s.USER_ID WHERE s.CRN = %s", (CRN,))
    results = cursor.fetchall()
    return [user[0] for user in results]


def getUnsubValue(email):
    cursor.execute("SELECT UNSUBSCRIBE FROM Users WHERE EMAIL_ADDRESS = %s", (email,))
    result = cursor.fetchone()
    if result is None:
        return False
    return result[0]
