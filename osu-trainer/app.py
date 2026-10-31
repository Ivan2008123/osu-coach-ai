import os
import glob
import json
import webbrowser
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import osrparse
from osu_api_client import get_official_profile_data
from vault_sync import sync_score_to_vault

app = FastAPI(title="osu! Personal Coach")

OSU_FILES_DIR = r"C:\Users\iples\AppData\Roaming\osu\files"
EXPORTS_DIR = r"C:\Users\iples\AppData\Roaming\osu\exports"

CURATED_MAP_PACKS = [
    {
        "id": "acc-control-1",
        "title": "Укрощение паники (Ритм и Early-Fix)",
        "stars": "3.9★ – 4.3★",
        "bpm": "160 - 175 BPM",
        "focus": "Accuracy / Early tap correction",
        "badge": "Ритм-база",
        "description": "Золотая классика osu! с выраженным битом. Заставляет слушать музыку и выбивать стабильные 97%+ вместо панических кликов.",
        "maps": [
            {
                "title": "KANA-BOON - Silhouette",
                "mapper": "Kagetsu",
                "diff": "pkhg's Insane (4.21★)",
                "link": "https://osu.ppy.sh/beatmapsets/399358#osu/896855"
            },
            {
                "title": "ClariS - Hitorigoto -TV MIX-",
                "mapper": "Doormat",
                "diff": "Insane (4.26★)",
                "link": "https://osu.ppy.sh/beatmapsets/596704#osu/1264070"
            },
            {
                "title": "Kira Kira Days",
                "mapper": "Kagetsu",
                "diff": "pkhg's Insane!! (4.08★)",
                "link": "https://osu.ppy.sh/beatmapsets/444335#osu/961692"
            },
            {
                "title": "Harumachi Clover (Swing)",
                "mapper": "Sotarks",
                "diff": "NiNo's Insane (4.27★)",
                "link": "https://osu.ppy.sh/beatmapsets/842412#osu/1762730"
            }
        ]
    },
    {
        "id": "mouse-aim-jump",
        "title": "Легендарный Джамп-Аим (Snap & Micro-Aim)",
        "stars": "4.4★ – 4.7★",
        "bpm": "175 - 190 BPM",
        "focus": "Mouse precision / Snap jumping",
        "badge": "Аим мыши",
        "description": "Карты для постановки мышиного аима. Четкий угол и понятные джампы без мусорных слайдеров.",
        "maps": [
            {
                "title": "Black Rover (TV Size)",
                "mapper": "Sotarks",
                "diff": "NiNo's Insane (4.45★)",
                "link": "https://osu.ppy.sh/beatmapsets/781509#osu/1645699"
            },
            {
                "title": "Daidai Genome",
                "mapper": "Lust",
                "diff": "Insane (4.43★)",
                "link": "https://osu.ppy.sh/beatmapsets/221954#osu/519080"
            },
            {
                "title": "Reol - No title",
                "mapper": "VINXIS",
                "diff": "toybot's Insane (4.71★)",
                "link": "https://osu.ppy.sh/beatmapsets/320118#osu/715074"
            },
            {
                "title": "Kyouran Hey Kids!!",
                "mapper": "monstrata",
                "diff": "Insane (4.55★)",
                "link": "https://osu.ppy.sh/beatmapsets/372510#osu/819944"
            }
        ]
    },
    {
        "id": "stamina-bursts",
        "title": "Берсты и Стамина (Finger Control & Alternate)",
        "stars": "4.5★ – 4.9★",
        "bpm": "175 - 195 BPM",
        "focus": "Stamina / 5-note bursts / Alternate",
        "badge": "Стамина",
        "description": "Очереди по 3 и 5 нот. Развивают второй палец и плавность без перенапряжения кисти.",
        "maps": [
            {
                "title": "LiSA - ADAMAS (TV Size)",
                "mapper": "Sotarks",
                "diff": "NiNo's iNSANE (4.84★)",
                "link": "https://osu.ppy.sh/beatmapsets/859718#osu/1796421"
            },
            {
                "title": "KANA-BOON - Baton Road",
                "mapper": "Gero",
                "diff": "-HARUTO'S INSANE- (4.71★)",
                "link": "https://osu.ppy.sh/beatmapsets/609700#osu/1289982"
            },
            {
                "title": "Chikatto Chika Chika",
                "mapper": "Lami",
                "diff": "Little's Insane (4.57★)",
                "link": "https://osu.ppy.sh/beatmapsets/921889#osu/1936122"
            },
            {
                "title": "Make a Move (Speed Up)",
                "mapper": "Sotarks",
                "diff": "NiNo's Insane (4.73★)",
                "link": "https://osu.ppy.sh/beatmapsets/765778#osu/1614054"
            }
        ]
    },
    {
        "id": "push-5star",
        "title": "Штурм 5★ (Твой рубеж на 90%+ pass)",
        "stars": "5.0★ – 5.3★",
        "bpm": "180 - 200 BPM",
        "focus": "High speed / Fast reading / 90%+ pass",
        "badge": "Штурм 5★",
        "description": "Легендарные хиты с рейтингом 5★. Оптимальная плотность и высокая читаемость для первого чистого пасса.",
        "maps": [
            {
                "title": "RADWIMPS - Zen Zen Zense",
                "mapper": "Monstrata",
                "diff": "Haruto's Insane (5.02★)",
                "link": "https://osu.ppy.sh/beatmapsets/513590#osu/1093507"
            },
            {
                "title": "Reol - No title",
                "mapper": "VINXIS",
                "diff": "Insane (5.10★)",
                "link": "https://osu.ppy.sh/beatmapsets/320118#osu/712376"
            },
            {
                "title": "Black Rover (TV Size)",
                "mapper": "Sotarks",
                "diff": "Nevo's Expert (5.22★)",
                "link": "https://osu.ppy.sh/beatmapsets/781509#osu/1645698"
            },
            {
                "title": "KANA-BOON - Baton Road",
                "mapper": "Gero",
                "diff": "-BOR'S INSANE- (5.05★)",
                "link": "https://osu.ppy.sh/beatmapsets/609700#osu/1288559"
            }
        ]
    }
]

