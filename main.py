import os
import random
import telebot
from flask import Flask
from threading import Thread


TOKEN = os.environ.get('TOKEN') or 'توکن_خود_را_وارد_کنید'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


user_data = {}

class Game:
    def __init__(self):
        self.secret = random.sample(['❤️', '💙', '💚', '💜'], 3)
        self.attempts = 0

# صفحه اصلی وب
@app.route('/')
def home():
    return "ربات Mastermind فعال است! 🤖"


@bot.message_handler(commands=['start', 'game'])
def start_game(message):
    chat_id = message.chat.id
    user_data[chat_id] = Game()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    markup.add('❤️', '💙', '💚', '💜')
    
    bot.send_message(
        chat_id,
        "🎮 بازی Mastermind شروع شد!\n"
        "ترکیب 3 رنگ مخفی ساخته شده است.\n"
        "شما 5 فرصت دارید با ارسال ترکیبی مثل ❤️💙💚 حدس بزنید.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()
    
   
    if chat_id not in user_data:
        start_game(message)
        return
    
    game = user_data[chat_id]
    
   
    if len(text) == 3 and all(emoji in ['❤️', '💙', '💚', '💜'] for emoji in text):
        game.attempts += 1
        guess = list(text)
        correct_pos = sum(s == g for s, g in zip(game.secret, guess))
        correct_col = len(set(game.secret) & set(guess)) - correct_pos
        
        if correct_pos == 3:
            bot.send_message(
                chat_id,
                f"🎉 برنده شدید! پاسخ صحیح: {''.join(game.secret)}",
                reply_markup=types.ReplyKeyboardRemove()
            )
            del user_data[chat_id]
        elif game.attempts >= 5:
            bot.send_message(
                chat_id,
                f"☹️ باختید! پاسخ صحیح بود: {''.join(game.secret)}",
                reply_markup=types.ReplyKeyboardRemove()
            )
            del user_data[chat_id]
        else:
            bot.send_message(
                chat_id,
                f"🔍 حدس {game.attempts}/5:\n"
                f"در موقعیت صحیح: {correct_pos}\n"
                f"رنگ صحیح در موقعیت اشتباه: {correct_col}"
            )
    else:
        bot.send_message(
            chat_id,
            "⚠️ لطفاً دقیقاً 3 ایموجی از ❤️💙💚💜 ارسال کنید\n"
            "مثال: ❤️💙💚"
        )


def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    print("✅ ربات فعال شد!")
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    bot.infinity_polling()
