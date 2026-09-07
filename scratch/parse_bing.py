import re

with open('scratch/bing_resp.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Look for json blobs or purl / murl / tit / desc
purls = re.findall(r'&quot;purl&quot;:&quot;(https?://[^&]+)&quot;', html)
print('Page URLs (purl):', len(purls))
for p in purls[:15]:
    print('  PURL:', p)

murls = re.findall(r'&quot;murl&quot;:&quot;(https?://[^&]+)&quot;', html)
print('Media URLs (murl):', len(murls))
for m in murls[:5]:
    print('  MURL:', m)

# Also check for data-url, href, or metadata
titles = re.findall(r'&quot;t&quot;:&quot;([^&]+)&quot;', html)
print('Titles:', len(titles))
for t in titles[:5]:
    print('  Title:', t)

# Look for ig= / visual search result containers
matches = re.findall(r'href="(https?://[^"]+)"', html)
external = [l for l in matches if not any(b in l for b in ['bing.com', 'microsoft.com', 'w3.org'])]
print(f'Found {len(external)} external href links:')
for e in external[:15]:
    print('  Href:', e)
