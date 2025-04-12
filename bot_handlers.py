from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import add, add_user_mapping
import logging

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    add(chat_id)
    await update.message.reply_text('✅ Вы подписаны на обновления!')

async def send_notification(application, chat_id: int, message: str):
    try:
        await application.bot.send_message(
            chat_id=chat_id,
            text=message
        )
    except Exception as e:
        logging.error(f"Ошибка отправки: {e}")


async def set_github(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        await update.message.reply_text('❌ Укажите ваш GitHub-логин. Пример: /setgithub mylogin')
        return

    github_login = args[0].strip()
    add_user_mapping(chat_id, github_login)
    await update.message.reply_text(f'✅ GitHub-логин {github_login} привязан к вашему чату!')
