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
from vault_sync import sync_score_to_vault, sync_rhythm_session_to_vault

app = FastAPI(title="osu! Personal Coach AI")

OSU_FILES_DIR = r"C:\Users\iples\AppData\Roaming\osu\files"
EXPORTS_DIR = r"C:\Users\iples\AppData\Roaming\osu\exports"
VAULT_DIR = r"C:\Users\iples\Downloads\osu\osu-vault"

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
        "id": "tablet-aim-jump",
        "title": "Легендарный Джамп-Аим (Snap & Micro-Aim)",
        "stars": "4.4★ – 4.7★",
        "bpm": "175 - 190 BPM",
        "focus": "Tablet precision / Snap jumping",
        "badge": "Аим пера (ГП)",
        "description": "Карты для постановки четкого аима пером на планшете. Четкий угол, фиксация курсора (Snap) и понятные джампы без мусорных слайдеров.",
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
        focus_title = "Точность довода пера (Tablet Snap Aim)"
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
            "title": "Идеальный контроль пера на ГП (0 Miss)",
            "text": "Перо стабильно фиксируется в центре нот без дрожания и срывов. Мышечная память на текущей области планшета работает чисто."
        })
    else:
        coach_feedbacks.append({
            "badge": "Аим",
            "type": "danger",
            "title": f"{replay.count_miss} промахов на карте",
            "text": "Промахи вызваны недоводом пера (under-aim) на размашистых углах. В OpenTabletDriver (OTD) проверь активную область: если она шире 85-90 мм, пальцы могут не дотягиваться до дальних нот без смещения кисти. Также проверь стиль: Drag (ведение по доске) дает стабильный упор трением, а для Hover рекомендуется фильтр сглаживания (Devocub / Reconstructor)."
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

@app.get("/api/vault/notes")
def api_vault_notes():
    notes = []
    if os.path.exists(VAULT_DIR):
        for f in sorted(os.listdir(VAULT_DIR)):
            if f.endswith(".md"):
                fp = os.path.join(VAULT_DIR, f)
                try:
                    mtime = os.path.getmtime(fp)
                    with open(fp, "r", encoding="utf-8") as file:
                        content = file.read()
                    title = f.replace(".md", "")
                    for line in content.strip().split("\n"):
                        if line.startswith("# "):
                            title = line.replace("# ", "").strip()
                            break
                    notes.append({
                        "filename": f,
                        "title": title,
                        "mtime": datetime.fromtimestamp(mtime).strftime("%d.%m.%Y %H:%M"),
                        "content": content
                    })
                except:
                    pass
    return {"notes": notes}

@app.post("/api/vault/save-rhythm")
async def api_save_rhythm(request: Request):
    try:
        data = await request.json()
        success = sync_rhythm_session_to_vault(data)
        return {"status": "ok" if success else "error"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/vault/open")
def api_open_vault():
    try:
        os.system(f'explorer "{VAULT_DIR}"')
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --bg-base: #07080f;
            --card-glass: rgba(18, 20, 36, 0.75);
            --card-border: rgba(255, 255, 255, 0.08);
            --neon-pink: #ff1361;
            --neon-cyan: #00fff2;
            --neon-purple: #9d00ff;
            --neon-green: #00ff88;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-glow: rgba(0, 255, 242, 0.2);
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
            padding: 24px;
            position: relative;
            z-index: 1;
        }

        /* Glass Cards */
        .cyber-card {
            background: var(--card-glass);
            backdrop-filter: blur(28px) saturate(190%);
            -webkit-backdrop-filter: blur(28px) saturate(190%);
            border: 1px solid var(--card-border);
            border-radius: 20px;
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
            padding: 20px 28px;
            margin-bottom: 20px;
            border-color: rgba(255, 19, 97, 0.25);
            box-shadow: 0 0 30px rgba(255, 19, 97, 0.12);
        }

        .user-block { display: flex; align-items: center; gap: 18px; }

        .avatar-wrap {
            position: relative;
            width: 68px; height: 68px;
        }

        .user-avatar {
            width: 100%; height: 100%;
            border-radius: 18px;
            object-fit: cover;
            border: 2px solid var(--neon-pink);
            box-shadow: 0 0 20px rgba(255, 19, 97, 0.5);
        }

        .user-titles h1 {
            font-family: 'Syne', sans-serif;
            font-size: 24px; font-weight: 800;
            display: flex; align-items: center; gap: 12px;
        }

        .badge-live {
            background: rgba(0, 255, 136, 0.12);
            border: 1px solid var(--neon-green);
            color: var(--neon-green);
            font-size: 11px; font-weight: 800;
            padding: 3px 10px; border-radius: 99px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .user-ranks {
            font-size: 13.5px; color: #94a3b8; margin-top: 4px;
        }
        .user-ranks b { color: #fff; font-family: 'JetBrains Mono', monospace; font-size: 14.5px; }

        .hero-telemetry {
            display: flex; gap: 32px;
        }

        .t-item { text-align: right; }
        .t-val {
            font-size: 24px; font-weight: 800;
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

        /* NAVIGATION TABS */
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 24px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 12px;
            overflow-x: auto;
        }

        .tab-btn {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #94a3b8;
            padding: 10px 20px;
            border-radius: 14px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
            white-space: nowrap;
        }

        .tab-btn:hover {
            color: #fff;
            background: rgba(255, 255, 255, 0.07);
            border-color: rgba(255, 255, 255, 0.18);
        }

        .tab-btn.active {
            color: #fff;
            background: linear-gradient(135deg, rgba(255, 19, 97, 0.2), rgba(0, 255, 242, 0.15));
            border-color: var(--neon-pink);
            box-shadow: 0 0 15px rgba(255, 19, 97, 0.3);
        }

        .tab-content { display: none; }
        .tab-content.active { display: block; animation: tabFade 0.3s ease; }

        @keyframes tabFade {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* 5-STAR READINESS GAUGE */
        .readiness-strip {
            background: linear-gradient(135deg, rgba(157, 0, 255, 0.12), rgba(255, 19, 97, 0.12));
            border: 1px solid rgba(157, 0, 255, 0.35);
            border-radius: 20px;
            padding: 20px 28px;
            margin-bottom: 24px;
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 24px;
            align-items: center;
        }

        .gauge-title {
            font-size: 17px; font-weight: 800;
            font-family: 'Syne', sans-serif;
            display: flex; align-items: center; gap: 10px;
        }

        .gauge-track {
            height: 10px; width: 100%;
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
            box-shadow: 0 0 15px var(--neon-cyan);
        }

        .gauge-desc { font-size: 13px; color: #cbd5e1; margin-top: 8px; }

        .stat-box {
            text-align: center;
            padding: 10px 16px;
            background: rgba(0, 0, 0, 0.35);
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }
        .sb-val {
            font-size: 24px; font-weight: 900;
            font-family: 'JetBrains Mono', monospace;
            color: var(--neon-cyan);
        }
        .sb-lbl { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin-top: 2px; }

        /* Top Plays */
        .top-plays-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin-bottom: 24px;
        }

        .top-play-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 12px 14px;
            display: flex; align-items: center; gap: 12px;
            text-decoration: none; color: inherit;
            transition: all 0.25s ease;
        }

        .top-play-card:hover {
            transform: translateY(-3px);
            border-color: var(--neon-cyan);
            background: rgba(255, 255, 255, 0.05);
        }

        .tp-thumb {
            width: 48px; height: 48px;
            border-radius: 10px;
            object-fit: cover;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .tp-title { font-size: 13px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .tp-meta { font-size: 11.5px; color: #94a3b8; margin-top: 2px; }
        .tp-pp { font-family: 'JetBrains Mono', monospace; font-size: 15px; font-weight: 800; color: var(--neon-green); margin-left: auto; }

        /* Core Grid */
        .core-grid {
            display: grid;
            grid-template-columns: 2.1fr 1fr;
            gap: 24px;
        }

        .panel-pad { padding: 24px; margin-bottom: 24px; }
        .panel-head {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 20px;
        }
        .panel-title { font-size: 18px; font-weight: 800; font-family: 'Syne', sans-serif; display: flex; align-items: center; gap: 10px; }

        .focus-pill {
            background: rgba(255, 19, 97, 0.12);
            border: 1px solid var(--neon-pink);
            color: var(--neon-pink);
            font-size: 11px; font-weight: 700;
            padding: 4px 12px; border-radius: 99px;
            text-transform: uppercase;
        }

        /* 4 Big Tiles */
        .metric-tiles {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }

        .tile {
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            padding: 14px 16px;
        }
        .tile-lbl { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 4px; }
        .tile-val { font-size: 24px; font-weight: 900; font-family: 'JetBrains Mono', monospace; }

        /* Skill Radar */
        .skill-matrix {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }

        .skill-box {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 12px 14px;
        }
        .skill-head { display: flex; justify-content: space-between; font-size: 12.5px; font-weight: 700; margin-bottom: 6px; }
        .skill-track { height: 6px; background: rgba(255, 255, 255, 0.08); border-radius: 99px; overflow: hidden; }
        .skill-fill { height: 100%; border-radius: 99px; transition: width 1s ease; }
        .sf-acc { background: var(--neon-green); }
        .sf-aim { background: var(--neon-cyan); }
        .sf-stam { background: var(--neon-pink); }
        .sf-cons { background: var(--neon-purple); }

        /* Chart Dual */
        .charts-dual {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-top: 20px;
        }
        .chart-wrap {
            background: rgba(0, 0, 0, 0.28);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 14px;
            height: 220px;
        }

        /* Right Column Side Panel */
        .replay-select-box {
            display: flex; gap: 8px; margin-bottom: 20px;
        }
        .osu-select {
            flex: 1;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #fff;
            padding: 10px 14px;
            border-radius: 12px;
            font-family: 'Outfit', sans-serif;
            font-size: 13.5px;
            outline: none;
        }
        .osu-btn {
            background: var(--neon-pink);
            border: none;
            color: #fff;
            padding: 10px 16px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 13.5px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .osu-btn:hover {
            filter: brightness(1.15);
            box-shadow: 0 0 15px rgba(255, 19, 97, 0.4);
        }

        .feedback-card {
            background: rgba(255, 255, 255, 0.02);
            border-left: 4px solid #64748b;
            border-radius: 0 12px 12px 0;
            padding: 12px 14px;
            margin-bottom: 12px;
        }
        .fb-danger { border-left-color: var(--neon-pink); background: rgba(255, 19, 97, 0.04); }
        .fb-warning { border-left-color: #f59e0b; background: rgba(245, 158, 11, 0.04); }
        .fb-success { border-left-color: var(--neon-green); background: rgba(0, 255, 136, 0.04); }
        .fb-title { font-size: 13.5px; font-weight: 700; margin-bottom: 4px; display: flex; align-items: center; gap: 8px; }
        .fb-text { font-size: 12.5px; color: #94a3b8; line-height: 1.45; }

        /* Map Pack Card */
        .pack-card {
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 14px;
        }
        .pack-rec {
            border-color: var(--neon-pink);
            box-shadow: 0 0 20px rgba(255, 19, 97, 0.2);
        }
        .pack-meta-row { display: flex; gap: 8px; margin: 8px 0; }
        .pill-meta {
            background: rgba(255, 255, 255, 0.06);
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
        }
        .map-item-link {
            display: flex; justify-content: space-between; align-items: center;
            padding: 8px 10px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            margin-top: 6px;
            text-decoration: none;
            color: #cbd5e1;
            font-size: 12.5px;
            transition: all 0.2s ease;
        }
        .map-item-link:hover {
            background: rgba(255, 255, 255, 0.08);
            color: var(--neon-cyan);
            transform: translateX(3px);
        }

        /* ------------------ TAB 2: RHYTHM TRAINER ------------------ */
        .trainer-container {
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            gap: 24px;
        }

        .hit-arena {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            position: relative;
            user-select: none;
        }

        .target-circle {
            width: 140px; height: 140px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255, 19, 97, 0.25) 0%, rgba(18, 20, 36, 0.8) 70%);
            border: 3px solid var(--neon-pink);
            box-shadow: 0 0 35px rgba(255, 19, 97, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Syne', sans-serif;
            font-size: 26px;
            font-weight: 900;
            color: #fff;
            position: relative;
            cursor: pointer;
            transition: transform 0.08s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .target-circle:active {
            transform: scale(0.94);
        }

        .target-circle.beat-pulse {
            transform: scale(1.08);
            border-color: var(--neon-cyan);
            box-shadow: 0 0 45px rgba(0, 255, 242, 0.7);
        }

        .ripple-ring {
            position: absolute;
            width: 140px; height: 140px;
            border-radius: 50%;
            border: 2px solid var(--neon-cyan);
            pointer-events: none;
            opacity: 0;
        }

        .ripple-ring.animate {
            animation: ringApproach 0.4s ease-out;
        }

        @keyframes ringApproach {
            0% { transform: scale(1.7); opacity: 0.8; }
            100% { transform: scale(1); opacity: 0; }
        }

        /* Timing Error Bar */
        .timing-bar-container {
            width: 100%;
            max-width: 500px;
            margin: 32px 0 16px;
        }

        .timing-bar {
            height: 18px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 99px;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .zone-300 {
            position: absolute;
            left: 45%; width: 10%; height: 100%;
            background: rgba(0, 255, 136, 0.4);
            border-left: 1px solid var(--neon-green);
            border-right: 1px solid var(--neon-green);
        }
        .zone-100 {
            position: absolute;
            left: 30%; width: 40%; height: 100%;
            background: rgba(245, 158, 11, 0.15);
        }
        .zone-center {
            position: absolute;
            left: 50%; width: 2px; height: 100%;
            background: #fff;
            transform: translateX(-50%);
            box-shadow: 0 0 6px #fff;
        }

        .timing-needle {
            position: absolute;
            top: 0; left: 50%; width: 4px; height: 100%;
            background: var(--neon-cyan);
            border-radius: 99px;
            transform: translateX(-50%);
            transition: left 0.1s ease;
            box-shadow: 0 0 12px var(--neon-cyan);
        }

        .timing-labels {
            display: flex; justify-content: space-between;
            font-size: 11px; font-weight: 700; color: #64748b;
            margin-top: 6px;
        }

        .hit-feedback-text {
            font-family: 'JetBrains Mono', monospace;
            font-size: 20px;
            font-weight: 800;
            margin-top: 8px;
            height: 28px;
        }

        .key-hints {
            display: flex; gap: 14px; margin-top: 24px;
        }
        .key-badge {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            padding: 8px 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 15px;
            font-weight: 800;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .key-badge.pressed {
            background: var(--neon-pink);
            border-color: var(--neon-pink);
            box-shadow: 0 0 18px var(--neon-pink);
        }

        /* ------------------ TAB 3: BEATMAP HUB ------------------ */
        .hub-filters {
            display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;
        }
        .filter-btn {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #94a3b8;
            padding: 8px 16px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .filter-btn:hover, .filter-btn.active {
            color: #fff;
            background: rgba(255, 255, 255, 0.1);
            border-color: var(--neon-cyan);
        }

        .hub-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 16px;
        }

        .hub-card {
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.25s ease;
        }
        .hub-card:hover {
            transform: translateY(-4px);
            border-color: var(--neon-cyan);
            box-shadow: 0 10px 30px rgba(0, 255, 242, 0.15);
        }
        .hub-card-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; margin-bottom: 8px; }
        .hub-card-title { font-size: 15px; font-weight: 800; font-family: 'Syne', sans-serif; color: #fff; }
        .hub-diff-badge {
            background: linear-gradient(135deg, rgba(255, 19, 97, 0.3), rgba(157, 0, 255, 0.3));
            border: 1px solid var(--neon-pink);
            color: #fff;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 6px;
            white-space: nowrap;
        }

        /* ------------------ TAB 4: SECOND BRAIN OBSIDIAN ------------------ */
        .vault-split {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 20px;
            height: 720px;
        }

        .vault-list {
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 14px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .vault-note-item {
            padding: 12px 14px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .vault-note-item:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(255, 255, 255, 0.15);
        }
        .vault-note-item.active {
            background: rgba(0, 255, 242, 0.1);
            border-color: var(--neon-cyan);
        }
        .v-note-title { font-size: 13.5px; font-weight: 700; color: #fff; margin-bottom: 2px; }
        .v-note-mtime { font-size: 11px; color: #64748b; font-family: 'JetBrains Mono', monospace; }

        .vault-reader {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 28px;
            overflow-y: auto;
            line-height: 1.6;
        }

        .markdown-body h1, .markdown-body h2, .markdown-body h3 {
            font-family: 'Syne', sans-serif;
            color: #fff;
            margin-top: 18px;
            margin-bottom: 10px;
        }
        .markdown-body h1 { font-size: 24px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 8px; }
        .markdown-body h2 { font-size: 18px; color: var(--neon-cyan); }
        .markdown-body p { margin-bottom: 12px; color: #cbd5e1; font-size: 14px; }
        .markdown-body ul, .markdown-body ol { margin-left: 20px; margin-bottom: 14px; color: #cbd5e1; font-size: 14px; }
        .markdown-body table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 13px; }
        .markdown-body th, .markdown-body td { border: 1px solid rgba(255, 255, 255, 0.1); padding: 8px 12px; }
        .markdown-body th { background: rgba(255, 255, 255, 0.05); color: #fff; font-weight: 700; }
        .markdown-body code { background: rgba(255, 255, 255, 0.08); padding: 2px 6px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; }

        /* Toast notification */
        #toast {
            position: fixed;
            bottom: 24px; right: 24px;
            background: #12131c;
            border: 1px solid var(--neon-cyan);
            box-shadow: 0 10px 30px rgba(0, 255, 242, 0.3);
            color: #fff;
            padding: 14px 20px;
            border-radius: 14px;
            font-weight: 600;
            font-size: 13.5px;
            z-index: 9999;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        #toast.show {
            transform: translateY(0);
            opacity: 1;
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

        <!-- Navigation Tabs Bar -->
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('hud')">⚡ HUD & Аналитика</button>
            <button class="tab-btn" onclick="switchTab('trainer')">🎵 Ритм-Тренажёр (Разминка)</button>
            <button class="tab-btn" onclick="switchTab('hub')">🗺️ Каталог карт (Beatmap Hub)</button>
            <button class="tab-btn" onclick="switchTab('vault')">🧠 Вторая память (Obsidian)</button>
            <button class="tab-btn" onclick="switchTab('settings')">⚙️ Тюнинг & Настройки</button>
        </div>

        <!-- ================= TAB 1: HUD & АНАЛИТИКА ================= -->
        <div id="tab-hud" class="tab-content active">
            <!-- 5-Star Readiness Gauge -->
            <div class="readiness-strip">
                <div>
                    <div class="gauge-title">
                        🎯 Индекс Готовности к 5★ (Target Milestone)
                        <span style="font-size:12px; color:var(--neon-cyan); font-weight:normal;">[Цель: 5★ на 90%+ pass]</span>
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

            <!-- Top Plays Row -->
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
                                <div class="tile-val" style="font-size:18px; color:#c084fc;" id="val-hits">--</div>
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
                        <div style="margin-bottom: 20px;">
                            <div style="font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 10px;">
                                ДНК Игрока (Skill Radar Breakdown)
                            </div>
                            <div class="skill-matrix">
                                <div class="skill-box">
                                    <div class="skill-head">
                                        <span>Ритм & Аккураси</span>
                                        <span id="sk-acc-val">--%</span>
                                    </div>
                                    <div class="skill-track"><div class="skill-fill sf-acc" id="sk-acc-bar" style="width:0%;"></div></div>
                                </div>
                                <div class="skill-box">
                                    <div class="skill-head">
                                        <span>Аим пера (ГП • Snap & Precision)</span>
                                        <span id="sk-aim-val">--%</span>
                                    </div>
                                    <div class="skill-track"><div class="skill-fill sf-aim" id="sk-aim-bar" style="width:0%;"></div></div>
                                </div>
                                <div class="skill-box">
                                    <div class="skill-head">
                                        <span>Баланс пальцев & Стамина</span>
                                        <span id="sk-stam-val">--%</span>
                                    </div>
                                    <div class="skill-track"><div class="skill-fill sf-stam" id="sk-stam-bar" style="width:0%;"></div></div>
                                </div>
                                <div class="skill-box">
                                    <div class="skill-head">
                                        <span>Стабильность комбо</span>
                                        <span id="sk-cons-val">--%</span>
                                    </div>
                                    <div class="skill-track"><div class="skill-fill sf-cons" id="sk-cons-bar" style="width:0%;"></div></div>
                                </div>
                            </div>
                        </div>

                        <!-- Dual Charts -->
                        <div class="charts-dual">
                            <div class="chart-wrap">
                                <canvas id="hitsChart"></canvas>
                            </div>
                            <div class="chart-wrap">
                                <canvas id="fingersChart"></canvas>
                            </div>
                        </div>
                    </div>

                    <!-- Coach Feedbacks -->
                    <div class="cyber-card panel-pad">
                        <div class="panel-head">
                            <div class="panel-title">🔬 Диагностика и Разбор Ошибок</div>
                        </div>
                        <div id="coach-feedbacks"></div>
                    </div>
                </div>

                <!-- Right Column -->
                <div>
                    <!-- Replay Selector -->
                    <div class="cyber-card panel-pad">
                        <div class="panel-head">
                            <div class="panel-title">🎮 История сессий lazer</div>
                        </div>
                        <div class="replay-select-box">
                            <select id="replay-dropdown" class="osu-select"></select>
                        </div>
                        <button class="osu-btn" style="width:100%;" onclick="loadReplay()">
                            ⚡ Анализировать выбранную игру
                        </button>
                    </div>

                    <!-- Recommended Training Map Pack -->
                    <div class="cyber-card panel-pad">
                        <div class="panel-head">
                            <div class="panel-title">🎯 Рекомендованные Карты</div>
                        </div>
                        <div id="recommended-packs"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ================= TAB 2: RHYTHM TRAINER ================= -->
        <div id="tab-trainer" class="tab-content">
            <div class="cyber-card panel-pad">
                <div class="panel-head">
                    <div class="panel-title">🎵 Ритм-Тренажёр & Постановка Тайминга</div>
                    <div class="focus-pill">Лечение Early Tap & Стабилизация UR</div>
                </div>

                <div class="trainer-container">
                    <!-- Left: Interactive Hit Arena -->
                    <div class="hit-arena">
                        <div class="ripple-ring" id="rippleRing"></div>
                        <div class="target-circle" id="targetCircle" onclick="registerTap('K1')">
                            HIT
                        </div>

                        <!-- Timing Error Bar -->
                        <div class="timing-bar-container">
                            <div class="timing-bar">
                                <div class="zone-100"></div>
                                <div class="zone-300"></div>
                                <div class="zone-center"></div>
                                <div class="timing-needle" id="timingNeedle"></div>
                            </div>
                            <div class="timing-labels">
                                <span>-120ms (Early)</span>
                                <span>0ms (300 Perfect)</span>
                                <span>+120ms (Late)</span>
                            </div>
                        </div>

                        <div class="hit-feedback-text" id="hitFeedbackText" style="color:var(--neon-cyan);">
                            Нажми Старт или пробей ритм клавишами Z / X
                        </div>

                        <div class="key-hints">
                            <button class="key-badge" id="badgeK1" style="cursor:pointer;" onclick="registerTap('K1')">K1: [ Z ]</button>
                            <button class="key-badge" id="badgeK2" style="cursor:pointer;" onclick="registerTap('K2')">K2: [ X ]</button>
                        </div>
                    </div>

                    <!-- Right: Stats & Controls -->
                    <div style="display:flex; flex-direction:column; justify-content:space-between;">
                        <div>
                            <!-- BPM Controls -->
                            <div style="background:rgba(0,0,0,0.3); padding:16px; border-radius:14px; border:1px solid rgba(255,255,255,0.06); margin-bottom:16px;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                    <span style="font-size:14px; font-weight:700;">Темп метронома:</span>
                                    <span style="font-family:'JetBrains Mono'; font-size:20px; font-weight:900; color:var(--neon-cyan);" id="bpmVal">165 BPM</span>
                                </div>
                                <input type="range" id="bpmSlider" min="120" max="230" value="165" style="width:100%; accent-color:var(--neon-pink); cursor:pointer;" oninput="updateBpm(this.value)">
                                
                                <div style="display:flex; gap:6px; margin-top:10px;">
                                    <button class="filter-btn" onclick="updateBpm(140)">140</button>
                                    <button class="filter-btn" onclick="updateBpm(160)">160</button>
                                    <button class="filter-btn" onclick="updateBpm(175)">175</button>
                                    <button class="filter-btn" onclick="updateBpm(185)">185</button>
                                    <button class="filter-btn" onclick="updateBpm(200)">200</button>
                                </div>
                            </div>

                            <!-- Live Telemetry -->
                            <div class="metric-tiles" style="grid-template-columns: repeat(2, 1fr); margin-bottom:16px;">
                                <div class="tile">
                                    <div class="tile-lbl">Точность (Acc)</div>
                                    <div class="tile-val" id="trAcc" style="color:var(--neon-green);">100%</div>
                                </div>
                                <div class="tile">
                                    <div class="tile-lbl">Unstable Rate (UR)</div>
                                    <div class="tile-val" id="trUR" style="color:var(--neon-cyan);">0.0</div>
                                </div>
                                <div class="tile">
                                    <div class="tile-lbl">300 / 100 / 50 / Miss</div>
                                    <div class="tile-val" style="font-size:17px;" id="trHits">0 / 0 / 0 / 0</div>
                                </div>
                                <div class="tile">
                                    <div class="tile-lbl">Баланс K1 / K2</div>
                                    <div class="tile-val" style="font-size:17px; color:var(--neon-pink);" id="trFingers">0 / 0 (50%)</div>
                                </div>
                            </div>
                        </div>

                        <!-- Action Buttons -->
                        <div style="display:flex; flex-direction:column; gap:10px;">
                            <div style="display:flex; gap:10px;">
                                <button class="osu-btn" id="startTrainerBtn" style="flex:1; background:var(--neon-green); color:#000;" onclick="toggleTrainer()">
                                    ▶ Запустить метроном
                                </button>
                                <button class="filter-btn" style="padding:10px 16px;" onclick="resetTrainer()">
                                    ↺ Сброс
                                </button>
                            </div>
                            <button class="osu-btn" style="background:linear-gradient(135deg, rgba(157,0,255,0.8), rgba(255,19,97,0.8));" onclick="saveRhythmToVault()">
                                💾 Записать разминку в Obsidian Vault
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ================= TAB 3: BEATMAP HUB ================= -->
        <div id="tab-hub" class="tab-content">
            <div class="cyber-card panel-pad">
                <div class="panel-head">
                    <div class="panel-title">🗺️ Каталог проверенных тренировочных карт</div>
                    <div style="display:flex; gap:10px; align-items:center;">
                        <input type="text" id="hubSearch" placeholder="Поиск по песне или артисту..." class="osu-select" style="width:240px; padding:6px 12px;" oninput="filterHubMaps()">
                    </div>
                </div>

                <div class="hub-filters">
                    <button class="filter-btn active" onclick="setHubCategory('all', this)">Все карты</button>
                    <button class="filter-btn" onclick="setHubCategory('acc-control-1', this)">🎯 Ритм и Early-Fix (3.9–4.3★)</button>
                    <button class="filter-btn" onclick="setHubCategory('tablet-aim-jump', this)">🖊️ Аим пера (ГП 4.4–4.7★)</button>
                    <button class="filter-btn" onclick="setHubCategory('stamina-bursts', this)">⚡ Стамина и берсты (4.5–4.9★)</button>
                    <button class="filter-btn" onclick="setHubCategory('push-5star', this)">🌟 Штурм 5★ (5.0–5.3★)</button>
                </div>

                <div class="hub-grid" id="hubGrid"></div>
            </div>
        </div>

        <!-- ================= TAB 4: SECOND BRAIN OBSIDIAN ================= -->
        <div id="tab-vault" class="tab-content">
            <div class="cyber-card panel-pad">
                <div class="panel-head">
                    <div class="panel-title">🧠 Вторая память агента (Obsidian Second Brain)</div>
                    <div style="display:flex; gap:10px;">
                        <button class="osu-btn" style="background:var(--neon-purple); font-size:12.5px; padding:8px 14px;" onclick="openVaultExplorer()">
                            📂 Открыть папку вольта
                        </button>
                    </div>
                </div>

                <div class="vault-split">
                    <!-- Left Notes List -->
                    <div class="vault-list" id="vaultNotesList">
                        <div style="color:#64748b; font-size:13px; text-align:center; padding:20px;">Загрузка заметок...</div>
                    </div>

                    <!-- Right Note Reader -->
                    <div class="vault-reader">
                        <div id="vaultNoteContent" class="markdown-body">
                            <h2 style="color:var(--neon-cyan);">Выбери заметку слева для просмотра</h2>
                            <p style="color:#94a3b8;">Здесь отображаются все заметки твоей базы знаний Obsidian: профиль, журнал сессий, гипотезы тренера и гайды по пальцам.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ================= TAB 5: SETTINGS ================= -->
        <div id="tab-settings" class="tab-content">
            <div class="cyber-card panel-pad" style="max-width:800px; margin:0 auto;">
                <div class="panel-head">
                    <div class="panel-title">⚙️ Тюнинг и Настройки Тренера</div>
                </div>

                <div style="display:flex; flex-direction:column; gap:20px;">
                    <!-- Tablet Area Calculator -->
                    <div style="background:rgba(0,0,0,0.3); padding:18px; border-radius:14px; border:1px solid rgba(255,255,255,0.06);">
                        <h4 style="font-size:15px; font-weight:800; margin-bottom:12px; color:var(--neon-cyan);">🖊️ Тюнинг Графического Планшета (OTD & Tablet Area)</h4>
                        <div style="display:grid; grid-template-columns:1fr 1fr 1.2fr; gap:14px; align-items:center;">
                            <div>
                                <label style="font-size:11px; color:#64748b; font-weight:700;">ШИРИНА (WIDTH мм)</label>
                                <input type="number" id="cfgAreaW" value="78" step="0.5" class="osu-select" style="width:100%; margin-top:4px;" oninput="calcTabletArea()">
                            </div>
                            <div>
                                <label style="font-size:11px; color:#64748b; font-weight:700;">ВЫСОТА (HEIGHT мм)</label>
                                <input type="number" id="cfgAreaH" value="43.88" step="0.5" class="osu-select" style="width:100%; margin-top:4px;" oninput="calcTabletArea()">
                            </div>
                            <div class="stat-box" style="margin-top:14px;">
                                <div class="sb-val" style="font-size:18px; color:var(--neon-green);" id="cfgAreaRatio">16:9 (1.78 ✓)</div>
                                <div class="sb-lbl" id="cfgAreaDiag">Диагональ: ~89 мм</div>
                            </div>
                        </div>
                        <div style="margin-top:12px; display:flex; gap:14px; align-items:center;">
                            <label style="font-size:11px; color:#64748b; font-weight:700;">СТИЛЬ ИГРЫ:</label>
                            <select id="cfgGripStyle" class="osu-select" style="padding:6px 12px; width:auto;" onchange="calcTabletArea()">
                                <option value="drag">Drag (ведение пера по поверхности с трением)</option>
                                <option value="hover">Hover (зависание пера над планшетом)</option>
                            </select>
                        </div>
                        <p style="font-size:12px; color:#94a3b8; margin-top:12px; line-height:1.5;" id="cfgTabletAdvice">
                            💡 <b>Совет тренера по ГП:</b> Пропорция 16:9 идеальна — курсор двигается равномерно по X и Y. Для карт 5★ со взрывными джампами рекомендуется ширина <b>72 – 85 мм</b>. При стиле <b>Drag</b> трение дает максимальный контроль и естественный упор при Snap-остановке.
                        </p>
                    </div>

                    <!-- Keyboard binds -->
                    <div style="background:rgba(0,0,0,0.3); padding:18px; border-radius:14px; border:1px solid rgba(255,255,255,0.06);">
                        <h4 style="font-size:15px; font-weight:800; margin-bottom:12px; color:var(--neon-pink);">⌨️ Клавиши ритм-тренажера</h4>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px;">
                            <div>
                                <label style="font-size:11px; color:#64748b; font-weight:700;">КНОПКА 1 (K1)</label>
                                <input type="text" id="cfgKey1" value="Z" maxlength="1" class="osu-select" style="width:100%; margin-top:4px; text-transform:uppercase;" oninput="updateKeyBinds()">
                            </div>
                            <div>
                                <label style="font-size:11px; color:#64748b; font-weight:700;">КНОПКА 2 (K2)</label>
                                <input type="text" id="cfgKey2" value="X" maxlength="1" class="osu-select" style="width:100%; margin-top:4px; text-transform:uppercase;" oninput="updateKeyBinds()">
                            </div>
                        </div>
                    </div>

                    <!-- Paths check -->
                    <div style="background:rgba(0,0,0,0.3); padding:18px; border-radius:14px; border:1px solid rgba(255,255,255,0.06);">
                        <h4 style="font-size:15px; font-weight:800; margin-bottom:10px; color:var(--neon-green);">🔌 Статус подключений</h4>
                        <div style="font-size:12.5px; color:#cbd5e1; display:flex; flex-direction:column; gap:6px;">
                            <div>• <b>osu!lazer кэш:</b> <span style="color:var(--neon-green);">Подключен (AppData/Roaming/osu)</span></div>
                            <div>• <b>Obsidian Vault:</b> <span style="color:var(--neon-green);">Подключен (osu-vault/)</span></div>
                            <div>• <b>Официальный osu! API v2:</b> <span style="color:var(--neon-green);">Активен (ID 73273)</span></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Feedback -->
    <div id="toast">
        <span id="toastIcon">✨</span>
        <span id="toastMsg">Уведомление</span>
    </div>

    <script>
        // Particles Canvas Background
        const canvas = document.getElementById('bgCanvas');
        const ctx = canvas.getContext('2d');
        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;

        window.addEventListener('resize', () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        });

        const particles = [];
        for (let i = 0; i < 35; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.4,
                vy: (Math.random() - 0.5) * 0.4,
                size: Math.random() * 2 + 1,
                color: Math.random() > 0.5 ? 'rgba(255, 19, 97, 0.25)' : 'rgba(0, 255, 242, 0.25)'
            });
        }

        function animBg() {
            ctx.clearRect(0, 0, width, height);
            particles.forEach(p => {
                p.x += p.vx; p.y += p.vy;
                if (p.x < 0) p.x = width;
                if (p.x > width) p.x = 0;
                if (p.y < 0) p.y = height;
                if (p.y > height) p.y = 0;
                ctx.fillStyle = p.color;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fill();
            });
            requestAnimationFrame(animBg);
        }
        animBg();

        // Global State
        let allPacks = [];
        let allNotes = [];
        let hitsChart = null;
        let fingersChart = null;
        let currentTab = 'hud';

        // Toast
        function showToast(msg, icon = '✨') {
            const toast = document.getElementById('toast');
            document.getElementById('toastMsg').innerText = msg;
            document.getElementById('toastIcon').innerText = icon;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3200);
        }

        // Tab Switching
        function switchTab(tabId) {
            currentTab = tabId;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            const targetContent = document.getElementById(`tab-${tabId}`);
            if (targetContent) targetContent.classList.add('active');

            document.querySelectorAll('.tab-btn').forEach(btn => {
                if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes("'" + tabId + "'")) {
                    btn.classList.add('active');
                }
            });

            if (tabId === 'vault' && allNotes.length === 0) {
                loadVaultNotes();
            }
        }

        // Initialize Data
        async function init() {
            try {
                // Profile
                const resProf = await fetch('/api/profile');
                const p = await resProf.json();
                if (!p.error) {
                    document.getElementById('u-name').innerText = p.username;
                    document.getElementById('u-avatar').src = p.avatar_url;
                    document.getElementById('u-rank').innerText = '#' + (p.global_rank ? p.global_rank.toLocaleString() : '--');
                    document.getElementById('u-country-rank').innerText = '#' + (p.country_rank ? p.country_rank.toLocaleString() : '--');
                    const ppVal = (p.pp !== undefined) ? p.pp : (p.pp_raw || 0);
                    const hoursVal = (p.play_time_hours !== undefined) ? p.play_time_hours : Math.round((p.play_time || 0) / 3600);

                    document.getElementById('u-pp').innerText = Math.round(ppVal).toLocaleString() + ' pp';
                    document.getElementById('u-acc').innerText = (p.accuracy || 0).toFixed(2) + '%';
                    document.getElementById('u-playtime').innerText = hoursVal + ' ч';

                    if (p.top_plays && p.top_plays.length) {
                        const box = document.getElementById('top-plays-box');
                        box.innerHTML = '';
                        p.top_plays.forEach(tp => {
                            box.innerHTML += `
                                <a href="${tp.url || tp.beatmap_url || '#'}" target="_blank" class="top-play-card">
                                    <img src="${tp.cover_url}" class="tp-thumb" alt="Cover">
                                    <div style="overflow:hidden;">
                                        <div class="tp-title">${tp.title}</div>
                                        <div class="tp-meta">${tp.version} • ${tp.acc || tp.accuracy}%</div>
                                    </div>
                                    <div class="tp-pp">${Math.round(tp.pp)}pp</div>
                                </a>
                            `;
                        });
                    }
                }

                // Replays list
                const resR = await fetch('/api/replays');
                const rData = await resR.json();
                const dd = document.getElementById('replay-dropdown');
                dd.innerHTML = '';
                rData.replays.forEach(r => {
                    const opt = document.createElement('option');
                    opt.value = r.id;
                    opt.innerText = `${r.date} • ${r.name}`;
                    dd.appendChild(opt);
                });

                // Packs
                const resP = await fetch('/api/packs');
                const pData = await resP.json();
                allPacks = pData.packs;
                renderHubGrid(allPacks);

                // Initial Replay Analysis
                if (rData.replays.length) {
                    loadReplay();
                }

                // Preload vault notes
                loadVaultNotes();
            } catch (e) {
                console.error('Init error:', e);
            }
        }

        async function loadReplay() {
            const dd = document.getElementById('replay-dropdown');
            const targetId = dd.value || '';
            const res = await fetch(`/api/analyze?id=${encodeURIComponent(targetId)}`);
            const data = await res.json();
            if (data.error) {
                showToast(data.error, '⚠️');
                return;
            }

            document.getElementById('map-header').innerText = `Игра [${data.time}] • Скор: ${data.score}`;
            document.getElementById('focus-pill').innerText = data.focus_title;

            document.getElementById('val-acc').innerText = data.accuracy + '%';
            document.getElementById('val-hits').innerText = `${data.count_300} / ${data.count_100} / ${data.count_50}`;
            document.getElementById('val-miss').innerText = data.count_miss;
            document.getElementById('val-combo').innerText = data.max_combo + 'x';

            // Skill Radar Bars
            document.getElementById('sk-acc-val').innerText = data.skills.accuracy + '%';
            document.getElementById('sk-acc-bar').style.width = data.skills.accuracy + '%';
            document.getElementById('sk-aim-val').innerText = data.skills.aim + '%';
            document.getElementById('sk-aim-bar').style.width = data.skills.aim + '%';
            document.getElementById('sk-stam-val').innerText = data.skills.stamina + '%';
            document.getElementById('sk-stam-bar').style.width = data.skills.stamina + '%';
            document.getElementById('sk-cons-val').innerText = data.skills.consistency + '%';
            document.getElementById('sk-cons-bar').style.width = data.skills.consistency + '%';

            // 5-Star Readiness Gauge
            document.getElementById('gauge-bar').style.width = data.target_5star_readiness + '%';
            document.getElementById('gauge-percent').innerText = data.target_5star_readiness + '%';
            document.getElementById('potential-pp').innerText = '+' + data.potential_pp_gain + ' pp';
            document.getElementById('gauge-desc').innerText =
                `Текущий контроль нестабилен для 5★. Рекомендуется FC на картах 3.9★ – 4.3★ с точностью 96%+.`;

            // Feedbacks
            const fbBox = document.getElementById('coach-feedbacks');
            fbBox.innerHTML = '';
            data.feedbacks.forEach(fb => {
                fbBox.innerHTML += `
                    <div class="feedback-card fb-${fb.type}">
                        <div class="fb-title">
                            <span class="focus-pill" style="font-size:10px;">${fb.badge}</span>
                            <span>${fb.title}</span>
                        </div>
                        <div class="fb-text">${fb.text}</div>
                    </div>
                `;
            });

            // Recommended Map Pack
            renderRecommendedPack(data.recommended_pack);

            // Dual Charts
            renderCharts(data);
        }

        function renderRecommendedPack(pack) {
            const container = document.getElementById('recommended-packs');
            container.innerHTML = '';
            if (!pack) return;

            let mapsHtml = '';
            pack.maps.forEach(m => {
                mapsHtml += `
                    <a href="${m.link}" target="_blank" class="map-item-link">
                        <span><b>${m.title}</b> (${m.mapper})</span>
                        <span style="font-family:'JetBrains Mono'; font-size:11px; color:var(--neon-pink);">${m.diff}</span>
                    </a>
                `;
            });

            container.innerHTML = `
                <div class="pack-card pack-rec">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="font-size:15px; font-weight:800; font-family:'Syne',sans-serif;">${pack.title}</h4>
                        <span class="focus-pill">Тебе сюда!</span>
                    </div>
                    <div class="pack-meta-row">
                        <span class="pill-meta">${pack.stars}</span>
                        <span class="pill-meta">${pack.bpm}</span>
                    </div>
                    <p style="font-size:12.5px; color:#94a3b8; margin-bottom:8px;">${pack.description}</p>
                    ${mapsHtml}
                </div>
            `;
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

        // ================= TAB 2: RHYTHM TRAINER LOGIC =================
        let trBpm = 165;
        let trIsPlaying = false;
        let trInterval = null;
        let audioCtx = null;
        let beatTimes = [];
        let tapOffsets = [];
        let tr300 = 0, tr100 = 0, tr50 = 0, trMiss = 0;
        let trK1 = 0, trK2 = 0;
        let keyK1 = 'Z';
        let keyK2 = 'X';

        function playClick(freq = 880) {
            try {
                if (!audioCtx) {
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                }
                if (audioCtx.state === 'suspended') {
                    audioCtx.resume();
                }
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.05);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.05);
            } catch (e) {}
        }

        function updateBpm(val) {
            trBpm = parseInt(val);
            document.getElementById('bpmVal').innerText = `${trBpm} BPM`;
            document.getElementById('bpmSlider').value = trBpm;
            if (trIsPlaying) {
                clearInterval(trInterval);
                startMetronomeLoop();
            }
        }

        function toggleTrainer() {
            trIsPlaying = !trIsPlaying;
            const btn = document.getElementById('startTrainerBtn');
            if (trIsPlaying) {
                try {
                    if (!audioCtx) {
                        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    }
                    if (audioCtx.state === 'suspended') {
                        audioCtx.resume();
                    }
                } catch(e) {}
                btn.innerText = '⏸ Пауза';
                btn.style.background = 'var(--neon-pink)';
                btn.style.color = '#fff';
                startMetronomeLoop();
                document.getElementById('hitFeedbackText').innerText = 'Слушай бит и тапай в такт!';
                document.getElementById('hitFeedbackText').style.color = 'var(--neon-cyan)';
            } else {
                btn.innerText = '▶ Запустить метроном';
                btn.style.background = 'var(--neon-green)';
                btn.style.color = '#000';
                if (trInterval) clearInterval(trInterval);
            }
        }

        function startMetronomeLoop() {
            const intervalMs = (60 / trBpm) * 1000;
            beatTimes = [performance.now()];

            if (trInterval) clearInterval(trInterval);
            trInterval = setInterval(() => {
                const now = performance.now();
                beatTimes.push(now);
                if (beatTimes.length > 40) beatTimes.shift();

                playClick(880);

                const circle = document.getElementById('targetCircle');
                const ring = document.getElementById('rippleRing');
                if (circle) {
                    circle.classList.add('beat-pulse');
                    setTimeout(() => circle.classList.remove('beat-pulse'), 80);
                }
                if (ring) {
                    ring.classList.remove('animate');
                    void ring.offsetWidth;
                    ring.classList.add('animate');
                }
            }, intervalMs);
        }

        function resetTrainer() {
            tapOffsets = [];
            tr300 = tr100 = tr50 = trMiss = 0;
            trK1 = trK2 = 0;
            updateTrainerTelemetry();
            document.getElementById('hitFeedbackText').innerText = 'Сброшено. Начни тапать Z / X';
            document.getElementById('hitFeedbackText').style.color = 'var(--neon-cyan)';
            document.getElementById('timingNeedle').style.left = '50%';
        }

        function registerTap(keyName) {
            // Auto-start metronome on tap if stopped
            if (!trIsPlaying) {
                toggleTrainer();
            }

            const tapTime = performance.now();
            if (keyName === 'K1') trK1++;
            else trK2++;

            // Highlight key badge
            const badge = document.getElementById(keyName === 'K1' ? 'badgeK1' : 'badgeK2');
            if (badge) {
                badge.classList.add('pressed');
                setTimeout(() => badge.classList.remove('pressed'), 90);
            }

            if (beatTimes.length === 0) {
                updateTrainerTelemetry();
                return;
            }

            const intervalMs = (60 / trBpm) * 1000;
            const lastBeat = beatTimes[beatTimes.length - 1];
            const nextBeat = lastBeat + intervalMs;

            // Difference from last beat (late -> positive)
            const diffFromLast = tapTime - lastBeat;
            // Difference from next beat (early -> negative)
            const diffFromNext = tapTime - nextBeat;

            // Pick closest in time
            const closestDiff = Math.abs(diffFromLast) <= Math.abs(diffFromNext) ? diffFromLast : diffFromNext;

            // Visual needle: -120ms to +120ms
            const needlePercent = Math.max(0, Math.min(100, 50 + (closestDiff / 240) * 100));
            const needle = document.getElementById('timingNeedle');
            if (needle) needle.style.left = needlePercent + '%';

            tapOffsets.push(closestDiff);
            if (tapOffsets.length > 50) tapOffsets.shift();

            const absDiff = Math.abs(closestDiff);
            const fbText = document.getElementById('hitFeedbackText');
            const sign = closestDiff > 0 ? '+' : '';
            const roundedMs = Math.round(closestDiff);

            if (absDiff <= 25) {
                tr300++;
                fbText.innerText = `300 PERFECT (${sign}${roundedMs}ms)`;
                fbText.style.color = 'var(--neon-green)';
            } else if (absDiff <= 70) {
                tr100++;
                const label = closestDiff < 0 ? 'EARLY' : 'LATE';
                fbText.innerText = `${label} 100 (${sign}${roundedMs}ms)`;
                fbText.style.color = '#f59e0b';
            } else if (absDiff <= 115) {
                tr50++;
                const label = closestDiff < 0 ? 'TOO EARLY' : 'TOO LATE';
                fbText.innerText = `${label} 50 (${sign}${roundedMs}ms)`;
                fbText.style.color = '#c084fc';
            } else {
                trMiss++;
                fbText.innerText = `MISS (${sign}${roundedMs}ms)`;
                fbText.style.color = 'var(--neon-pink)';
            }

            updateTrainerTelemetry();
        }

        function updateTrainerTelemetry() {
            const totalHits = tr300 + tr100 + tr50 + trMiss;
            const acc = totalHits > 0 ? ((tr300 * 300 + tr100 * 100 + tr50 * 50) / (totalHits * 300) * 100).toFixed(1) : 100;
            document.getElementById('trAcc').innerText = acc + '%';
            document.getElementById('trHits').innerText = `${tr300} / ${tr100} / ${tr50} / ${trMiss}`;

            // Unstable Rate (UR) = stdDev * 10
            if (tapOffsets.length > 2) {
                const mean = tapOffsets.reduce((a, b) => a + b, 0) / tapOffsets.length;
                const variance = tapOffsets.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / tapOffsets.length;
                const ur = (Math.sqrt(variance) * 10).toFixed(1);
                document.getElementById('trUR').innerText = ur;
            } else {
                document.getElementById('trUR').innerText = '0.0';
            }

            // Finger ratio
            const totalTaps = trK1 + trK2;
            const k1Ratio = totalTaps > 0 ? Math.round((trK1 / totalTaps) * 100) : 50;
            const k2Ratio = totalTaps > 0 ? 100 - k1Ratio : 50;
            document.getElementById('trFingers').innerText = `${trK1} / ${trK2} (${k1Ratio}% / ${k2Ratio}%)`;
        }

        // Global Key Listener for Z / X (Layout-Independent: RU / EN)
        window.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;

            const code = e.code;
            const key = e.key ? e.key.toUpperCase() : '';

            // Match K1: KeyZ, 'Z', or Russian 'Я'
            const isK1 = (code === 'Key' + keyK1) || (key === keyK1) || 
                         (keyK1 === 'Z' && (code === 'KeyZ' || key === 'Я' || e.key === 'я'));

            // Match K2: KeyX, 'X', or Russian 'Ч'
            const isK2 = (code === 'Key' + keyK2) || (key === keyK2) || 
                         (keyK2 === 'X' && (code === 'KeyX' || key === 'Ч' || e.key === 'ч'));

            if (isK1) {
                e.preventDefault();
                registerTap('K1');
            } else if (isK2) {
                e.preventDefault();
                registerTap('K2');
            }
        });

        async function saveRhythmToVault() {
            const totalHits = tr300 + tr100 + tr50 + trMiss;
            if (totalHits < 10) {
                showToast('Сделай хотя бы 10 тапов перед сохранением!', '⚠️');
                return;
            }
            const totalTaps = trK1 + trK2;
            const k1Ratio = totalTaps > 0 ? Math.round((trK1 / totalTaps) * 100) : 50;
            const k2Ratio = 100 - k1Ratio;
            const acc = ((tr300 * 300 + tr100 * 100 + tr50 * 50) / (totalHits * 300) * 100).toFixed(1);
            const ur = document.getElementById('trUR').innerText;

            try {
                const res = await fetch('/api/vault/save-rhythm', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        bpm: trBpm,
                        taps: totalHits,
                        acc: parseFloat(acc),
                        ur: parseFloat(ur),
                        k1_ratio: k1Ratio,
                        k2_ratio: k2Ratio
                    })
                });
                const d = await res.json();
                if (d.status === 'ok') {
                    showToast('Разминка успешно записана во Вторую Память Obsidian!', '🧠');
                    loadVaultNotes();
                } else {
                    showToast('Ошибка записи в вольт', '⚠️');
                }
            } catch (e) {
                showToast('Ошибка отправки: ' + e, '⚠️');
            }
        }

        // ================= TAB 3: BEATMAP HUB LOGIC =================
        let currentHubCat = 'all';

        function setHubCategory(cat, btn) {
            currentHubCat = cat;
            document.querySelectorAll('.hub-filters .filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterHubMaps();
        }

        function filterHubMaps() {
            const q = document.getElementById('hubSearch').value.toLowerCase();
            let filteredPacks = allPacks;
            if (currentHubCat !== 'all') {
                filteredPacks = allPacks.filter(p => p.id === currentHubCat);
            }

            let mapList = [];
            filteredPacks.forEach(p => {
                p.maps.forEach(m => {
                    if (!q || m.title.toLowerCase().includes(q) || m.mapper.toLowerCase().includes(q)) {
                        mapList.push({ ...m, packTitle: p.title, packStars: p.stars, packBpm: p.bpm });
                    }
                });
            });

            renderHubGridCards(mapList);
        }

        function renderHubGrid(packs) {
            let mapList = [];
            packs.forEach(p => {
                p.maps.forEach(m => {
                    mapList.push({ ...m, packTitle: p.title, packStars: p.stars, packBpm: p.bpm });
                });
            });
            renderHubGridCards(mapList);
        }

        function renderHubGridCards(maps) {
            const grid = document.getElementById('hubGrid');
            grid.innerHTML = '';
            if (maps.length === 0) {
                grid.innerHTML = '<div style="color:#64748b; padding:20px;">Карты не найдены.</div>';
                return;
            }

            maps.forEach(m => {
                grid.innerHTML += `
                    <div class="hub-card">
                        <div>
                            <div class="hub-card-head">
                                <div class="hub-card-title">${m.title}</div>
                                <span class="hub-diff-badge">${m.diff}</span>
                            </div>
                            <div style="font-size:12px; color:#94a3b8; margin-bottom:6px;">Маппер: <b>${m.mapper}</b></div>
                            <div class="pack-meta-row">
                                <span class="pill-meta">${m.packBpm}</span>
                                <span class="pill-meta">${m.packStars}</span>
                            </div>
                        </div>
                        <div style="display:flex; gap:8px; margin-top:12px;">
                            <a href="${m.link}" target="_blank" class="osu-btn" style="flex:1; text-align:center; text-decoration:none; font-size:12px; padding:8px 12px; background:rgba(0,255,242,0.15); border:1px solid var(--neon-cyan); color:#fff;">
                                🌐 Открыть карту
                            </a>
                        </div>
                    </div>
                `;
            });
        }

        // ================= TAB 4: OBSIDIAN SECOND BRAIN =================
        async function loadVaultNotes() {
            try {
                const res = await fetch('/api/vault/notes');
                const data = await res.json();
                allNotes = data.notes || [];

                const listEl = document.getElementById('vaultNotesList');
                listEl.innerHTML = '';
                if (allNotes.length === 0) {
                    listEl.innerHTML = '<div style="color:#64748b; padding:20px;">Заметки не найдены в osu-vault/</div>';
                    return;
                }

                allNotes.forEach((n, idx) => {
                    const item = document.createElement('div');
                    item.className = 'vault-note-item' + (idx === 0 ? ' active' : '');
                    item.innerHTML = `
                        <div class="v-note-title">📄 ${n.filename}</div>
                        <div class="v-note-mtime">Обновлено: ${n.mtime}</div>
                    `;
                    item.onclick = () => selectVaultNote(idx, item);
                    listEl.appendChild(item);
                });

                if (allNotes.length > 0) {
                    renderNoteMarkdown(allNotes[0].content);
                }
            } catch (e) {
                console.error('Vault load error:', e);
            }
        }

        function selectVaultNote(index, el) {
            document.querySelectorAll('.vault-note-item').forEach(i => i.classList.remove('active'));
            el.classList.add('active');
            renderNoteMarkdown(allNotes[index].content);
        }

        function renderNoteMarkdown(content) {
            const reader = document.getElementById('vaultNoteContent');
            if (window.marked) {
                reader.innerHTML = marked.parse(content);
            } else {
                reader.innerText = content;
            }
        }

        async function openVaultExplorer() {
            await fetch('/api/vault/open');
            showToast('Папка osu-vault открыта в Проводнике Windows', '📂');
        }

        // ================= TAB 5: SETTINGS =================
        function calcTabletArea() {
            const w = parseFloat(document.getElementById('cfgAreaW').value) || 78;
            const h = parseFloat(document.getElementById('cfgAreaH').value) || 43.88;
            const style = document.getElementById('cfgGripStyle').value;
            const ratio = (w / (h || 1)).toFixed(2);
            const diag = Math.round(Math.sqrt(w*w + h*h));

            const is169 = Math.abs(ratio - 1.78) < 0.05;
            const ratioEl = document.getElementById('cfgAreaRatio');
            ratioEl.innerText = is169 ? `${ratio} (16:9 ✓)` : `${ratio} (Не 16:9)`;
            ratioEl.style.color = is169 ? 'var(--neon-green)' : '#f59e0b';
            document.getElementById('cfgAreaDiag').innerText = `Диагональ: ~${diag} мм`;

            const adviceEl = document.getElementById('cfgTabletAdvice');
            let text = '';
            if (!is169) {
                text += '⚠️ <b>Внимание:</b> Соотношение не 16:9! Горизонтальная и вертикальная скорость различаются, что ломает мышечную память на углах. В OpenTabletDriver включи <b>Lock Aspect Ratio</b>. ';
            } else {
                text += '✓ <b>Пропорция идеальна (16:9):</b> Движение пера строго согласовано с экраном. ';
            }

            if (w < 65) {
                text += 'Область довольно мала (<65 мм) — возможен тремор пера на мелких кругах 5★. ';
            } else if (w > 92) {
                text += 'Область широкая (>92 мм) — пальцам трудно дотягиваться до дальних углов, возможен under-aim. ';
            } else {
                text += `Ширина ${w} мм — золотой баланс скорости и точности для 4-5★. `;
            }

            if (style === 'hover') {
                text += 'Для стиля <b>Hover</b> обязательно подключи фильтр <i>Devocub</i> или <i>Reconstructor</i> в OTD, чтобы гасить дрожание пера в воздухе.';
            } else {
                text += 'При стиле <b>Drag</b> естественное трение помогает резко стопать перо (Snap) прямо на ноте.';
            }

            adviceEl.innerHTML = `💡 <b>Совет тренера по ГП:</b> ${text}`;
        }

        function updateKeyBinds() {
            const k1 = document.getElementById('cfgKey1').value.toUpperCase() || 'Z';
            const k2 = document.getElementById('cfgKey2').value.toUpperCase() || 'X';
            keyK1 = k1;
            keyK2 = k2;
            document.getElementById('badgeK1').innerText = `K1: [ ${k1} ]`;
            document.getElementById('badgeK2').innerText = `K2: [ ${k2} ]`;
            showToast(`Кнопки ритм-тренажера обновлены: ${k1} и ${k2}`, '⌨️');
        }

        window.onload = init;
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:8765")
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
