import requests
from bs4 import BeautifulSoup as bs

def check_seo(url: str):
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +https://www.google.com/bot.html)',
        'Connection': 'Keep-alive',
        'Accept-Encoding': 'gzip, deflate'
    }
    
    response = requests.get(url, headers=headers)
    
    soup = bs(response.text, 'html.parser')
    
    head = soup.find('head')
    
    print(head.prettify())

    return

# check_seo("https://reperio.usi.ch/permalink/41SLSP_USI/vo4h9m/alma990001450100205507")
