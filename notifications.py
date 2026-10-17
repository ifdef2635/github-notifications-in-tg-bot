import asyncio
import logging
from datetime import datetime, timezone

from database import get_all, get_chat_id_by_github_login
from github_handler import get_due_date, get_issues
from bot_handlers import send_notification

REMIND_DAYS = (10, 5, 3, 2, 1)


def days_word(n):
    """Склонение слова «день»: 1 день, 2 дня, 5 дней, 11 дней, 21 день."""
    if 11 <= n % 100 <= 14:
        return 'дней'
    return {1: 'день', 2: 'дня', 3: 'дня', 4: 'дня'}.get(n % 10, 'дней')


def build_message(title, url, delta):
    """Текст уведомления; delta — дней до дедлайна (отрицательное — просрочка)."""
    if delta in REMIND_DAYS:
        return (f'⏳ Задача "{title}"\n'
                f'Осталось {delta} {days_word(delta)} до дедлайна\n'
                f'Ссылка: {url}')
    if delta < 0:
        return (f'🔴 Задача "{title}"\n'
                f'Просрочена: {-delta} {days_word(-delta)}\n'
                f'Ссылка: {url}')
    return None


def get_recipients(issue):
    """Чаты assignee'ов задачи (с привязанным логином); без assignee — все подписчики."""
    logins = [assignee.login for assignee in issue.assignees]
    if not logins:
        return get_all()

    chat_ids = []
    for login in logins:
        chat_id = get_chat_id_by_github_login(login)
        if chat_id is None:
            logging.info(f'Нет chat_id для GitHub-логина {login}')
        elif chat_id not in chat_ids:
            chat_ids.append(chat_id)
    return chat_ids


async def check_deadlines(app):
    today = datetime.now(timezone.utc).date()

    # PyGithub делает сетевые запросы синхронно — не блокируем event loop.
    try:
        issues = await asyncio.to_thread(get_issues)
    except Exception:
        logging.exception('Не удалось получить задачи из GitHub')
        return

    for issue in issues:
        due_date = get_due_date(issue)
        if not due_date:
            continue

        message = build_message(issue.title, issue.html_url, (due_date - today).days)
        if message:
            for chat_id in get_recipients(issue):
                await send_notification(app, chat_id, message)
