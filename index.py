import random
import requests
from bs4 import BeautifulSoup as bs
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)

user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
]

def get_soup(url):
    headers = {'User-Agent': random.choice(user_agent_list)}
    res = requests.get(url, headers=headers)
    return bs(res.text, 'html.parser')

@app.route('/live')
def get_live_ids():
    soup = get_soup("https://www.cricbuzz.com/cricket-match/live-scores")
    live_match_ids = []
    # Looks for matches that are currently "Live"
    for container in soup.find_all('div', class_='cb-mtch-lst'):
        link = container.find('a', href=True)
        if link and '/live-cricket-scores/' in link['href']:
            match_id = link['href'].split('/')[2]
            if match_id not in live_match_ids:
                live_match_ids.append(match_id)
    return jsonify({"live_match_ids": live_match_ids})

@app.route('/score', methods=['GET'])
def get_score():
    match_id = request.args.get('id')
    url = f"https://www.cricbuzz.com/live-cricket-scores/{match_id}"
    soup = get_soup(url)
    
    try:
        # Title
        title = soup.find("h1", class_="cb-nav-hdr").text.replace(", Commentary", "").strip() if soup.find("h1") else "Match Name Unavailable"
        
        # Livescore - more robust selector
        score_section = soup.find("div", class_="cb-min-bat-rw")
        livescore = score_section.find("span", class_="cb-font-20").text.strip() if score_section else "Live Score TBD"
        
        # Status/Update
        status_div = soup.find("div", class_="cb-text-inprogress") or soup.find("div", class_="cb-text-complete") or soup.find("div", class_="cb-text-stumps")
        update = status_div.text.strip() if status_div else "Match Stats will Update Soon"
        
        # Run Rate
        rr_tag = soup.find("span", class_="cb-font-12")
        runrate = rr_tag.text.strip() if rr_tag and "CRR" in rr_tag.text else "CRR: N/A"

        return jsonify({
            'title': title,
            'livescore': livescore,
            'update': update,
            'runrate': runrate
        })
    except:
        return jsonify({'title': 'Error Loading', 'livescore': 'N/A', 'update': 'N/A', 'runrate': 'N/A'})

@app.route('/upcoming')
def get_upcoming():
    soup = get_soup("https://www.cricbuzz.com/cricket-match/live-scores/upcoming-matches")
    upcoming = []
    # Targeted containers for upcoming matches
    for match in soup.find_all('div', class_='cb-mtch-lst'):
        title = match.find('a', class_='text-hvr-underline')
        time = match.find('div', class_='cb-mtch-crd-state')
        if title:
            upcoming.append({
                "title": title.text.strip(),
                "time": time.text.strip() if time else "Time TBD"
            })
    return jsonify(upcoming)

@app.route('/results')
def get_results():
    soup = get_soup("https://www.cricbuzz.com/cricket-match/live-scores/recent-matches")
    results = []
    for match in soup.find_all('div', class_='cb-mtch-lst'):
        title = match.find('a', class_='text-hvr-underline')
        result_text = match.find('div', class_='cb-text-complete')
        
        # To get actual scores like "NZ 125/2...", we look for the score div
        score_div = match.find('div', class_='cb-scr-itms')
        score_display = score_div.text.strip() if score_div else ""

        if title and result_text:
            results.append({
                "title": title.text.strip(),
                "result": result_text.text.strip(),
                "score": score_display # This contains the summary of runs
            })
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
