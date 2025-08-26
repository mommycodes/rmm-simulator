import json
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from github import Github

load_dotenv()

# --- Конфигурация ---
SECRET_KEY = os.getenv("CONTENT_KEY")
if not SECRET_KEY:
    raise ValueError("CONTENT_KEY не найден!")

cipher = Fernet(SECRET_KEY.encode())

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_FILE_PATH = os.getenv("GITHUB_FILE_PATH")

if not all([GITHUB_TOKEN, GITHUB_REPO, GITHUB_FILE_PATH]):
    raise ValueError("GITHUB_TOKEN, GITHUB_REPO или GITHUB_FILE_PATH не настроены!")

# --- Инициализация GitHub ---
g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)


def save_content_to_github(data: dict):
    """Сохраняем словарь разделов в зашифрованный файл и пушим на GitHub"""
    raw = json.dumps(data, ensure_ascii=False, indent=2).encode()
    encrypted = cipher.encrypt(raw)

    # Проверяем, есть ли файл в репозитории
    try:
        contents = repo.get_contents(GITHUB_FILE_PATH)
        repo.update_file(contents.path, "Update content", encrypted, contents.sha)
    except Exception:
        # Если файла нет
        repo.create_file(GITHUB_FILE_PATH, "Create content", encrypted)


def load_content_from_github() -> dict:
    """Загружаем словарь разделов из зашифрованного файла с GitHub"""
    try:
        contents = repo.get_contents(GITHUB_FILE_PATH)
        encrypted = contents.decoded_content
        decrypted = cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())
    except Exception:
        return {}
