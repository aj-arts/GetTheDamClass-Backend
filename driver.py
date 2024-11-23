import mysql.connector

myDb = mysql.connector.connect(
    host="localhost:3306",
    user="root",
    password="root",
)

def valid(email, pin):

    return False

def addUser(email, pin):

    return False

def linkCRN(CRN, email):
    
    return False

def unlinkCRN(CRN, email):

    return False

def getCRNsByUser(email):

    return []

def delUser(unsubEmail):

    return False

def getUniqueCRNs():

    return {}

def getUsersByCRN(CRN):

    return []

def getUnsubValue(email):

    return False

