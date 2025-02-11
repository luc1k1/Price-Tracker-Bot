"""
Price Tracker Bot

Features:
- Scrapes product prices using BeautifulSoup.
- Stores and updates prices in an SQLite database.
- Sends Telegram alerts if a price drops.
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
import logging
import telebot

# === Configuration ===
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
CHECK_INTERVAL = 3600  # Check every hour
HEADERS = {"User-Agent": "Mozilla/5.0"}
DB_FILE = "prices.db"

# Initialize Telegram bot
bot = telebot.TeleBot(TOKEN)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === Database Setup ===
def init_db():
    """Initializes the SQLite database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS prices (id INTEGER PRIMARY KEY, url TEXT UNIQUE, price REAL)''')
        conn.commit()

# === Price Fetching & Parsing ===
def get_price(url):
    """Fetches the price from the given URL."""
    try:
        with requests.Session() as session:
            response = session.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        return parse_price(soup)
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def parse_price(soup):
    """Extracts the price from a BeautifulSoup object. Modify for different sites."""
    price_tag = soup.select_one("span.a-price-whole")
    if price_tag:
        try:
            return float(price_tag.text.replace(",", "").strip())
        except ValueError:
            logging.warning("Failed to parse price.")
    return None

# === Price Checking & Notification ===
def check_price(url):
    """Checks the price of a product and sends an alert if it drops."""
    price = get_price(url)
    if price is None:
        logging.warning(f"Failed to retrieve price for {url}")
        return
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT price FROM prices WHERE url = ?", (url,))
        row = cursor.fetchone()

        if row:
            old_price = row[0]
            if price < old_price:
                send_price_alert(url, old_price, price)
                cursor.execute("UPDATE prices SET price = ? WHERE url = ?", (price, url))
        else:
            cursor.execute("INSERT INTO prices (url, price) VALUES (?, ?)", (url, price))
        conn.commit()

def send_price_alert(url, old_price, new_price):
    """Sends a Telegram alert when a price drop is detected."""
    message = f"💰 Price Drop Alert!\n\nProduct: {url}\nOld Price: {old_price} USD\nNew Price: {new_price} USD\n\nCheck now!"
    bot.send_message(CHAT_ID, message)
    logging.info(f"Price drop alert sent: {url} ({old_price} -> {new_price})")

# === Main Execution ===
if __name__ == "__main__":
    init_db()
    urls = [
        "https://www.amazon.com/dp/B09G3HRMVB",  # Example Amazon product
    ]

    while True:
        for url in urls:
            check_price(url)
        logging.info(f"Waiting {CHECK_INTERVAL} seconds before next check...")
        time.sleep(CHECK_INTERVAL)
