import wmi
import pythoncom
import pickle
import os
import telebot
import logging
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загрузка конфигурации из файла
CONFIG_FILE = "config.txt"
config = {}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        for line in f:
            key, value = line.strip().split("=", 1)
            config[key] = value

BOT_TOKEN = config.get("BOT_TOKEN", "")
CHAT_ID = config.get("CHAT_ID", "")

bot = telebot.TeleBot(BOT_TOKEN)
MODEL_FILE = "isolation_forest_model.pkl"
ANOMALY_LOG_FILE = "anomalies.log"
EVENT_COUNT = 100
FAILED_LOGINS = {}
MAX_FAILED_ATTEMPTS = 3

THREAT_CATEGORIES = {
    "Brute-force атака": [4625, 4771, 4776],
    "Подключение RDP": [4624, 4778, 4779],
    "Повышение привилегий": [4672, 4673, 4674],
    "Запуск вредоносного процесса": [4688, 7045],
    "Сетевые атаки": [5156, 5157, 4754, 4755],
    "Попытка эксфильтрации данных": [4663, 4656]
}

# Закрепление аномальных событий и предпринятых решений
def log_anomaly(event_id, event_message, event_time, action="None"):
    with open(ANOMALY_LOG_FILE, "a") as f:
        f.write(f"{event_time} - Event ID: {event_id} - {event_message} - Action: {action}\n")

# Обучение модели
def train_anomaly_detector(event_messages):
    logging.info("Обучение модели...")
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(event_messages)
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)
    with open(MODEL_FILE, "wb") as f:
        pickle.dump((model, vectorizer), f)
    logging.info("Модель обучена и сохранена.")
    return model, vectorizer

# Загрузка модели
def load_anomaly_detector():
    if os.path.exists(MODEL_FILE):
        logging.info("Загрузка модели...")
        with open(MODEL_FILE, "rb") as f:
            return pickle.load(f)
    return None, None

# Проверка аномалий
def detect_anomaly(model, vectorizer, event_message):
    X = vectorizer.transform([event_message])
    return model.predict(X)[0] == -1

# Форматирование времени
def format_time(timestamp):
    return datetime.strptime(timestamp.split('.')[0], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")

# Блокировка IP при 3 неудачных попытках RDP
def block_ip(ip_address):
    os.system(f"netsh advfirewall firewall add rule name=\"Block {ip_address}\" dir=in action=block remoteip={ip_address}")
    logging.warning(f"IP {ip_address} заблокирован за множественные неудачные попытки входа.")
    return f"IP {ip_address} заблокирован"

# Отправка в Telegram
def send_telegram_message(event_id, event_message, event_time, is_anomaly, action="None"):
    category = next((cat for cat, ids in THREAT_CATEGORIES.items() if event_id in ids), "Другое событие безопасности")
    event_time = format_time(event_time)
    
    if is_anomaly:
        log_anomaly(event_id, event_message, event_time, action)
        message = f"""🚨 Аномальное событие!\n🔹 Время: {event_time}\n🔹 Категория: {category}\n🔹 Event ID: {event_id}\n🔹 Описание: {event_message}\n🔹 Действие: {action}"""
        # logging.warning(f"Аномалия: {message}")
    else:
        message = f"""✅ Обычное событие\n🔹 Время: {event_time}\n🔹 Категория: {category}\n🔹 Event ID: {event_id}"""
        # logging.info(f"Обычное событие: {message}")
    
    bot.send_message(CHAT_ID, message)

# Мониторинг событий безопасности
def get_security_events():
    pythoncom.CoInitialize()
    c = wmi.WMI()
    watcher = c.Win32_NTLogEvent.watch_for(notification_type="Creation", Logfile="Security")
    model, vectorizer = load_anomaly_detector()
    event_messages = []
    
    if model is None:
        logging.info("Сбор данных для обучения...")
        while len(event_messages) < EVENT_COUNT:
            event = watcher()
            if event.EventCode in [id for ids in THREAT_CATEGORIES.values() for id in ids]:
                event_messages.append(event.Message)
                logging.info(f"{len(event_messages)}/{EVENT_COUNT} - ID: {event.EventCode} - {event.Message.splitlines()[0]}...")
        model, vectorizer = train_anomaly_detector(event_messages)
    
    logging.info("Мониторинг событий запущен...")
    while True:
        event = watcher()
        event_id = event.EventCode
        event_message = event.Message
        event_time = event.TimeGenerated
        
        logging.info(f"Событие: ID {event_id}, время: {event_time}, сообщение: {event_message.splitlines()[0]}...")
        action = "None"
        
        if event_id == 4625:  # Неудачная попытка входа
            ip_address = "неизвестно"
            FAILED_LOGINS[ip_address] = FAILED_LOGINS.get(ip_address, 0) + 1
            if FAILED_LOGINS[ip_address] >= MAX_FAILED_ATTEMPTS:
                action = block_ip(ip_address)
                FAILED_LOGINS[ip_address] = 0
        
        if event_id in [id for ids in THREAT_CATEGORIES.values() for id in ids]:
            is_anomaly = detect_anomaly(model, vectorizer, event_message)
            send_telegram_message(event_id, event_message, event_time, is_anomaly, action)

logging.info("Бот запущен...")
get_security_events()