# Chore Rota Bot

## Description
The Chore Rota Bot is a Telegram bot written in Python that helps users manage and schedule daily chores. It allows users to set names for specific days of the week, view the scheduled days and names, and retrieve the name for the current day. The bot interacts with users through commands and conversation handlers.

## Features
- Set a name for a specific day of the week
- View the scheduled days and names
- Retrieve the name for the current day
- Clear all definitions
- User-friendly interface with command-based interaction

## Requirements
To run the Chore Rota Bot, the following Python libraries need to be installed:

- python-telegram-bot: Used for interacting with the Telegram Bot API
- sqlite3: Included in Python's standard library for working with SQLite database

Install the required libraries using the following command:

```
pip install python-telegram-bot sqlite3
```


## Usage
1. Obtain a Telegram Bot token from the BotFather on Telegram.
2. Create a file named `tgb.token` and paste your token into the file.
3. Run the script by executing the command `python main.py`.
4. Start a conversation with the bot on Telegram.
5. Use the available commands to interact with the bot and manage chore names and schedules.

## Author
This script was created by [W. van der Toorren](https://github.com/TorreiroW).

## License
This project is licensed under the GPL-3.0 License. See the [LICENSE](LICENSE) file for more details.

