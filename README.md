# The number one team represents their bot

This is a repository for Telegram bot that will be developed by first team.

### Now implemented
1. History (/history) - The output of the last message

## Set up Python environment

1. Create virtual environment `python -m venv venv`
2. Activate virtual environment and install requirements: 

    `venv\Scripts\activate` - on Linux
    
    `venv\Scripts\activate.bat` - on Windows
    
    `pip install -r requirements.txt`

## Create your Telegram Bot

1. Follow official [Telegram instructions](https://core.telegram.org/bots#6-botfather) to create your bot and obtain token.
2. Insert obtained token to `setup.py` `TOKEN` variable.

## Run your bot

1. Execute ``python chat_bot_template.py``
2. Try your bot - find it in Telegram and press `/start`.