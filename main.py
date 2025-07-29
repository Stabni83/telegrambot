import os
import telebot
from flask import Flask
from threading import Thread


TOKEN = os.environ.get('TOKEN')  
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route('/')
def home():
    return "ربات تلگرام در حال اجراست 🚀"


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "👋 سلام! به ربات من خوش آمدید!\n/game را برای شروع بازی ارسال کنید")

@bot.message_handler(commands=['game'])
def start_game(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('❤️', '💙', '💚', '💜')
    bot.send_message(message.chat.id, "یک رنگ انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    if message.text in ['❤️', '💙', '💚', '💜']:
        bot.send_message(message.chat.id, f"شما {message.text} را انتخاب کردید!")
    else:
        bot.send_message(message.chat.id, "دستور نامعتبر! /start را امتحان کنید")

# 4. اجرای همزمان
def run_flask():
    app.run(host='0.0.0.0', port=8080)

def run_bot():
    print("✅ ربات فعال شد!")
    bot.polling(non_stop=True)

if __name__ == '__main__':
    Thread(target=run_flask).start()
    run_bot()
