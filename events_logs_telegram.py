import requests
import wmi
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest
import pickle
import os

# Твой токен и chat ID
BOT_TOKEN = "7688031766:AAHdy2pFPEqXCYaV0LyvCL5FiKKHRr-sRNU"
CHAT_ID = "728491010"

# Файл для сохранения модели
MODEL_FILE = "isolation_forest_model.pkl"

def send_telegram_message(message):
    """Функция отправки уведомлений в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[Ошибка отправки в Telegram] {e}")

def train_anomaly_detector(event_messages):
    """Обучение Isolation Forest на нормальных событиях"""
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(event_messages)

    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)

    # Сохраняем модель и TF-IDF в файл
    with open(MODEL_FILE, "wb") as f:
        pickle.dump((model, vectorizer), f)

    return model, vectorizer

def load_anomaly_detector():
    """Загрузка модели из файла (если есть)"""
    if os.path.exists(MODEL_FILE):
        with open(MODEL_FILE, "rb") as f:
            return pickle.load(f)
    return None, None

def detect_anomaly(model, vectorizer, event_message):
    """Определяет, является ли событие аномальным"""
    X = vectorizer.transform([event_message])
    prediction = model.predict(X)  # -1 = аномалия, 1 = нормальное событие
    return prediction[0] == -1

def get_security_events():
    """Функция мониторинга событий безопасности Windows"""
    c = wmi.WMI()
    watcher = c.Win32_NTLogEvent.watch_for(notification_type="Creation", Logfile="Security")

    # Загружаем или обучаем модель
    model, vectorizer = load_anomaly_detector()
    event_messages = []

    if model is None:
        print("[!] Модель не найдена, сначала собираем данные...")
        while len(event_messages) < 200:
            event = watcher()
            event_messages.append(event.Message)
            print(f"[Сбор данных] {len(event_messages)}/200")

        print("[+] Обучаем модель аномалий...")
        model, vectorizer = train_anomaly_detector(event_messages)

    print("[+] Мониторинг событий запущен...")

    while True:
        event = watcher()
        event_id = event.EventCode
        event_message = event.Message

        # Проверяем на аномалию
        if detect_anomaly(model, vectorizer, event_message):
            send_telegram_message(f"🚨 Аномальное событие!\n🔹 Event ID: {event_id}\n🔹 Описание: {event_message}")
            print(f"[Аномалия] ID {event_id} отправлен в Telegram.")

if __name__ == "__main__":
    get_security_events()
