import urllib.request
import re
import html
import json

def fetch_profile(username="tamik228_old_2"):
    url = f"https://osu.ppy.sh/users/{username}/osu"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read().decode('utf-8', errors='ignore')
            
        m = re.search(r'data-initial-data="([^"]+)"', raw)
        if m:
            decoded = html.unescape(m.group(1))
            data = json.loads(decoded)
            user = data.get('user', {})
            stats = user.get('statistics', {})
            return {
                "username": user.get("username", username),
                "avatar_url": user.get("avatar_url"),
                "country_code": user.get("country_code"),
                "global_rank": stats.get("global_rank"),
                "country_rank": stats.get("country_rank"),
                "pp": stats.get("pp"),
                "accuracy": round(stats.get("hit_accuracy", 0), 2),
                "play_count": stats.get("play_count"),
                "play_time_hours": round(stats.get("play_time", 0) / 3600, 1),
                "max_combo": stats.get("maximum_combo"),
                "grade_counts": stats.get("grade_counts", {})
            }
    except Exception as e:
        print("Fetch error:", e)
    return None

if __name__ == "__main__":
    prof = fetch_profile()
    print("SUCCESS RESULT:", json.dumps(prof, indent=2))
