from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

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
    subs = {"crn": "cname"}
    return jsonify({"subs": subs}), 200

@app.route('/unsubscribe', methods=['GET'])
def unsubscribe():
    value = request.args.get("value")
    return jsonify({"message": f"Unsubscribed successfully"}), 200

if __name__ == '__main__':
    task_thread = threading.Thread(target=loop, daemon=True)
    task_thread.start()
    app.run(debug=True)