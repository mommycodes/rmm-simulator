import json
import base64
import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv
load_dotenv()

# Генерация ключа
SECRET_KEY = os.getenv("CONTENT_KEY")
if not SECRET_KEY:
    raise ValueError("KEY не найден!")

cipher = Fernet(SECRET_KEY.encode())

STORAGE_FILE = "content.json.enc"


def save_content(data: dict):
    """Сохраняем словарь разделов в зашифрованный файл"""
    raw = json.dumps(data, ensure_ascii=False, indent=2).encode()
    encrypted = cipher.encrypt(raw)
    with open(STORAGE_FILE, "wb") as f:
        f.write(encrypted)


def load_content() -> dict:
    """Загружаем словарь разделов из зашифрованного файла"""
    if not os.path.exists(STORAGE_FILE):
        return {}
    with open(STORAGE_FILE, "rb") as f:
        encrypted = f.read()
    try:
        decrypted = cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())
    except Exception:
        return {}
