from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")

low = 1
high = 100
guess = 50


@app.route("/")
def home():
    return send_from_directory("static", "index.html")


@app.route("/guess", methods=["POST"])
def process():

    global low, high, guess

    data = request.json
    answer = data["answer"]

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
    app.run(host="0.0.0.0", port=5000)