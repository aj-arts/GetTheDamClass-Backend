import smtplib
import requests
import bs4
from dotenv import load_dotenv
import os
from email.mime.text import MIMEText
import ssl
from driver import getUniqueCRNs, getUsersByCRN, getUnsubValue, wasVacant, setWasVacant, getCourseNameDB, setCourseNameDB

load_dotenv()

def crnExists(crn):
    data = {
        'term': '202502',
        'courseReferenceNumber': crn,
    }

    response = requests.post(
        'https://prodapps.isadm.oregonstate.edu/StudentRegistrationSsb/ssb/searchResults/getClassDetails',
        data=data,
    )

    return response.status_code == 200

def getCourseName(crn):
    cname = getCourseNameDB(crn)
    if not cname:
        data = {
            'term': '202502',
            'courseReferenceNumber': crn,
        }

        response = requests.post(
            'https://prodapps.isadm.oregonstate.edu/StudentRegistrationSsb/ssb/searchResults/getClassDetails',
            data=data,
        )

        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        subject = soup.find('span', {'id': 'subject'}).text
        courseNumber = soup.find('span', {'id': 'courseNumber'}).text
        courseTitle = soup.find('span', {'id': 'courseTitle'}).text

        name = f'{subject} {courseNumber} - {courseTitle}'
        setCourseNameDB(crn, name)
        return name
    return cname

def isVacant(crn):
    response = requests.post(
        'https://prodapps.isadm.oregonstate.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo',
        data={
            'term': '202502',
            'courseReferenceNumber': crn,
        },
    )

    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    actual = int(soup.find('span', string='Enrollment Actual:').find_next('span').text.strip())
    capacity = int(soup.find('span', string='Enrollment Maximum:').find_next('span').text.strip())
    vacancy = capacity - actual
    return vacancy > 0

def notifyUsers(crn, isvacant, users):
    cname = getCourseName(crn)

    port = os.getenv("EMAIL_PORT")
    smtp_server = os.getenv("EMAIL_HOST")
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    status = "vacant" if isvacant else "full"

    body = f"Your class {cname} with CRN {crn} is {status}. Please check your schedule."
    msg = MIMEText(body)
    msg["From"] = sender_email
    msg["To"] = sender_email
    msg["Subject"] = f"GetTheDamClass Notification for {cname}"
    msg["BCC"] = ", ".join(users)

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(msg["From"], users + [msg["To"]], msg.as_string())
            print(f"Notification sent to {users}")
    except:
        print("Failed to send notification email")

def confirmSub(crn, email):
    status = isVacant(crn)
    setWasVacant(crn, status)
    cname = getCourseName(crn)
    unsubval = getUnsubValue(email, crn)

    port = os.getenv("EMAIL_PORT")
    smtp_server = os.getenv("EMAIL_HOST")
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    baseurl = os.getenv("BASE_URL")

    body = f"Thank you for subscribing to {cname} with CRN {crn}. To unsubscribe, click the following link: {baseurl}/unsubscribe?value={unsubval}"
    msg = MIMEText(body)
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = f"GetTheDamClass Subscription Confirmation for {cname}"

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(msg["From"], msg["To"], msg.as_string())
            print(f"Confirmation sent to {email}")
    except:
        print("Failed to send confirmation email")

def checkVacancies():
    print("Checking for vacancies...")
    for crn in getUniqueCRNs():
        isvacant = isVacant(crn)
        print(f"CRN {crn} is vacant: {isvacant}")
        wasvacant = wasVacant(crn)
        print(f"CRN {crn} was vacant: {wasvacant}")
        if isvacant and not wasvacant:
            users = getUsersByCRN(crn)
            notifyUsers(crn, isvacant, users)
            setWasVacant(crn, True)
            print(f"Notification class is vacant sent for CRN {crn}")
            print(f"CRN {crn} is now marked as vacant")
        elif not isvacant and wasvacant:
            users = getUsersByCRN(crn)
            notifyUsers(crn, isvacant, users)
            setWasVacant(crn, False)
            print(f"Notification class is not vacant anymore sent for CRN {crn}")
            print(f"CRN {crn} is now marked as full")
    print("Vacancy check complete")