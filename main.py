import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application, CommandHandler

from bot_handlers import start, send_notification, set_github
from config import TELEGRAM_TOKEN
from database import init_db, get_all, get_chat_id_by_github_login
from github_handler import get_issues, get_due_date

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def check_deadlines(app: Application):
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).date()

    for issue in get_issues():
        due_date = get_due_date(issue)
        if not due_date:
            continue

        delta = (due_date - now).days
        message = None

        if delta in [10, 5, 3, 2, 1]:
            message = f'⏳ Задача "{issue.title}"\nДо дедлайна: {delta} дней\nСсылка: {issue.html_url}'
        elif delta < 0:
            message = f'🔴 Задача "{issue.title}"\nПросрочена: {-delta} дней\nСсылка: {issue.html_url}'

        if message:
            # Проверяем, есть ли assignee
            if issue.assignee:
                github_login = issue.assignee.login
                chat_id = get_chat_id_by_github_login(github_login)
                if chat_id:
                    await send_notification(app, chat_id, message)
                else:
                    logging.info(f"Нет chat_id для GitHub-логина {github_login}")
            else:
                # Если assignee нет, отправляем всем подписчикам
                for chat_id in get_all():
                    await send_notification(app, chat_id, message)


async def main():
    init_db()
    global application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setgithub", set_github))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_deadlines, 'cron', hour=9, minute=0, args=[application])
    scheduler.start()

    await application.initialize()
    await application.start()
    logging.info("Бот успешно запущен")

    await test_notifications()

    try:
        await application.updater.start_polling()
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Остановка бота...")
    finally:
        await application.stop()
        scheduler.shutdown()


async def test_notifications():
    logging.info("Тестирование уведомлений...")
    await check_deadlines(application)
    logging.info("Тест завершен.")


if __name__ == '__main__':
    asyncio.run(main())
