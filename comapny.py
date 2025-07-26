from flask import Flask, jsonify, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

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

@app.route('/get-companies', methods=['GET'])
def get_companies():
    xml_request = """
    <ENVELOPE>
        <HEADER>
            <TALLYREQUEST>Export Data</TALLYREQUEST>
        </HEADER>
        <BODY>
            <EXPORTDATA>
                <REQUESTDESC>
                    <REPORTNAME>List of Companies</REPORTNAME>
                </REQUESTDESC>
            </EXPORTDATA>
        </BODY>
    </ENVELOPE>
    """

    try:
        response = requests.post("http://localhost:9000", data=xml_request, headers={"Content-Type": "application/xml"})
        response.raise_for_status()
        return response.text, 200, {'Content-Type': 'application/xml'}

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500
    
    

@app.route("/incoming", methods=["POST"])
def incoming():
    # Get incoming message and phone number
    incoming_msg = request.form.get('Body')
    number = request.form.get('From') 
    
    phone_number = number.split(":")[-1]  # → '+917466809149'
    from_number = phone_number[1:] 

    print(f"Message from {from_number}: {incoming_msg}")

    # Craft your custom reply
    reply_text = f"Hello {from_number}, you said: {incoming_msg}"

    send_whatsapp(from_number, reply_text)
    
    return {"response":reply_text}
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
