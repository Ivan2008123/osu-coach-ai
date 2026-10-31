from ossapi import Ossapi

OSU_CLIENT_ID = 73273
OSU_CLIENT_SECRET = "YronFT9ppsY72ef26LCZKOM0TawZECEATHYCL39D"

try:
    api = Ossapi(OSU_CLIENT_ID, OSU_CLIENT_SECRET)
except Exception as e:
    api = None
    print("Ossapi init error:", e)

def get_official_profile_data(username="tamik228_old_2"):
    if not api:
        return None
    try:
        user = api.user(username)
        stats = user.statistics
        
        # Получаем топ 5 скоров пользователя (Top Plays)
        best_scores = api.user_scores(user.id, type="best", limit=5)
        top_plays = []
        for s in best_scores:
            top_plays.append({
                "title": s.beatmapset.title,
                "version": s.beatmap.version,
                "stars": round(s.beatmap.difficulty_rating, 2),
                "pp": round(s.pp or 0, 1),
                "acc": round(s.accuracy * 100, 2),
                "rank": str(s.rank.name) if s.rank else "A",
                "cover_url": s.beatmapset.covers.cover_2x or s.beatmapset.covers.card_2x,
                "url": f"https://osu.ppy.sh/beatmaps/{s.beatmap.id}"
            })

        # Получаем недавние игры (Recent Plays)
        recent_scores = api.user_scores(user.id, type="recent", limit=5)
        recent_plays = []
        for s in recent_scores:
            recent_plays.append({
                "title": s.beatmapset.title,
                "version": s.beatmap.version,
                "stars": round(s.beatmap.difficulty_rating, 2),
                "acc": round(s.accuracy * 100, 2),
                "rank": str(s.rank.name) if s.rank else "F",
                "cover_url": s.beatmapset.covers.cover or s.beatmapset.covers.card
            })

        return {
            "username": user.username,
            "avatar_url": user.avatar_url,
            "country_code": user.country_code,
            "global_rank": stats.global_rank,
            "country_rank": stats.country_rank,
            "pp": round(stats.pp, 1),
            "accuracy": round(stats.hit_accuracy, 2),
            "play_count": stats.play_count,
            "play_time_hours": round(stats.play_time / 3600, 1),
            "max_combo": stats.maximum_combo,
            "top_plays": top_plays,
            "recent_plays": recent_plays
        }
    except Exception as e:
        print("API fetch error:", e)
        return None
