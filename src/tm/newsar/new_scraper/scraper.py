import requests
import asyncio
from bs4 import BeautifulSoup


# url = "https://..."

async def extract_data(url, heading, content):
    headers = {
    }
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    headings = []
    contents = []
    for h in heading:
        headings.extend([i.text for i in soup.find_all(h)])
    for c in content:
        contents.extend([i.text for i in soup.find_all(c)])

    print(f"Headings: {headings}\n - Contents: {contents}")
    return headings, contents

# heading = ['h1']
# content = ['p']
# asyncio.run(extract_data(url, heading, content))