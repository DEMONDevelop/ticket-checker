import os
from flask import Flask,render_template, request, jsonify
from firebase_admin import messaging, credentials, initialize_app
from threading import Thread

app = Flask(__name__)
# cred = credentials.Certificate('./serviceAccountKey.json')  # Path to your Firebase Admin SDK key
# initialize_app(cred)
service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if service_account_path:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)
else:
    raise Exception("Service account key path is not set!")

@app.route('/')
def index():
    return "Alive"

@app.route('/send-notification', methods=['POST'])
def send_notification():
    data = request.json
    message = messaging.Message(
        notification=messaging.Notification(
            title=data['title'],
            body=data['body'],
        ),
        token=data['token'],  # The FCM token for the target device
    )

    response = messaging.send(message)  # Send the message
    return jsonify({"success": True, "message_id": response}), 200

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():  
    t = Thread(target=run)
    t.start()
