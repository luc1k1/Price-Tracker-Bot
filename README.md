![Python](https://img.shields.io/badge/Python-3-blue)
![License](https://img.shields.io/badge/License-MIT-green)

# Price Tracker Bot
This Python script tracks product prices from Amazon and sends notifications via Telegram when the price drops.

## Description
A Python script that tracks product prices from Amazon and sends Telegram notifications when the price drops.

## Features
 Scrapes product prices using BeautifulSoup  
 Stores & updates prices in an SQLite database  
 Sends Telegram alerts if the price decreases  
 Runs in a loop, checking prices every hour  

## Installation
```sh
pip install requests beautifulsoup4 telebot
```

## Setup
1. Replace `YOUR_TELEGRAM_BOT_TOKEN` and `YOUR_CHAT_ID` with your actual values.
2. Modify the parsing logic for different e-commerce websites if needed.
3. Run the script:  
   ```sh
   python price_tracker.py
   ```

## License
MIT License
