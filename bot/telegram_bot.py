from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from dotenv import load_dotenv
import os
import re
from datetime import date

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello 👋 I am your AI Expense Agent.\n\n"
        "You can add expenses like:\n"
        "/add 50 groceries\n"
        "add 100 to travel\n\n"
        "View summary:\n"
        "/summary (today)\n"
        "/summary all\n"
        "/summary YYYY-MM-DD"
    )

# Function to save expense with date
def save_expense(amount, category):
    today = date.today().isoformat()  # YYYY-MM-DD
    with open("expenses.txt", "a") as file:
        file.write(f"{today},{amount},{category}\n")

# /add command
async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = context.args[0]
        category = context.args[1]
        save_expense(amount, category)

        await update.message.reply_text(
            f"Saved ₹{amount} under {category} for today ✅"
        )
    except IndexError:
        await update.message.reply_text(
            "❌ Invalid format\n"
            "Use: /add <amount> <category>\n"
            "Example: /add 50 groceries"
        )

# Natural language handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    numbers = re.findall(r"\d+", text)
    if not numbers:
        return

    amount = numbers[0]
    words = text.split()
    category = words[-1]

    save_expense(amount, category)

    await update.message.reply_text(
        f"Saved ₹{amount} under {category} for today ✅"
    )

# /summary command
async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        filter_date = date.today().isoformat()  # default: today

        if context.args:
            if context.args[0] == "all":
                filter_date = None
            else:
                filter_date = context.args[0]

        total = 0
        category_totals = {}

        with open("expenses.txt", "r") as file:
            for line in file:
                entry_date, amount, category = line.strip().split(",")

                if filter_date and entry_date != filter_date:
                    continue

                amount = int(amount)
                total += amount
                category_totals[category] = category_totals.get(category, 0) + amount

        if total == 0:
            await update.message.reply_text("No expenses found for this date.")
            return

        message = "📊 Expense Summary\n\n"
        if filter_date:
            message += f"Date: {filter_date}\n"
        else:
            message += "Date: All\n"

        message += f"\nTotal Spent: ₹{total}\n\n"

        for category, amount in category_totals.items():
            message += f"{category}: ₹{amount}\n"

        await update.message.reply_text(message)

    except FileNotFoundError:
        await update.message.reply_text(
            "No expenses found yet.\nAdd expenses first."
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_expense))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()