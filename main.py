from flask import Flask, request, jsonify
import ssl
import smtplib
import email
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import requests
import bs4
import hashlib

load_dotenv()

app = Flask(__name__)

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

def notifyUsers(crn, users):
    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    body = f"Class with CRN {crn} has been updated. Please check your schedule."
    msg = MIMEText(body)
    msg["From"] = sender_email
    msg["To"] = sender_email
    msg["Subject"] = f"Class Notification for CRN {crn}"
    msg["BCC"] = ", ".join(users)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(msg["From"], users + [msg["To"]], msg.as_string())

def loop():
    while True:
        pass

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get("email")
    pin = data.get("pin")
    return jsonify({"message": "User signed up successfully"}), 200

@app.route('/sub', methods=['POST'])
def sub():
    data = request.json
    crn = data.get("crn")
    email = data.get("email")
    pin = data.get("pin")
    return jsonify({"message": f"Subscribed to class {crn} successfully"}), 200

@app.route('/unsub', methods=['POST'])
def unsub():
    data = request.json
    crn = data.get("crn")
    email = data.get("email")
    pin = data.get("pin")
    return jsonify({"message": f"Unsubscribed from class {crn} successfully"}), 200

@app.route('/getsubs', methods=['POST'])
def getsubs():
    data = request.json
    email = data.get("email")
    pin = data.get("pin")
    subs = []
    return jsonify({"subs": subs}), 200

@app.route('/unsubscribe', methods=['GET'])
def unsubscribe():
    value = request.args.get("value")
    return jsonify({"message": f"Unsubscribed successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)