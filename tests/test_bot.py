import os
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from github_handler import get_due_date, parse_deadline
from notifications import build_message, days_word, get_recipients


def issue(body=None, due_on=None, assignees=()):
    milestone = SimpleNamespace(due_on=due_on) if due_on else None
    return SimpleNamespace(
        body=body, milestone=milestone,
        assignees=[SimpleNamespace(login=login) for login in assignees])


class DeadlineParsingTest(unittest.TestCase):
    def test_formats(self):
        for body in ('Дедлайн: 2025-04-08', 'Deadline: 2025.04.08',
                     'дедлайн: 08/04/2025', 'Дедлайн 08-04-2025'):
            self.assertEqual(parse_deadline(issue(body)), date(2025, 4, 8), body)

    def test_none(self):
        self.assertIsNone(parse_deadline(issue(None)))
        self.assertIsNone(parse_deadline(issue('без даты')))
        self.assertIsNone(parse_deadline(issue('Дедлайн: 2025-13-45')))

    def test_milestone_wins(self):
        due = datetime(2025, 5, 1, tzinfo=timezone.utc)
        self.assertEqual(get_due_date(issue('Дедлайн: 2025-04-08', due_on=due)),
                         date(2025, 5, 1))


class MessageTest(unittest.TestCase):
    def test_days_word(self):
        words = {1: 'день', 2: 'дня', 5: 'дней', 11: 'дней', 12: 'дней',
                 21: 'день', 22: 'дня', 25: 'дней'}
        for n, word in words.items():
            self.assertEqual(days_word(n), word, n)

    def test_build_message(self):
        self.assertIn('Осталось 3 дня', build_message('T', 'u', 3))
        self.assertIn('Осталось 1 день', build_message('T', 'u', 1))
        self.assertIn('Просрочена: 2 дня', build_message('T', 'u', -2))
        for delta in (0, 4, 7, 11):
            self.assertIsNone(build_message('T', 'u', delta))


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        database.DB_PATH = os.path.join(self.dir.name, 'users.db')
        database.init_db()

    def tearDown(self):
        self.dir.cleanup()

    def test_login_is_case_insensitive_and_replaced(self):
        database.add_user_mapping(1, 'Alice')
        self.assertEqual(database.get_chat_id_by_github_login('alice'), 1)
        database.add_user_mapping(1, 'alice2')
        self.assertIsNone(database.get_chat_id_by_github_login('alice'))
        database.add_user_mapping(2, 'ALICE2')
        self.assertEqual(database.get_chat_id_by_github_login('alice2'), 2)

    def test_remove_clears_everything(self):
        database.add(1)
        database.add_user_mapping(1, 'bob')
        database.remove(1)
        self.assertEqual(database.get_all(), [])
        self.assertIsNone(database.get_chat_id_by_github_login('bob'))

    def test_recipients(self):
        database.add(1)
        database.add(2)
        database.add_user_mapping(2, 'bob')
        database.add_user_mapping(3, 'carol')
        self.assertEqual(sorted(get_recipients(issue())), [1, 2])
        self.assertEqual(get_recipients(issue(assignees=['bob', 'carol', 'nobody'])),
                         [2, 3])
        self.assertEqual(get_recipients(issue(assignees=['nobody'])), [])


if __name__ == '__main__':
    unittest.main()
