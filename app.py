from flask import Flask,request,make_response,jsonify,redirect
import logging
import os
import py_eureka_client.eureka_client as eureka_client
import jwt
import datetime
from functools import wraps
import math,random
import pyotp
import DateTime.DateTime
import time
import redis
import boto3
import json
from django_otp.oath import totp
from datetime import datetime

# Current date time in local system
Time=datetime.now()
print(Time)

client = boto3.client(
    'ses',
    region_name='resgion name',
    aws_access_key_id='your-key-id',
    aws_secret_access_key='your-access-key'
)

app = Flask(__name__)



from firebase_admin import credentials, firestore, initialize_app
credential_path = r"C:\Users\Black\Downloads\gcp1.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
from pyrebase import pyrebase
config = {
    "apiKey": "your-firebase-key",
    "authDomain": "project-name.firebaseapp.com",
    "databaseURL": "your-database-url",
    "projectId": "your-project-id",
    "storageBucket": "project-name.appspot.com",
    "messagingSenderId": "your-messenger-id",
    "appId": "your-app-id"
  };
firebase = pyrebase.initialize_app(config)

db = firebase.database()

from flask import Flask, request,render_template
from google.cloud import storage
from pyotp.otp import OTP
from pygments.lexers import d



# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET = 'pan_test'


@app.route('/upload', methods=['POST'])
def upload():
    try:


#         # The public URL can be used to directly access the uploaded file via HTTP.
        if request.method == 'POST':
            # if request.form['submit'] == 'add':
                Full_Name = request.form['Full_Name']
                Email_Id = request.form['Email_Id']
                base32secret = 'S3K3TPI5MYA2M6HY'

                totp = pyotp.TOTP(base32secret,interval=60)
                a=totp.now()
                OTP=a
                Time=str(datetime.now())
                
                db.child("patient_info/User_Details").child(OTP).set({'Full_Name':Full_Name,'Email_Id':Email_Id,'OTP':OTP,'Time':Time})
                db_events=db.child("patient_info/User_Details").child(OTP).set({'Full_Name':Full_Name,'Email_Id':Email_Id,'OTP':OTP,'Time':Time})
               
                info_json = json.loads(json.dumps(db_events))
                print(info_json)
                d=info_json.get('OTP')
                e=d
                print(e)
            
                response = client.send_email(
                     Destination={
                        'ToAddresses': [Email_Id],
                                },
                        Message={
                            'Body': {
                                'Text': {
                                    'Charset': 'UTF-8',
                                    'Data':'your OTP is:'+OTP,
                                    
                                },
                                },
                                'Subject': {
                                    'Charset': 'UTF-8',
                                    'Data': 'One Time Password',
                                },
                            },
                        Source='OrboCare<vishal@loyaljuice.com>',
                )
                return ('Enter the otp sent to your emailid')
            
                
                

                
        
    except KeyError:
        return 'Keys are not passed'
    return redirect('/verify')

@app.route('/verify',methods=['POST'])
def verify():
    if request.method=='POST':
        # Email_Id=request.form['Email_Id']
        OTP_1=request.form['OTP_1']
        
        db_events = db.child("patient_info/User_Details").order_by_key().get().val()
        info_json = json.loads(json.dumps(db_events))
        

        d=info_json
        
    try:
        otp=(d[OTP_1]['OTP'])
        email=(d[OTP_1]['Email_Id'])
        fullname=(d[OTP_1]['Full_Name'])
    

        
        print(otp)
        print(email)
       
        Time=str(datetime.now())
        
        
        
        if OTP_1==otp:
            db.child('patient_info/Valid_Users').push({'Full_Name':fullname,'Email_Id':email,'OTP':OTP_1,'Time':Time})
      
            db.child('patient_info/User_Details').child(OTP_1).remove()
        


            return('validated')
    except:
        return ('wrong/invalid otp')
    
    

if __name__ == '__main__':
    
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=9090, debug=True)