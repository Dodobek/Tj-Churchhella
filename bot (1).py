"""
Telegram-бот магазина сухофруктов: курага, чурчхела (5 вкусов), сушёное яблоко.
4 языка интерфейса (ru/tg/uz/en) с автоматической конвертацией валюты,
корзина, оформление заказа с уведомлением владельцу, вопрос производителю,
история заказов.

Запуск:
    1. pip install -r requirements.txt
    2. export BOT_TOKEN="токен_от_BotFather"
    3. export OWNER_CHAT_ID="ваш_telegram_chat_id"
    4. python bot.py
"""

import asyncio
import logging
import os

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import db
import keep_alive
from config import BOT_TOKEN, CURRENCIES, LANGUAGE_NAMES, OWNER_CHAT_ID, PRODUCTS, QTY_PRESETS, SUPPORTED_LANGUAGES
from locales import t

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

NO_VARIANT = "_"  # плейсхолдер для товаров без вариантов (курага)

# ──────────────────────────────────────────────────────────────────────────
# УТИЛИТЫ
# ──────────────────────────────────────────────────────────────────────────


def format_qty(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def format_money(value: float, currency_code: str) -> str:
    if currency_code == "UZS":
        return f"{value:,.0f}".replace(",", " ")
    return f"{value:,.2f}".replace(",", " ")


def convert_price(price_tjs: float, lang: str) -> tuple[str, str]:
    cur = CURRENCIES[lang]
    value = price_tjs * cur["rate_from_tjs"]
    return format_money(value, cur["code"]), cur["symbol"]


def get_product(product_key: str) -> dict:
    return PRODUCTS[product_key]


def get_variant(product_key: str, variant_key: str) -> dict | None:
    product = get_product(product_key)
    if not product.get("variants") or variant_key == NO_VARIANT:
        return None
    return product["variants"][variant_key]


def item_name(product_key: str, variant_key: str, lang: str) -> str:
    product = get_product(product_key)
    if variant_key != NO_VARIANT and product.get("variants"):
        variant = product["variants"][variant_key]
        return f'{product["name"][lang]} — {variant["name"][lang]}'
    return product["name"][lang]


def item_price_tjs(product_key: str) -> float | None:
    return get_product(product_key).get("price_tjs")


async def ensure_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    """Возвращает язык пользователя. Если язык ещё не выбран — показывает выбор языка и возвращает None."""
    user_id = update.effective_user.id
    lang = context.user_data.get("lang") or db.get_user_lang(user_id)
    if lang:
        context.user_data["lang"] = lang
        return lang
    await send_language_picker(update, context)
    return None


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(t("btn_products", lang))],
        [KeyboardButton(t("btn_cart", lang)), KeyboardButton(t("btn_orders", lang))],
        [KeyboardButton(t("btn_question", lang)), KeyboardButton(t("btn_language", lang))],
    ]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def resolve_menu_action(text: str, lang: str) -> str | None:
    mapping = {
        t("btn_products", lang): "products",
        t("btn_cart", lang): "cart",
        t("btn_orders", lang): "orders",
        t("btn_question", lang): "question",
        t("btn_language", lang): "language",
    }
    return mapping.get(text)


async def send_language_picker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"setlang:{code}")]
        for code, name in LANGUAGE_NAMES.items()
    ]
    text = t("choose_language", "ru")
    if update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await update.effective_message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


async def send_main_menu(chat_id: int, lang: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=chat_id,
        text=t("welcome", lang),
        reply_markup=main_menu_keyboard(lang),
        parse_mode=ParseMode.HTML,
    )


