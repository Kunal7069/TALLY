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
    from_number = phone_number[1:]
    num_media = int(request.form.get("NumMedia", 0))

    # Create timestamp group key (minute precision)
    timestamp_key = datetime.now().strftime("%Y-%m-%dT%H:%M")

    redis_key = f"{from_number}:{timestamp_key}"

    # --- CASE 1: Media message (image/audio/video) ---
    if num_media > 0 and not incoming_msg:
        media_url = request.form.get("MediaUrl0")
        media_entry = {
            "url": media_url,
            "timestamp": datetime.now().isoformat()
        }

        existing_data = redis_client.get(redis_key)
        if existing_data:
            media_list = json.loads(existing_data)
        else:
            media_list = []

        media_list.append(media_entry)
        redis_client.set(redis_key, json.dumps(media_list))
        return {"message": "Media saved", "timestamp_group": timestamp_key}

    # --- CASE 2: Text message ---
    if incoming_msg:
        existing_data = redis_client.get(redis_key)
        if existing_data:
            media_list = json.loads(existing_data)
        else:
            media_list = []

        return {
            "from_number": from_number,
            "timestamp_group": timestamp_key,
            "media": media_list,
            "body": incoming_msg
        }

    return {"message": "No valid input"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
