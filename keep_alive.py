"""
Мини веб-сервер для «пробуждения» бота на бесплатных хостингах (Render и т.п.),
которые требуют, чтобы приложение слушало HTTP-порт, и усыпляют сервис
после периода бездействия. Внешний пинг-сервис (например, UptimeRobot)
раз в несколько минут обращается к этому серверу, не давая сервису уснуть.
"""

import os
import threading

from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Бот о Таджикистане работает ✅"


def _run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def start() -> None:
    """Запускает Flask-сервер в отдельном потоке, не блокируя основной поток бота."""
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
