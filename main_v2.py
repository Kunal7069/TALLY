# from flask import Flask, request
# from datetime import datetime
# import json
# import redis
# import assemblyai as aai

# aai.settings.api_key = "62e782d9190040b3adf668249441e727"

# redis_url = "redis://default:qPBK2AqZ4JCHnNuQJj8pS8PekYd56niD@redis-17874.crce182.ap-south-1-1.ec2.redns.redis-cloud.com:17874"

# if not redis_url:
#     raise ValueError("Missing Redis credentials")

# redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

# app = Flask(__name__)


# @app.route("/incoming", methods=["POST"])
# def incoming():
#     incoming_msg = request.form.get("Body", "").strip()
#     number = request.form.get("From")
#     phone_number = number.split(":")[-1]
#     from_number = phone_number[1:]  # remove '+' if exists
#     num_media = int(request.form.get("NumMedia", 0))

#     # Current timestamp with second precision
#     current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

#     # Use only phone number as Redis key
#     redis_key = from_number

#     # --- CASE 1: Media message ---
#     if num_media > 0:
#         media_url = request.form.get("MediaUrl0")
#         media_entry = {
#             "url": media_url,
#             "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
#         }

#         existing_data = redis_client.get(redis_key)
#         media_list = json.loads(existing_data) if existing_data else []
#         media_list.append(media_entry)
#         redis_client.set(redis_key, json.dumps(media_list))
#         # return {"message": "Media saved", "timestamp": media_entry["timestamp"]}

#     # --- CASE 2: Text message ---
#     if incoming_msg:
#         existing_data = redis_client.get(redis_key)
#         if existing_data:
#             media_list = json.loads(existing_data)
#         else:
#             media_list = []

#         # Filter only media entries that match the current second group
#         filtered_media = [
#             item for item in media_list
#             if item["timestamp"][:19] == current_timestamp  # compare up to seconds
#         ]

#         return {
#             "from_number": from_number,
#             "timestamp": current_timestamp,
#             "media": filtered_media,
#             "body": incoming_msg
#         }

#     return {"message": "Media saved", "timestamp": media_entry["timestamp"]}


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)



from flask import Flask, request
from twilio.rest import Client
import os
import redis
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Redis setup ---
redis_url = os.getenv("REDIS_URL")
if not redis_url:
    raise ValueError("Missing REDIS_URL in environment variables")

r = redis.Redis.from_url(redis_url, decode_responses=True)

# --- Twilio setup ---
rev_sid = '7e2604f91d47cbeb831f2b2982ee632eCA'
rev_token = '5465b1cb4708f4a9544aa1c88fb2b84c'
rev_number = '68883255141+:ppastahw'

account_sid = rev_sid[::-1]
auth_token = rev_token[::-1]
twilio_whatsapp_number = rev_number[::-1]

client = Client(account_sid, auth_token)

# --- Flask setup ---
app = Flask(__name__)

# --- Config ---
MEDIA_EXPIRY_SECONDS = 20   # keep a bit longer than grouping window
GROUP_TIME_WINDOW = 10      # collect media within 10 seconds


@app.route("/incoming", methods=["POST"])
def incoming():
    incoming_msg = request.form.get("Body", "").strip()
    from_number = request.form.get("From")
    num_media = int(request.form.get("NumMedia", 0))
    current_time = time.time()

    # ---- Case 1: Only media (no body) ----
    if num_media > 0 and incoming_msg == "":
        new_media = []
        for i in range(num_media):
            media_url = request.form.get(f"MediaUrl{i}")
            media_type = request.form.get(f"MediaContentType{i}")
            new_media.append({
                "url": media_url,
                "type": media_type,
                "timestamp": current_time
            })

        # Get existing media (if any)
        existing = r.get(from_number)
        if existing:
            existing_data = json.loads(existing)
        else:
            existing_data = {"media": []}

        # Add new media and save back
        existing_data["media"].extend(new_media)
        r.set(from_number, json.dumps(existing_data), ex=MEDIA_EXPIRY_SECONDS)

        return {"response": f"Saved {num_media} media file(s) from {from_number}"}

    # ---- Case 2: Has Body (fetch + combine) ----
    elif incoming_msg != "":
        redis_data = r.get(from_number)
        grouped_urls = []

        if redis_data:
            data = json.loads(redis_data)
            if "media" in data:
                # ✅ filter media within 10-second window
                grouped_urls = [
                    m["url"]
                    for m in data["media"]
                    if current_time - m["timestamp"] <= GROUP_TIME_WINDOW
                ]
            # Delete Redis key after using
            r.delete(from_number)

        response = {
            "from": from_number,
            "text": incoming_msg,
            "media_urls": grouped_urls
        }

        return response

    # ---- Case 3: Nothing meaningful ----
    else:
        return {"response": "No valid data received."}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
