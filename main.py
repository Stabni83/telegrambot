import telebot
from telebot import types
import random
import os


TOKEN = os.environ['TOKEN']  
bot = telebot.TeleBot(TOKEN)

def mastermind(guess, secret):
    correct_select = len(set(guess) & set(secret))
    correct_position = sum(g == s for g, s in zip(guess, secret))
    return {
        'correct_select': correct_select,
        'correct_position': correct_position,
        'is_correct': correct_position == len(secret)
    }

def select_nuts():
    colors = ['r', 'b', 'g', 'p']
    return [random.choice(colors) for _ in range(3)]

user_attempts = {}
user_guesses = {}
nuts_select = {}



# نگاشت حروف به استیکرها
color_to_emoji = {
    'r': '❤️',
    'b': '💙',
    'g': '💚',
    'p': '💜'
}

@bot.message_handler(commands=['start'])
def say_hello(message):
    bot.reply_to(message, "سلام سلام! برای شروع بازی /game را ارسال کنید")

@bot.message_handler(commands=['game'])
def start_game(message):
    user_guesses[message.chat.id] = []
    user_attempts[message.chat.id] = 0
    nuts_select[message.chat.id] = select_nuts()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for emoji in ['❤️', '💙', '💚', '💜']:
        markup.add(types.KeyboardButton(emoji))

    bot.send_message(message.chat.id, 'بازی شروع شد! 3 مهره انتخاب کنید:', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['شروع دوباره', 'بازگشت'])
def handle_buttons(message):
    if message.text == 'شروع دوباره':
        start_game(message)
    else:
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'بازی پایان یافت. امیدوارم لذت برده باشید!', reply_markup=markup)
        clean_user_data(message.chat.id)

def clean_user_data(chat_id):
    for dictionary in [user_guesses, user_attempts, nuts_select]:
        if chat_id in dictionary:
            del dictionary[chat_id]

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    
    if chat_id not in user_guesses:
        return

    emoji_map = {'❤️': 'r', '💙': 'b', '💚': 'g', '💜': 'p'}
    
    if message.text in emoji_map:
        user_guesses[chat_id].append(emoji_map[message.text])
        
        if len(user_guesses[chat_id]) < 3:
            remaining = 3 - len(user_guesses[chat_id])
            bot.send_message(chat_id, f'{remaining} مهره دیگر انتخاب کنید')
            return
            
        result = mastermind(user_guesses[chat_id], nuts_select[chat_id])
        user_attempts[chat_id] += 1
        
        feedback = [
            f"نتیجه حدس شما (تلاش {user_attempts[chat_id]}/3):",
            f"مهره‌های صحیح: {result['correct_select']}",
            f"مهره‌های در موقعیت صحیح: {result['correct_position']}",
            "\nوضعیت مهره‌ها:"
        ]
        
        for i in range(3):
            status = "✅ درست" if user_guesses[chat_id][i] == nuts_select[chat_id][i] else "❌ نادرست"
            feedback.append(f"مهره {i+1}: {status}")
        
        if result['is_correct']:
            feedback.append("\n🎉 شما برنده شدید!")
            markup = types.ReplyKeyboardMarkup()
            markup.add(types.KeyboardButton('شروع دوباره'), types.KeyboardButton('بازگشت'))
            bot.send_message(chat_id, '\n'.join(feedback), reply_markup=markup)
            clean_user_data(chat_id)
        elif user_attempts[chat_id] >= 3:
            # تبدیل حروف به استیکرها برای نمایش
            correct_emojis = [color_to_emoji[color] for color in nuts_select[chat_id]]
            feedback.append("\n😞 شما باختید! مهره‌های صحیح بودند: " + ' '.join(correct_emojis))
            markup = types.ReplyKeyboardMarkup()
            markup.add(types.KeyboardButton('شروع دوباره'), types.KeyboardButton('بازگشت'))
            bot.send_message(chat_id, '\n'.join(feedback), reply_markup=markup)
            clean_user_data(chat_id)
        else:
            feedback.append(f"\nدوباره امتحان کنید! (حدس‌های باقیمانده: {3 - user_attempts[chat_id]})")
            bot.send_message(chat_id, '\n'.join(feedback))
            user_guesses[chat_id] = []

if __name__ == '__main__':
    bot.polling()
