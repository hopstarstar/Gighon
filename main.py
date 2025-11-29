import os
import time
import threading
from flask import Flask, request
import telebot

BOT_TOKEN = os.getenv("8301751505:AAGMrreQgWuEhDpjA_dmYDP0viNueMJMVE4")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is required")

# webhook url can be provided via WEBHOOK_URL or Render's RENDER_EXTERNAL_URL
WEBHOOK_BASE = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL")
if not WEBHOOK_BASE:
    # will try to continue, but webhook won't be set automatically
    print("WARNING: WEBHOOK_URL or RENDER_EXTERNAL_URL not set. You must set WEBHOOK_URL to your public URL + /webhook")
else:
    if WEBHOOK_BASE.endswith("/"):
        WEBHOOK_BASE = WEBHOOK_BASE[:-1]
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = (WEBHOOK_BASE + WEBHOOK_PATH) if WEBHOOK_BASE else None

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
app = Flask(__name__)

codes = {
    "1111": "https://site.com/link1",
    "2222": "https://site.com/link2",
    "3333": "https://site.com/link3",
    "4444": "https://site.com/link4",
    "5555": "https://site.com/link5",
}

def schedule_clear(chat_id, last_message_id):
    def clear():
        # wait 30 minutes
        time.sleep(1800)
        # try to delete last ~100 messages (may fail for some)
        for i in range(100):
            try:
                bot.delete_message(chat_id, last_message_id - i)
            except Exception:
                pass
    threading.Thread(target=clear, daemon=True).start()

# --- Bot handlers ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Написать код")
    bot.send_message(message.chat.id, "Привет! Нажми кнопку чтобы ввести код.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "Написать код")
def ask_code(message):
    bot.send_message(message.chat.id, "Введите код:")

@bot.message_handler(func=lambda m: True)
def check_code(message):
    text = message.text.strip()
    if text in codes:
        bot.send_message(message.chat.id, f"Код верный!\nВот ваша ссылка:\n{codes[text]}")
    else:
        bot.send_message(message.chat.id, "❌ Неверный код. Попробуйте снова.")
    # schedule clearing chat after 30 minutes (use last message id)
    try:
        last_id = message.message_id
        schedule_clear(message.chat.id, last_id)
    except Exception:
        pass

# --- Flask webhook endpoint ---
@app.route("/", methods=['GET'])
def index():
    return "OK"

@app.route("/webhook", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    if not json_string:
        return "", 400
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "", 200

# Helper to set webhook on startup
def set_webhook_if_needed():
    if not WEBHOOK_URL:
        print("WEBHOOK_URL not set; skipping automatic webhook setup.")
        return
    try:
        bot.remove_webhook()
    except Exception:
        pass
    # set webhook
    ok = bot.set_webhook(url=WEBHOOK_URL)
    print("set_webhook result:", ok, "WEBHOOK_URL:", WEBHOOK_URL)

if __name__ == "__main__":
    # When running locally (for testing), you can run Flask dev server.
    set_webhook_if_needed()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
