import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📘 Credit Education", callback_data="education")],
        [InlineKeyboardButton("❓ Credit Report Errors", callback_data="errors")],
        [InlineKeyboardButton("📞 Contact Consultant", callback_data="contact")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome 👋\n\nChoose an option below:",
        reply_markup=reply_markup,
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "education":
        await query.message.reply_text(
            "📘 Credit Education\n\n"
            "• How credit scores work\n"
            "• What affects your score\n"
            "• How to improve credit legally"
        )

    elif query.data == "errors":
        await query.message.reply_text(
            "❓ Credit Report Errors\n\n"
            "• Late payments that aren't yours\n"
            "• Collections you don't recognize\n"
            "• Incorrect balances\n\n"
            "If you suspect errors, click Contact Consultant."
        )

    elif query.data == "contact":
        context.user_data["contacting"] = True
        await query.message.reply_text(
            "📞 Please describe your situation.\n"
            "A consultant will review your message."
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("contacting"):
        user = update.message.from_user
        text = update.message.text

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                "🔥 New interested user\n\n"
                f"Name: {user.full_name}\n"
                f"Username: @{user.username}\n\n"
                f"Message:\n{text}"
            ),
        )

        await update.message.reply_text(
            "✅ Thank you! A consultant will contact you soon."
        )
        context.user_data["contacting"] = False

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    app.run_polling()

if __name__ == "__main__":
    main()
