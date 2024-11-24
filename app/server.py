from flask import Flask, request, jsonify
from loop import checkVacancies, confirmSub, getCourseName, crnExists
from driver import valid, addUser, linkCRN, unlinkCRN, getCRNsByUser, delSubscription, deleteUser, userExists, subExists
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/sub": {"origins": "*"}})

def validEmail(email):
    if email is None or email == "" or "@" not in email or email.strip() == "":
        return False
    return True

def validPin(pin):
    if pin is None or pin == "" or pin.strip() == "" or len(pin) != 4 or not pin.isdigit():
        return False
    return True

def validCRN(crn):
    if crn is None or crn == "" or crn.strip() == "" or not crn.isdigit():
        return False
    return True

def validValue(value):
    if value is None or value == "" or value.strip() == "":
        return False
    return True

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get("email")
    pin = data.get("pin")

    if not validEmail(email) or not validPin(pin):
        return jsonify({"message": "Invalid email or pin"}), 400
    
    if userExists(email):
        return jsonify({"message": "User already exists"}), 400
    
    if not addUser(email, pin):
        return jsonify({"message": "Couldn't add use. Try siging up again!"}), 400

    return jsonify({"message": "User signed up successfully"}), 200

@app.route('/deleteuser', methods=['POST'])
def deleteuser():
    data = request.json
    email = data.get("email")
    pin = data.get("pin")

    if not validEmail(email) or not validPin(pin) or not valid(email, pin):
        return jsonify({"message": "Invalid email or pin"}), 400
    
    if not deleteUser(email):
        return jsonify({"message": "Couldn't delete user. Try again!"}), 400

    return jsonify({"message": "User deleted successfully"}), 200

@app.route('/sub', methods=['POST'])
def sub():
    data = request.json
    crn = data.get("crn")
    email = data.get("email")
    pin = data.get("pin")

    if not validEmail(email) or not validPin(pin) or not validCRN(crn) or not valid(email, pin):
        return jsonify({"message": "Invalid email, pin, or crn"}), 400
    
    if not crnExists(crn):
        return jsonify({"message": "CRN doesn't exist"}), 400
    
    if subExists(crn, email):
        return jsonify({"message": "Already subscribed to class"}), 400
    
    if not linkCRN(crn, email):
        return jsonify({"message": "Couldn't subscribe to class. Try again!"}), 400
    
    confirmSub(crn, email)

    return jsonify({"message": f"{email} subscribed to class {crn} successfully"}), 200

@app.route('/unsub', methods=['POST'])
def unsub():
    data = request.json
    crn = data.get("crn")
    email = data.get("email")
    pin = data.get("pin")

    if not validEmail(email) or not validPin(pin) or not validCRN(crn) or not valid(email, pin):
        return jsonify({"message": "Invalid email, pin, or crn"}), 400
    
    if not crnExists(crn):
        return jsonify({"message": "CRN doesn't exist"}), 400
    
    if not subExists(crn, email):
        return jsonify({"message": "Not subscribed to class"}), 400

    if not unlinkCRN(crn, email):
        return jsonify({"message": "Couldn't unsubscribe from class. Try again!"}), 400

    return jsonify({"message": f"Unsubscribed from class {crn} successfully"}), 200

@app.route('/getsubs', methods=['POST'])
def getsubs():
    data = request.json
    email = data.get("email")
    pin = data.get("pin")
    sublist = []

    if not validEmail(email) or not validPin(pin) or not valid(email, pin):
        return jsonify({"message": "Invalid email or pin"}), 400

    crns = getCRNsByUser(email)

    for crn in crns:
        sublist.append({
            "crn": crn,
            "cname": getCourseName(crn)
        })

    return jsonify({"subs": sublist}), 200

@app.route('/unsubscribe', methods=['GET'])
def unsubscribe():
    value = request.args.get("value")

    if not validValue(value):
        return jsonify({"message": "Invalid value"}), 400
    
    if not delSubscription(value):
        return jsonify({"message": "Couldn't unsubscribe. Try again!"}), 400
    
    return jsonify({"message": f"Unsubscribed successfully"}), 200

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

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except (KeyboardInterrupt, SystemExit):
        scheduler_shutdown()