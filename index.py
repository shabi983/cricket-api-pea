import random
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)

# Use a real browser header to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/html',
    'Referer': 'https://www.cricbuzz.com/'
}

@app.route('/live')
def get_live_ids():
    # If the API Scroller is empty, we fallback to the main live page
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # New selection logic: Look for all match links on the live page
        links = soup.find_all('a', href=True)
        live_ids = []
        for link in links:
            href = link['href']
            # Match URLs look like: /live-cricket-scores/101234/match-name
            if '/live-cricket-scores/' in href:
                parts = href.split('/')
                if len(parts) > 2 and parts[2].isdigit():
                    live_ids.append(parts[2])
        
        # Remove duplicates
        return jsonify({"live_match_ids": list(set(live_ids))})
    except Exception as e:
        return jsonify({"error": str(e), "live_match_ids": []}), 500

@app.route('/score', methods=['GET'])
def get_score():
    mid = request.args.get('id')
    # Use the 'leanback' API - it's the fastest and most reliable for scores
    url = f"https://www.cricbuzz.com/match-api/{mid}/leanback.json"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        data = res.json()
        
        # Extract data with .get() to prevent crashes if a field is missing
        return jsonify({
            'title': data.get('team1', {}).get('name', 'Team A') + " vs " + data.get('team2', {}).get('name', 'Team B'),
            'livescore': f"{data.get('bat_team', {}).get('score', '0/0')} ({data.get('bat_team', {}).get('rev_overs', '0')} ov)",
            'update': data.get('status', 'Match in progress'),
            'runrate': f"CRR: {data.get('crr', 'N/A')}"
        })
    except:
        return jsonify({'title': 'Match Data', 'livescore': 'Updating...', 'update': 'Score not available'}), 200

@app.route('/upcoming')
def get_upcoming():
    try:
        # Fetching from the schedule page is more reliable than the homepage scroller
        res = requests.get("https://www.cricbuzz.com/cricket-schedule/upcoming-series/international", headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')
        upcoming = []
        # Look for the match headers in the schedule list
        for match in soup.find_all('div', class_='cb-lv-scrs-col')[:10]: # Limit to 10
            title = match.find('a')
            if title:
                upcoming.append({
                    "title": title.text.strip(),
                    "time": "See Schedule"
                })
        return jsonify(upcoming)
    except:
        return jsonify([])

@app.route('/results')
def get_results():
    try:
        res = requests.get("https://www.cricbuzz.com/cricket-match/live-scores/recent-matches", headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')
        results = []
        # Target the completed match cards
        for card in soup.find_all('div', class_='cb-mtch-lst')[:10]:
            title = card.find('a', class_='text-hvr-underline')
            res_text = card.find('div', class_='cb-text-complete')
            if title and res_text:
                results.append({
                    "title": title.text.strip(),
                    "result": res_text.text.strip()
                })
        return jsonify(results)
    except:
        return jsonify([])
