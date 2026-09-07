import httpx
import re
import json

url = 'https://yandex.com/images/search?rpt=imageview'
with open('data/test_face.jpg', 'rb') as f:
    r = httpx.post(
        url,
        files={'upfile': ('face.jpg', f, 'image/jpeg')},
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        follow_redirects=True,
        timeout=15.0
    )

# Save text to scratch
with open('scratch/yandex_resp.html', 'w', encoding='utf-8') as f:
    f.write(r.text)

# Search for data-state or data-bem or json
matches = re.findall(r'data-state="([^"]+)"', r.text)
print('data-state matches:', len(matches))

bem = re.findall(r'data-bem="([^"]+)"', r.text)
print('data-bem matches:', len(bem))

# Search for cbir-similar or pages with image
# Look for URLs with .html or domains
domains = re.findall(r'https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,6}/[^\s\"\'<>]*', r.text)
ext = [d for d in domains if not any(x in d for x in ['yandex', 'w3.org', 'schema.org'])]
print('External domain links in text:', len(ext))
for x in ext[:10]:
    print('  ->', x)
