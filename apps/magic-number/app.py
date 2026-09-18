import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")

low = 1
high = 100
guess = 50


@app.route("/")
def home():
    return send_from_directory("static", "index.html")

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200
    
@app.route("/guess", methods=["POST"])
def process():

    global low, high, guess

    if not request.is_json:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    answer = data.get("answer")
    if answer is None:
        return jsonify({"error": "Field 'answer' is required"}), 400

    if answer == "start":
        low = 1
        high = 100

    elif answer == "higher":
        low = guess + 1

    elif answer == "lower":
        high = guess - 1

    elif answer == "correct":
        return jsonify({
            "message": f"I guessed it: {guess}"
        })

    guess = (low + high) // 2

    return jsonify({
        "message": f"Is it {guess}?"
    })


if __name__ == "__main__":
    # Default to 0.0.0.0 for Docker/CI compatibility, or override via env
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0") 
    app.run(host=host, port=5000)