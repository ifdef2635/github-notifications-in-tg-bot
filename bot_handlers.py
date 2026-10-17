import logging
import re

from telegram import Update
from telegram.error import Forbidden
from telegram.ext import ContextTypes

from database import add, add_user_mapping, remove

# Логин GitHub: буквы, цифры и дефисы, до 39 символов, не начинается с дефиса.
GITHUB_LOGIN_RE = re.compile(r'^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add(update.effective_chat.id)
    await update.message.reply_text(
        '✅ Вы подписаны на обновления!\n'
        'Чтобы получать только свои задачи, привяжите логин: /setgithub <логин>.\n'
        'Отписаться: /stop.')


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    remove(update.effective_chat.id)
    await update.message.reply_text('🔕 Вы отписаны от уведомлений. Вернуться: /start.')


async def send_notification(application, chat_id: int, message: str):
    try:
        await application.bot.send_message(chat_id=chat_id, text=message)
    except Forbidden:
        # Пользователь заблокировал бота — больше не пишем ему.
        logging.info(f'Чат {chat_id} заблокировал бота, подписка удалена')
        remove(chat_id)
    except Exception as e:
        logging.error(f'Ошибка отправки: {e}')


async def set_github(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not context.args:
        await update.message.reply_text('❌ Укажите ваш GitHub-логин. Пример: /setgithub mylogin')
        return

    github_login = context.args[0].strip().lstrip('@')
    if not GITHUB_LOGIN_RE.match(github_login):
        await update.message.reply_text('❌ Некорректный GitHub-логин.')
        return

    add_user_mapping(chat_id, github_login)
    await update.message.reply_text(f'✅ GitHub-логин {github_login} привязан к вашему чату!')
