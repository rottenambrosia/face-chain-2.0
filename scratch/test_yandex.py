import httpx
import re
from bs4 import BeautifulSoup

url = 'https://yandex.com/images/search?rpt=imageview'
with open('data/test_face.jpg', 'rb') as f:
    r = httpx.post(
        url,
        files={'upfile': ('face.jpg', f, 'image/jpeg')},
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        },
        follow_redirects=True,
        timeout=15.0
    )

print('Yandex URL:', r.url)
print('Yandex text length:', len(r.text))

soup = BeautifulSoup(r.text, 'html.parser')
# Find visual match links
tags = soup.find_all('a', href=True)
links = [t['href'] for t in tags if t['href'].startswith('http')]
print(f'Total http links found: {len(links)}')
external = [l for l in links if not any(b in l for b in ['yandex.', 'ya.ru'])]
print(f'External links: {len(external)}')
for e in external[:15]:
    print(' -', e)
