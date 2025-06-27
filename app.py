import os
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# 👇 Debug line to check if token is available
print("🔐 Replicate API Token:", REPLICATE_API_TOKEN)

# ✅ Updated model version
MODEL_VERSION = "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get("prompt")

    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers={
            "Authorization": f"Token {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "version": MODEL_VERSION,
            "input": { "prompt": prompt }
        }
    )

    prediction = response.json()

    if response.status_code != 201:
        return jsonify({"error": prediction}), 500

    prediction_id = prediction["id"]

    while prediction["status"] not in ["succeeded", "failed"]:
        poll = requests.get(
            f"https://api.replicate.com/v1/predictions/{prediction_id}",
            headers={"Authorization": f"Token {REPLICATE_API_TOKEN}"}
        )
        prediction = poll.json()

    if prediction["status"] == "succeeded":
        return jsonify({"output": prediction["output"][0]})
    else:
        return jsonify({"error": prediction}), 500

if __name__ == "__main__":
    app.run(debug=True)
