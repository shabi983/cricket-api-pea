import requests
from bs4 import BeautifulSoup as bs
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Use Cricinfo RSS for stability and no limits
RSS_URL = "http://static.cricinfo.com/rss/livescores.xml"

def get_flag_url(team_name):
    """Returns a flag URL based on team name using a public CDN."""
    # Mapping for common World Cup 2026 teams
    flags = {
        "India": "in", "Pakistan": "pk", "England": "gb", "Australia": "au",
        "South Africa": "za", "New Zealand": "nz", "Sri Lanka": "lk",
        "West Indies": "wi", "Afghanistan": "af", "Netherlands": "nl"
    }
    code = flags.get(team_name, "un") # 'un' for unknown
    return f"https://flagcdn.com/w80/{code}.png"

@app.route('/wc-data')
def get_world_cup_data():
    try:
        response = requests.get(RSS_URL, timeout=10)
        soup = bs(response.content, 'xml')
        items = soup.find_all('item')
        
        live, upcoming, recent = [], [], []

        for item in items:
            title = item.find('title').text
            desc = item.find('description').text
            link = item.find('link').text
            
            # Filter specifically for the World Cup
            if "T20 World Cup" in title or "2026" in title or "T20WC" in title:
                match_data = {
                    "full_title": title,
                    "teams": title.split(" v ")[0] if " v " in title else title,
                    "status": desc,
                    "link": link
                }
                
                # Logic to categorize based on status text
                if "Match starts" in desc:
                    upcoming.append(match_data)
                elif "won by" in desc or "Match drawn" in desc or "result" in desc.lower():
                    recent.append(match_data)
                else:
                    live.append(match_data)
                    
        return jsonify({"live": live, "upcoming": upcoming, "recent": recent})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
