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
    get_id = request.args.get('id')
    live_match_ids = []
    for link in soup.find_all('a', href=True):
        if '/live-cricket-scores/' in link['href']:
            parts = link['href'].split('/')
            if len(parts) >= 3 and parts[2].isdigit():
                if parts[2] not in live_match_ids:
                    live_match_ids.append(parts[2])
    id = escape(get_id)
    if id:
        session_object = requests.Session()
        r = session_object.get(
            'https://www.cricbuzz.com/cricket-match/live-scores' + id, headers=headers)
        soup = bs(r.text, 'html.parser')
        try:
            update = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-100 cb-min-stts cb-text-complete"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-100 cb-min-stts cb-text-complete"}) else 'Match Stats will Update Soon'
            process = soup.find_all(
                "div", attrs={"class": "cb-text-inprogress"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-text-inprogress"}) else 'Match Stats will Update Soon'
            noresult = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-100 cb-font-18 cb-toss-sts cb-text-abandon"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-100 cb-font-18 cb-toss-sts cb-text-abandon"}) else 'Match Stats will Update Soon'
            stumps = soup.find_all(
                "div", attrs={"class": "cb-text-stumps"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-text-stumps"}) else 'Match Stats will Update Soon'
            lunch = soup.find_all(
                "div", attrs={"class": "cb-text-lunch"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-text-lunch"}) else 'Match Stats will Update Soon'
            inningsbreak = soup.find_all(
                "div", attrs={"class": "cb-text-inningsbreak"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-text-inningsbreak"}) else 'Match Stats will Update Soon'
            tea = soup.find_all("div", attrs={"class": "cb-text-tea"})[0].text.strip() if soup.find(
                "div", attrs={"class": "cb-text-tea"}) else 'Match Stats will Update Soon'
            rain_break = soup.find_all("div", attrs={"class": "cb-text-rain"})[0].text.strip(
            ) if soup.find("div", attrs={"class": "cb-text-rain"}) else 'Match Stats will Update Soon'
            wet_outfield = soup.find_all("div", attrs={"class": "cb-text-wetoutfield"})[0].text.strip(
            ) if soup.find("div", attrs={"class": "cb-text-wetoutfield"}) else 'Match Stats will Update Soon'
            match_date_element = soup.find('span', itemprop='startDate')
            if match_date_element:
                match_time = match_date_element.get('content')
                new_dt = match_time.split('+')[0]
                utc_time = datetime.strptime(new_dt, "%Y-%m-%dT%H:%M:%S")
                utc_time_utc = utc_time.replace(tzinfo=pytz.UTC)
                target_timezone = pytz.timezone("Asia/Kolkata")
                local_time = utc_time_utc.astimezone(target_timezone)
                formatted_local_time = local_time.strftime(
                    "Date: %Y-%m-%d - Time: %I:%M:%S %p (Indian Local Time)")
                match_date = formatted_local_time
            else:
                match_date = 'Match Stats will Update Soon'
            live_score = soup.find(
                "span", attrs={"class": "cb-font-20 text-bold"}).text.strip() if soup.find("span", attrs={"class": "cb-font-20 text-bold"}) else 'Data Not Found'
            title = soup.find(
                "h1", attrs={"class": "cb-nav-hdr cb-font-18 line-ht24"}).text.strip().replace(", Commentary", "") if soup.find("h1", attrs={"class": "cb-nav-hdr cb-font-18 line-ht24"}) else 'Data Not Found'
            run_rate = soup.find_all(
                "span", attrs={"class": "cb-font-12 cb-text-gray"})[0].text.strip().replace("CRR:\u00a0", "") if soup.find_all("span", attrs={"class": "cb-font-12 cb-text-gray"}) else 'Data Not Found'
            batter_one = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-50"})[1].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-50"}) else 'Data Not Found'
            batter_two = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-50"})[2].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-50"}) else 'Data Not Found'
            batter_one_run = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-10 ab text-right"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-10 ab text-right"}) else 'Data Not Found'
            batter_two_run = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-10 ab text-right"})[2].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-10 ab text-right"}) else 'Data Not Found'
            batter_one_ball = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-10 ab text-right"})[1].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-10 ab text-right"}) else 'Data Not Found'
            batter_two_ball = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-10 ab text-right"})[3].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-10 ab text-right"}) else 'Data Not Found'
            batter_one_sr = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-14 ab text-right"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-14 ab text-right"}) else 'Data Not Found'
            batter_two_sr = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-14 ab text-right"})[1].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-14 ab text-right"}) else 'Data Not Found'
            bowler_one = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-50"})[4].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-50"}) else 'Data Not Found'
            bowler_two = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-50"})[5].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-50"}) else 'Data Not Found'
            bowler_one_over = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-10 text-right"})[4].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-10 text-right"}) else 'Data Not Found'
            bowler_two_over = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-10 text-right"})[6].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-10 text-right"}) else 'Data Not Found'
            bowler_one_run = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-10 text-right"})[5].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-10 text-right"}) else 'Data Not Found'
            bowler_two_run = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-10 text-right"})[7].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-10 text-right"}) else 'Data Not Found'
            bowler_one_eco = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-14 text-right"})[2].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-10 ab text-right"}) else 'Data Not Found'
            bowler_two_eco = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-14 text-right"})[3].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-10 ab text-right"}) else 'Data Not Found'
            bowler_one_wicket = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-8 text-right"})[5].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-8 text-right"}) else 'Data Not Found'
            bowler_two_wicket = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-8 text-right"})[7].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-8 text-right"}) else 'Data Not Found'
        except IndexError:
            update = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-100 cb-min-stts cb-text-complete"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-100 cb-min-stts cb-text-complete"}) else 'Match Stats will Update Soon'
            process = soup.find_all(
                "div", attrs={"class": "cb-text-inprogress"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-text-inprogress"}) else 'Match Stats will Update Soon'
            noresult = soup.find_all(
                "div", attrs={"class": "cb-col cb-col-100 cb-font-18 cb-toss-sts cb-text-abandon"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-col cb-col-100 cb-font-18 cb-toss-sts cb-text-abandon"}) else 'Match Stats will Update Soon'
            stumps = soup.find_all(
                "div", attrs={"class": "cb-text-stumps"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-text-stumps"}) else 'Match Stats will Update Soon'
            lunch = soup.find_all(
                "div", attrs={"class": "cb-text-lunch"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-text-lunch"}) else 'Match Stats will Update Soon'
            inningsbreak = soup.find_all(
                "div", attrs={"class": "cb-text-inningsbreak"})[0].text.strip() if soup.find_all("div", attrs={"class": "cb-text-inningsbreak"}) else 'Match Stats will Update Soon'
            tea = soup.find_all("div", attrs={"class": "cb-text-tea"})[0].text.strip() if soup.find(
                "div", attrs={"class": "cb-text-tea"}) else 'Match Stats will Update Soon'
            rain_break = soup.find_all("div", attrs={"class": "cb-text-rain"})[0].text.strip(
            ) if soup.find("div", attrs={"class": "cb-text-rain"}) else 'Match Stats will Update Soon'
            wet_outfield = soup.find_all("div", attrs={"class": "cb-text-wetoutfield"})[0].text.strip(
            ) if soup.find("div", attrs={"class": "cb-text-wetoutfield"}) else 'Match Stats will Update Soon'
            match_date_element = soup.find('span', itemprop='startDate')
            if match_date_element:
                match_time = match_date_element.get('content')
                new_dt = match_time.split('+')[0]
                utc_time = datetime.strptime(new_dt, "%Y-%m-%dT%H:%M:%S")
                utc_time_utc = utc_time.replace(tzinfo=pytz.UTC)
                target_timezone = pytz.timezone("Asia/Kolkata")
                local_time = utc_time_utc.astimezone(target_timezone)
                formatted_local_time = local_time.strftime(
                    "Date: %Y-%m-%d - Time: %I:%M:%S %p (Indian Local Time)")
                match_date = formatted_local_time
            else:
                match_date = 'Match Stats will Update Soon'
            live_score = soup.find(
                "span", attrs={"class": "cb-font-20 text-bold"}).text.strip() if soup.find("span", attrs={"class": "cb-font-20 text-bold"}) else 'Data Not Found'
            title = soup.find(
                "h1", attrs={"class": "cb-nav-hdr cb-font-18 line-ht24"}).text.strip().replace(", Commentary", "") if soup.find("h1", attrs={"class": "cb-nav-hdr cb-font-18 line-ht24"}) else 'Data Not Found'
            run_rate = 'Match Stats will Update Soon'
            batter_one = 'Match Stats will Update Soon'
            batter_two = 'Match Stats will Update Soon'
            batter_one_run = 'Match Stats will Update Soon'
            batter_two_run = 'Match Stats will Update Soon'
            batter_one_ball = 'Match Stats will Update Soon'
            batter_two_ball = 'Match Stats will Update Soon'
            batter_one_sr = 'Match Stats will Update Soon'
            batter_two_sr = 'Match Stats will Update Soon'
            bowler_one = 'Match Stats will Update Soon'
            bowler_two = 'Match Stats will Update Soon'
            bowler_one_over = 'Match Stats will Update Soon'
            bowler_two_over = 'Match Stats will Update Soon'
            bowler_one_run = 'Match Stats will Update Soon'
            bowler_two_run = 'Match Stats will Update Soon'
            bowler_one_eco = 'Match Stats will Update Soon'
            bowler_two_eco = 'Match Stats will Update Soon'
            bowler_one_wicket = 'Match Stats will Update Soon'
            bowler_two_wicket = 'Match Stats will Update Soon'
        if (update != 'Match Stats will Update Soon'):
            status = update
        elif (process != 'Match Stats will Update Soon'):
            status = process
        elif (noresult != 'Match Stats will Update Soon'):
            status = noresult
        elif (stumps != 'Match Stats will Update Soon'):
            status = stumps
        elif (lunch != 'Match Stats will Update Soon'):
            status = lunch
        elif (inningsbreak != 'Match Stats will Update Soon'):
            status = inningsbreak
        elif (tea != 'Match Stats will Update Soon'):
            status = tea
        elif (rain_break != 'Match Stats will Update Soon'):
            status = rain_break
        elif (wet_outfield != 'Match Stats will Update Soon'):
            status = wet_outfield
        elif (match_date != 'Match Stats will Update Soon'):
            status = match_date
        else:
            status = 'Match Stats will Update Soon...'
        return jsonify({
            "success": 'true',
             "live_match_ids": live_match_ids},
            "livescore": {
                'title': title,
                'update': status,
                'current': live_score,
                'runrate': 'CRR: ' + run_rate,
                'batsman': batter_one,
                'batsmanrun': batter_one_run,
                'ballsfaced': '(' + batter_one_ball + ')',
                'sr': batter_one_sr,
                'batsmantwo': batter_two,
                'batsmantworun': batter_two_run,
                'batsmantwoballfaced':  '(' + batter_two_ball + ')',
                'batsmantwosr': batter_two_sr,
                'bowler': bowler_one,
                "bowlerover": bowler_one_over,
                "bowlerruns": bowler_one_run,
                "bowlerwickets": bowler_one_wicket,
                "bowlereconomy": bowler_one_eco,
                'bowlertwo': bowler_two,
                "bowlertwoover": bowler_two_over,
                "bowlertworuns": bowler_two_run,
                "bowlertwowickets": bowler_two_wicket,
                "bowlertwoeconomy": bowler_two_eco
            }

        })
    else:
        return jsonify({
            "success": 'true',
            "live_match_ids": live_match_ids},
            "livescore": {
                'title': 'Data not Found',
                'update': 'Data not Found',
                'current': 'Data not Found',
                'runrate': 'Data not Found',
                'batsman': 'Data not Found',
                'batsmanrun': 'Data not Found',
                'ballsfaced': 'Data not Found',
                'sr': 'Data not Found',
                'batsmantwo': 'Data not Found',
                'batsmantworun': 'Data not Found',
                'batsmantwoballfaced': 'Data not Found',
                'batsmantwosr': 'Data not Found',
                'bowler': 'Data not Found',
                "bowlerover": 'Data not Found',
                "bowlerruns": 'Data not Found',
                "bowlerwickets": 'Data not Found',
                "bowlereconomy": 'Data not Found',
                'bowlertwo': 'Data not Found',
                "bowlertwoover": 'Data not Found',
                "bowlertworuns": 'Data not Found',
                "bowlertwowickets": 'Data not Found',
                "bowlertwoeconomy": 'Data not Found'
            }

        })

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
