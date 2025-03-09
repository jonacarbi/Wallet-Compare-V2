from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

def fetch_assets_from_api(address, page=1, limit=100):
    api_url = f"https://tokenscan.io/api/balances/{address}?page={page}&limit={limit}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and data['data']:
            return {
                asset['asset']: asset['quantity']
                for asset in data['data']
            }
        else:
            return {}

    except requests.exceptions.RequestException:
        return {}

def get_all_assets(address):
    all_assets = {}
    page = 1
    limit = 100

    while True:
        assets = fetch_assets_from_api(address, page, limit)
        if not assets:
            break
        all_assets.update(assets)
        page += 1

    return all_assets

def compare_wallets(your_address, their_address):
    your_assets = get_all_assets(your_address)
    their_assets = get_all_assets(their_address)

    unique_assets = {asset: quantity for asset, quantity in their_assets.items() if asset not in your_assets}
    return {
        "your_assets_count": len(your_assets),
        "their_assets_count": len(their_assets),
        "unique_assets": unique_assets
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        your_address = request.form['your_address']
        their_address = request.form['their_address']
        
        # Perform the comparison
        result = compare_wallets(your_address, their_address)
        
        return render_template('index.html', result=result)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
