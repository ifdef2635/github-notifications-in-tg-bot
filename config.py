import os
from functools import lru_cache

from dotenv import load_dotenv
from github import Auth, Github

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = os.getenv('REPO_NAME')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


def check_config():
    """Падает с понятным сообщением, если не заданы переменные окружения."""
    missing = [name for name in ('GITHUB_TOKEN', 'REPO_NAME', 'TELEGRAM_TOKEN')
               if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            'Не заданы переменные окружения: ' + ', '.join(missing)
            + '. Укажите их в файле .env (см. README).')


@lru_cache(maxsize=1)
def get_repo():
    """Репозиторий создаётся при первом обращении, а не при импорте модуля."""
    return Github(auth=Auth.Token(GITHUB_TOKEN)).get_repo(REPO_NAME)
