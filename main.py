import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application, CommandHandler

from bot_handlers import set_github, start, stop
from config import TELEGRAM_TOKEN, check_config
from database import init_db
from notifications import check_deadlines

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def post_init(app: Application):
    scheduler = AsyncIOScheduler(timezone='UTC')
    scheduler.add_job(check_deadlines, 'cron', hour=9, minute=0, args=[app])
    if os.getenv('CHECK_ON_START') == '1':
        # Для отладки: проверить дедлайны сразу при запуске.
        scheduler.add_job(check_deadlines, 'date', args=[app])
    scheduler.start()
    app.bot_data['scheduler'] = scheduler
    logging.info('Бот успешно запущен')


async def post_shutdown(app: Application):
    app.bot_data['scheduler'].shutdown(wait=False)


def main():
    check_config()
    init_db()

    application = (Application.builder()
                   .token(TELEGRAM_TOKEN)
                   .post_init(post_init)
                   .post_shutdown(post_shutdown)
                   .build())
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stop', stop))
    application.add_handler(CommandHandler('setgithub', set_github))
    application.run_polling()


if __name__ == '__main__':
    main()
