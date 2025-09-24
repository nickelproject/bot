import telebot
import requests
import os
import threading

# ===================== تنظیمات =====================
TOKEN = "8298436590:AAHVx8DJIBm-ip3PguRwjtdemYb0w_eQVaQ"
CHANNEL_USERNAME = "@dainadownloader"  # کانال موردنظر
DOWNLOAD_DIR = "downloads"  # پوشه دانلود
MAX_FILE_SIZE = 1_073_741_824  # 1 گیگابایت

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

bot = telebot.TeleBot(TOKEN)

# ===================== /start =====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, message.chat.id)
        if member.status not in ["member", "creator", "administrator"]:
            bot.reply_to(message,
                         f"برای استفاده از ربات، ابتدا باید عضو کانال {CHANNEL_USERNAME} شوی.\n"
                         "بعد دوباره /start را بزن.")
            return
    except Exception as e:
        bot.reply_to(message, "خطا در بررسی عضویت. لطفاً بعداً امتحان کن.")
        return

    bot.reply_to(message, "سلام! حالا می‌توانی لینک دانلود بدهی، من فایل را برایت می‌فرستم.")

# ===================== دانلود و ارسال فایل =====================
def download_and_send(url, chat_id):
    try:
        # بررسی حجم فایل
        head = requests.head(url, allow_redirects=True)
        size = head.headers.get("content-length")
        if size and int(size) > MAX_FILE_SIZE:
            bot.send_message(chat_id, "حجم فایل بیش از 1 گیگ است. اجازه دانلود داده نمی‌شود.")
            return

        fname = url.split("/")[-1].split("?")[0] or "file"
        filepath = os.path.join(DOWNLOAD_DIR, fname)

        bot.send_message(chat_id, "در حال دانلود فایل... صبر کن :)")

        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        with open(filepath, "rb") as f:
            bot.send_document(chat_id, f)

        os.remove(filepath)

    except Exception as e:
        bot.send_message(chat_id, f"خطا در دانلود یا ارسال فایل:\n{e}")

# ===================== دریافت لینک کاربر =====================
@bot.message_handler(func=lambda message: True)
def handle_url(message):
    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        bot.reply_to(message, "این یک لینک معتبر نیست. لطفاً لینک درست بده.")
        return

    # اجرای دانلود در Thread جدا
    threading.Thread(target=download_and_send, args=(url, message.chat.id)).start()

# ===================== اجرای ربات =====================
bot.polling()
