import os
from datetime import datetime

VAULT_MEMORY_PATH = r"C:\Users\iples\Downloads\osu\osu-vault\06_Вторая_Память_Агента.md"

def sync_score_to_vault(data):
    """
    Автоматически записывает сыгранную сессию во Вторую Память Obsidian Vault
    """
    if not os.path.exists(VAULT_MEMORY_PATH):
        return

    try:
        time_str = data.get("time", datetime.now().strftime("%Y-%m-%d %H:%M"))
        score_val = data.get("score", "0")
        acc_val = f"{data.get('accuracy', 0)}%"
        hits_str = f"{data.get('count_300', 0)} / {data.get('count_100', 0)} / {data.get('count_50', 0)} / {data.get('count_miss', 0)}"
        focus_title = data.get("focus_title", "Анализ сессии")

        # Формируем строку таблицы
        new_row = f"| **{time_str}** | Скор: {score_val} | **{acc_val}** | {hits_str} | {focus_title} |\n"

        with open(VAULT_MEMORY_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # Добавляем в таблицу, если этой записи еще нет
        if f"Скор: {score_val}" not in content:
            target_marker = "| :--- | :--- | :--- | :--- | :--- |\n"
            if target_marker in content:
                parts = content.split(target_marker, 1)
                updated_content = parts[0] + target_marker + new_row + parts[1]
                with open(VAULT_MEMORY_PATH, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                print(f"[Vault Sync] Успешно записан новый результат в Obsidian: {score_val}")
    except Exception as e:
        print("[Vault Sync Error]:", e)

def sync_session_summary_to_vault(summary):
    """
    Записывает агрегированную сводку сессии в Obsidian Vault
    """
    if not os.path.exists(VAULT_MEMORY_PATH):
        return False
    try:
        games_count = summary.get("games_count", 0)
        avg_acc = summary.get("avg_acc", 0)
        best_score = summary.get("best_score", "0")
        total_300 = summary.get("total_300", 0)
        total_100 = summary.get("total_100", 0)
        total_50 = summary.get("total_50", 0)
        total_miss = summary.get("total_miss", 0)
        ratio_100 = summary.get("ratio_100", 0)
        time_span = summary.get("session_time_span", datetime.now().strftime("%Y-%m-%d %H:%M"))

        row_id = f"Сессия ({games_count} игр): Скор {best_score}"
        new_row = f"| **{time_span}** | {row_id} | **{avg_acc}%** | {total_300} / {total_100} / {total_50} / {total_miss} | Сводка: {ratio_100}% ранних нажатий (Early Tap) |\n"

        with open(VAULT_MEMORY_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        if row_id not in content:
            target_marker = "| :--- | :--- | :--- | :--- | :--- |\n"
            if target_marker in content:
                parts = content.split(target_marker, 1)
                updated_content = parts[0] + target_marker + new_row + parts[1]
                with open(VAULT_MEMORY_PATH, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                print(f"[Vault Sync] Успешно записана сводка сессии в Obsidian: {avg_acc}% Acc")
                return True
    except Exception as e:
        print("[Vault Sync Session Error]:", e)
    return False

def sync_rhythm_session_to_vault(session_data):
    """
    Записывает результаты разминки в ритм-тренажере в Obsidian Vault
    """
    if not os.path.exists(VAULT_MEMORY_PATH):
        return False
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        bpm = session_data.get("bpm", 165)
        taps = session_data.get("taps", 0)
        acc = session_data.get("acc", 0)
        ur = session_data.get("ur", 0)
        k1_ratio = session_data.get("k1_ratio", 50)
        k2_ratio = session_data.get("k2_ratio", 50)

        entry = (
            f"\n- **[{now_str}] Разминка в Ритм-Тренажере**: "
            f"Темп **{bpm} BPM** | Тапов: {taps} | Точность: **{acc}%** | UR: {ur} | Баланс пальцев: {k1_ratio}% K1 / {k2_ratio}% K2\n"
        )
        with open(VAULT_MEMORY_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        target = "## 🎮 Сессионный Журнал (Play Session History)"
        if target in content:
            parts = content.split(target, 1)
            updated = parts[0] + target + "\n" + entry + parts[1]
            with open(VAULT_MEMORY_PATH, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"[Vault Sync] Успешно сохранена разминка в Obsidian: {bpm} BPM, {acc}% Acc")
            return True
    except Exception as e:
        print("[Vault Sync Rhythm Error]:", e)
    return False
