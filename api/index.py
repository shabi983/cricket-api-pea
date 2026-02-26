import requests
import random
from bs4 import BeautifulSoup as bs
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

RSS_URL = "http://static.cricinfo.com/rss/livescores.xml"

def get_flag_url(team_name):
    flags = {
        "India": "in", "Pakistan": "pk", "England": "gb", "Australia": "au",
        "South Africa": "za", "New Zealand": "nz", "Sri Lanka": "lk",
        "West Indies": "wi", "Afghanistan": "af", "Netherlands": "nl",
        "USA": "us", "Canada": "ca", "Ireland": "ie", "Scotland": "gb-sct",
        "Namibia": "na", "Oman": "om", "Nepal": "np", "Bangladesh": "bd"
    }
    # Clean team name (remove " (W)" or score snippets)
    clean_name = team_name.split(' ')[0] if team_name else ""
    code = flags.get(clean_name, "un")
    return f"https://flagcdn.com/w80/{code}.png"

@app.route('/wc-data')
def get_world_cup_data():
    try:
        response = requests.get(RSS_URL, timeout=10)
        soup = bs(response.content, 'xml')
        items = soup.find_all('item')
        
        live, upcoming, recent = [], [], []

        for item in items:
            title = item.find('title').text # e.g. "Pakistan 150/2 v England"
            desc = item.find('description').text # e.g. "Match starts in 3h 8m"
            
            # Filter specifically for the T20 World Cup 2026
            if "T20 World Cup" in title or "2026" in title:
                # Split teams accurately
                teams_part = title.split(' v ')
                t1_name = teams_part[0].split(' ')[0] if len(teams_part) > 0 else "TBD"
                t2_name = teams_part[1].split(' ')[0] if len(teams_part) > 1 else "TBD"

                match_data = {
                    "full_title": title,
                    "team1": t1_name,
                    "team2": t2_name,
                    "flag1": get_flag_url(t1_name),
                    "flag2": get_flag_url(t2_name),
                    "status": desc,
                }
                
                if "Match starts" in desc or "Today" in desc or ":" in desc:
                    upcoming.append(match_data)
                elif "won by" in desc or "result" in desc.lower():
                    recent.append(match_data)
                else:
                    live.append(match_data)
                    
        return jsonify({"live": live, "upcoming": upcoming, "recent": recent})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This handles the root URL on Vercel
@app.route('/')
def home():
    return "T20 World Cup API is Live. Use /wc-data to fetch results."

if __name__ == '__main__':
    # Render provides a PORT environment variable
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
