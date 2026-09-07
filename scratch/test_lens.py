import httpx
import re
import json

def test_lens():
    with open('data/test_face.jpg', 'rb') as f:
        r = httpx.post(
            'https://lens.google.com/v3/upload',
            files={'encoded_image': ('face.jpg', f, 'image/jpeg')},
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
            follow_redirects=True,
            timeout=15.0
        )
    print('Final URL:', r.url)
    print('Length:', len(r.text))
    # Look for data-item-title or visual matches or links
    links = re.findall(r'https?://[a-zA-Z0-9_\-\./%?=&+@#~]+', r.text)
    filtered = []
    for link in links:
        if any(bad in link for bad in ['google.', 'gstatic.', 'schema.org', 'w3.org', 'ggpht.', 'googleapis.']):
            continue
        if link not in filtered:
            filtered.append(link)
    print(f'Found {len(filtered)} external links:')
    for l in filtered[:15]:
        print(' -', l)

if __name__ == '__main__':
    test_lens()
