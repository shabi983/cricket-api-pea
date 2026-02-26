import random
import requests
from bs4 import BeautifulSoup as bs
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)

# A more modern list of user agents
user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
]

@app.route('/')
def hello():
    return jsonify({'message': 'Cricbuzz XML API is running'})

@app.route('/live')
def get_live_ids():
    url = "http://synd.cricbuzz.com/j2me/1.0/livematches.xml"
    headers = {'User-Agent': random.choice(user_agent_list)}
    r = requests.get(url, headers=headers)
    soup = bs(r.content, 'xml') # Use XML parser
    
    matches = soup.find_all('match')
    live_match_ids = []
    
    for m in matches:
        # The 'datapath' usually contains the ID at the end of the URL
        path = m.get('datapath')
        if path:
            # Extract ID from path (e.g., http://.../cricket/live/scorecard/12345/)
            match_id = path.strip('/').split('/')[-1]
            live_match_ids.append(match_id)
            
    return jsonify({"live_match_ids": live_match_ids})

@app.route('/score', methods=['GET'])
def get_score():
    match_id = request.args.get('id')
    # We reconstruct the commentary URL using the ID
    # Note: This is an example path structure
    url = f"http://synd.cricbuzz.com/j2me/1.0/match/{match_id}/commentary.xml"
    
    headers = {'User-Agent': random.choice(user_agent_list)}
    try:
        r = requests.get(url, headers=headers)
        soup = bs(r.content, 'xml')
        
        # Pulling data from the XML structure
        mscr = soup.find('mscr') # Match Score tag
        btm = soup.find_all('btsmn') # Batsmen tags
        
        # Get team scores
        inns = mscr.find('inngs') if mscr else None
        runs = inns.get('r') if inns else "0"
        wickets = inns.get('wkts') if inns else "0"
        overs = inns.get('ovrs') if inns else "0"

        # Get Batsmen
        bat1 = f"{btm[0].get('sname')} ({btm[0].get('r')})" if len(btm) > 0 else "N/A"
        bat2 = f"{btm[1].get('sname')} ({btm[1].get('r')})" if len(btm) > 1 else "N/A"

        return jsonify({
            'title': soup.find('match').get('mchDesc') if soup.find('match') else "Live Match",
            'livescore': f"{runs}/{wickets} ({overs} ov)",
            'update': soup.find('c').text if soup.find('c') else "No commentary available",
            'runrate': f"Batsmen: {bat1}, {bat2}"
        })
    except Exception as e:
        return jsonify({"error": "Match data not available in XML format"}), 404

# Keep your /upcoming and /results from the previous version as they work best with HTML scraping
