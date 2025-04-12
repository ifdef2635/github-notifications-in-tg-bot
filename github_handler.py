import re
from datetime import datetime
from config import repo
from functools import lru_cache

_last_update = None
_cache_timeout = 300


@lru_cache(maxsize=1)
def get_issues_cached(timestamp):
    return list(repo.get_issues(state='open'))


def get_issues():
    global _last_update
    current_time = datetime.now().timestamp()

    if _last_update is None or (current_time - _last_update) > _cache_timeout:
        _last_update = current_time
        return get_issues_cached(current_time)
    return get_issues_cached(_last_update)


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
    date_formats = ['%Y-%m-%d', '%Y.%m.%d', '%d/%m/%Y', '%d-%m-%Y']

    for pattern in patterns:
        match = re.search(pattern, issue.body, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            date_str = re.sub(r'[.\s/]', '-', date_str)
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