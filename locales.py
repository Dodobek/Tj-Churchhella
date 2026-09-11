"""
Тексты интерфейса бота на 4 языках: ru, tg, uz, en.
"""

TEXTS = {
    "choose_language": {
        "ru": "🌐 Выберите язык / Забон интихоб кунед / Tilni tanlang / Choose language",
        "en": "🌐 Выберите язык / Забон интихоб кунед / Tilni tanlang / Choose language",
    },
    "welcome": {
        "ru": "Добро пожаловать в наш магазин сухофруктов! 🍇🍎🍑\nВыберите действие в меню ниже 👇",
        "en": "Welcome to our dried fruits shop! 🍇🍎🍑\nChoose an action from the menu below 👇",
    },
    "language_changed": {
        "ru": "✅ Язык изменён на русский.",
        "en": "✅ Language changed to English.",
    },
    "btn_products": {
        "ru": "🛍 Показать товары",
        "en": "🛍 Show products",
    },
    "btn_cart": {
        "ru": "🛒 Корзина",
        "en": "🛒 Cart",
    },
    "btn_question": {
        "ru": "❓ Вопрос к производителю",
        "en": "❓ Ask the producer",
    },
    "btn_orders": {
        "ru": "📦 Мои заказы",
        "en": "📦 My orders",
    },
    "btn_language": {
        "ru": "🌐 Язык",
        "en": "🌐 Language",
    },
    "catalog_title": {
        "ru": "🛍 <b>Наши товары</b>\nВыберите категорию:",
        "en": "🛍 <b>Our products</b>\nChoose a category:",
    },
    "choose_flavor": {
        "ru": "Выберите вкус:",
        "en": "Choose a flavor:",
    },
    "choose_variant": {
        "ru": "Выберите вид:",
        "en": "Choose a variety:",
    },
    "price_per_kg": {
        "ru": "💰 Цена: {price} {currency}/кг",
        "en": "💰 Price: {price} {currency}/kg",
    },
    "price_unknown": {
        "ru": "💰 Цена уточняется у производителя",
        "en": "💰 Price to be confirmed with the producer",
    },
    "choose_qty": {
        "ru": "Сколько килограммов оформить?",
        "en": "How many kilograms would you like?",
    },
    "btn_custom_qty": {
        "ru": "✏️ Своё количество",
        "en": "✏️ Custom amount",
    },
    "ask_custom_qty": {
        "ru": "Введите количество в кг (например: 1.5):",
        "en": "Enter the quantity in kg (e.g. 1.5):",
    },
    "qty_invalid": {
        "ru": "⚠️ Пожалуйста, введите положительное число, например 1 или 1.5",
        "en": "⚠️ Please enter a positive number, e.g. 1 or 1.5",
    },
    "selected_qty": {
        "ru": "Выбрано: <b>{qty} кг</b>",
        "en": "Selected: <b>{qty} kg</b>",
    },
    "btn_add_to_cart": {
        "ru": "✅ Добавить в корзину",
        "en": "✅ Add to cart",
    },
    "btn_change_qty": {
        "ru": "🔁 Изменить количество",
        "en": "🔁 Change quantity",
    },
    "item_added": {
        "ru": "✅ Товар добавлен в корзину!",
        "en": "✅ Item added to cart!",
    },
    "btn_go_to_cart": {
        "ru": "🛒 Перейти в корзину",
        "en": "🛒 Go to cart",
    },
    "btn_back_to_catalog": {
        "ru": "🛍 К товарам",
        "en": "🛍 Back to products",
    },
    "btn_back": {
        "ru": "⬅️ Назад",
        "en": "⬅️ Back",
    },
    "btn_back_to_menu": {
        "ru": "🏠 Главное меню",
        "en": "🏠 Main menu",
    },
    "cart_title": {
        "ru": "🛒 <b>Ваша корзина</b>",
        "en": "🛒 <b>Your cart</b>",
    },
    "cart_empty": {
        "ru": "🛒 Ваша корзина пуста.\nЗагляните в раздел «Показать товары» 🙂",
        "en": "🛒 Your cart is empty.\nCheck out the “Show products” section 🙂",
    },
    "cart_line_known": {
        "ru": "• {name} — {qty} кг × {price} {currency} = <b>{sum} {currency}</b>",
        "en": "• {name} — {qty} kg × {price} {currency} = <b>{sum} {currency}</b>",
    },
    "cart_line_unknown": {
        "ru": "• {name} — {qty} кг (цена уточняется)",
        "en": "• {name} — {qty} kg (price to be confirmed)",
    },
    "cart_total": {
        "ru": "\n💵 <b>Итого: {total} {currency}</b>",
        "en": "\n💵 <b>Total: {total} {currency}</b>",
    },
    "cart_note_unknown_prices": {
        "ru": "\n⚠️ Часть товаров без указанной цены — окончательная сумма будет согласована с производителем.",
        "en": "\n⚠️ Some items have no listed price — the final amount will be confirmed with the producer.",
    },
    "btn_order": {
        "ru": "✅ Оформить заказ",
        "en": "✅ Place order",
    },
    "btn_clear_cart": {
        "ru": "🗑 Очистить корзину",
        "en": "🗑 Clear cart",
    },
    "btn_receipt": {
        "ru": "🧾 Чек",
        "en": "🧾 Receipt",
    },
    "clear_cart_confirm": {
        "ru": "Точно очистить корзину?",
        "en": "Clear the cart for sure?",
    },
    "btn_yes": {
        "ru": "Да",
        "en": "Yes",
    },
    "btn_no": {
        "ru": "Нет",
        "en": "No",
    },
    "cart_cleared": {
        "ru": "🗑 Корзина очищена.",
        "en": "🗑 Cart cleared.",
    },
    "receipt_title": {
        "ru": "🧾 <b>Чек</b>",
        "en": "🧾 <b>Receipt</b>",
    },
    "order_placed_user": {
        "ru": "🎉 Спасибо! Ваш заказ №{order_id} принят.\nПроизводитель скоро свяжется с вами для подтверждения.",
        "en": "🎉 Thank you! Your order #{order_id} has been placed.\nThe producer will contact you shortly to confirm.",
    },
    "question_prompt": {
        "ru": "✏️ Напишите ваш вопрос производителю — он получит его и ответит вам здесь же.",
        "en": "✏️ Write your question to the producer — they'll receive it and reply here.",
    },
    "question_sent": {
        "ru": "✅ Ваш вопрос отправлен производителю. Ожидайте ответа.",
        "en": "✅ Your question has been sent to the producer. Please wait for a reply.",
    },
    "orders_title": {
        "ru": "📦 <b>Ваши заказы</b>",
        "en": "📦 <b>Your orders</b>",
    },
    "orders_empty": {
        "ru": "📦 У вас пока нет заказов.",
        "en": "📦 You don't have any orders yet.",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    """Возвращает переведённый текст по ключу с подстановкой переменных."""
    entry = TEXTS.get(key, {})
    template = entry.get(lang) or entry.get("ru") or key
    return template.format(**kwargs) if kwargs else template
