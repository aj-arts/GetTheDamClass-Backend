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
