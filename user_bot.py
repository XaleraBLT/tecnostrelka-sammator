import asyncio
import json
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import Message
import datetime
import pytz
import neuro

load_dotenv()

# Настройки
api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
phone = os.environ["PHONE"]
password = os.environ["PASSWORD"]
timezone = 'Europe/Moscow'
tz = pytz.timezone(timezone)


async def create_client():
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start(
        phone=phone,
        password=password,
        code_callback=lambda: input("Введите код из Telegram: ")
    )
    return client


def is_in_time_range(post_time, start_str, end_str):
    try:
        post_time = post_time.astimezone(tz)
        start_time = datetime.datetime.strptime(start_str, '%H:%M %d.%m.%Y').replace(tzinfo=tz)
        end_time = datetime.datetime.strptime(end_str, '%H:%M %d.%m.%Y').replace(tzinfo=tz)
        return start_time <= post_time <= end_time
    except ValueError as e:
        print(f"Ошибка формата времени: {e}")
        return False


async def get_posts(client, start_input, end_input, channel_username):
    messages = await client.get_messages(channel_username, limit=200)
    found_posts = [
        msg for msg in messages
        if isinstance(msg, Message) and is_in_time_range(msg.date, start_input, end_input)
    ]

    posts = []
    if found_posts:
        print(f"\nНайдено постов: {len(found_posts)}")
        for i, post in enumerate(found_posts, 1):
            if post.text:
                post_time = post.date.astimezone(tz)
                print(f"\n[{i}] {post_time.strftime('%H:%M %d.%m.%Y')}")
                posts.append(post.text + f" [ИСТОЧНИК {channel_username}]")
    else:
        print("Постов не найдено")

    return posts


async def get_result(client_id: int):
    client = await create_client()
    print("\nАвторизация успешна!")

    with open("data.json", encoding="utf-8") as file:
        data = json.load(file)

    hours = data[f"{client_id}"]["hours"]
    channels = data[f"{client_id}"]["channels_from"]
    all_posts = []

    for channel in channels:
        posts = await get_posts(
            client,
            (datetime.datetime.now(tz) - datetime.timedelta(hours=hours)).strftime("%H:%M %d.%m.%Y"),
            datetime.datetime.now(tz).strftime("%H:%M %d.%m.%Y"),
            channel
        )
        all_posts.extend(posts)

    await client.disconnect()

    if all_posts:
        post = neuro.get_post(all_posts, client_id)
        return post
    return "Не найдено подходящих постов"


async def main():
    post = await get_result(0)

if __name__ == "__main__":
    asyncio.run(main())