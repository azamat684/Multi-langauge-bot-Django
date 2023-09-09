from pathlib import Path
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.i18n import I18nMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)


TOKEN = '6155093611:AAGQKG0uQP-li7EBIkphJbI0UBZCiOZmgGI'
I18N_DOMAIN = 'mybot'

BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'

bot = Bot(TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# Setup i18n middleware
i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)
dp.middleware.setup(i18n)

# Alias for gettext method
_ = i18n.gettext


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    # Simply use `_('message')` instead of `'message'` and never use f-strings for translatable texts.
    await message.reply(_('Hello, <b>{user}</b>!').format(user=message.from_user.full_name))


@dp.message_handler(commands='lang')
async def cmd_lang(message: types.Message, locale):
    # For setting custom lang you have to modify i18n middleware
    await message.reply(_('Your current language: <i>{language}</i>').format(language=locale))


# If you care about pluralization, here's small handler
# And also, there's and example of comments for translators. Most translation tools support them.

# Alias for gettext method, parser will understand double underscore as plural (aka ngettext)
__ = i18n.gettext


# some likes manager
LIKES_STORAGE = {'count': 0}


def get_likes() -> int:
    return LIKES_STORAGE['count']


def increase_likes() -> int:
    LIKES_STORAGE['count'] += 1
    return get_likes()


@dp.message_handler(commands='like')
async def cmd_like(message: types.Message, locale):
    likes = increase_likes()

    # NOTE: This is comment for a translator
    await message.reply(__('Aiogram has {number} like!', 'Aiogram has {number} likes!', likes).format(number=likes))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
