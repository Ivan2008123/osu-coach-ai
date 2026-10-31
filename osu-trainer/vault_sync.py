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
