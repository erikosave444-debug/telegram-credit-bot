import os
from flask import Flask, request, abort
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен из env (на Render добавь в Environment Variables: TELEGRAM_TOKEN = твой_новый_токен)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
WEBHOOK_PATH = f'/{TOKEN}'
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'your-render-app.onrender.com')}{WEBHOOK_PATH}"

app_flask = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# Команды и функции (как раньше)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я бот-помощник по улучшению кредитной истории. Команды: /help.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
/dispute - Шаблон для спора ошибок
/calculate <баланс> <лимит> - Калькулятор utilization
/remind <дни> <сообщение> - Напоминание
/faq - FAQ по кредитной истории
    """
    await update.message.reply_text(help_text)

async def dispute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    template = """
[Your Name]
[Your Address]
[City, State, ZIP Code]
[Date]

[Credit Bureau Name]  # Equifax, Experian or TransUnion
[Bureau Address]

Subject: Dispute of Inaccurate Information

Dear Sir/Madam,

I dispute the following:

Name: [Your Name]
SSN: [Last 4 digits]
DOB: [Date of Birth]
Address: [Address]

Disputed items: [Describe error]

Please investigate.

Sincerely,
[Your Name]
    """
    await update.message.reply_text(f'Шаблон для спора:\n{template}')

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text('/calculate <баланс> <лимит>')
        return
    try:
        balance = float(context.args[0])
        limit = float(context.args[1])
        utilization = (balance / limit) * 100
        advice = 'Good!' if utilization < 30 else 'Pay down!'
        await update.message.reply_text(f'Utilization: {utilization:.2f}%. {advice}')
    except:
        await update.message.reply_text('Numbers only!')

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text('/remind <days> <msg>')
        return
    days = int(context.args[0])
    msg = ' '.join(context.args[1:])
    chat_id = update.message.chat_id
    context.job_queue.run_once(callback_remind, days * 86400, data=(chat_id, msg))
    await update.message.reply_text(f'Reminder set for {days} days.')

async def callback_remind(context: ContextTypes.DEFAULT_TYPE):
    chat_id, msg = context.job.data
    await context.bot.send_message(chat_id=chat_id, text=f'Reminder: {msg}')

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    faq_text = """
FAQ:
1. Check report: AnnualCreditReport.com
2. Dispute errors: Use /dispute
3. Pay on time
4. Lower utilization: /calculate
5. Build history: Secured cards
    """
    await update.message.reply_text(faq_text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'You said: {update.message.text}. Use commands.')

application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', help_command))
application.add_handler(CommandHandler('dispute', dispute))
application.add_handler(CommandHandler('calculate', calculate))
application.add_handler(CommandHandler('remind', remind))
application.add_handler(CommandHandler('faq', faq))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app_flask.route(WEBHOOK_PATH, methods=['GET', 'POST'])
async def webhook():
    if request.method == 'GET':
        return 'OK'
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string, application.bot)
        await application.process_update(update)
        return '', 200
    abort(403)

@app_flask.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    pass
