from flask import Flask, jsonify, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import assemblyai as aai
import requests
import json

aai.settings.api_key = "62e782d9190040b3adf668249441e727"

# Replace these with your actual credentials from Twilio Console
rev_sid = '7e2604f91d47cbeb831f2b2982ee632eCA'
rev_token = '5465b1cb4708f4a9544aa1c88fb2b84c'
rev_number = '68883255141+:ppastahw'  

# Reverse them back before using
account_sid = rev_sid[::-1]
auth_token = rev_token[::-1]
twilio_whatsapp_number = rev_number[::-1]


client = Client(account_sid, auth_token)

def send_whatsapp(to_number, message):
    message = client.messages.create(
        from_=twilio_whatsapp_number,
        body=message,
        to=f'whatsapp:{to_number}'
    )
    print("Message sent! SID:", message.sid)



import requests

app = Flask(__name__)


@app.route("/incoming", methods=["POST"])
def incoming():
    # Get text and number
    incoming_msg = request.form.get('Body', '')
    number = request.form.get('From')  
    phone_number = number.split(":")[-1]  
    from_number = phone_number[1:]      

    num_media = int(request.form.get('NumMedia', 0))

    if num_media > 0:
        media_url = request.form.get('MediaUrl0')
        media_type = request.form.get('MediaContentType0')
        
        reply_text = f"Hello {from_number}, we received your audio: {media_url}. type {media_type} with text: {incoming_msg}"
    else:
       
        reply_text = f"Hello {from_number}, you said: {incoming_msg}"


    return {"response": reply_text}



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
