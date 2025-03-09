from flask import Flask, request
import requests

app = Flask(__name__)

@app.route("/proxy", methods=["GET"])
def proxy():
    address = request.args.get("address")
    if not address:
        return {"error": "Missing address"}, 400

    url = f"https://tokenscan.io/api/balances/{address}"
    response = requests.get(url)

    return response.json(), response.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5027)