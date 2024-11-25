import smtplib
import requests
import bs4
from dotenv import load_dotenv
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from driver import getUniqueCRNs, getUsersByCRN, getUnsubValue, wasVacant, setWasVacant, getCourseNameDB, setCourseNameDB, purgeUnusedCRNs

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

        # subject = soup.find('span', {'id': 'subject'}).text
        # courseNumber = soup.find('span', {'id': 'courseNumber'}).text
        courseTitle = soup.find('span', {'id': 'courseTitle'}).text

        name = f'{courseTitle}'
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

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"GetTheDamClass Notification for {cname}"
    msg["From"] = sender_email
    msg["To"] = sender_email
    msg["BCC"] = ", ".join(users)

    html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                :root {{
                    --lt-color-gray-100: #f8f9fc;
                    --lt-color-gray-300: #dee3ed;
                    --accent-color: #D73F09;
                    --text-color: var(--lt-color-gray-300);
                    --background-color: #383737;
                }}
                
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: var(--lt-color-gray-100);
                    color: var(--text-color);
                }}

                .email-container {{
                    max-width: 600px;
                    margin: 2rem auto;
                    background-color: var(--background-color);
                    border-radius: 8px;
                    padding: 2rem;
                    color: var(--lt-color-gray-100);
                }}

                .email-header {{
                    text-align: center;
                    padding-bottom: 1rem;
                    border-bottom: 2px solid var(--accent-color);
                }}

                .email-header h1 {{
                    margin: 0;
                    color: var(--lt-color-gray-100);
                }}

                .email-body {{
                    margin-top: 1.5rem;
                    line-height: 1.6;
                    font-size: 1rem;
                }}

                .email-footer {{
                    text-align: center;
                    margin-top: 2rem;
                    padding-top: 1rem;
                    border-top: 2px solid var(--accent-color);
                    font-size: 0.9rem;
                    color: var(--lt-color-gray-300);
                }}

                .cta-button {{
                    display: inline-block;
                    padding: 0.8rem 1.5rem;
                    margin-top: 1.5rem;
                    background-color: var(--accent-color);
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-size: 1rem;
                    font-weight: bold;
                }}

                .cta-button:hover {{
                    background-color: #bf2e08;
                }}
            </style>
            <title>Notification Email</title>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">
                    <h1>Notification for {cname} - {crn}</h1>
                </div>
                <div class="email-body">
                    <p>Hello,</p>
                    <p>We wanted to let you know that your class {cname} with CRN {crn} is {status}. If you want to unsubscribe from notifications, feel free to use the extension.</p>
                    <p>If you have any questions, feel free to reach out to us.</p>
                </div>
                <div class="email-footer">
                    <p>&copy; 2024 Nothing Suspicious | All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
    """

    msg.attach(MIMEText(html_content, "html"))
    
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

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"GetTheDamClass Subscription Confirmation for {cname} with CRN {crn}"
    msg["From"] = sender_email
    msg["To"] = email

    html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                :root {{
                    --lt-color-gray-100: #f8f9fc;
                    --lt-color-gray-300: #dee3ed;
                    --accent-color: #D73F09;
                    --text-color: var(--lt-color-gray-300);
                    --background-color: #383737;
                }}
                
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: var(--lt-color-gray-100);
                    color: var(--text-color);
                }}

                .email-container {{
                    max-width: 600px;
                    margin: 2rem auto;
                    background-color: var(--background-color);
                    border-radius: 8px;
                    padding: 2rem;
                    color: var(--lt-color-gray-100);
                }}

                .email-header {{
                    text-align: center;
                    padding-bottom: 1rem;
                    border-bottom: 2px solid var(--accent-color);
                }}

                .email-header h1 {{
                    margin: 0;
                    color: var(--lt-color-gray-100);
                }}

                .email-body {{
                    margin-top: 1.5rem;
                    line-height: 1.6;
                    font-size: 1rem;
                }}

                .email-footer {{
                    text-align: center;
                    margin-top: 2rem;
                    padding-top: 1rem;
                    border-top: 2px solid var(--accent-color);
                    font-size: 0.9rem;
                    color: var(--lt-color-gray-300);
                }}

                .cta-button {{
                    display: inline-block;
                    padding: 0.8rem 1.5rem;
                    margin-top: 1.5rem;
                    background-color: var(--accent-color);
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-size: 1rem;
                    font-weight: bold;
                }}

                .cta-button:hover {{
                    background-color: #bf2e08;
                }}
            </style>
            <title>Confirmation Email</title>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">
                    <h1>Confirmation for {cname} - {crn}</h1>
                </div>
                <div class="email-body">
                    <p>Hello,</p>
                    <p>We wanted to let you know that you have successfully subscribed to notifications for the class {cname} with CRN {crn}. If you want to unsubscribe from notifications, feel free to click the following button or use the extension.</p>
                    <a href="{baseurl}/unsubscribe?value={unsubval}" class="cta-button">Unsubscribe</a>
                    <p>If you have any questions, feel free to reach out to us.</p>
                </div>
                <div class="email-footer">
                    <p>&copy; 2024 Nothing Suspicious | All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
    """
    # Attach the HTML content to the email
    mime_html = MIMEText(html_content, "html")
    msg.attach(mime_html)

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
    print("Purged unused CRNs") if purgeUnusedCRNs() else print("Failed to purge unused CRNs")
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