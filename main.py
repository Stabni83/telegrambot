import os
import random
from telebot import TeleBot, types
from flask import Flask
from threading import Thread


TOKEN = os.environ.get('TOKEN')  
bot = TeleBot(TOKEN)
app = Flask(__name__)


games = {}

class GameState:
    def __init__(self):
        self.secret = random.sample(['❤️', '💙', '💚', '💜'], 3)
        self.attempts = 0


@app.route('/')
def home():
    return "🤖 ربات Mastermind فعال | https://t.me/{}".format(bot.get_me().username)


@bot.message_handler(commands=['start', 'game'])
def start_game(message):
    chat_id = message.chat.id
    games[chat_id] = GameState()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    markup.add('❤️', '💙', '💚', '💜', '🔄 بازی جدید', '🚪 خروج')
    
    bot.send_message(
        chat_id=chat_id,  # اصلاح شده: استفاده از chat_id به جای reply_to
        text=(
            "🎮 بازی Mastermind\n\n"
            "ترکیب 3 رنگ مخفی ساخته شد!\n"
            "حدس بزنید (مثال: ❤️💙💚)\n"
            "شما 5 فرصت دارید"
        ),
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: True)
def handle_guess(message):
    chat_id = message.chat.id
    text = message.text
    
    if text == '🔄 بازی جدید':
        start_game(message)
        return
        
    if text == '🚪 خروج':
        if chat_id in games:
            del games[chat_id]
        bot.send_message(
            chat_id=chat_id,
            text="بازی پایان یافت",
            reply_markup=types.ReplyKeyboardRemove()
        )
        return
        
    if chat_id not in games:
        start_game(message)
        return
        
    game = games[chat_id]
    
  
    if len(text) != 3 or not all(emoji in ['❤️', '💙', '💚', '💜'] for emoji in text):
        bot.send_message(
            chat_id=chat_id,
            text="⚠️ لطفاً دقیقاً 3 ایموجی از ❤️💙💚💜 ارسال کنید"
        )
        return
        
    game.attempts += 1
    guess = list(text)
    correct_pos = sum(s == g for s, g in zip(game.secret, guess))
    correct_col = len(set(game.secret) & set(guess)) - correct_pos
    
    
    if correct_pos == 3:
        bot.send_message(
            chat_id=chat_id,
            text=f"🎉 برنده شدید! پاسخ: {''.join(game.secret)}",
            reply_markup=types.ReplyKeyboardRemove()
        )
        del games[chat_id]
    elif game.attempts >= 5:
        bot.send_message(
            chat_id=chat_id,
            text=f"💔 باختید! پاسخ: {''.join(game.secret)}",
            reply_markup=types.ReplyKeyboardRemove()
        )
        del games[chat_id]
    else:
        bot.send_message(
            chat_id=chat_id,
            text=(
                f"🔍 حدس {game.attempts}/5:\n"
                f"• درست در جای درست: {correct_pos}\n"
                f"• درست در جای نادرست: {correct_col}"
            )
        )


def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    print("✅ ربات فعال شد!")
    Thread(target=run_flask).start()
    bot.infinity_polling()
