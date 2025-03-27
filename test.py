import wmi
import pythoncom
import pickle
import os
import telebot
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest

# Твой токен Telegram
BOT_TOKEN = "7688031766:AAHdy2pFPEqXCYaV0LyvCL5FiKKHRr-sRNU"
bot = telebot.TeleBot(BOT_TOKEN)
CHAT_ID = "728491010"
MODEL_FILE = "isolation_forest_model.pkl"
ANOMALY_LOG = "anomalies.log"

THREAT_CATEGORIES = {
    "Brute-force атака": [4625, 4771, 4776],
    "Подключение RDP": [4624, 4778, 4779],
    "Повышение привилегий": [4672, 4673, 4674],
    "Запуск вредоносного процесса": [4688, 7045],
    "Сетевые атаки": [5156, 5157, 4754, 4755],
    "Попытка эксфильтрации данных": [4663, 4656]
}

def train_anomaly_detector(event_messages):
    print("[!] Обучение модели на отфильтрованных событиях...")
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(event_messages)
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)
    with open(MODEL_FILE, "wb") as f:
        pickle.dump((model, vectorizer), f)
    print("[+] Обучение завершено.")
    return model, vectorizer

def load_anomaly_detector():
    if os.path.exists(MODEL_FILE):
        with open(MODEL_FILE, "rb") as f:
            return pickle.load(f)
    return None, None

def detect_anomaly(model, vectorizer, event_message):
    X = vectorizer.transform([event_message])
    return model.predict(X)[0] == -1

def format_time(timestamp):
    return datetime.strptime(timestamp.split('.')[0], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")

def log_anomaly(event_id, event_message, event_time):
    with open(ANOMALY_LOG, "a") as f:
        f.write(f"{event_time} | Event ID: {event_id} | {event_message}\n")

def send_telegram_message(event_id, event_message, event_time, is_anomaly):
    category = next((cat for cat, ids in THREAT_CATEGORIES.items() if event_id in ids), None)
    if not category:
        return
    event_time = format_time(event_time)
    
    if is_anomaly:
        log_anomaly(event_id, event_message, event_time)
        print(f"🚨 Аномальное событие! Время: {event_time}, Категория: {category}, Event ID: {event_id}")
        bot.send_message(CHAT_ID, f"""🚨 Аномальное событие!
🔹 Время: {event_time}
🔹 Категория: {category}
🔹 Event ID: {event_id}
🔹 Описание: {event_message}""")
    else:
        print(f"✅ Обычное событие. Время: {event_time}, Категория: {category}, Event ID: {event_id}")
        bot.send_message(CHAT_ID, f"""✅ Обычное событие
🔹 Время: {event_time}
🔹 Категория: {category}
🔹 Event ID: {event_id}""")

def get_security_events():
    pythoncom.CoInitialize()
    c = wmi.WMI()
    watcher = c.Win32_NTLogEvent.watch_for(notification_type="Creation", Logfile="Security")
    model, vectorizer = load_anomaly_detector()
    event_messages = []
    
    if model is None:
        print("[!] Обучение модели...")
        while len(event_messages) < 200:
            event = watcher()
            event_id = event.EventCode
            if any(event_id in ids for ids in THREAT_CATEGORIES.values()):
                event_messages.append(event.Message)
        model, vectorizer = train_anomaly_detector(event_messages)
    
    print("[+] Мониторинг событий...")
    while True:
        event = watcher()
        event_id = event.EventCode
        event_message = event.Message
        event_time = event.TimeGenerated

        if any(event_id in ids for ids in THREAT_CATEGORIES.values()):
            is_anomaly = detect_anomaly(model, vectorizer, event_message)
            send_telegram_message(event_id, event_message, event_time, is_anomaly)
            print("[-] Событие обработано.\n")

print("[+] Бот запущен...")
get_security_events()
