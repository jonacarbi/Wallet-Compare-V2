from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Mapping of directories to their respective asset files and API usage
ASSET_FILES = {
    "Dank Rare": "Dank_Assets.txt",
    "Rare Pepe": "Rare_Assets.txt",
    "Fake Rare": "Fake_Assets.txt",
    "Wojaks": "Wojaks_Assets.txt",
    "STAMPs": "STAMPs_Assets.txt",
    "Bitcorn": "Bitcorns_Assets.txt",
    "Fake Commons": "Fake_Commons_Assets.txt",
    "Rare Coco": "Rare_Coco_Assets.txt",
    "Kaleidoscope": None  # Kaleidoscope uses a different data source/API
}

# Fetch assets from the Kaleidoscope API
def fetch_kaleidoscope_assets():
    api_url = "https://www.kaleidoscopexcp.com/api/v1/assets/"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return {item['asset_name'] for item in data}  # Adjust key if needed
    except requests.exceptions.RequestException:
        return set()

# Read the asset file or fetch from API for the selected directory
def load_assets(directory):
    if directory == "Kaleidoscope":
        return fetch_kaleidoscope_assets()
    
    filename = ASSET_FILES.get(directory)
    if not filename:
        return set()
    
    try:
        with open(filename, "r") as file:
            return {line.strip() for line in file.readlines()}
    except FileNotFoundError:
        return set()

# Determine whether to parse a number as an int or a float
def parse_quantity(quantity_str):
    try:
        # Attempt to parse as an integer first
        value = int(quantity_str)
    except ValueError:
        # Fallback to parsing as a float if int parsing fails
        value = float(quantity_str)
    return value

# Fetch assets from the API based on a wallet address
def fetch_assets_from_api(address, page=1, limit=100):
    api_url = f"https://tokenscan.io/api/balances/{address}?page={page}&limit={limit}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and data['data']:
            return {asset['asset']: parse_quantity(asset['quantity']) for asset in data['data']}
        else:
            return {}

    except requests.exceptions.RequestException:
        return {}

# Retrieve all assets by iterating through paginated responses
def get_all_assets(address, selected_assets):
    all_assets = {}
    page = 1
    limit = 100

    while True:
        assets = fetch_assets_from_api(address, page, limit)
        if not assets:
            break
        filtered_assets = {asset: quantity for asset, quantity in assets.items() if asset in selected_assets}
        all_assets.update(filtered_assets)
        page += 1

    return all_assets

# Compare assets between two wallet addresses based on selected category
def compare_wallets(your_address, their_address, directory):
    selected_assets = load_assets(directory)
    your_assets = get_all_assets(your_address, selected_assets)
    their_assets = get_all_assets(their_address, selected_assets)

    unique_assets = {asset: quantity for asset, quantity in their_assets.items() if asset not in your_assets}
    return {
        "your_assets_count": len(your_assets),
        "their_assets_count": len(their_assets),
        "unique_assets": unique_assets
    }

# Find duplicate assets in a given wallet and directory
def find_dupes(address, directory):
    selected_assets = load_assets(directory)
    all_assets = get_all_assets(address, selected_assets)

    dupes = {asset: quantity for asset, quantity in all_assets.items() if quantity > 1}
    return dupes

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    selected_directory = "Dank Rare"  # Default selection

    if request.method == 'POST':
        your_address = request.form['your_address']
        their_address = request.form['their_address']
        selected_directory = request.form['directory']
        
        if 'compare' in request.form:
            result = compare_wallets(your_address, their_address, selected_directory)
        elif 'find_dupes' in request.form:
            your_dupes = find_dupes(your_address, selected_directory)
            their_dupes = find_dupes(their_address, selected_directory)
            result = {
                "your_dupes": your_dupes,
                "their_dupes": their_dupes
            }

    return render_template('index.html', result=result, directories=ASSET_FILES.keys(), selected_directory=selected_directory)

if __name__ == "__main__":
    app.run(debug=True)