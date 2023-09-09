import logging
from pathlib import Path
from typing import Tuple, Any

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from db import Database
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Configure logging
logging.basicConfig(level=logging.INFO)


TOKEN = "6155093611:AAGQKG0uQP-li7EBIkphJbI0UBZCiOZmgGI"
I18N_DOMAIN = "django"

from aiogram.utils import i18n
BASE_DIR = Path(__file__).parent
# Specify the path to your locale directory
LOCALES_DIR = BASE_DIR / "backend/locales"

# Compile the 'en' locale
i18n.I18nCompilers(locale_dir=LOCALES_DIR).compile()




bot = Bot(TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
db = Database(path_to_db="backend/db.sqlite3")


# LANG_STORAGE = {}
LANGS = ["ru", "en", "uz"]


class Localization(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> str:
        """
        User locale getter
        You can override the method if you want to use different way of getting user language.
        :param action: event name
        :param args: event arguments
        :return: locale name
        """
        user: types.User = types.User.get_current()
        # print(user)
        user_data = db.select_user(tg_id=user.id)
        # print(user_data)
        if user_data is None:
            db.add_user(tg_id=user.id, full_name=user.first_name, user_name=user.username, language=user.language_code)
            # LANG_STORAGE[user.id] = "en"
        *_, data = args
        language = data['locale'] = db.get_lang(tg_id=user.id)[0]

        return language


# Setup i18n middleware
i18n = Localization(I18N_DOMAIN, LOCALES_DIR)
dp.middleware.setup(i18n)

# Alias for gettext method
_ = i18n.lazy_gettext


numbers = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(_("One"))],
        [types.KeyboardButton(_("Two"))],
        [types.KeyboardButton(_("Three"))],
    ],
    resize_keyboard=True,
)

langs = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=_("🇺🇿 Uzbek"), callback_data='uz')],
        [InlineKeyboardButton(text=_("🇷🇺 Russian"), callback_data='ru')],
        [InlineKeyboardButton(text=_("🏴󠁧󠁢󠁥󠁮󠁧󠁿 English"), callback_data='en')]
    ]
)


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):

    await message.answer(
        _("Hello, <b>{user}</b>!").format(user=message.from_user.full_name),
        reply_markup=langs,
    )


@dp.message_handler(commands="lang")
async def cmd_lang(message: types.Message, locale):
    await message.answer(
        _("Your current language: <i>{language}</i>").format(language=locale), reply_markup=numbers
    )


@dp.message_handler(commands="setlang")
async def cmd_setlang(message: types.Message):
    lang = message.get_args()

    if not lang:
        return await message.answer(_("Specify your language.\nExample: /setlang en"))
    if lang not in LANGS:
        return await message.answer(_("This language is not available. Use en or ru or uz"))

    # LANG_STORAGE[message.from_user.id] = lang
    db.update_user_lang(lang=lang, tg_id=message.from_user.id)

    await message.answer(_("Language set.", locale=lang))


@dp.callback_query_handler(text="en")
async def change_lang_en(call: types.CallbackQuery):
    db.update_user_lang(lang='en', tg_id=call.from_user.id)
    await call.message.edit_text("You are choice english")


@dp.callback_query_handler(text="ru")
async def change_lang_ru(call: types.CallbackQuery):
    db.update_user_lang(lang='ru', tg_id=call.from_user.id)
    await call.message.edit_text("Вы выбирали русский язык")


@dp.callback_query_handler(text="uz")
async def change_lang_en(call: types.CallbackQuery):
    db.update_user_lang(lang='uz', tg_id=call.from_user.id)
    await call.message.edit_text("Siz o'zbek tilini tanladingiz")


@dp.message_handler(text=_("One"))
async def text_one(message: types.Message):
    await message.answer(_("Really one"))


@dp.message_handler(text=_("Two"))
async def text_two(message: types.Message):
    await message.answer(_("Really two"))


@dp.message_handler(text=_("Three"))
async def text_three(message: types.Message):
    await message.answer(_("Really three"))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
