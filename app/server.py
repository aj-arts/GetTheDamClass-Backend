from flask import Flask, request, jsonify
from loop import checkVacancies, confirmSub, getCourseName, crnExists
from driver import valid, addUser, linkCRN, unlinkCRN, getCRNsByUser, delSubscription, deleteUser, userExists, subExists
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
cors = CORS(app, resources={r"/sub": {"origins": "*"}})

# Helper function to validate email format
def validEmail(email):
    if email is None or email == "" or "@" not in email or email.strip() == "":
        print(f"Invalid email: {email}")
        return False
    return True

# Helper function to validate pin format
def validPin(pin):
    if pin is None or pin == "" or pin.strip() == "" or len(pin) != 4 or not pin.isdigit():
        return False
    return True

# Helper function to validate CRN format
def validCRN(crn):
    if crn is None or crn == "" or crn.strip() == "" or not crn.isdigit():
        print(f"Invalid CRN: {crn}")
        return False
    return True

# Helper function to validate general values
def validValue(value):
    if value is None or value == "" or value.strip() == "":
        print(f"Invalid value: {value}")
        return False
    return True

# Route for user signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get("email")
    pin = data.get("pin")

    print(f"Signup attempt: email={email}, pin={pin}")

    if not validEmail(email) or not validPin(pin):
        return jsonify({"message": "Invalid email or pin"}), 400
    
    if userExists(email):
        print(f"User already exists: {email}")
        return jsonify({"message": "User already exists"}), 409
    
    if not addUser(email, pin):
        print(f"Failed to add user: {email}")
        return jsonify({"message": "Couldn't add user. Try signing up again!"}), 400

    print(f"User signed up successfully: {email}")
    return jsonify({"message": "User signed up successfully"}), 200

# Route to delete a user
@app.route('/deleteuser', methods=['POST'])
def deleteuser():
    data = request.json
    email = data.get("email")
    pin = data.get("pin")

    print(f"Delete user attempt: email={email}, pin={pin}")

    if not validEmail(email) or not validPin(pin) or not valid(email, pin):
        return jsonify({"message": "Invalid email or pin"}), 400
    
    if not valid(email, pin):
        return jsonify({"message": "User authentication failed"}), 401
    
    if not userExists(email):
        return jsonify({"message": "User doesn't exist"}), 400
    
    if not deleteUser(email):
        print(f"Failed to delete user: {email}")
        return jsonify({"message": "Couldn't delete user. Try again!"}), 400

    print(f"User deleted successfully: {email}")
    return jsonify({"message": "User deleted successfully"}), 200

# Route to subscribe to a class
@app.route('/sub', methods=['POST'])
def sub():
    data = request.json
    crn = data.get("crn")
    email = data.get("email")
    pin = data.get("pin")

    print(f"Subscribe attempt: email={email}, pin={pin}, crn={crn}")

    if not validEmail(email) or not validPin(pin) or not validCRN(crn):
        return jsonify({"message": "Invalid email, pin, or crn"}), 400
    
    if not valid(email, pin):
        return jsonify({"message": "User authentication failed"}), 401
    
    if not userExists(email):
        print(f"User doesn't exist: {email}")
        return jsonify({"message": "User doesn't exist"}), 400
    
    if not crnExists(crn):
        print(f"CRN doesn't exist: {crn}")
        return jsonify({"message": "CRN doesn't exist"}), 400
    
    if subExists(email, crn):
        print(f"Already subscribed: email={email}, crn={crn}")
        return jsonify({"message": "Already subscribed to class"}), 409
    
    if not linkCRN(crn, email):
        print(f"Failed to link CRN: email={email}, crn={crn}")
        return jsonify({"message": "Couldn't subscribe to class. Try again!"}), 400
    
    confirmSub(crn, email)
    print(f"Subscribed successfully: email={email}, crn={crn}")
    return jsonify({"message": f"{email} subscribed to class {crn} successfully"}), 200

# Route to unsubscribe from a class
@app.route('/unsub', methods=['POST'])
def unsub():
    data = request.json
    crn = data.get("crn")
    email = data.get("email")
    pin = data.get("pin")

    print(f"Unsubscribe attempt: email={email}, pin={pin}, crn={crn}")

    if not validEmail(email) or not validPin(pin) or not validCRN(crn):
        return jsonify({"message": "Invalid email, pin, or crn"}), 400
    
    if not valid(email, pin):
        return jsonify({"message": "User authentication failed"}), 401
    
    if not userExists(email):
        print(f"User doesn't exist: {email}")
        return jsonify({"message": "User doesn't exist"}), 400
    
    if not crnExists(crn):
        print(f"CRN doesn't exist: {crn}")
        return jsonify({"message": "CRN doesn't exist"}), 400
    
    if not subExists(email, crn):
        print(f"Not subscribed: email={email}, crn={crn}")
        return jsonify({"message": "Not subscribed to class"}), 400

    if not unlinkCRN(crn, email):
        print(f"Failed to unlink CRN: email={email}, crn={crn}")
        return jsonify({"message": "Couldn't unsubscribe from class. Try again!"}), 400

    print(f"Unsubscribed successfully: email={email}, crn={crn}")
    return jsonify({"message": f"Unsubscribed from class {crn} successfully"}), 200

# Route to get all subscriptions for a user
@app.route('/getsubs', methods=['POST'])
def getsubs():
    data = request.json
    email = data.get("email")
    pin = data.get("pin")

    print(f"Get subscriptions: email={email}, pin={pin}")

    if not validEmail(email) or not validPin(pin):
        return jsonify({"message": "Invalid email or pin"}), 400
    
    if not valid(email, pin):
        return jsonify({"message": "User authentication failed"}), 401

    crns = getCRNsByUser(email)
    sublist = [{"crn": crn, "name": getCourseName(crn)} for crn in crns]

    print(f"Subscriptions retrieved for {email}: {sublist}")
    return jsonify({"subs": sublist}), 200

# Route to unsubscribe using a value
@app.route('/unsubscribe', methods=['GET'])
def unsubscribe():
    value = request.args.get("value")
    print(f"Unsubscribe using value: {value}")

    if not validValue(value):
        return jsonify({"message": "Invalid value"}), 400
    
    if not delSubscription(value):
        print(f"Failed to unsubscribe using value: {value}")
        return jsonify({"message": "Couldn't unsubscribe. Try again!"}), 400
    
    print(f"Unsubscribed successfully using value: {value}")
    return jsonify({"message": f"Unsubscribed successfully"}), 200

# Scheduler to check for vacancies
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=checkVacancies,
    trigger=IntervalTrigger(seconds=60),
    id='checkVacancies',
    name='Check for class vacancies every 60 seconds',
    replace_existing=True,
)
scheduler.start()
print("Scheduler started...")

def scheduler_shutdown():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("Scheduler stopped...")

# Application entry point
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except (KeyboardInterrupt, SystemExit):
        scheduler_shutdown()
