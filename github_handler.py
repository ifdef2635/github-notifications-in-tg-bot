import re
import time
from datetime import datetime

from config import get_repo

_CACHE_TTL = 300  # секунд
_cache_time = None
_cache_issues = []


def get_issues():
    """Открытые задачи (без pull request'ов), кэшируются на 5 минут.

    Вызов блокирующий (сетевые запросы PyGithub), из асинхронного кода его
    нужно запускать через asyncio.to_thread.
    """
    global _cache_time, _cache_issues
    if _cache_time is None or time.monotonic() - _cache_time > _CACHE_TTL:
        # GitHub отдаёт pull request'ы вместе с задачами — отбрасываем их.
        _cache_issues = [issue for issue in get_repo().get_issues(state='open')
                         if not issue.pull_request]
        _cache_time = time.monotonic()
    return _cache_issues


def parse_deadline(issue):
    """
    Парсинг дедлайна из тела issue с поддержкой разных форматов.
    Поддерживаемые варианты:
    - Дедлайн: 2025-04-08
    - Deadline: 2025.04.08
    - Дедлайн: 08/04/2025
    - Дедлайн 08-04-2025
    """
    if not issue.body:
        return None

    patterns = [
        # YYYY-MM-DD или YYYY.MM.DD
        r'(?:Дедлайн|Deadline)[:\s]*(\d{4}[-.\s]\d{2}[-.\s]\d{2})',
        # DD/MM/YYYY или DD-MM-YYYY
        r'(?:Дедлайн|Deadline)[:\s]*(\d{2}[-/\s]\d{2}[-/\s]\d{4})',
    ]
    date_formats = ['%Y-%m-%d', '%d-%m-%Y']

    for pattern in patterns:
        match = re.search(pattern, issue.body, re.IGNORECASE)
        if match:
            date_str = re.sub(r'[.\s/]', '-', match.group(1))
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
    return None


def get_due_date(issue):
    """
    Получение даты дедлайна из milestone или тела issue.
    """
    if issue.milestone and issue.milestone.due_on:
        return issue.milestone.due_on.date()
    return parse_deadline(issue)
