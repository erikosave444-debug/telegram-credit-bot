import os
from flask import Flask, request, abort
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ===== ENV =====
TOKEN = os.environ.get("TELEGRAM_TOKEN")
HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = f"https://{HOST}{WEBHOOK_PATH}"

# ===== APP =====
flask_app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# ===== LANGUAGE HELPER =====
def lang(update: Update):
    code = update.effective_user.language_code
    return "ru" if code == "ru" else "en"

# ===== TEXTS =====
TEXT = {
    "start": {
        "en": "Hi! 👋 I’m a credit education bot.\nType /help to see commands.",
        "ru": "Привет! 👋 Я бот по кредитному образованию.\nНапиши /help для списка команд."
    },
    "help": {
        "en": (
            "/dispute – Credit report dispute template\n"
            "/calculate <balance> <limit> – Credit utilization\n"
            "/faq – Credit tips\n"
        ),
        "ru": (
            "/dispute – Шаблон спора в кредитное бюро\n"
            "/calculate <баланс> <лимит> – Utilization\n"
            "/faq – Советы по кредиту\n"
        )
    },
    "faq": {
        "en": (
            "📌 Credit Tips (USA):\n"
            "• Pay on time\n"
            "• Keep utilization <30%\n"
            "• Dispute errors\n"
            "• Avoid too many inquiries\n"
        ),
        "ru": (
            "📌 Советы по кредиту (США):\n"
            "• Плати вовремя\n"
            "• Utilization <30%\n"
            "• Спорь ошибки\n"
            "• Не делай много inquiries\n"
        )
    }
}

# ===== COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    l = lang(update)
    await update.message.reply_text(TEXT["start"][l])

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    l = lang(update)
    await update.message.reply_text(TEXT["help"][l])

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    l = lang(update)
    await update.message.reply_text(TEXT["faq"][l])

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    l = lang(update)
    if len(context.args) != 2:
        msg = "Usage: /calculate <balance> <limit>" if l == "en" else "Используй: /calculate <баланс> <лимит>"
        await update.message.reply_text(msg)
        return

    try:
        balance = float(context.args[0])
        limit = float(context.args[1])
        util = (balance / limit) * 100
        advice = "Good 👍" if util < 30 else "Too high ⚠️"
        await update.message.reply_text(f"Utilization: {util:.2f}% — {advice}")
    except:
        await update.message.reply_text("Numbers only.")

async def dispute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    l = lang(update)
    if l == "en":
        text = "Use this dispute template for credit bureaus (Equifax / Experian / TransUnion)."
    else:
        text = "Используй этот шаблон для спора в кредитные бюро."
    await update.message.reply_text(text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    l = lang(update)
    msg = "Type /help to see commands." if l == "en" else "Напиши /help для команд."
    await update.message.reply_text(msg)

# ===== HANDLERS =====
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_cmd))
application.add_handler(CommandHandler("faq", faq))
application.add_handler(CommandHandler("calculate", calculate))
application.add_handler(CommandHandler("dispute", dispute))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ===== WEBHOOK =====
@flask_app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    if request.headers.get("content-type") == "application/json":
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return "OK"
    abort(403)

@flask_app.route("/")
def index():
    return "Bot is running"
