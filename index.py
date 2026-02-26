import requests
from bs4 import BeautifulSoup

def get_live_scores():
    # Official Cricinfo RSS Feed for Live Scores
    url = "http://static.cricinfo.com/rss/livescores.xml"
    response = requests.get(url)
    
    # Use 'xml' parser for RSS
    soup = BeautifulSoup(response.content, 'xml')
    items = soup.find_all('item')
    
    live_matches = []
    for item in items:
        live_matches.append({
            "title": item.find('title').text,
            "description": item.find('description').text,
            "link": item.find('link').text
        })
    return live_matches

# Usage
for match in get_live_scores():
    print(f"Match: {match['title']}\nScore: {match['description']}\n")
