import os
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
MODEL_VERSION = "stability-ai/sdxl:put-your-model-version-id-here"  # Replace with your actual model version ID

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
