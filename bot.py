import os
from flask import Flask, request, abort
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get('TELEGRAM_TOKEN')          # берём из env vars на Render
WEBHOOK_PATH = f'/{TOKEN}'                        # секретный путь, чтобы никто не угадал
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

app = Flask(__name__)

application = Application.builder().token(TOKEN).build()

# Твои handlers (добавь свои функции)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот по кредитной истории. Используй /dispute, /calculate и т.д.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ты написал: {update.message.text}")

# Добавь все handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
# ... добавь свои /dispute, /calculate, /remind и т.д.

@app.route(WEBHOOK_PATH, methods=['POST'])
async def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string, application.bot)
        await application.process_update(update)
        return '', 200
    else:
        abort(403)

@app.route('/')
def index():
    return "Бот работает! Webhook активен."

if __name__ == '__main__':
    # Локально можно polling для теста
    # application.run_polling()
    pass  # на Render Flask сам запустится
