import json
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from github import Github

load_dotenv()

SECRET_KEY = os.getenv("CONTENT_KEY")
if not SECRET_KEY:
    raise ValueError("CONTENT_KEY не найден!")

cipher = Fernet(SECRET_KEY.encode())

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_FILE_PATH = os.getenv("GITHUB_FILE_PATH")

if not all([GITHUB_TOKEN, GITHUB_REPO, GITHUB_FILE_PATH]):
    raise ValueError("GITHUB_TOKEN, GITHUB_REPO или GITHUB_FILE_PATH не настроены!")

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)

def save_content_to_github(data: dict):
    raw = json.dumps(data, ensure_ascii=False, indent=2).encode()
    encrypted = cipher.encrypt(raw)
    
    try:
        repo.update_file(
            GITHUB_FILE_PATH,
            "Update content",
            encrypted.decode(),
            repo.get_contents(GITHUB_FILE_PATH).sha
        )
        return True
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False

def load_content_from_github():
    try:
        content = repo.get_contents(GITHUB_FILE_PATH)
        encrypted = content.decoded_content
        decrypted = cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return {}