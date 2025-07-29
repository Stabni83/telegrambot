import os
import random
from telebot import TeleBot, types
from flask import Flask
from threading import Thread

TOKEN = os.environ.get('TOKEN')
bot = TeleBot(TOKEN)
app = Flask(__name__)

# ذخیره وضعیت بازی
games = {}

class GameState:
    def __init__(self):
        self.secret = random.sample(['❤️', '💙', '💚', '💜'], 3)
        self.attempts = 0

@app.route('/')
def home():
    return "ربات فعال است!"

@bot.message_handler(commands=['start', 'game'])
def start_game(message):
    chat_id = message.chat.id
    games[chat_id] = GameState()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    markup.add('❤️', '💙', '💚', '💜')
    
    bot.send_message(
        chat_id=chat_id,
        text="🎮 3 رنگ انتخاب کنید (مثال: ❤️💙💚)",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: True)
def handle_guess(message):
    chat_id = message.chat.id
    text = message.text
    
    if chat_id not in games:
        start_game(message)
        return
        
    game = games[chat_id]
    
    # اعتبارسنجی حدس
    if len(text) != 3 or not all(emoji in ['❤️', '💙', '💚', '💜'] for emoji in text):
        bot.send_message(chat_id, "⚠️ لطفاً دقیقاً 3 ایموجی ارسال کنید")
        return
        
    game.attempts += 1
    guess = list(text)
    
    # محاسبه نتایج
    correct_pos = sum(s == g for s, g in zip(game.secret, guess))
    correct_col = len(set(game.secret) & set(guess)) - correct_pos
    
    # پاسخ به کاربر
    if correct_pos == 3:
        bot.send_message(
            chat_id,
            f"🎉 برنده شدید! پاسخ: {''.join(game.secret)}",
            reply_markup=types.ReplyKeyboardRemove()
        )
        del games[chat_id]
    elif game.attempts >= 5:
        bot.send_message(
            chat_id,
            f"💔 باختید! پاسخ: {''.join(game.secret)}",
            reply_markup=types.ReplyKeyboardRemove()
        )
        del games[chat_id]
    else:
        bot.send_message(
            chat_id,
            f"🔍 نتیجه حدس {game.attempts}/5:\n"
            f"موقعیت صحیح: {correct_pos}\n"
            f"رنگ صحیح: {correct_col}"
        )

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    print("✅ ربات فعال شد!")
    Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
