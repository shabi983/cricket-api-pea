import random
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)

# JSON headers are simpler and more stable
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

@app.route('/live')
def get_live_ids():
    # This is the internal URL Cricbuzz uses for the match list
    url = "https://www.cricbuzz.com/api/html/homepage-scroller"
    try:
        res = requests.get(url, headers=HEADERS)
        # We parse the IDs from the HTML scroller (more stable than the main page)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.find_all('a', href=True)
        ids = []
        for link in links:
            parts = link['href'].split('/')
            if len(parts) > 2 and parts[2].isdigit():
                ids.append(parts[2])
        return jsonify({"live_match_ids": list(set(ids))})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/score', methods=['GET'])
def get_score():
    mid = request.args.get('id')
    # Internal JSON API for specific match details
    url = f"https://www.cricbuzz.com/api/cricket-match/commentary/{mid}"
    
    try:
        data = requests.get(url, headers=HEADERS).json()
        
        # Extracting data from the JSON structure
        match_header = data.get('matchHeader', {})
        min_details = data.get('minDetails', {})
        
        # Team scores are nested deeply in JSON but always in the same place
        score_info = min_details.get('matchScoreDetails', {}).get('inningsScoreList', [])
        latest_score = score_info[0] if score_info else {}
        
        return jsonify({
            'title': match_header.get('matchDescription', 'Match'),
            'livescore': f"{latest_score.get('score', '0')}/{latest_score.get('wickets', '0')} ({latest_score.get('overs', '0')} ov)",
            'update': min_details.get('status', 'Match Updating...'),
            'runrate': f"CRR: {latest_score.get('runRate', 'N/A')}"
        })
    except Exception as e:
        return jsonify({"title": "Error", "livescore": "Data Unavailable"}), 500

# Upcoming and Results usually require HTML scraping as they don't have public JSON endpoints
@app.route('/upcoming')
def upcoming():
    # Logic from previous stable version...
    return jsonify([]) 

if __name__ == '__main__':
    app.run(debug=True)
