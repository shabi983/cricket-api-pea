import random
import requests
from bs4 import BeautifulSoup as bs
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import pytz

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)

user_agent_list = [
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
]

def get_soup(url):
    headers = {'User-Agent': random.choice(user_agent_list), 'Cache-Control': 'no-cache'}
    res = requests.get(url, headers=headers)
    return bs(res.text, 'html.parser')

@app.route('/')
def hello():
    return jsonify({'Code': 200, 'message': 'Python - Free Cricket Score API'})

@app.route('/score', methods=['GET'])
def get_score():
    match_id = request.args.get('id')
    if not match_id:
        return jsonify({"error": "No ID provided"}), 400

    url = f"https://www.cricbuzz.com/live-cricket-scores/{match_id}"
    soup = get_soup(url)
    
    try:
        # Status/Update Logic
        status_selectors = [
            ("cb-text-complete", "cb-col-100 cb-min-stts"),
            ("cb-text-inprogress", ""),
            ("cb-text-stumps", ""),
            ("cb-text-lunch", ""),
            ("cb-text-tea", ""),
            ("cb-text-rain", ""),
        ]
        
        status = "Match Stats will Update Soon"
        for cls, extra in status_selectors:
            found = soup.find("div", class_=lambda x: x and cls in x)
            if found:
                status = found.text.strip()
                break

        # Basic Info
        title = soup.find("h1", class_="cb-nav-hdr").text.strip().replace(", Commentary", "") if soup.find("h1", class_="cb-nav-hdr") else "Data Not Found"
        live_score = soup.find("span", class_="cb-font-20 text-bold").text.strip() if soup.find("span", class_="cb-font-20 text-bold") else "Data Not Found"
        run_rate = soup.find("span", class_="cb-font-12 cb-text-gray").text.strip().replace("CRR: ", "") if soup.find("span", class_="cb-font-12 cb-text-gray") else "N/A"

        return jsonify({
            'title': title,
            'update': status,
            'livescore': live_score,
            'runrate': 'CRR: ' + run_rate,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/live')
def get_live_ids():
    soup = get_soup("https://www.cricbuzz.com/cricket-match/live-scores")
    live_match_ids = []
    for link in soup.find_all('a', href=True):
        if '/live-cricket-scores/' in link['href']:
            parts = link['href'].split('/')
            if len(parts) >= 3 and parts[2].isdigit():
                if parts[2] not in live_match_ids:
                    live_match_ids.append(parts[2])
    return jsonify({"live_match_ids": live_match_ids})

@app.route('/upcoming')
def get_upcoming():
    soup = get_soup("https://www.cricbuzz.com/cricket-match/live-scores/upcoming-matches")
    upcoming = []
    for link in soup.find_all('a', href=True, title=True):
        if '/live-cricket-scores/' in link['href']:
            time_tag = link.find('span', class_=lambda x: x and 'text-cbPreview' in x)
            upcoming.append({
                "title": link['title'],
                "time": time_tag.text.strip() if time_tag else "Date TBD"
            })
    return jsonify(upcoming[:15])

@app.route('/results')
def get_results():
    soup = get_soup("https://www.cricbuzz.com/cricket-match/live-scores/recent-matches")
    results = []
    for link in soup.find_all('a', href=True, title=True):
        if '/live-cricket-scores/' in link['href']:
            res_tag = link.find('span', class_=lambda x: x and 'text-cbComplete' in x)
            results.append({
                "title": link['title'],
                "result": res_tag.text.strip() if res_tag else "Finished"
            })
    return jsonify(results[:15])

if __name__ == '__main__':
    app.run(debug=True)
