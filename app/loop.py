import smtplib
import requests
import bs4
from dotenv import load_dotenv
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from driver import (
    getUniqueCRNs,
    getUsersByCRN,
    getUnsubValue,
    wasVacant,
    setWasVacant,
    wasWaitlistAvail,
    setWasWaitlistAvail,
    getCourseNameDB,
    setCourseNameDB,
    purgeUnusedCRNs,
)

load_dotenv()

TERM = 202603

def crnExists(crn):
    data = {
        'term': str(TERM),
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
            'term': str(TERM),
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
            'term': str(TERM),
            'courseReferenceNumber': crn,
        },
    )

    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    actual = int(soup.find('span', string='Enrollment Actual:').find_next('span').text.strip())
    capacity = int(soup.find('span', string='Enrollment Maximum:').find_next('span').text.strip())
    vacancy = capacity - actual
    return vacancy > 0

def hasWaitlistAvail(crn):
    url = "https://classes.oregonstate.edu/api/?page=fose&route=details"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    }
    payload = {"key": f"crn:{crn}", "srcdb": str(TERM)}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        body = response.json()
        if not isinstance(body, dict):
            raise ValueError(f"Unexpected response shape: {type(body)}")
        avail = int(body.get("ssbsect_wait_avail", "0"))
        return avail > 0
    except (requests.RequestException, ValueError, TypeError) as err:
        print(f"Failed to fetch waitlist availability for CRN {crn}: {err}")
        return None

def getNotificationContent(event_type, cname, crn):
    content_map = {
        "class_open": {
            "subject_prefix": "Class Open",
            "headline": "Class seat available",
            "message": f"your class {cname} with CRN {crn} now has an open seat.",
        },
        "class_closed": {
            "subject_prefix": "Class Full",
            "headline": "Class is full",
            "message": f"your class {cname} with CRN {crn} is now full.",
        },
        "waitlist_open": {
            "subject_prefix": "Waitlist Open",
            "headline": "Waitlist spots available",
            "message": f"the waitlist for {cname} with CRN {crn} now has available spots.",
        },
        "waitlist_closed": {
            "subject_prefix": "Waitlist Full",
            "headline": "Waitlist is full",
            "message": f"the waitlist for {cname} with CRN {crn} is now full.",
        },
    }
    if event_type not in content_map:
        raise ValueError(f"Unsupported notification event type: {event_type}")
    return content_map[event_type]

def notifyUsers(crn, event_type, users):
    if not users:
        print(f"No users to notify for CRN {crn} event {event_type}")
        return

    cname = getCourseName(crn)
    content = getNotificationContent(event_type, cname, crn)

    port = os.getenv("EMAIL_PORT")
    smtp_server = os.getenv("EMAIL_HOST")
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"GetTheDamClass {content['subject_prefix']} Notification for {cname}"
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
                    <h1>{content['headline']} for {cname} - {crn}</h1>
                </div>
                <div class="email-body">
                    <p>Hello,</p>
                    <p>We wanted to let you know that {content['message']} If you want to unsubscribe from notifications, feel free to use the extension.</p>
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
    waitlist_status = hasWaitlistAvail(crn)
    if waitlist_status is not None:
        setWasWaitlistAvail(crn, waitlist_status)
    else:
        print(f"Failed to initialize waitlist status for CRN {crn}")
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
        try:
            isvacant = isVacant(crn)
        except Exception as err:
            print(f"Failed to fetch class vacancy for CRN {crn}: {err}")
            continue
        iswaitlistavail = hasWaitlistAvail(crn)

        print(f"CRN {crn} is vacant: {isvacant}")
        wasvacant = wasVacant(crn)
        print(f"CRN {crn} was vacant: {wasvacant}")
        class_event = None
        if isvacant and not wasvacant:
            class_event = "class_open"
        elif not isvacant and wasvacant:
            class_event = "class_closed"

        waitlist_event = None
        if iswaitlistavail is not None:
            print(f"CRN {crn} has waitlist availability: {iswaitlistavail}")
            waswaitlistavail = wasWaitlistAvail(crn)
            print(f"CRN {crn} previously had waitlist availability: {waswaitlistavail}")
            if iswaitlistavail and not waswaitlistavail:
                waitlist_event = "waitlist_open"
            elif not iswaitlistavail and waswaitlistavail:
                waitlist_event = "waitlist_closed"
        else:
            print(f"Skipping waitlist notifications for CRN {crn} due to API error")

        if class_event or waitlist_event:
            users = getUsersByCRN(crn)
            if class_event:
                notifyUsers(crn, class_event, users)
                setWasVacant(crn, isvacant)
                print(f"Sent class transition notification for CRN {crn}: {class_event}")
                print(f"CRN {crn} vacancy state updated to {isvacant}")
            if waitlist_event:
                notifyUsers(crn, waitlist_event, users)
                setWasWaitlistAvail(crn, iswaitlistavail)
                print(f"Sent waitlist transition notification for CRN {crn}: {waitlist_event}")
                print(f"CRN {crn} waitlist state updated to {iswaitlistavail}")
    print("Vacancy check complete")