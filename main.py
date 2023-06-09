"""
Telegram Bot for Chore Rota

This script implements a Telegram bot that allows users to schedule names for different days of the week.

Author: W. van der Toorren (wvdtoorren)
License: GPL-3.0 License
"""

import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import datetime

# Variables for user data
user_id = None
user_name = None

SET_DAY, SET_NAME = range(2)

# Function to clear all data for the current Telegram client from the database
def clear_all(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_name = update.effective_user.username
    conn = context.bot_data['conn']
    c = conn.cursor()
    c.execute("DELETE FROM namen WHERE user_id = ?", (user_id,))
    conn.commit()

    update.message.reply_text(f"All data has been cleared for {user_name}.")


def handle_invalid_command(update, context):
    update.message.reply_text("Invalid command. Please use a valid command.")


# Function to display the weekday and corresponding name for tomorrow
def show_tomorrow(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    conn = context.bot_data['conn']
    c = conn.cursor()

    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    tomorrow_weekday = tomorrow.strftime("%A")

    c.execute("SELECT naam FROM namen WHERE user_id = ? AND dag = ?", (user_id, tomorrow_weekday))
    row = c.fetchone()

    if row:
        name = row[0]
        message = f"The name for tomorrow ({tomorrow_weekday}) is '{name}'."
    else:
        message = f"No name scheduled for tomorrow ({tomorrow_weekday})."

    update.message.reply_text(message)


# Function to display the list of scheduled days and names
def show_schedule(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    conn = context.bot_data['conn']
    c = conn.cursor()
    c.execute("SELECT * FROM namen WHERE user_id = ?", (user_id,))
    rows = c.fetchall()

    if rows:
        message = "Your scheduled days and names:\n"
        for row in rows:
            day, name = row[1], row[2]
            message += f"{day}: {name}\n"
    else:
        message = "No days and names scheduled yet."

    update.message.reply_text(message)


# Function to retrieve the name associated with the current day
def show_name(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    conn = context.bot_data['conn']
    c = conn.cursor()

    today = datetime.datetime.now().strftime('%A')
    c.execute("SELECT * FROM namen WHERE user_id = ? AND dag = ?", (user_id, today))
    row = c.fetchone()

    if row:
        name = row[2]
        message = f"The name for today is '{name}'."
    else:
        message = "No name scheduled for today."

    update.message.reply_text(message)


# Function to save the day and name in the database
def set_day(update: Update, context: CallbackContext):
    reply_keyboard = [['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
    update.message.reply_text(
        'Please select a day of the week:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )

    return SET_DAY


def set_name(update: Update, context: CallbackContext):
    context.user_data['day'] = update.message.text

    update.message.reply_text("Please enter the name:")

    return SET_NAME


def save_name(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    day = context.user_data['day']
    name = update.message.text

    conn = context.bot_data['conn']
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO namen VALUES (?, ?, ?)", (user_id, day, name))
    conn.commit()

    update.message.reply_text(f"Name '{name}' is linked to day '{day}'.")

    del context.user_data['day']

    return ConversationHandler.END


# Function to restore the chat state after processing a command
def restore_chat_state(update: Update, context: CallbackContext):
    context.bot.send_chat_action(update.effective_chat.id, "typing")


# Function to display the welcome message and available commands
def start(update: Update, context: CallbackContext):
    message = "Welcome to the Chore Rota Bot!\n\n"
    message += "Available commands:\n"
    message += "/start - Display available commands\n"
    message += "/clearall - Clear all definitions\n"
    message += "/schedule - Show your scheduled days and names\n"
    message += "/set - Set a name for a day\n"
    message += "/who - Show the name for the current day\n"
    message += "Usage: /set <day> <name>\n"

    update.message.reply_text(message)


def main():

    # Connect to the database
    conn = sqlite3.connect('namen.db', check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS namen (user_id INT, dag TEXT, naam TEXT, PRIMARY KEY (user_id, dag))")

    # Initialize the dispatcher
    with open('tgb.token', 'r') as file:
        tgb_token = file.read().strip()

    updater = Updater(tgb_token)
    dispatcher = updater.dispatcher

    # Add the database connection to bot_data
    dispatcher.bot_data['conn'] = conn

    # Command Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("schedule", show_schedule))
    dispatcher.add_handler(CommandHandler("tomorrow", show_tomorrow))
    dispatcher.add_handler(CommandHandler("who", show_name))
    dispatcher.add_handler(CommandHandler("clearall", clear_all))

    # Add the MessageHandler for invalid commands
    invalid_command_handler = MessageHandler(Filters.command, handle_invalid_command)
    dispatcher.add_handler(invalid_command_handler)

    # Conversation Handler for setting name and day
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('set', set_day)],
        states={
            SET_DAY: [MessageHandler(Filters.text & ~Filters.command, set_name)],
            SET_NAME: [MessageHandler(Filters.text & ~Filters.command, save_name)]
        },
        fallbacks=[]
    )
    dispatcher.add_handler(conv_handler)

    # Message Handler to restore the chat state after a command
    dispatcher.add_handler(MessageHandler(Filters.all, restore_chat_state))

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

