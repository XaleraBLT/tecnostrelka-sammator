import datetime
import os
from dotenv import load_dotenv
import json
import asyncio
from aiogram.types import FSInputFile
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import WebAppInfo, CallbackQuery, ChatMemberUpdated, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import user_bot

load_dotenv()
# Инициализация бота
bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()

# Константы
DATA_FILE = "data.json"
DEFAULT_SETTINGS = {
    "channels_to": [],
    "channels_from": [],
    "hours": 128,
    "max_posts": None,
    "history": [],
    "style": "Аналитический",
    "message_id": 18,
    "run": False
}

class States(StatesGroup):
    waiting_for_data = State()

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

@dp.message(StateFilter(States.waiting_for_data))
async def edit_data(message: types.Message, state: FSMContext):
    markup = InlineKeyboardBuilder([[InlineKeyboardButton(text="↩ | Назад", callback_data="main")]])

    try:
        data_new = message.text
        try:
            await bot.delete_message(message.chat.id, message.message_id - 1)
        except Exception:
            pass
        await message.delete()
        data_new = json.loads(data_new)

        data = json.loads(open("data.json", encoding="utf-8").read())

        timel = data_new["post_frequency"]
        if timel.split()[1] == "days":
            hours = int(timel.split()[0]) * 24
        else:
            hours = int(timel.split()[0])
        print(hours)

        data[f"{message.from_user.id}"]["channels_from"] = data_new["channels"]
        data[f"{message.from_user.id}"]["hours"] = hours
        data[f"{message.from_user.id}"]["max_posts"] = int(data_new["news_count"])
        data[f"{message.from_user.id}"]["style"] = data_new["writing_style"] + " " + data_new["custom_style_description"]


        with open("data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        await state.clear()
        await message.answer_photo(photo=FSInputFile("./images/edit.png"), text="Данные заполнены успешно! Чтобы запустить", reply_markup=markup.as_markup())
    except Exception as e:
        print(e)
        await message.answer(photo=FSInputFile("./images/error.png"), text="Данные заполнены неправильно! Может быть воспользуетесь конфигуратором?", reply_markup=markup.as_markup())


@dp.message()
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    try:
        await bot.delete_message(message.chat.id, message.message_id - 1)
    except Exception:
        pass
    await message.delete()

    data = load_data()
    user_id = str(message.from_user.id)

    # Инициализация данных пользователя, если их нет
    if user_id not in data:
        data[user_id] = DEFAULT_SETTINGS.copy()
        save_data(data)

    # Создаем кнопки в зависимости от состояния
    button_text = "⏹ | Остановить" if data[user_id]["run"] else "▶ | Запустить"
    button_callback = "stop" if data[user_id]["run"] else "run"


    await message.answer_photo(photo=FSInputFile("./images/Welcome.png"), caption=
        """Привет! 👋 Я — ваш инвестиционный саммари-бот, который помогает отслеживать и анализировать ключевые инвестиционные сообщения. 📈

Каждый раз, когда появляется новое сообщение или обновление, я создам для вас краткий обзор с основными моментами, чтобы вы могли принимать решения быстро и без лишней суеты. Просто отправьте мне запрос, и я покажу вам самые важные новости и события на рынке.

Давайте вместе держать руку на пульсе инвестиций! 💼""",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=button_text,
                    callback_data=button_callback
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="📝 | Настройки",
                    callback_data="edit"
                )
            ]
        ])
    )
    print(2)

