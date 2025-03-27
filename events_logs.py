import wmi
import json
import time
from datetime import datetime

# Определяем события, которые хотим отслеживать
WATCHED_EVENTS = {
    4625: "Неудачная попытка входа",
    4771: "Ошибка аутентификации Kerberos",
    4776: "Ошибка проверки учетных данных NTLM",
    4624: "Успешный вход",
    4672: "Вход с привилегиями администратора",
    4688: "Запуск нового процесса",
    7034: "Неожиданный сбой службы",
    7045: "Установка новой службы",
    5156: "Разрешённое соединение через брандмауэр",
    5157: "Заблокированное соединение через брандмауэр",
    4663: "Доступ к файлу",
    4720: "Создана новая учетная запись",
    4732: "Добавление пользователя в группу администраторов"
}

def get_security_events():
    c = wmi.WMI("localhost", privileges=["Security"])
    watcher = c.Win32_NTLogEvent.watch_for(notification_type="Creation", Logfile="Security")
    
    while True:
        event = watcher()
        event_id = event.EventCode
        if event_id in WATCHED_EVENTS:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_id": event_id,
                "event_type": WATCHED_EVENTS[event_id],
                "message": event.InsertionStrings if event.InsertionStrings else "No details"
            }
            print(json.dumps(log_entry, indent=4, ensure_ascii=False))
            analyze_event(log_entry)
        
        time.sleep(1)

def analyze_event(log_entry):
    """Анализ событий на угрозы и аномалии."""
    event_id = log_entry["event_id"]
    
    if event_id == 4625:
        print("⚠ Обнаружена неудачная попытка входа!")
    elif event_id == 4688 and "powershell.exe" in log_entry.get("message", "").lower():
        print("⚠ Подозрительный запуск PowerShell!")
    elif event_id == 4720:
        print("⚠ Создана новая учетная запись! Возможно, инсайдерская угроза.")
    
if __name__ == "__main__":
    print("[+] Мониторинг событий безопасности Windows...")
    get_security_events()
