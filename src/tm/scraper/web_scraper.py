import requests
from bs4 import BeautifulSoup

def get_h3_html(url):
    def extract_headings(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        headings = {}
        for level in range(1, 7):
            tag = f'h{level}'
            headings[tag] = [str(heading.a) for heading in soup.find_all(tag)]
        
        return headings


    headings = extract_headings(url)
    return headings.get('h3', [])