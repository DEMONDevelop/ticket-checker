import logging
import os
import time
import requests
from flask import Flask,render_template, request, jsonify
from firebase_admin import messaging, credentials, initialize_app
from threading import Thread

app = Flask(__name__)
# cred = credentials.Certificate('./serviceAccountKey.json')  # Path to your Firebase Admin SDK key
# initialize_app(cred)
service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
test_variable = []

if service_account_path:
    cred = credentials.Certificate(service_account_path)
    initialize_app(cred)
else:
    raise Exception("Service account key path is not set!")

def fetch_now_showing(token):
    logging.info(f"Testing in fetch: {test_variable}")
    test_variable.append("in")
    url = "https://api3.pvrcinemas.com/api/v1/booking/content/nowshowing"
    headers = {
        "appversion": "1.0",
        "authorization": "Bearer",
        "chain": "PVR",
        "city": "Chennai",
        "content-type": "application/json",
        "country": "INDIA",
        "origin": "https://www.pvrcinemas.com",
        "platform": "WEBSITE"
    }
    body = {
        "city": "Chennai"
    }

    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()  # Raise an HTTPError if the response status is 4xx/5xx
        res = response.json()
        movies = res['output']['mv']
        mvNames = [x['filmName'].lower() for x in movies]
        print("Available movies", mvNames)
        logging.info(f"Available movies: {mvNames}")
        for i in movies:
            if('solo' in i['filmName'].lower()):
                print('Solo test done. It works')
                logging.info('Solo test done. It works')
                message = messaging.Message(
                    notification=messaging.Notification(
                        title='Movie Available',
                        body='',
                    ),
                    token=token,  # The FCM token for the target device
                )
                messaging.send(message)
                body2 = {
                    "city": "Chennai",
                    "mid": i['id'],
                    "experience": "ALL",
                    "lat": "12.883208",
                    "lng": "80.3613280",
                    "lang": "ALL",
                    "format": "ALL",
                    "dated": "NA",
                    "time": "08:00-24:00",
                    "cinetype": "ALL",
                    "hc": "ALL",
                    "adFree": False
                }
                url2 = 'https://api3.pvrcinemas.com/api/v1/booking/content/msessions'
                try:
                    response2 = requests.post(url2, json=body2, headers=headers)
                    response2.raise_for_status()  # Raise an HTTPError if the response status is 4xx/5xx
                    res2 = response2.json()
                    logging.info(f"Issue of key {i['id']} with res: {res2['output'].keys()}")
                    cinemas = res2['output']['movieCinemaSessions']
                    for j in cinemas:
                        if('escape' in j['cinema']['name'].lower()):
                            print("Solo available in esacape")
                            logging.info("Solo available in esacape")
                            message = messaging.Message(
                                notification=messaging.Notification(
                                    title='In Escape Movie Available',
                                    body='',
                                ),
                                token=token,  # The FCM token for the target device
                            )
                            messaging.send(message)
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred in 2nd request: {e}")
                    return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


@app.route('/')
def index():
    return "Alive"

@app.route('/send-notification', methods=['POST'])
def send_notification():
    print("Testing", test_variable)
    logging.info(f"Testing: {test_variable}")
    data = request.json
    message = messaging.Message(
        notification=messaging.Notification(
            title=data['title'],
            body=data['body'],
        ),
        token=data['token'],  # The FCM token for the target device
    )

    # test_code(message)
    t1 = Thread(target=fetch_now_showing, args= (data['token'],))
    t1.daemon = True
    t1.start()

    # response = messaging.send(message)  # Send the message
    return jsonify({"success": True}), 200



def test_code(message):
    i = 0
    while True:
      print("Running", i)
      i+= 1
      time.sleep(5)
      response = messaging.send(message)  # Send the message

def run():
  app.run(host='0.0.0.0',port=8080)

def run_infitnitly():
  i = 0
  while True:
      print("Running", i)
      i+= 1
      time.sleep(5)

def keep_alive():  
    t = Thread(target=run)
    t.start()
    t2 = Thread(target=run_infitnitly)
    t2.start()
