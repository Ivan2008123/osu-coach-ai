import urllib.request
import re
import json

url = 'https://osu.ppy.sh/users/tamik228_old_2/osu'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

scripts = re.findall(r'<script id=[\'"]json-([^\'"]+)[\'"][^>]*>(.*?)</script>', html, re.DOTALL)
for name, content in scripts:
    print('Found tag:', name, 'Length:', len(content))
    if 'tamik' in content.lower():
        print('Target user found in:', name)
        try:
            d = json.loads(content)
            if isinstance(d, dict):
                # Save to test.json
                with open(r'C:\Users\iples\Downloads\osu\osu-trainer\profile_cache.json', 'w', encoding='utf-8') as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
                print('Saved sample keys:', list(d.keys())[:10])
        except Exception as e:
            print('JSON error:', e)
