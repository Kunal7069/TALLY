from flask import Flask, jsonify, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import assemblyai as aai
import requests
import json
import redis

aai.settings.api_key = "62e782d9190040b3adf668249441e727"


redis_url = "redis://default:qPBK2AqZ4JCHnNuQJj8pS8PekYd56niD@redis-17874.crce182.ap-south-1-1.ec2.redns.redis-cloud.com:17874"  # os.getenv("REDIS_URL")
# redis_token = os.getenv("REDIS_TOKEN")

if not redis_url:
    raise ValueError("Missing Redis credentials in environment variables")

redis = redis.Redis.from_url(redis_url, decode_responses=True)


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
    
    if num_media > 0 and incoming_msg.strip() == "":
        redis_urls = redis.get(from_number)
        if redis_urls:
            redis_urls_temp = json.loads(redis_urls)
            redis_urls_temp.append(request.form.get('MediaUrl0'))
            redis.set(from_number, json.dumps(redis_urls_temp))
    
    # if num_media > 0:
    #     media_url = request.form.get('MediaUrl0')
    #     media_type = request.form.get('MediaContentType0')
        
    #     reply_text = f"Hello {from_number}, we received your audio: {media_url}. type {media_type} with text: {incoming_msg}"
    # else:
       
    #     reply_text = f"Hello {from_number}, you said: {incoming_msg}"
    
    if incoming_msg.strip().lower() != "":
        redis_urls = redis.get(from_number)
        redis_urls_temp = json.loads(redis_urls)
        return {"from_number": from_number, "redis_urls":redis_urls_temp}
      


    return {"response": from_number}



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
