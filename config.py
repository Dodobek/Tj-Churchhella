"""
Конфигурация магазина: токен бота, ID владельца, курсы валют и каталог товаров.
Все "человеческие" тексты (названия, описания) хранятся по языкам:
ru — русский, en — английский.
"""

import os

# ──────────────────────────────────────────────────────────────────────────
# ОСНОВНЫЕ НАСТРОЙКИ
# ──────────────────────────────────────────────────────────────────────────

BOT_TOKEN = os.environ.get("BOT_TOKEN", "PUT_YOUR_TOKEN_HERE")

# Telegram chat_id владельца (получателя уведомлений о заказах и вопросах).
# Как узнать свой chat_id: напишите боту @userinfobot в Telegram, он пришлёт ваш ID.
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID", "PUT_YOUR_CHAT_ID_HERE")

DB_PATH = os.environ.get("DB_PATH", "shop.db")

# ──────────────────────────────────────────────────────────────────────────
# ВАЛЮТЫ
# Базовая валюта — сомони (TJS). Курсы — ПРИМЕРНЫЕ, обновляйте вручную,
# так как курс валют меняется. Формула: цена_в_валюте = цена_в_somoni * rate.
# ──────────────────────────────────────────────────────────────────────────

CURRENCIES = {
    "ru": {"code": "TJS", "symbol": "смн", "rate_from_tjs": 1.0},
    "en": {"code": "TJS", "symbol": "смн", "rate_from_tjs": 1.0},
}

LANGUAGE_NAMES = {
    "ru": "Русский 🇷🇺",
    "en": "English 🇬🇧",
}

SUPPORTED_LANGUAGES = ["ru", "en"]

# ──────────────────────────────────────────────────────────────────────────
# КАТАЛОГ ТОВАРОВ
# photo: прямая ссылка на изображение (https://...) ИЛИ путь к локальному файлу
#        (например "photos/kuraga.jpg") ИЛИ None, если фото пока нет —
#        тогда бот просто не будет прикреплять картинку.
# price_tjs: цена за 1 кг в сомони. None — значит цена уточняется у производителя.
# ──────────────────────────────────────────────────────────────────────────

PRODUCTS = {
    "kuraga": {
        "name": {
            "ru": "Курага",
            "en": "Dried Apricots (Kuraga)",
        },
        "description": {
            "ru": "Натуральная курага без сахара и консервантов — вяленый абрикос, "
            "в меру плотный, с насыщенным медовым вкусом. Отличный перекус и источник "
            "калия, клетчатки и витаминов.",
            "en": "Natural dried apricots (kuraga) with no added sugar or preservatives — "
            "sweet, chewy, with a rich honey-like taste. A great snack and a good source "
            "of potassium, fiber and vitamins.",
        },
        "photo": None,  # TODO: добавить фото — ссылку или photos/kuraga.jpg
        "price_tjs": None,  # TODO: уточнить цену за 1 кг
        "variants": None,
    },
    "churchkhela": {
        "name": {
            "ru": "Турецкая чурчхела (сучук)",
            "en": "Turkish Churchkhela (Sujuk)",
        },
        "description": {
            "ru": "Орехи в нити, обмакнутые в загущённый фруктовый сок и высушенные. "
            "Плотная, тягучая сладость без сахара и муки — натуральный источник энергии. "
            "5 вкусов на выбор 👇",
            "en": "Walnuts strung on a thread, dipped in thickened fruit juice and dried. "
            "A dense, chewy natural sweet with no added sugar or flour. 5 flavors to choose 👇",
        },
        "photo": None,  # TODO: сюда встанет фото, которое вы пришлёте
        "price_tjs": 85,
        "variants": {
            "apple": {
                "name": {"ru": "🟢 Яблоко (зелёное)", "en": "🟢 Apple (green)"},
                "description": {
                    "ru": "На яблочном соке — мягкий, освежающий вкус.",
                    "en": "Made with apple juice — soft, refreshing flavor.",
                },
                "photo": "photos/churchkhela_apple.jpg",
            },
            "lemon": {
                "name": {"ru": "🟡 Лимон (жёлтое)", "en": "🟡 Lemon (yellow)"},
                "description": {
                    "ru": "На лимонном соке — с приятной кислинкой.",
                    "en": "Made with lemon juice — pleasantly tangy.",
                },
                "photo": "photos/churchkhela_lemon.jpg",
            },
            "orange": {
                "name": {"ru": "🟠 Апельсин (оранжевое)", "en": "🟠 Orange"},
                "description": {
                    "ru": "На апельсиновом соке — яркий цитрусовый вкус.",
                    "en": "Made with orange juice — bright citrus flavor.",
                },
                "photo": "photos/churchkhela_orange.jpg",
            },
            "dark": {
                "name": {"ru": "⚫️ Тёмный (ангур/виноград)", "en": "⚫️ Dark (grape / angur)"},
                "description": {
                    "ru": "На виноградном соке — насыщенный, тёмный, слегка терпкий вкус.",
                    "en": "Made with grape juice — rich, dark and slightly tart.",
                },
                "photo": "photos/churchkhela_dark.jpg",
            },
            "red": {
                "name": {"ru": "🔴 Красный (гранат)", "en": "🔴 Red (pomegranate)"},
                "description": {
                    "ru": "На гранатовом соке — кисло-сладкий, насыщенный вкус.",
                    "en": "Made with pomegranate juice — tangy-sweet and rich.",
                },
                "photo": "photos/churchkhela_red.jpg",
            },
        },
    },
    "dried_apple": {
        "name": {
            "ru": "Сушёное яблоко",
            "en": "Dried Apple",
        },
        "description": {
            "ru": "Натуральные яблочные дольки, высушенные традиционным способом — "
            "сохраняют вкус и аромат свежих яблок. 2 вида на выбор 👇",
            "en": "Natural apple slices dried the traditional way — they keep the taste "
            "and aroma of fresh apples. 2 varieties to choose 👇",
        },
        "photo": None,  # TODO: добавить фото
        "price_tjs": None,  # TODO: уточнить цену за 1 кг
        "variants": {
            "red": {
                "name": {"ru": "🔴 Красное яблоко", "en": "🔴 Red apple"},
                "description": {
                    "ru": "Из красных яблок — более сладкий вкус.",
                    "en": "Made from red apples — sweeter taste.",
                },
                "photo": None,
            },
            "green": {
                "name": {"ru": "🟢 Зелёное яблоко", "en": "🟢 Green apple"},
                "description": {
                    "ru": "Из зелёных яблок — с приятной кислинкой.",
                    "en": "Made from green apples — pleasantly tart.",
                },
                "photo": None,
            },
        },
    },
}

# Пресеты количества (в кг), которые предлагаются кнопками при выборе объёма
QTY_PRESETS = [10, 25, 50, 100]
