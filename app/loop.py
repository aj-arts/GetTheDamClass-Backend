import smtplib
import requests
import bs4
from dotenv import load_dotenv
import os
from email.mime.text import MIMEText
import ssl
from driver import valid, addUser, linkCRN, unlinkCRN, getCRNsByUser, delUser, getUniqueCRNs, getUsersByCRN, getUnsubValue

load_dotenv()

def getCourseName(crn):
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
    return name

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

    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    status = "vacant" if isvacant else "full"

    body = f"Your class {cname} with CRN {crn} is {status}. Please check your schedule."
    msg = MIMEText(body)
    msg["From"] = sender_email
    msg["To"] = sender_email
    msg["Subject"] = f"GetTheDamClass Notification for {cname}"
    msg["BCC"] = ", ".join(users)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(msg["From"], users + [msg["To"]], msg.as_string())

def loop():
    while True:
        for crn in unique_crns:
            isvacant = isVacant(crn)
            wasvacant = wasVacant(crn)
            if isvacant and not wasvacant:
                users = getUsersByCRN(crn)
                notifyUsers(crn, isvacant, users)
                setWasVacant(crn, True)
            elif not isvacant and wasvacant:
                users = getUsersByCRN(crn)
                notifyUsers(crn, isvacant, users)
                setWasVacant(crn, False)