import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ESPN Cricinfo RSS URL (Stable & Free)
RSS_URL = "http://static.cricinfo.com/rss/livescores.xml"

@app.route('/')
def home():
    return jsonify({"status": "API is running", "source": "Cricinfo RSS"})

@app.route('/live')
def get_live_scores():
    try:
        # Fetch the XML feed
        response = requests.get(RSS_URL, timeout=10)
        # Use 'xml' parser
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        live_matches = []
        for item in items:
            # RSS provides:
            # <title> matches the score (e.g., "India 250/4 vs Australia")
            # <description> matches the status (e.g., "Day 2: Session 1")
            live_matches.append({
                "title": item.find('title').text.strip(),
                "status": item.find('description').text.strip(),
                "link": item.find('link').text.strip()
            })
            
        return jsonify(live_matches)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# For local testing
if __name__ == '__main__':
    app.run(debug=True)
