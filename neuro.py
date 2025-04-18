import json
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
# Инициализация клиента

client = OpenAI(
    api_key=os.environ["API_TOKEN_DS"],
    base_url="https://api.deepseek.com",
)

def save_data(data: dict):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



def get_post(posts_original: list, client_id: int):
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)


    style = data[f"{client_id}"]["style"]
    history = data[f"{client_id}"]["history"]
    max_posts = data[f"{client_id}"]["max_posts"]

    if not history:
        history = [
            {
                "role": "system",
                "content": """1. Фильтрация контента:
        - Отсеивай непроверенные/сомнительные данные (отмечай низкую достоверность)
        - Объединяй дублирующие инвестиционные новости-посты, оставляя наиболее информативный вариант
        - Выделяй ключевые тезисы и цифры инвестиционных новостей-постов
        - Удаляй новости-посты, которые кажутся сомнительными (например реклама, щит-посты, контент не содержащий смысловой и полезной нагрузки для инвестора)
        - Проверяй на дубликат всю историю чата (т.е. все посты которые были в истории чата)

        2. Структура подачи (на каждый кейс):
        [Заголовок] - кратко, ёмко, с эмодзи
        [Описание] - 2-3 предложения сути
        [Факторы/причины] - маркированный список
        [Последствия] - четкие формулировки
        [Прогноз] - при наличии данных
        [Источники] - @ссылки на каналы (будут приложены к посту)

        3. Стилистика (по умолчанию - информационный):
        - Информационный (info): нейтральный тон, факты, цифры
        - Телеграфный (telegraph): короткие предложения, только суть
        - Аналитический (analytical): с прогнозами и интерпретацией
        - Упрощенный (simple): минимум терминов, пояснения
        - Кликбейт (clickbait): эмоциональные заголовки (по запросу)
        - Свой выбор (custom): пользователь сам пришлёт описание стиля

        4. Форматирование (HTML для Telegram):
        <b>Заголовки</b>
        <i>Описание</i>
        • Списки
        ✓ Перечисления
        [Курсив для источников]

        5. Дополнительно:
        - Добавляй эмодзи для визуального разделения (не более 3-4 на блок)
        - Сохраняй единый стиль внутри одного обзора
        - Для цифр указывай период сравнения (г/г, м/м)
        - Отмечай конфликтующие данные разных источников
        - Максимальное ограничение по количеству под-постов (не всегда указывается), если под-постов много, то выбирай те посты, которые наиболее информативны

        Пример вывода (единичного под-поста):
        <b>📌 Рост инфляции до 7.8% г/г</b>
        <i>По данным Росстата за март, годовая инфляция ускорилась на 0.5 п.п.</i>

        Основные драйверы:
        • Продовольствие +9.1%
        • Непродовольственные товары +6.7%
        • Услуги +5.4%"""
        }
    ]


    user_message = {
        "role": "user",
        "content": f"{[f'[ПОСТ {i}]: {post}' for i, post in enumerate(posts_original)]}\n\n[СТИЛЬ: {style}]\n[МАКСИМАЛЬНОЕ КОЛИЧЕСТВО ПОД-ПОСТОВ: {max_posts}]"
    }
    history.append(user_message)

    # Отправка запроса к API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=history,
        max_tokens=8192,
    )

    # Получаем и сохраняем ответ
    ai_response = response.choices[0].message.content
    history.append({"role": "assistant", "content": ai_response})

    data[f"{client_id}"]["history"] = history
    save_data(data)

    return ai_response