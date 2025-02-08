"""
Price Tracker Bot

Features:
- Scrapes product prices using BeautifulSoup.
- Stores and updates prices in an SQLite database.
- Sends Telegram alerts if a price decreases.
- Runs in a loop to check prices every hour.

Requirements:
- Install dependencies: `pip install requests beautifulsoup4 telebot`
- Replace `YOUR_TELEGRAM_BOT_TOKEN` and `YOUR_CHAT_ID` with actual values.
- Modify the parsing logic if needed for different e-commerce websites.

Author: luc1k1

---

"""
import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import telebot

# Telegram Bot Token
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
bot = telebot.TeleBot(TOKEN)

# Database setup
def init_db():
    conn = sqlite3.connect("prices.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS prices (id INTEGER PRIMARY KEY, url TEXT, price REAL)''')
    conn.commit()
    conn.close()

# Function to fetch price
def get_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Example: Parsing Amazon price (modify for different sites)
    price_tag = soup.select_one("span.a-price-whole")
    if price_tag:
        return float(price_tag.text.replace(",", ""))
    return None

# Function to check and update price
def check_price(url):
    conn = sqlite3.connect("prices.db")
    cursor = conn.cursor()
    price = get_price(url)
    
    if price is None:
        print("Failed to fetch price.")
        return
    
    cursor.execute("SELECT price FROM prices WHERE url = ?", (url,))
    row = cursor.fetchone()
    
    if row:
        old_price = row[0]
        if price < old_price:
            bot.send_message(CHAT_ID, f'Price dropped! New price: {price} USD')
            cursor.execute("UPDATE prices SET price = ? WHERE url = ?", (price, url))
    else:
        cursor.execute("INSERT INTO prices (url, price) VALUES (?, ?)", (url, price))
    
    conn.commit()
    conn.close()

# List of product URLs to track
urls = [
    "https://www.amazon.com/dp/B09G3HRMVB",  # Example Amazon product
]

if __name__ == "__main__":
    init_db()
    while True:
        for url in urls:
            check_price(url)
        time.sleep(3600)  # Check every hour
