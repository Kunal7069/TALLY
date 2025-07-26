from flask import Flask, jsonify, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

# Replace these with your actual credentials from Twilio Console
account_sid = 'ACe236ee2892b2f138bebc74d19f4062e7'
auth_token = '49a0e973ddac8d6894b65dbe4cf9eb8e'
twilio_whatsapp_number = 'whatsapp:+14155238886'  

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
    from_number = request.form.get('From')  

    print(f"Message from {from_number}: {incoming_msg}")

    # Craft your custom reply
    reply_text = f"Hello {from_number}, you said: {incoming_msg}"

    send_whatsapp(from_number, reply_text)
    
    return {"response":reply_text}
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