def get_recent_replays():
    replays = []
    if os.path.exists(EXPORTS_DIR):
        for f in glob.glob(os.path.join(EXPORTS_DIR, "*.osr")):
            try:
                mtime = os.path.getmtime(f)
                replays.append({
                    "id": f,
                    "path": f,
                    "name": f"Экспорт: {os.path.basename(f)[:38]}...",
                    "mtime": mtime,
                    "date": datetime.fromtimestamp(mtime).strftime("%H:%M:%S (%d.%m)")
                })
            except:
                pass

    cutoff = datetime.now() - timedelta(days=7)
    if os.path.exists(OSU_FILES_DIR):
        for root, dirs, fnames in os.walk(OSU_FILES_DIR):
            for f in fnames:
                p = os.path.join(root, f)
                try:
                    sz = os.path.getsize(p)
                    if 1500 < sz < 25000000:
                        mtime = os.path.getmtime(p)
                        if datetime.fromtimestamp(mtime) > cutoff:
                            with open(p, "rb") as fp:
                                head = fp.read(1)
                                if head in [b'\x00', b'\x01', b'\x02', b'\x03']:
                                    r = osrparse.Replay.from_path(p)
                                    replays.append({
                                        "id": p,
                                        "path": p,
                                        "name": f"Скор {r.score:,} • {r.count_300}x300 • {r.count_100}x100 • {r.count_miss}M",
                                        "mtime": mtime,
                                        "date": datetime.fromtimestamp(mtime).strftime("%H:%M:%S (%d.%m)")
                                    })
                except:
                    continue

    replays.sort(key=lambda x: x["mtime"], reverse=True)
    return replays

