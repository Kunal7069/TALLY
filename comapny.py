from flask import Flask, jsonify, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import assemblyai as aai

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

# def send_whatsapp(to_number, message):
#     message = client.messages.create(
#         from_=twilio_whatsapp_number,
#         body=message,
#         to=f'whatsapp:{to_number}'
#     )
#     print("Message sent! SID:", message.sid)

def send_whatsapp_buttons(to_number, body_text, options):
    """
    Send a WhatsApp message with clickable buttons via Twilio.
    options: list of strings, max 3 (WhatsApp limitation)
    """
    if len(options) > 3:
        options = options[:3]  # WhatsApp allows max 3 buttons

    buttons = [{"type": "reply", "reply": {"id": f"btn{i}", "title": option}} 
               for i, option in enumerate(options)]

    message = client.messages.create(
        from_=twilio_whatsapp_number,
        to=f'whatsapp:{to_number}',
        interactive={
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": buttons}
        }
    )
    print("Interactive message sent! SID:", message.sid)

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
    

# @app.route("/incoming", methods=["POST"])
# def incoming():
#     # Get text and number
#     incoming_msg = request.form.get('Body', '')
#     number = request.form.get('From')  
#     phone_number = number.split(":")[-1]  
#     from_number = phone_number[1:]      

#     num_media = int(request.form.get('NumMedia', 0))

#     if num_media > 0:
#         media_url = request.form.get('MediaUrl0')
#         media_type = request.form.get('MediaContentType0')
#         # audio_file = media_url

#         # config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)

#         # transcript = aai.Transcriber(config=config).transcribe(audio_file)
#         # print(f"Received media from {from_number}: {media_url} ({media_type})")

#         reply_text = f"Hello {from_number}, we received your audio: {media_url}. with text: {incoming_msg}"
#     else:
#         # print(f"Message from {from_number}: {incoming_msg}")
#         reply_text = f"Hello {from_number}, you said: {incoming_msg}"

#     # Send response
#     send_whatsapp(from_number, reply_text)

#     return {"response": reply_text}

@app.route("/incoming", methods=["POST"])
def incoming():
    number = request.form.get('From')  
    from_number = number.split(":")[-1]
    incoming_msg = request.form.get('Body', '')

    # Detect if user clicked a button (Twilio sends the title as Body)
    if incoming_msg in ["Option 1", "Option 2", "Option 3"]:
        reply_text = f"You clicked: {incoming_msg}"
        send_whatsapp(from_number, reply_text)
        return {"response": reply_text}

    # Otherwise, send the options as buttons
    options = ["Option 1", "Option 2", "Option 3"]
    send_whatsapp_buttons(from_number, "Please select one option:", options)

    return {"response": "Buttons sent"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