async def send_card(context: ContextTypes.DEFAULT_TYPE, chat_id: int, photo, caption: str, reply_markup):
    if photo:
        try:
            if str(photo).startswith("http"):
                await context.bot.send_photo(chat_id, photo=photo, caption=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
                return
            else:
                with open(photo, "rb") as f:
                    await context.bot.send_photo(chat_id, photo=f, caption=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
                return
        except Exception:
            logger.warning("Не удалось отправить фото %s — отправляю без картинки.", photo, exc_info=True)
    # Фото нет, не задано или не удалось загрузить — отправляем просто текст, чтобы бот не завис
    await context.bot.send_message(chat_id, text=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


async def edit_or_reply(query, text: str, reply_markup):
    try:
        if query.message.photo:
            await query.edit_message_caption(caption=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception:
        await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


# ──────────────────────────────────────────────────────────────────────────
# КАТАЛОГ
# ──────────────────────────────────────────────────────────────────────────


async def show_catalog(chat_id: int, lang: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    buttons = [
        [InlineKeyboardButton(product["name"][lang], callback_data=f"cat:{key}")]
        for key, product in PRODUCTS.items()
    ]
    await context.bot.send_message(
        chat_id=chat_id,
        text=t("catalog_title", lang),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML,
    )


def price_line(product_key: str, lang: str) -> str:
    price_tjs = item_price_tjs(product_key)
    if price_tjs is None:
        return t("price_unknown", lang)
    price_str, currency = convert_price(price_tjs, lang)
    return t("price_per_kg", lang, price=price_str, currency=currency)


async def open_category(query, product_key: str, lang: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    product = get_product(product_key)

    if product.get("variants"):
        caption = f'<b>{product["name"][lang]}</b>\n\n{product["description"][lang]}\n\n{price_line(product_key, lang)}'
        buttons = [
            [InlineKeyboardButton(v["name"][lang], callback_data=f"var:{product_key}:{vkey}")]
            for vkey, v in product["variants"].items()
        ]
        buttons.append([InlineKeyboardButton(t("btn_back", lang), callback_data="backcatalog")])
        buttons.append([InlineKeyboardButton(t("btn_back_to_menu", lang), callback_data="gohome")])
        await send_card(context, query.message.chat_id, product.get("photo"), caption, InlineKeyboardMarkup(buttons))
    else:
        await send_qty_picker_card(query.message.chat_id, product_key, NO_VARIANT, lang, context)


async def open_variant(query, product_key: str, variant_key: str, lang: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_qty_picker_card(query.message.chat_id, product_key, variant_key, lang, context)


async def send_qty_picker_card(
    chat_id: int,
    product_key: str,
    variant_key: str,
    lang: str,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Отправляет карточку товара/варианта (фото + описание + цена) с кнопками выбора кг."""
    product = get_product(product_key)
    variant = get_variant(product_key, variant_key)

    name = item_name(product_key, variant_key, lang)
    description = variant["description"][lang] if variant else product["description"][lang]
    photo = variant.get("photo") if variant and variant.get("photo") else product.get("photo")

    caption = f'<b>{name}</b>\n\n{description}\n\n{price_line(product_key, lang)}\n\n{t("choose_qty", lang)}'

    qty_buttons = [
        InlineKeyboardButton(f"{format_qty(q)} кг", callback_data=f"qty:{product_key}:{variant_key}:{q}")
        for q in QTY_PRESETS
    ]
    rows = [qty_buttons[i : i + 3] for i in range(0, len(qty_buttons), 3)]
    rows.append([InlineKeyboardButton(t("btn_custom_qty", lang), callback_data=f"qtycustom:{product_key}:{variant_key}")])
    rows.append([InlineKeyboardButton(t("btn_back", lang), callback_data="backcatalog")])
    rows.append([InlineKeyboardButton(t("btn_back_to_menu", lang), callback_data="gohome")])

    await send_card(context, chat_id, photo, caption, InlineKeyboardMarkup(rows))


async def confirm_qty_screen(query, product_key: str, variant_key: str, qty: float, lang: str) -> None:
    name = item_name(product_key, variant_key, lang)
    text = f'<b>{name}</b>\n\n{t("selected_qty", lang, qty=format_qty(qty))}'
    buttons = [
        [InlineKeyboardButton(t("btn_add_to_cart", lang), callback_data=f"addcart:{product_key}:{variant_key}:{qty}")],
        [InlineKeyboardButton(t("btn_change_qty", lang), callback_data=f"changeqty:{product_key}:{variant_key}")],
        [InlineKeyboardButton(t("btn_back", lang), callback_data="backcatalog")],
        [InlineKeyboardButton(t("btn_back_to_menu", lang), callback_data="gohome")],
    ]
    await edit_or_reply(query, text, InlineKeyboardMarkup(buttons))


# ──────────────────────────────────────────────────────────────────────────
# КОРЗИНА
# ──────────────────────────────────────────────────────────────────────────


def compute_cart(rows, lang: str):
    lines = []
    total = 0.0
    has_unknown = False
    cur = CURRENCIES[lang]
    for row in rows:
        name = item_name(row["product_key"], row["variant_key"] or NO_VARIANT, lang)
        qty = row["qty_kg"]
        if row["price_tjs"] is None:
            lines.append(t("cart_line_unknown", lang, name=name, qty=format_qty(qty)))
            has_unknown = True
        else:
            unit_price = row["price_tjs"] * cur["rate_from_tjs"]
            line_sum = unit_price * qty
            total += line_sum
            lines.append(
                t(
                    "cart_line_known",
                    lang,
                    name=name,
                    qty=format_qty(qty),
                    price=format_money(unit_price, cur["code"]),
                    currency=cur["symbol"],
                    sum=format_money(line_sum, cur["code"]),
                )
            )
    return lines, total, has_unknown


async def show_cart(chat_id: int, user_id: int, lang: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    rows = db.get_cart(user_id)
    if not rows:
        await context.bot.send_message(chat_id, t("cart_empty", lang), parse_mode=ParseMode.HTML)
        return

    lines, total, has_unknown = compute_cart(rows, lang)
    cur = CURRENCIES[lang]
    text = t("cart_title", lang) + "\n\n" + "\n".join(lines)
    if total > 0:
        text += t("cart_total", lang, total=format_money(total, cur["code"]), currency=cur["symbol"])
    if has_unknown:
        text += t("cart_note_unknown_prices", lang)

    buttons = [
        [InlineKeyboardButton(t("btn_order", lang), callback_data="cartorder")],
        [InlineKeyboardButton(t("btn_receipt", lang), callback_data="cartreceipt")],
        [InlineKeyboardButton(t("btn_clear_cart", lang), callback_data="cartclearask")],
        [InlineKeyboardButton(t("btn_back_to_catalog", lang), callback_data="backcatalog")],
        [InlineKeyboardButton(t("btn_back_to_menu", lang), callback_data="gohome")],
    ]
    await context.bot.send_message(chat_id, text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)


async def build_receipt_text(user_id: int, lang: str) -> str | None:
    rows = db.get_cart(user_id)
    if not rows:
        return None
    lines, total, has_unknown = compute_cart(rows, lang)
    cur = CURRENCIES[lang]
    text = t("receipt_title", lang) + "\n\n" + "\n".join(lines)
    if total > 0:
        text += t("cart_total", lang, total=format_money(total, cur["code"]), currency=cur["symbol"])
    if has_unknown:
        text += t("cart_note_unknown_prices", lang)
    return text


async def place_order(chat_id: int, user, lang: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    rows = db.get_cart(user.id)
    if not rows:
        await context.bot.send_message(chat_id, t("cart_empty", lang), parse_mode=ParseMode.HTML)
        return

    lines, total, has_unknown = compute_cart(rows, lang)
    cur = CURRENCIES[lang]
    total_str = f"{format_money(total, cur['code'])} {cur['symbol']}" if total > 0 else "—"

    items_payload = [
        {
            "name": item_name(r["product_key"], r["variant_key"] or NO_VARIANT, lang),
            "qty_kg": r["qty_kg"],
        }
        for r in rows
    ]
    order_id = db.create_order(user.id, user.username, lang, items_payload, total_str)
    db.clear_cart(user.id)

    await context.bot.send_message(
        chat_id, t("order_placed_user", lang, order_id=order_id), parse_mode=ParseMode.HTML
    )

    # Уведомление владельцу
    username_display = f"@{user.username}" if user.username else f"id {user.id}"
    full_name = " ".join(filter(None, [user.first_name, user.last_name])) or "—"
    admin_text = (
        f"🆕 <b>Новый заказ №{order_id}</b>\n\n"
        f"👤 Клиент: {full_name} ({username_display})\n"
        f"🌐 Язык клиента: {LANGUAGE_NAMES.get(lang, lang)}\n\n"
        + "\n".join(lines)
        + (f"\n\n💵 <b>Итого: {total_str}</b>" if total > 0 else "")
        + ("\n\n⚠️ Есть позиции без цены — согласуйте с клиентом." if has_unknown else "")
    )
    await notify_owner(context, admin_text)


async def notify_owner(context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    try:
        owner_id = int(OWNER_CHAT_ID)
    except (ValueError, TypeError):
        logger.warning("OWNER_CHAT_ID не настроен — уведомление не отправлено.")
        return
    try:
        await context.bot.send_message(owner_id, text, parse_mode=ParseMode.HTML)
    except Exception:
        logger.exception("Не удалось отправить уведомление владельцу.")


# ──────────────────────────────────────────────────────────────────────────
# ЗАКАЗЫ ПОЛЬЗОВАТЕЛЯ
# ──────────────────────────────────────────────────────────────────────────


async def show_orders(chat_id: int, user_id: int, lang: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    orders = db.get_user_orders(user_id)
    if not orders:
        await context.bot.send_message(chat_id, t("orders_empty", lang), parse_mode=ParseMode.HTML)
        return

    parts = [t("orders_title", lang)]
    for o in orders:
        import json

        items = json.loads(o["items_json"])
        items_str = ", ".join(f'{i["name"]} ({format_qty(i["qty_kg"])} кг)' for i in items)
        date_str = o["created_at"][:16].replace("T", " ")
        parts.append(f'\n<b>№{o["id"]}</b> · {date_str}\n{items_str}\n💵 {o["total_str"]}')

    await context.bot.send_message(chat_id, "\n".join(parts), parse_mode=ParseMode.HTML)


# ──────────────────────────────────────────────────────────────────────────
# ХЕНДЛЕРЫ
# ──────────────────────────────────────────────────────────────────────────


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = await ensure_lang(update, context)
    if lang:
        await send_main_menu(update.effective_chat.id, lang, context)


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    try:
        await _handle_callback(query, update, context)
    except Exception:
        logger.exception("Ошибка при обработке нажатия кнопки: data=%s", query.data)
        lang = context.user_data.get("lang") or db.get_user_lang(update.effective_user.id) or "ru"
        try:
            await context.bot.send_message(
                query.message.chat_id,
                "⚠️ Что-то пошло не так. Попробуйте ещё раз или вернитесь в меню.",
            )
            await send_main_menu(query.message.chat_id, lang, context)
        except Exception:
            logger.exception("Не удалось отправить сообщение об ошибке пользователю.")


async def _handle_callback(query, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = query.data
    user = update.effective_user

    if data.startswith("setlang:"):
        lang = data.split(":", 1)[1]
        db.set_user_lang(user.id, user.username, lang)
        context.user_data["lang"] = lang
        await query.message.reply_text(t("language_changed", lang), parse_mode=ParseMode.HTML)
        await send_main_menu(query.message.chat_id, lang, context)
        return

    lang = context.user_data.get("lang") or db.get_user_lang(user.id)
    if not lang:
        await send_language_picker(update, context)
        return

    if data == "backcatalog":
        await show_catalog(query.message.chat_id, lang, context)
        return

    if data == "gohome":
        await send_main_menu(query.message.chat_id, lang, context)
        return

    if data.startswith("cat:"):
        product_key = data.split(":", 1)[1]
        await open_category(query, product_key, lang, context)
        return

    if data.startswith("var:"):
        _, product_key, variant_key = data.split(":", 2)
        await open_variant(query, product_key, variant_key, lang, context)
        return

    if data.startswith("qty:"):
        _, product_key, variant_key, qty_str = data.split(":", 3)
        await confirm_qty_screen(query, product_key, variant_key, float(qty_str), lang)
        return

    if data.startswith("qtycustom:"):
        _, product_key, variant_key = data.split(":", 2)
        context.user_data["awaiting_qty"] = (product_key, variant_key)
        await query.message.reply_text(t("ask_custom_qty", lang))
        return

    if data.startswith("changeqty:"):
        _, product_key, variant_key = data.split(":", 2)
        await send_qty_picker_card(query.message.chat_id, product_key, variant_key, lang, context)
        return

    if data.startswith("addcart:"):
        _, product_key, variant_key, qty_str = data.split(":", 3)
        qty = float(qty_str)
        price_tjs = item_price_tjs(product_key)
        db.add_to_cart(user.id, product_key, None if variant_key == NO_VARIANT else variant_key, qty, price_tjs)
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(t("btn_go_to_cart", lang), callback_data="gocart")],
                [InlineKeyboardButton(t("btn_back_to_catalog", lang), callback_data="backcatalog")],
                [InlineKeyboardButton(t("btn_back_to_menu", lang), callback_data="gohome")],
            ]
        )
        await edit_or_reply(query, t("item_added", lang), buttons)
        return

    if data == "gocart":
        await show_cart(query.message.chat_id, user.id, lang, context)
        return

    if data == "cartorder":
        await place_order(query.message.chat_id, user, lang, context)
        return

    if data == "cartreceipt":
        receipt = await build_receipt_text(user.id, lang)
        if receipt:
            await query.message.reply_text(receipt, parse_mode=ParseMode.HTML)
        else:
            await query.message.reply_text(t("cart_empty", lang), parse_mode=ParseMode.HTML)
        return

    if data == "cartclearask":
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton(t("btn_yes", lang), callback_data="cartclearyes"), InlineKeyboardButton(t("btn_no", lang), callback_data="cartclearno")]]
        )
        await query.message.reply_text(t("clear_cart_confirm", lang), reply_markup=buttons)
        return

    if data == "cartclearyes":
        db.clear_cart(user.id)
        await query.edit_message_text(t("cart_cleared", lang))
        return

    if data == "cartclearno":
        await query.message.delete()
        return


async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await _handle_text(update, context)
    except Exception:
        logger.exception("Ошибка при обработке текстового сообщения.")
        user = update.effective_user
        lang = context.user_data.get("lang") or db.get_user_lang(user.id) or "ru"
        try:
            await update.message.reply_text("⚠️ Что-то пошло не так. Попробуйте ещё раз или вернитесь в меню.")
            await send_main_menu(update.effective_chat.id, lang, context)
        except Exception:
            logger.exception("Не удалось отправить сообщение об ошибке пользователю.")


async def _handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    text = update.message.text.strip()

    lang = context.user_data.get("lang") or db.get_user_lang(user.id)
    if not lang:
        await send_language_picker(update, context)
        return

    # Ожидание количества кг (после нажатия "Своё количество")
    if "awaiting_qty" in context.user_data:
        product_key, variant_key = context.user_data["awaiting_qty"]
        normalized = text.replace(",", ".")
        try:
            qty = float(normalized)
            if qty <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text(t("qty_invalid", lang))
            return
        del context.user_data["awaiting_qty"]
        name = item_name(product_key, variant_key, lang)
        msg_text = f'<b>{name}</b>\n\n{t("selected_qty", lang, qty=format_qty(qty))}'
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(t("btn_add_to_cart", lang), callback_data=f"addcart:{product_key}:{variant_key}:{qty}")],
                [InlineKeyboardButton(t("btn_change_qty", lang), callback_data=f"changeqty:{product_key}:{variant_key}")],
                [InlineKeyboardButton(t("btn_back", lang), callback_data="backcatalog")],
            ]
        )
        await update.message.reply_text(msg_text, reply_markup=buttons, parse_mode=ParseMode.HTML)
        return

    # Ожидание текста вопроса производителю
    if context.user_data.get("awaiting_question"):
        context.user_data["awaiting_question"] = False
        username_display = f"@{user.username}" if user.username else f"id {user.id}"
        full_name = " ".join(filter(None, [user.first_name, user.last_name])) or "—"
        admin_text = f"❓ <b>Вопрос от клиента</b>\n👤 {full_name} ({username_display})\n\n{text}"
        await notify_owner(context, admin_text)
        await update.message.reply_text(t("question_sent", lang), parse_mode=ParseMode.HTML)
        return

    # Кнопки главного меню
    action = resolve_menu_action(text, lang)
    if action == "products":
        await show_catalog(update.effective_chat.id, lang, context)
    elif action == "cart":
        await show_cart(update.effective_chat.id, user.id, lang, context)
    elif action == "orders":
        await show_orders(update.effective_chat.id, user.id, lang, context)
    elif action == "question":
        context.user_data["awaiting_question"] = True
        await update.message.reply_text(t("question_prompt", lang), parse_mode=ParseMode.HTML)
    elif action == "language":
        await send_language_picker(update, context)
    # иначе — молча игнорируем нераспознанный текст


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Ошибка при обработке обновления:", exc_info=context.error)


def main() -> None:
    if BOT_TOKEN == "PUT_YOUR_TOKEN_HERE":
        raise SystemExit("Не задан BOT_TOKEN. Установите переменную окружения BOT_TOKEN.")

    db.init_db()
    keep_alive.start()
    asyncio.set_event_loop(asyncio.new_event_loop())

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CallbackQueryHandler(callback_router))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    application.add_error_handler(error_handler)

    logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