def analyze_replay(file_path):
    try:
        replay = osrparse.Replay.from_path(file_path)
    except Exception as e:
        return {"error": f"Ошибка парсинга реплея: {str(e)}"}

    total_hits = replay.count_300 + replay.count_100 + replay.count_50 + replay.count_miss
    acc = (replay.count_300 * 300 + replay.count_100 * 100 + replay.count_50 * 50) / (total_hits * 300) * 100 if total_hits > 0 else 0.0

    current_time = 0
    k1_presses = []
    k2_presses = []
    prev_keys = 0

    aim_speeds = []
    prev_x, prev_y = None, None

    for ev in replay.replay_data:
        current_time += ev.time_delta
        keys = int(ev.keys)
        k1_now = bool(keys & 1 or keys & 4)
        k2_now = bool(keys & 2 or keys & 8)
        k1_prev = bool(prev_keys & 1 or prev_keys & 4)
        k2_prev = bool(prev_keys & 2 or prev_keys & 8)

        if k1_now and not k1_prev:
            k1_presses.append(current_time)
        if k2_now and not k2_prev:
            k2_presses.append(current_time)

        if prev_x is not None and prev_y is not None:
            dist = ((ev.x - prev_x)**2 + (ev.y - prev_y)**2)**0.5
            if 0 < ev.time_delta < 50:
                speed = dist / ev.time_delta
                aim_speeds.append(speed)

        prev_x, prev_y = ev.x, ev.y
        prev_keys = keys

    total_presses = len(k1_presses) + len(k2_presses)
    k1_ratio = (len(k1_presses) / total_presses * 100) if total_presses > 0 else 50
    k2_ratio = (len(k2_presses) / total_presses * 100) if total_presses > 0 else 50

    acc_score = max(0, min(100, (acc - 70) * 3.33))
    aim_score = max(20, min(100, 100 - (replay.count_miss * 8)))
    balance_delta = abs(k1_ratio - k2_ratio)
    stamina_score = max(25, min(100, int(100 - balance_delta * 1.2)))
    consistency_score = max(15, min(100, int(acc * 0.7 + (100 - replay.count_miss * 10) * 0.3)))

    target_5star_readiness = int(acc_score * 0.45 + aim_score * 0.35 + stamina_score * 0.20)
    target_5star_readiness = max(10, min(99, target_5star_readiness))

    current_pp_estimate = int(replay.score / 9500) if replay.score else 0
    potential_pp_gain = int(current_pp_estimate * (1.35 if acc < 90 else 1.15))

    if acc < 91:
        recommended_pack = CURATED_MAP_PACKS[0]
        focus_title = "Лечение раннего нажатия (Early Tap) & Ритм"
    elif balance_delta > 40:
        recommended_pack = CURATED_MAP_PACKS[2]
        focus_title = "Прокачка второго пальца (Стамина & Альтернейт)"
    elif replay.count_miss > 4:
        recommended_pack = CURATED_MAP_PACKS[1]
        focus_title = "Точность довода мыши (Mouse Snap Aim)"
    else:
        recommended_pack = CURATED_MAP_PACKS[3]
        focus_title = "Штурм 5★ рубежа (Push 5 Stars)"

    coach_feedbacks = []
    if acc < 92:
        coach_feedbacks.append({
            "badge": "Ритм",
            "type": "danger",
            "title": f"Потеряно {replay.count_100 + replay.count_50} нот на ранних нажатиях",
            "text": "Ты видишь сближающийся круг подхода и инстинктивно жмешь кнопку раньше реального удара в треке. В osu! звук важнее картинки: играй ушами, заставляй себя слышать удар бочки/снейра."
        })
    else:
        coach_feedbacks.append({
            "badge": "Тайминг",
            "type": "success",
            "title": "Хорошая привязка к ритму",
            "text": "Тайминг попадания стабильный. Мышечная память готова к более высоким плотностям нот."
        })

    if balance_delta > 35:
        coach_feedbacks.append({
            "badge": "Пальцы",
            "type": "warning",
            "title": f"Один палец делает {max(k1_ratio, k2_ratio):.0f}% всей работы",
            "text": "Когда ты выйдешь на карты 5★, там начнутся стримы и берсты. Если жать одним пальцем, кисть зажимается, возникает 'finger lock', а комбо мгновенно слетает. Тебе жизненно необходимо подключать второй палец."
        })
    else:
        coach_feedbacks.append({
            "badge": "Баланс",
            "type": "success",
            "title": "Отличное распределение нагрузки",
            "text": "Оба пальца задействованы гармонично, что снижает риск туннельного синдрома и сохраняет выносливость."
        })

    if replay.count_miss == 0:
        coach_feedbacks.append({
            "badge": "Аим",
            "type": "success",
            "title": "Идеальный контроль курсора (0 Miss)",
            "text": "Ты ни разу не промахнулся мимо ноты. Мышь останавливается в нужных координатах без дрожания."
        })
    else:
        coach_feedbacks.append({
            "badge": "Аим",
            "type": "danger",
            "title": f"{replay.count_miss} промахов на карте",
            "text": "Промахи вызваны недоводом курсора (under-aim) на переходе между паттернами. Попробуй чуть-чуть снизить чувствительность мыши или играть более плавными движениями."
        })

    res = {
        "filename": os.path.basename(file_path),
        "username": replay.username,
        "score": f"{replay.score:,}",
        "max_combo": replay.max_combo,
        "count_300": replay.count_300,
        "count_100": replay.count_100,
        "count_50": replay.count_50,
        "count_miss": replay.count_miss,
        "accuracy": round(acc, 2),
        "k1_presses": len(k1_presses),
        "k2_presses": len(k2_presses),
        "k1_ratio": round(k1_ratio, 1),
        "k2_ratio": round(k2_ratio, 1),
        "skills": {
            "accuracy": int(acc_score),
            "aim": int(aim_score),
            "stamina": int(stamina_score),
            "consistency": int(consistency_score)
        },
        "target_5star_readiness": target_5star_readiness,
        "potential_pp_gain": potential_pp_gain,
        "focus_title": focus_title,
        "recommended_pack": recommended_pack,
        "feedbacks": coach_feedbacks,
        "time": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%H:%M:%S (%d.%m.%Y)")
    }
    
    sync_score_to_vault(res)
    return res

@app.get("/api/replays")
def api_replays():
    return {"replays": get_recent_replays()[:20]}

@app.get("/api/profile")
def api_profile():
    prof = get_official_profile_data("tamik228_old_2")
    if not prof:
        return {"error": "Не удалось загрузить данные через osu! API v2"}
    return prof

@app.get("/api/analyze")
def api_analyze(id: str = ""):
    replays = get_recent_replays()
    if not replays:
        return {"error": "Реплеи не найдены. Сыграй карту в osu!lazer!"}
    
    target_path = replays[0]["path"]
    if id:
        for r in replays:
            if r["id"] == id or r["path"] == id:
                target_path = r["path"]
                break
    return analyze_replay(target_path)

@app.get("/api/packs")
def api_packs():
    return {"packs": CURATED_MAP_PACKS}

