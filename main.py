import os
import random
import telebot
from flask import Flask
from threading import Thread

# تنظیمات اولیه
TOKEN = os.environ['TOKEN']
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# دیکشنری‌های ذخیره وضعیت بازی
games = {}
attempts = {}

# انتخاب تصادفی رنگ‌ها برای بازی
def generate_secret():
    colors = ['❤️', '💙', '💚', '💜']
    return random.sample(colors, 3)

# بررسی حدس کاربر
def check_guess(secret, guess):
    correct_pos = sum(s == g for s, g in zip(secret, guess))
    correct_col = len(set(secret) & set(guess))
    return correct_pos, correct_col - correct_pos

# دستور شروع بازی
@bot.message_handler(commands=['start', 'game'])
def start_game(message):
    chat_id = message.chat.id
    games[chat_id] = generate_secret()
    attempts[chat_id] = 0
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('❤️', '💙', '💚', '💜')
    markup.row('🔴 بازی جدید', '🔚 خروج')
    
    bot.send_message(chat_id, 
        "🎮 بازی Mastermind شروع شد!\n"
        "3 رنگ را انتخاب کنید (مثال: ❤️💙💚)\n"
        "شما 5 فرصت دارید",
        reply_markup=markup)

# پردازش حدس کاربر
@bot.message_handler(func=lambda m: True)
def handle_guess(message):
    chat_id = message.chat.id
    text = message.text
    
    if text == '🔴 بازی جدید':
        start_game(message)
        return
        
    if text == '🔚 خروج':
        bot.send_message(chat_id, "بازی پایان یافت", reply_markup=telebot.types.ReplyKeyboardRemove())
        return
        
    if chat_id not in games:
        start_game(message)
        return
        
    # بررسی حدس
    if len(text) != 3 or any(c not in ['❤️', '💙', '💚', '💜'] for c in text):
        bot.send_message(chat_id, "لطفاً دقیقاً 3 ایموجی از بین ❤️💙💚💜 انتخاب کنید")
        return
        
    attempts[chat_id] += 1
    guess = list(text)
    secret = games[chat_id]
    pos, col = check_guess(secret, guess)
    
    if pos == 3:
        bot.send_message(chat_id, f"🎉 برنده شدید! پاسخ صحیح بود: {''.join(secret)}")
        del games[chat_id]
        return
        
    if attempts[chat_id] >= 5:
        bot.send_message(chat_id, f"😞 باختید! پاسخ صحیح بود: {''.join(secret)}")
        del games[chat_id]
        return
        
    bot.send_message(chat_id,
        f"🔍 نتیجه حدس {attempts[chat_id]}/5:\n"
        f"تعداد در موقعیت صحیح: {pos}\n"
        f"تعداد رنگ صحیح در موقعیت اشتباه: {col}")

# سرور Flask برای فعال ماندن
@server.route('/')
def home():
    return "🤖 ربات بازی Mastermind فعال است"

# اجرای همزمان
def run_server():
    server.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    Thread(target=run_server).start()
    print("✅ ربات فعال شد!")
    bot.polling(non_stop=True)