@dp.callback_query(F.data == "main")
async def main_menu(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    try:
        await bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
    except Exception:
        pass

    await callback.message.delete()

    data = load_data()
    user_id = str(callback.message.from_user.id)

    # Инициализация данных пользователя, если их нет
    if user_id not in data:
        data[user_id] = DEFAULT_SETTINGS.copy()
        save_data(data)

    # Создаем кнопки в зависимости от состояния
    button_text = "⏹ | Остановить" if data[user_id]["run"] else "▶ | Запустить"
    button_callback = "stop" if data[user_id]["run"] else "run"

    await callback.message.answer_photo(photo=FSInputFile("./images/Welcome.png"), caption=
        """Привет! 👋 Я — ваш инвестиционный саммари-бот, который помогает отслеживать и анализировать ключевые инвестиционные сообщения. 📈

Каждый раз, когда появляется новое сообщение или обновление, я создам для вас краткий обзор с основными моментами, чтобы вы могли принимать решения быстро и без лишней суеты. Просто отправьте мне запрос, и я покажу вам самые важные новости и события на рынке.

Давайте вместе держать руку на пульсе инвестиций! 💼""",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=button_text,
                    callback_data=button_callback
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="📝 | Настройки",
                    callback_data="edit"
                )
            ]
        ])
    )

@dp.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def bot_added_to_group(event: ChatMemberUpdated):
    if event.chat.type == "private":
        return

    data = load_data()
    user_id = str(event.from_user.id)
    group_id = event.chat.id

    if user_id not in data:
        data[user_id] = DEFAULT_SETTINGS.copy()

    if group_id not in data[user_id]["channels_to"]:
        data[user_id]["channels_to"].append(group_id)
        save_data(data)

@dp.callback_query(F.data == "edit")
async def edit_settings(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    user_id = str(callback.from_user.id)
    data = load_data()
    settings = data.get(user_id, DEFAULT_SETTINGS.copy())

    settings_preview = (
        f"<b>📦 Текущие настройки:</b>\n\n"
        f"<b>📡 Каналы-источники:</b> {', '.join(map(str, settings.get('channels_from', []))) or '—'}\n"
        f"<b>⏱ Частота:</b> каждые {settings.get('hours', 0)} часов\n"
        f"<b>📰 Макс. постов:</b> {settings.get('max_posts', '—')}\n"
        f"<b>🎨 Стиль:</b> {settings.get('style', '—')}\n"
    )

    text = settings_preview + "\n<i>Введите новые json-данные:</i>"

    markup = InlineKeyboardBuilder([
        [InlineKeyboardButton(text="↩ | Назад", callback_data="main")],
        [InlineKeyboardButton(text="✏ | Конфигуратор", web_app=WebAppInfo(url="https://xalera.space/"))]
    ])

    await callback.message.answer_photo(FSInputFile("./images/config.png"), text, reply_markup=markup.as_markup(), parse_mode="html")
    await state.set_state(States.waiting_for_data)


@dp.callback_query(F.data.in_(["run", "stop"]))
async def handle_bot_state(callback: CallbackQuery):
    data = load_data()
    user_id = str(callback.from_user.id)

    if user_id not in data:
        await callback.answer("Ошибка: данные пользователя не найдены", show_alert=True)
        return

    # Обновляем состояние
    data[user_id]["run"] = callback.data == "run"
    save_data(data)

    # Обновляем кнопку
    button_text = "⏹ | Остановить" if data[user_id]["run"] else "▶ | Запустить"
    button_callback = "stop" if data[user_id]["run"] else "run"

    await callback.message.edit_reply_markup(
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=button_text,
                    callback_data=button_callback
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="📝 | Настройки",
                    callback_data="edit")
            ]
        ])
    )

    if data[user_id]["run"]:
        await asyncio.create_task(run_bot_for_user(user_id))
    try:
        await callback.message.delete()
    except:
        pass
    await callback.answer(f"Самматор {'запущен' if data[user_id]['run'] else 'остановлен'}")


async def run_bot_for_user(user_id: str):
    while True:
        data = load_data()

        # Проверяем, должен ли бот продолжать работать
        if user_id not in data or not data[user_id]["run"]:
            break

        user_data = data[user_id]
        post = await user_bot.get_result(int(user_id))

        # Отправляем пост во все каналы
        for channel_id in user_data["channels_to"]:
            try:
                await bot.send_message(chat_id=channel_id, text=post, parse_mode="html")
            except Exception as e:
                print(f"Ошибка при отправке в канал {channel_id}: {e}")

        # Ждем указанное количество часов
        await asyncio.sleep(user_data["hours"] * 3600)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())