@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>osu! Coach AI • CyberHUD Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700;800&family=Syne:wght@700;800;900&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-base: #07080f;
            --card-glass: rgba(18, 20, 36, 0.72);
            --card-border: rgba(255, 255, 255, 0.08);
            --neon-pink: #ff1361;
            --neon-cyan: #00fff2;
            --neon-purple: #9d00ff;
            --neon-green: #00ff88;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg-base);
            color: var(--text-main);
            font-family: 'Outfit', sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        /* Live Canvas Background with dynamic interactive particles */
        #bgCanvas {
            position: fixed;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            z-index: 0;
            pointer-events: none;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 32px 24px;
            position: relative;
            z-index: 1;
        }

        /* Glass Cards with Neon Glow & Shimmer */
        .cyber-card {
            background: var(--card-glass);
            backdrop-filter: blur(28px) saturate(190%);
            -webkit-backdrop-filter: blur(28px) saturate(190%);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .cyber-card::before {
            content: '';
            position: absolute;
            top: 0; left: -100%; width: 200%; height: 1.5px;
            background: linear-gradient(90deg, transparent, rgba(255, 19, 97, 0.8), rgba(0, 255, 242, 0.8), transparent);
            animation: cardShimmer 6s infinite linear;
        }

        @keyframes cardShimmer {
            0% { transform: translateX(0); }
            100% { transform: translateX(50%); }
        }

        /* Hero Banner */
        .hero-banner {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 24px 32px;
            margin-bottom: 24px;
            border-color: rgba(255, 19, 97, 0.25);
            box-shadow: 0 0 35px rgba(255, 19, 97, 0.15);
        }

        .user-block { display: flex; align-items: center; gap: 20px; }

        .avatar-wrap {
            position: relative;
            width: 72px; height: 72px;
        }

        .user-avatar {
            width: 100%; height: 100%;
            border-radius: 20px;
            object-fit: cover;
            border: 2px solid var(--neon-pink);
            box-shadow: 0 0 25px rgba(255, 19, 97, 0.6);
        }

        .user-titles h1 {
            font-family: 'Syne', sans-serif;
            font-size: 26px; font-weight: 800;
            display: flex; align-items: center; gap: 12px;
        }

        .badge-live {
            background: rgba(0, 255, 136, 0.12);
            border: 1px solid var(--neon-green);
            color: var(--neon-green);
            font-size: 11px; font-weight: 800;
            padding: 4px 12px; border-radius: 99px;
            text-transform: uppercase;
            box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
            letter-spacing: 0.5px;
        }

        .user-ranks {
            font-size: 14px; color: #94a3b8; margin-top: 4px;
        }
        .user-ranks b { color: #fff; font-family: 'JetBrains Mono', monospace; font-size: 15px; }

        .hero-telemetry {
            display: flex; gap: 36px;
        }

        .t-item { text-align: right; }
        .t-val {
            font-size: 26px; font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            background: linear-gradient(135deg, #fff, #cbd5e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .t-lbl {
            font-size: 11px; font-weight: 700;
            text-transform: uppercase; color: #64748b;
            letter-spacing: 0.8px; margin-top: 2px;
        }

        /* 5-STAR READINESS GAUGE STRIP */
        .readiness-strip {
            background: linear-gradient(135deg, rgba(157, 0, 255, 0.15), rgba(255, 19, 97, 0.15));
            border: 1px solid rgba(157, 0, 255, 0.4);
            border-radius: 22px;
            padding: 22px 30px;
            margin-bottom: 28px;
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 28px;
            align-items: center;
            box-shadow: 0 0 35px rgba(157, 0, 255, 0.2);
        }

        .gauge-title {
            font-size: 18px; font-weight: 800;
            font-family: 'Syne', sans-serif;
            display: flex; align-items: center; gap: 10px;
        }

        .gauge-track {
            height: 12px; width: 100%;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 99px;
            margin-top: 10px;
            overflow: hidden;
        }

        .gauge-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--neon-pink), var(--neon-purple), var(--neon-cyan));
            border-radius: 99px;
            width: 0%;
            transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
            box-shadow: 0 0 20px var(--neon-cyan);
        }

        .gauge-desc {
            font-size: 13px; color: #cbd5e1; margin-top: 8px;
        }

        .stat-box {
            text-align: center;
            padding: 12px 18px;
            background: rgba(0, 0, 0, 0.35);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }
        .sb-val {
            font-size: 26px; font-weight: 900;
            font-family: 'JetBrains Mono', monospace;
            color: var(--neon-cyan);
            text-shadow: 0 0 15px rgba(0, 255, 242, 0.5);
        }
        .sb-lbl { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin-top: 2px; }

        /* Top Plays */
        .top-plays-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 28px;
        }

        .top-play-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 14px 16px;
            display: flex; align-items: center; gap: 14px;
            text-decoration: none; color: inherit;
            transition: all 0.25s ease;
        }

        .top-play-card:hover {
            transform: translateY(-4px);
            border-color: var(--neon-cyan);
            box-shadow: 0 10px 30px rgba(0, 255, 242, 0.25);
            background: rgba(255, 255, 255, 0.05);
        }

        .tp-thumb {
            width: 52px; height: 52px;
            border-radius: 12px; object-fit: cover;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .tp-info h5 {
            font-size: 14px; font-weight: 700;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
            max-width: 250px;
        }
        .tp-info p { font-size: 12px; color: #94a3b8; margin-top: 2px; }
        .tp-pp {
            margin-left: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 17px; font-weight: 800;
            color: var(--neon-cyan);
        }

        /* Core Grid */
        .core-grid {
            display: grid;
            grid-template-columns: 1fr 430px;
            gap: 28px;
        }

        .panel-pad { padding: 28px; margin-bottom: 24px; }

        .panel-head {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 22px;
        }

        .panel-title {
            font-size: 20px; font-weight: 800;
            font-family: 'Syne', sans-serif;
            display: flex; align-items: center; gap: 10px;
        }

        .focus-pill {
            background: linear-gradient(135deg, rgba(255, 19, 97, 0.2), rgba(157, 0, 255, 0.2));
            border: 1px solid var(--neon-pink);
            color: var(--neon-pink);
            font-size: 11px; font-weight: 800;
            padding: 5px 14px; border-radius: 99px;
            text-transform: uppercase;
            box-shadow: 0 0 15px rgba(255, 19, 97, 0.35);
        }

        /* Metric Tiles */
        .metric-tiles {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 24px;
        }

        .tile {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 18px 14px;
            text-align: center;
            transition: 0.2s ease;
        }
        .tile:hover {
            border-color: rgba(255, 255, 255, 0.15);
            background: rgba(255, 255, 255, 0.04);
        }

        .tile-val {
            font-size: 32px; font-weight: 900;
            font-family: 'JetBrains Mono', monospace;
            margin-top: 4px;
        }
        .tile-lbl {
            font-size: 11px; font-weight: 700;
            text-transform: uppercase; color: #64748b;
            letter-spacing: 0.7px;
        }

        .acc-green { color: var(--neon-green); text-shadow: 0 0 20px rgba(0, 255, 136, 0.4); }
        .acc-yellow { color: #f59e0b; text-shadow: 0 0 20px rgba(245, 158, 11, 0.4); }
        .acc-red { color: var(--neon-pink); text-shadow: 0 0 20px rgba(255, 19, 97, 0.4); }

        /* Skill Matrix */
        .skill-matrix {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 24px;
        }

        .skill-box {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 14px;
            padding: 14px 18px;
        }

        .skill-head {
            display: flex; justify-content: space-between;
            font-size: 13.5px; font-weight: 600; margin-bottom: 8px;
        }

        .skill-track {
            height: 8px; width: 100%;
            background: rgba(255, 255, 255, 0.06);
            border-radius: 99px; overflow: hidden;
        }

        .skill-fill {
            height: 100%; border-radius: 99px;
            transition: width 1s ease;
        }

        .sf-acc { background: linear-gradient(90deg, #00ff88, #00fff2); box-shadow: 0 0 10px #00fff2; }
        .sf-aim { background: linear-gradient(90deg, #ff1361, #ff80bf); box-shadow: 0 0 10px #ff1361; }
        .sf-stam { background: linear-gradient(90deg, #9d00ff, #d946ef); box-shadow: 0 0 10px #9d00ff; }
        .sf-cons { background: linear-gradient(90deg, #f59e0b, #fbbf24); box-shadow: 0 0 10px #f59e0b; }

        /* Feedbacks */
        .feedback-item {
            display: flex; gap: 16px;
            padding: 16px 20px; border-radius: 16px;
            margin-bottom: 12px;
            border-left: 4px solid;
            background: rgba(255, 255, 255, 0.02);
        }

        .fb-danger { border-color: var(--neon-pink); background: rgba(255, 19, 97, 0.06); }
        .fb-warning { border-color: #f59e0b; background: rgba(245, 158, 11, 0.06); }
        .fb-success { border-color: var(--neon-green); background: rgba(0, 255, 136, 0.06); }

        .fb-badge {
            align-self: flex-start;
            font-size: 10.5px; font-weight: 800;
            padding: 3px 10px; border-radius: 6px;
            text-transform: uppercase;
        }
        .fb-danger .fb-badge { background: var(--neon-pink); color: #fff; }
        .fb-warning .fb-badge { background: #f59e0b; color: #000; }
        .fb-success .fb-badge { background: var(--neon-green); color: #000; }

        .fb-content h4 { font-size: 15px; font-weight: 700; margin-bottom: 3px; }
        .fb-content p { font-size: 13px; color: #94a3b8; line-height: 1.5; }

        /* Right Panel */
        .session-select {
            width: 100%;
            background: #0d0f1a;
            border: 1px solid var(--card-border);
            color: #fff; padding: 13px 16px;
            border-radius: 14px; font-size: 13.5px;
            font-family: inherit; margin-bottom: 14px;
            outline: none; cursor: pointer;
        }

        .btn-sync-neon {
            background: linear-gradient(135deg, var(--neon-pink), var(--neon-purple));
            border: none; color: #fff;
            padding: 14px 20px; border-radius: 14px;
            font-weight: 800; font-size: 14px;
            cursor: pointer; width: 100%;
            box-shadow: 0 0 25px rgba(255, 19, 97, 0.45);
            transition: 0.25s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .btn-sync-neon:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 35px rgba(255, 19, 97, 0.75);
        }

        .pack-item {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 18px; margin-bottom: 16px;
            transition: 0.25s ease;
        }

        .pack-item.active-rec {
            border-color: var(--neon-pink);
            background: rgba(255, 19, 97, 0.05);
            box-shadow: 0 0 30px rgba(255, 19, 97, 0.2);
        }

        .pack-meta-row { display: flex; gap: 8px; margin: 8px 0; }
        .pill-meta {
            background: rgba(255, 255, 255, 0.06);
            padding: 3px 8px; border-radius: 6px;
            font-size: 11px; font-weight: 700; color: #94a3b8;
        }

        .map-dl-link {
            display: flex; justify-content: space-between; align-items: center;
            padding: 11px 14px; border-radius: 12px;
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.04);
            margin-top: 8px; text-decoration: none;
            color: #fff; font-size: 13px;
            transition: 0.2s ease;
        }

        .map-dl-link:hover {
            background: rgba(255, 19, 97, 0.2);
            border-color: rgba(255, 19, 97, 0.5);
            transform: translateX(4px);
        }

        .diff-tag {
            color: var(--neon-cyan);
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px; font-weight: 700;
        }
    </style>
</head>
<body>
    <canvas id="bgCanvas"></canvas>

    <div class="container">
        <!-- Top Hero Profile Banner -->
        <div class="cyber-card hero-banner">
            <div class="user-block">
                <div class="avatar-wrap">
                    <img id="u-avatar" class="user-avatar" src="https://a.ppy.sh/27865640?1777477497.jpeg" alt="Avatar">
                </div>
                <div class="user-titles">
                    <h1>
                        <span id="u-name">tamik228_old_2</span>
                        <span class="badge-live">⚡ osu! API v2 Live</span>
                    </h1>
                    <div class="user-ranks">
                        Рейтинг в мире: <b id="u-rank">#--</b> &nbsp;•&nbsp; Страна: <b id="u-country-rank">#--</b>
                    </div>
                </div>
            </div>
            <div class="hero-telemetry">
                <div class="t-item">
                    <div class="t-val" style="color:var(--neon-cyan);" id="u-pp">-- pp</div>
                    <div class="t-lbl">Performance</div>
                </div>
                <div class="t-item">
                    <div class="t-val" style="color:var(--neon-pink);" id="u-acc">--%</div>
                    <div class="t-lbl">Overall Acc</div>
                </div>
                <div class="t-item">
                    <div class="t-val" id="u-playtime">-- ч</div>
                    <div class="t-lbl">Play Time</div>
                </div>
            </div>
        </div>

        <!-- 5-Star Readiness Gauge -->
        <div class="readiness-strip">
            <div>
                <div class="gauge-title">
                    🎯 Индекс Готовности к 5★ (Target Milestone)
                    <span style="font-size:12px; color:var(--neon-cyan); font-weight:normal;">[Режим: 5★ на 90%+ pass]</span>
                </div>
                <div class="gauge-track">
                    <div class="gauge-fill" id="gauge-bar"></div>
                </div>
                <div class="gauge-desc" id="gauge-desc">
                    Идет расчет готовности мышечной памяти...
                </div>
            </div>
            <div class="stat-box">
                <div class="sb-val" id="gauge-percent">--%</div>
                <div class="sb-lbl">Готовность к 5★</div>
            </div>
            <div class="stat-box">
                <div class="sb-val" style="color:var(--neon-green);" id="potential-pp">+-- pp</div>
                <div class="sb-lbl">Потенциал при 95% Acc</div>
            </div>
        </div>

        <!-- Top Plays -->
        <div style="margin-bottom: 12px; font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase;">
            🏆 Твои Топовые Ссылки (Official Top Plays)
        </div>
        <div class="top-plays-row" id="top-plays-box"></div>

        <!-- Core Grid -->
        <div class="core-grid">
            <!-- Left Column -->
            <div>
                <div class="cyber-card panel-pad">
                    <div class="panel-head">
                        <div class="panel-title">
                            <span id="map-header">Загрузка игры...</span>
                        </div>
                        <div class="focus-pill" id="focus-pill">Фокус: Анализ</div>
                    </div>

                    <!-- 4 Big Tiles -->
                    <div class="metric-tiles">
                        <div class="tile">
                            <div class="tile-lbl">Точность (ACC)</div>
                            <div class="tile-val" id="val-acc">--%</div>
                        </div>
                        <div class="tile">
                            <div class="tile-lbl">300 / 100 / 50</div>
                            <div class="tile-val" style="font-size:20px; color:#c084fc;" id="val-hits">--</div>
                        </div>
                        <div class="tile">
                            <div class="tile-lbl">Промахи (Miss)</div>
                            <div class="tile-val" style="color:var(--neon-pink);" id="val-miss">--</div>
                        </div>
                        <div class="tile">
                            <div class="tile-lbl">Макс комбо</div>
                            <div class="tile-val" style="color:var(--neon-cyan);" id="val-combo">--x</div>
                        </div>
                    </div>

                    <!-- Skill Matrix -->
                    <div style="margin-bottom: 22px;">
                        <div style="font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 10px;">
                            ДНК Игрока (Skill Radar Breakdown)
                        </div>
                        <div class="skill-matrix">
                            <div class="skill-box">
                                <div class="skill-head">
                                    <span>Ритм & Аккураси</span>
                                    <span id="sk-acc-val">--%</span>
                                </div>
                                <div class="skill-track">
                                    <div class="skill-fill sf-acc" id="sk-acc-bar" style="width:0%;"></div>
                                </div>
                            </div>
                            <div class="skill-box">
                                <div class="skill-head">
                                    <span>Аим мыши (Snap & Precision)</span>
                                    <span id="sk-aim-val">--%</span>
                                </div>
                                <div class="skill-track">
                                    <div class="skill-fill sf-aim" id="sk-aim-bar" style="width:0%;"></div>
                                </div>
                            </div>
                            <div class="skill-box">
                                <div class="skill-head">
                                    <span>Баланс пальцев & Стамина</span>
                                    <span id="sk-stam-val">--%</span>
                                </div>
                                <div class="skill-track">
                                    <div class="skill-fill sf-stam" id="sk-stam-bar" style="width:0%;"></div>
                                </div>
                            </div>
                            <div class="skill-box">
                                <div class="skill-head">
                                    <span>Стабильность комбо</span>
                                    <span id="sk-cons-val">--%</span>
                                </div>
                                <div class="skill-track">
                                    <div class="skill-fill sf-cons" id="sk-cons-bar" style="width:0%;"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Charts Row -->
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: center;">
                        <div style="height: 220px;">
                            <canvas id="hitsChart"></canvas>
                        </div>
                        <div style="height: 220px;">
                            <canvas id="fingersChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Feedbacks -->
                <div class="cyber-card panel-pad">
                    <div class="panel-head">
                        <div class="panel-title">🎯 Разбор Тренера: Где кроются ошибки</div>
                    </div>
                    <div id="feedbacks-container"></div>
                </div>
            </div>

            <!-- Right Column -->
            <div>
                <!-- Session Selector -->
                <div class="cyber-card panel-pad">
                    <div class="panel-head">
                        <div class="panel-title">🕹️ Игры из lazer</div>
                    </div>
                    <select id="session-select" class="session-select" onchange="loadScore(this.value)">
                        <option value="">Поиск последних игр...</option>
                    </select>
                    <button class="btn-sync-neon" onclick="init()">⚡ Синхронизировать с lazer</button>
                </div>

                <!-- Verified Map Packs -->
                <div class="cyber-card panel-pad">
                    <div class="panel-head">
                        <div class="panel-title">🗺️ Проверенные Хиты osu!</div>
                    </div>
                    <p style="font-size: 13px; color: #94a3b8; margin-bottom: 16px;">
                        Культовые карты, подобранные нейросетью под твои ошибки:
                    </p>
                    <div id="packs-container"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Interactive Particle Background Canvas Script -->
    <script>
        const canvas = document.getElementById('bgCanvas');
        const ctx = canvas.getContext('2d');
        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;

        window.addEventListener('resize', () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        });

        const particles = [];
        for (let i = 0; i < 48; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.7,
                vy: (Math.random() - 0.5) * 0.7,
                radius: Math.random() * 2.5 + 1.2,
                color: Math.random() > 0.5 ? '#ff1361' : '#00fff2'
            });
        }

        let mouse = { x: null, y: null };
        window.addEventListener('mousemove', (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        });

        function animateBg() {
            ctx.clearRect(0, 0, width, height);
            particles.forEach((p, idx) => {
                p.x += p.vx;
                p.y += p.vy;

                if (p.x < 0) p.x = width;
                if (p.x > width) p.x = 0;
                if (p.y < 0) p.y = height;
                if (p.y > height) p.y = 0;

                if (mouse.x && mouse.y) {
                    const dx = mouse.x - p.x;
                    const dy = mouse.y - p.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 130) {
                        p.x -= dx * 0.025;
                        p.y -= dy * 0.025;
                    }
                }

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.shadowBlur = 12;
                ctx.shadowColor = p.color;
                ctx.fill();

                for (let j = idx + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
                    if (dist < 150) {
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = `rgba(255, 255, 255, ${0.12 - dist / 1500})`;
                        ctx.stroke();
                    }
                }
            });
            requestAnimationFrame(animateBg);
        }
        animateBg();
    </script>

    <!-- App Logic & Charts -->
    <script>
        let hitsChart = null;
        let fingersChart = null;

        async function init() {
            await loadProfileData();
            await loadSessionList();
            const sel = document.getElementById('session-select');
            if (sel.value) {
                await loadScore(sel.value);
            }
        }

        async function loadProfileData() {
            try {
                const res = await fetch('/api/profile');
                const p = await res.json();
                if (p && !p.error) {
                    document.getElementById('u-name').innerText = p.username;
                    if (p.avatar_url) document.getElementById('u-avatar').src = p.avatar_url;
                    document.getElementById('u-rank').innerText = `#${p.global_rank.toLocaleString()}`;
                    document.getElementById('u-country-rank').innerText = `#${p.country_rank.toLocaleString()}`;
                    document.getElementById('u-pp').innerText = `${Math.round(p.pp)} pp`;
                    document.getElementById('u-acc').innerText = `${p.accuracy}%`;
                    document.getElementById('u-playtime').innerText = `${p.play_time_hours} ч`;

                    if (p.top_plays && p.top_plays.length > 0) {
                        const box = document.getElementById('top-plays-box');
                        box.innerHTML = '';
                        p.top_plays.slice(0, 3).forEach(tp => {
                            const a = document.createElement('a');
                            a.className = 'top-play-card';
                            a.href = tp.url;
                            a.target = '_blank';
                            a.innerHTML = `
                                <img class="tp-thumb" src="${tp.cover_url}" alt="Cover">
                                <div class="tp-info">
                                    <h5>${tp.title}</h5>
                                    <p>${tp.version} • ${tp.stars}★ • ${tp.acc}%</p>
                                </div>
                                <div class="tp-pp">${Math.round(tp.pp)}pp</div>
                            `;
                            box.appendChild(a);
                        });
                    }
                }
            } catch (e) {
                console.error(e);
            }
        }

        async function loadSessionList() {
            try {
                const res = await fetch('/api/replays');
                const data = await res.json();
                const sel = document.getElementById('session-select');
                sel.innerHTML = '';
                if (data.replays && data.replays.length > 0) {
                    data.replays.forEach(r => {
                        const opt = document.createElement('option');
                        opt.value = r.id;
                        opt.innerText = `${r.date} • ${r.name}`;
                        sel.appendChild(opt);
                    });
                } else {
                    sel.innerHTML = '<option value="">Нет сыгранных игр</option>';
                }
            } catch (e) {
                console.error(e);
            }
        }

        async function loadScore(id) {
            try {
                const url = id ? `/api/analyze?id=${encodeURIComponent(id)}` : '/api/analyze';
                const res = await fetch(url);
                const data = await res.json();

                if (data.error) {
                    alert(data.error);
                    return;
                }

                document.getElementById('map-header').innerText = `Игра [${data.time}] • Скор: ${data.score}`;
                document.getElementById('focus-pill').innerText = `Фокус: ${data.focus_title}`;

                const accEl = document.getElementById('val-acc');
                accEl.innerText = `${data.accuracy}%`;
                accEl.className = 'tile-val ' + (data.accuracy >= 95 ? 'acc-green' : data.accuracy >= 90 ? 'acc-yellow' : 'acc-red');

                document.getElementById('val-hits').innerText = `${data.count_300} / ${data.count_100} / ${data.count_50}`;
                document.getElementById('val-miss').innerText = data.count_miss;
                document.getElementById('val-combo').innerText = `${data.max_combo}x`;

                setSkill('sk-acc', data.skills.accuracy);
                setSkill('sk-aim', data.skills.aim);
                setSkill('sk-stam', data.skills.stamina);
                setSkill('sk-cons', data.skills.consistency);

                const rVal = data.target_5star_readiness;
                document.getElementById('gauge-bar').style.width = `${rVal}%`;
                document.getElementById('gauge-percent').innerText = `${rVal}%`;
                document.getElementById('potential-pp').innerText = `+${data.potential_pp_gain} pp`;
                
                let desc = "";
                if (rVal < 50) {
                    desc = "⚠️ Текущий контроль нестабилен для 5★. Рекомендуется FC на картах 3.9★ - 4.2★ с точностью 96%+.";
                } else if (rVal < 75) {
                    desc = "⚡ Хорошая база! Ты готов к 4.4★ - 4.7★ джампам. Еще немного контроля над ранними тапами — и 5★ твои!";
                } else {
                    desc = "🔥 Высокая готовность! Мышечная память созрела для стабильного прохождения 5★ на 90%+!";
                }
                document.getElementById('gauge-desc').innerText = desc;

                const fbContainer = document.getElementById('feedbacks-container');
                fbContainer.innerHTML = '';
                data.feedbacks.forEach(fb => {
                    const el = document.createElement('div');
                    el.className = `feedback-item fb-${fb.type}`;
                    el.innerHTML = `
                        <div class="fb-badge">${fb.badge}</div>
                        <div class="fb-content">
                            <h4>${fb.title}</h4>
                            <p>${fb.text}</p>
                        </div>
                    `;
                    fbContainer.appendChild(el);
                });

                renderPacks(data.recommended_pack.id);
                renderCharts(data);

            } catch (e) {
                console.error(e);
            }
        }

        function setSkill(id, val) {
            document.getElementById(`${id}-val`).innerText = `${val}%`;
            document.getElementById(`${id}-bar`).style.width = `${val}%`;
        }

        async function renderPacks(highlightId) {
            const res = await fetch('/api/packs');
            const data = await res.json();
            const container = document.getElementById('packs-container');
            container.innerHTML = '';

            data.packs.forEach(pack => {
                const isRec = pack.id === highlightId;
                const el = document.createElement('div');
                el.className = `pack-item ${isRec ? 'active-rec' : ''}`;
                
                let mapsHtml = '';
                pack.maps.forEach(m => {
                    mapsHtml += `
                        <a href="${m.link}" target="_blank" class="map-dl-link">
                            <div>
                                <span style="font-weight:600;">${m.title}</span>
                                <div style="font-size:11px; color:#94a3b8;">by ${m.mapper}</div>
                            </div>
                            <span class="diff-tag">${m.diff}</span>
                        </a>
                    `;
                });

                el.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="font-size:15px; font-weight:800; font-family:'Syne',sans-serif;">${pack.title}</h4>
                        ${isRec ? '<span class="focus-pill">Тебе сюда!</span>' : ''}
                    </div>
                    <div class="pack-meta-row">
                        <span class="pill-meta">${pack.stars}</span>
                        <span class="pill-meta">${pack.bpm}</span>
                    </div>
                    <p style="font-size:12.5px; color:#94a3b8; margin-bottom:8px;">${pack.description}</p>
                    ${mapsHtml}
                `;
                container.appendChild(el);
            });
        }

        function renderCharts(data) {
            const ctxHits = document.getElementById('hitsChart').getContext('2d');
            const ctxFingers = document.getElementById('fingersChart').getContext('2d');

            if (hitsChart) hitsChart.destroy();
            if (fingersChart) fingersChart.destroy();

            hitsChart = new Chart(ctxHits, {
                type: 'doughnut',
                data: {
                    labels: ['300 Perfect', '100 Early/Late', '50 Off-beat', 'Miss'],
                    datasets: [{
                        data: [data.count_300, data.count_100, data.count_50, data.count_miss],
                        backgroundColor: ['#00ff88', '#f59e0b', '#9d00ff', '#ff1361'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Outfit', size: 11 } } },
                        title: { display: true, text: 'Hit Window Precision', color: '#fff', font: { family: 'Syne', size: 13, weight: 'bold' } }
                    }
                }
            });

            fingersChart = new Chart(ctxFingers, {
                type: 'bar',
                data: {
                    labels: ['Кнопка 1 (K1)', 'Кнопка 2 (K2)'],
                    datasets: [{
                        label: 'Кликов',
                        data: [data.k1_presses, data.k2_presses],
                        backgroundColor: ['#ff1361', '#00fff2'],
                        borderRadius: 12
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        title: { display: true, text: `Finger Ratio (${data.k1_ratio}% / ${data.k2_ratio}%)`, color: '#fff', font: { family: 'Syne', size: 13, weight: 'bold' } }
                    },
                    scales: {
                        x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                        y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                    }
                }
            });
        }

        window.onload = init;
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:8765")
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
