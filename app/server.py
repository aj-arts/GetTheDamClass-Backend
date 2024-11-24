from flask import Flask, request, jsonify
import threading
from loop import loop, confirmSub, getCourseName
from driver import addUser, linkCRN, unlinkCRN, getCRNsByUser, delSubscription

app = Flask(__name__)

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
    
    if not addUser(email, pin):
        return jsonify({"message": "Couldn't add use. Try siging up again!"}), 400

    return jsonify({"message": "User signed up successfully"}), 200

@app.route('/sub', methods=['POST'])
def sub():
    data = request.json
    crn = data.get("crn")
    email = data.get("email")
    pin = data.get("pin")

    if not validEmail(email) or not validPin(pin) or not validCRN(crn):
        return jsonify({"message": "Invalid email, pin, or crn"}), 400
    
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

    if not validEmail(email) or not validPin(pin) or not validCRN(crn):
        return jsonify({"message": "Invalid email, pin, or crn"}), 400

    if not unlinkCRN(crn, email):
        return jsonify({"message": "Couldn't unsubscribe from class. Try again!"}), 400

    return jsonify({"message": f"Unsubscribed from class {crn} successfully"}), 200

@app.route('/getsubs', methods=['POST'])
def getsubs():
    data = request.json
    email = data.get("email")
    pin = data.get("pin")
    subs = {}

    if not validEmail(email) or not validPin(pin):
        return jsonify({"message": "Invalid email or pin"}), 400

    crns = getCRNsByUser(email)

    for crn in crns:
        subs[crn] = getCourseName(crn)

    return jsonify({"subs": subs}), 200

@app.route('/unsubscribe', methods=['GET'])
def unsubscribe():
    value = request.args.get("value")

    if not validValue(value):
        return jsonify({"message": "Invalid value"}), 400
    
    if not delSubscription(value):
        return jsonify({"message": "Couldn't unsubscribe. Try again!"}), 400
    
    return jsonify({"message": f"Unsubscribed successfully"}), 200

if __name__ == '__main__':
    task_thread = threading.Thread(target=loop, daemon=True)
    task_thread.start()
    app.run(host='0.0.0.0', port=5000)