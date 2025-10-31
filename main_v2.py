from flask import Flask, request
from datetime import datetime
import json
import redis
import assemblyai as aai

aai.settings.api_key = "62e782d9190040b3adf668249441e727"

redis_url = "redis://default:qPBK2AqZ4JCHnNuQJj8pS8PekYd56niD@redis-17874.crce182.ap-south-1-1.ec2.redns.redis-cloud.com:17874"

if not redis_url:
    raise ValueError("Missing Redis credentials")

redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

app = Flask(__name__)


@app.route("/incoming", methods=["POST"])
def incoming():
    incoming_msg = request.form.get("Body", "").strip()
    number = request.form.get("From")
    phone_number = number.split(":")[-1]
    from_number = phone_number[1:]  # remove '+' if exists
    num_media = int(request.form.get("NumMedia", 0))

    # Current timestamp with second precision
    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Use only phone number as Redis key
    redis_key = from_number

    # --- CASE 1: Media message ---
    if num_media > 0:
        media_url = request.form.get("MediaUrl0")
        media_entry = {
            "url": media_url,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }

        existing_data = redis_client.get(redis_key)
        media_list = json.loads(existing_data) if existing_data else []
        media_list.append(media_entry)
        redis_client.set(redis_key, json.dumps(media_list))
        # return {"message": "Media saved", "timestamp": media_entry["timestamp"]}

    # --- CASE 2: Text message ---
    if incoming_msg:
        existing_data = redis_client.get(redis_key)
        if existing_data:
            media_list = json.loads(existing_data)
        else:
            media_list = []

        # Filter only media entries that match the current second group
        filtered_media = [
            item for item in media_list
            if item["timestamp"][:19] == current_timestamp  # compare up to seconds
        ]

        return {
            "from_number": from_number,
            "timestamp": current_timestamp,
            "media": filtered_media,
            "body": incoming_msg
        }

    return {"message": "Media saved"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
