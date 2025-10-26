import os
import requests
import time
import json
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHECK_INTERVAL = 60

# === INISIALISASI BOT ===
bot = Bot(token=BOT_TOKEN)
sent_tokens_file = "sent_tokens.json"

# === MUAT DATA TOKEN YANG SUDAH DIKIRIM ===
try:
    with open(sent_tokens_file, "r") as f:
        sent_tokens = json.load(f)
except FileNotFoundError:
    sent_tokens = []

def fetch_tokens():
    """Ambil data token dari API MemePad"""
    url = "https://meme.xmagnetic.org/Memepad/GetMemeTokens"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ERROR] Gagal fetch data: {e}")
        return []

def format_message(token):
    """Bentuk pesan Telegram"""
    t = token["tokenOnMemePad"]
    name = t.get("projectName", "Unknown")
    desc = t.get("description", "No description.")
    twitter = t.get("twitter", "-")
    telegram = t.get("telegram", "-")
    site = t.get("site", "-")
    issuer = t.get("issuer", "")
    currency = t.get("currency", "")
    banner = f"https://{t['banner']}" if t.get("banner") else None
    logo = f"https://{t['logo']}" if t.get("logo") else None
    link_trade = f"https://xpmarket.com/dex/{currency}-{issuer}/XRP?trade=market"

    text = (
        f"🚀 <b>NEW TOKEN LAUNCH</b>\n\n"
        f"<b>Name:</b> {name}\n"
        f"<b>Symbol:</b> {currency}\n"
        f"<b>Description:</b> {desc}\n\n"
        f"<b>Site:</b> {site}\n"
        f"<b>Telegram:</b> {telegram}\n"
        f"<b>Twitter:</b> {twitter}\n"
    )

    buttons = [
        [InlineKeyboardButton("🌐 Website", url=f"https://{site}" if site != "-" else "https://xmagnetic.org")],
        [InlineKeyboardButton("💬 Telegram", url=f"https://{telegram}" if telegram != "-" else "https://t.me/xmagnetic")],
        [InlineKeyboardButton("🐦 Twitter", url=f"https://{twitter}" if twitter != "-" else "https://x.com/xmagnetic")],
        [InlineKeyboardButton("🪙 Trade on XPmarket", url=link_trade)],
    ]
    return text, banner, logo, buttons

def send_to_telegram(token):
    """Kirim pesan ke channel"""
    try:
        text, banner, logo, buttons = format_message(token)
        markup = InlineKeyboardMarkup(buttons)

        # kirim logo lebih dulu jika ada
        if logo:
            bot.send_photo(chat_id=CHANNEL_ID, photo=logo, caption="🆕 Token Detected!", parse_mode="HTML")

        # kirim banner dan detail token
        if banner:
            bot.send_photo(chat_id=CHANNEL_ID, photo=banner, caption=text, parse_mode="HTML", reply_markup=markup)
        else:
            bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="HTML", reply_markup=markup)

        print(f"[INFO] Token dikirim ke Telegram: {token['tokenOnMemePad']['projectName']}")
    except Exception as e:
        print(f"[ERROR] Gagal kirim ke Telegram: {e}")

def main():
    print("🤖 XMagnetic MemePad Bot aktif...")
    while True:
        data = fetch_tokens()
        if data:
            for token in data:
                unique_id = token["tokenOnMemePad"]["unique_token"]
                if unique_id not in sent_tokens:
                    send_to_telegram(token)
                    sent_tokens.append(unique_id)
                    # simpan daftar token yang sudah dikirim
                    with open(sent_tokens_file, "w") as f:
                        json.dump(sent_tokens, f, indent=2)
        else:
            print("[WARN] Tidak ada data diterima.")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
