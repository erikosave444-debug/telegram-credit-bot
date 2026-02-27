import os
from flask import Flask, request, abort
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Token from env var
TOKEN = os.environ.get('TELEGRAM_TOKEN')
WEBHOOK_PATH = f'/{TOKEN}'
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'your-render-app.onrender.com')}{WEBHOOK_PATH}"

app_flask = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# Handlers
def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.message.reply_text('Привет! Я бот-помощник по улучшению кредитной истории (educational only). Команды: /help для списка.')

def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Доступные команды:
/dispute - Шаблон для спора ошибок в кредитном отчёте
/calculate <баланс> <лимит> - Калькулятор credit utilization
/remind <дни> <сообщение> - Установить напоминание о платеже
/faq - Краткий FAQ по улучшению кредитной истории
    """
    update.message.reply_text(help_text)

def dispute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    template = """
[Your Name]
[Your Address]
[City, State, ZIP Code]
[Date]

[Credit Bureau Name]  # Equifax, Experian or TransUnion
[Bureau Address]

Subject: Dispute of Inaccurate Information on Credit Report

Dear Sir/Madam,

I am writing to dispute the following information in my file. My identifying information is as follows:

Name: [Your Full Name]
SSN: [Last 4 digits only]
DOB: [Your Date of Birth]
Current Address: [Your Address]

The items I dispute are: [Describe the error, e.g., "Account #XXXX with ABC Bank shows late payment on MM/YYYY, but I paid on time. See attached proof."]

Please investigate and delete or correct the disputed items as soon as possible.

Sincerely,
[Your Name]
    """
    update.message.reply_text(f'Вот шаблон для спора в бюро. Скопируй и заполни:\n{template}')

def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        update.message.reply_text('Используй: /calculate <баланс> <лимит> (например, /calculate 500 2000)')
        return
    try:
        balance = float(context.args[0])
        limit = float(context.args[1])
        utilization = (balance / limit) * 100
        advice = 'Идеально <10%. Цель <30%.' if utilization < 30 else 'Слишком высоко — плати вниз!'
        update.message.reply_text(f'Utilization: {utilization:.2f}%. {advice}')
    except ValueError:
        update.message.reply_text('Введи числа!')

def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        update.message.reply_text('Используй: /remind <дни до напоминания> <текст>')
        return
    try:
        days = int(context.args[0])
        msg = ' '.join(context.args[1:])
        chat_id = update.message.chat_id
        context.job_queue.run_once(callback_remind, days * 86400, data=(chat_id, msg))
        update.message.reply_text(f'Напоминание установлено на {days} дней: "{msg}"')
    except ValueError:
        update.message.reply_text('Первое значение должно быть числом (дни)!')

def callback_remind(context: ContextTypes.DEFAULT_TYPE):
    chat_id, msg = context.job.data
    context.bot.send_message(chat_id=chat_id, text=f'Напоминание: {msg}')

def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    faq_text = """
FAQ по улучшению кредитной истории (USA, 2026):
1. Проверь отчёт бесплатно: AnnualCreditReport.com (раз в неделю).
2. Dispute ошибки: Используй /dispute для шаблона.
3. Плати вовремя: Set auto-pay.
4. Снижай utilization: <30% (используй /calculate).
5. Строи историю: Secured cards (Self, Chime).
6. Избегай новых inquiries.
Нет быстрых "починонок" — всё занимает 1–12 месяцев. Консультация: NFCC.org.
    """
    update.message.reply_text(faq_text)

def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.message.reply_text(f'Ты написал: "{update.message.text}". Задай команду, или спроси в FAQ (/faq).')

# Add handlers (sync versions)
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', help_command))
application.add_handler(CommandHandler('dispute', dispute))
application.add_handler(CommandHandler('calculate', calculate))
application.add_handler(CommandHandler('remind', remind))
application.add_handler(CommandHandler('faq', faq))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Webhook endpoint (sync version to avoid 500 errors)
@app_flask.route(WEBHOOK_PATH, methods=['GET', 'POST'])
def webhook():
    print("Webhook hit with method:", request.method)  # Debug log
    if request.method == 'GET':
        return 'OK'
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        print("Received JSON:", json_string)  # Debug log
        update = Update.de_json(json_string, application.bot)
        application.process_update(update)
        return '', 200
    print("Invalid request")  # Debug log
    abort(403)

@app_flask.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    pass
