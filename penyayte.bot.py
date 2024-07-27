import os
import telebot
from telebot import types

bot = telebot.TeleBot('7258182952:AAH82Ao0wfPUCwzS-F1bqUuAa-8N2X0ycQc')

@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Оформить претензию?')
    btn3 = types.KeyboardButton('Правила по оформлению претензий')
    markup.add(btn1, btn3)
    bot.send_message(
        message.from_user.id,
    "👋 Привет! Я бот-помошник, совместно с группой компетентных юристов, помогу Вам корректно оформить "
        "претензию и направить её по надлежащему адресу",
        reply_markup=markup
    )
@bot.message_handler(commands=['button'])
def button_message(message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Кнопка")
    markup.add(item1)
    bot.send_message(message.chat.id,'Выберите что вам надо',reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == 'Оформить претензию?':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        msg = bot.send_message(message.from_user.id, 'Опишите, пожалуйста, Вашу проблему', reply_markup=markup)
        bot.register_next_step_handler(msg, step_after_input_message, message)
    elif message.text == 'Правила сайта':
        bot.send_message(message.from_user.id, 'Прочитать правила сайта вы можете по ' + '[ссылке](https://habr.com/ru/docs/help/rules/)', parse_mode='Markdown')

    elif message.text == 'Правила по оформлению претензий':
        bot.send_message(message.from_user.id, 'Подробно про советы по оформлению претензий можно ознакомится по ' + '[ссылке](https://petition.rospotrebnadzor.ru/petition/)', parse_mode='Markdown')
    else:
        start(message)

@bot.message_handler(content_types=['text'])
def step_after_input_message(message, parent_message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создание новых кнопок
    bot.send_message(message.from_user.id, f"Спасибо!", reply_markup=markup)
    path = f"messages/{parent_message.message_id}"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f'{path}/message.txt', 'w', encoding='utf-8') as f:
        f.write(message.text)
    msg = bot.send_message(message.from_user.id, 'Пришлите, пожалуйста, фотографии Вашей проблемы', reply_markup=markup)
    bot.register_next_step_handler(msg, step_add_photo, parent_message)

@bot.message_handler(content_types=['photo'])
def step_add_photo(message, parent_message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создание новых кнопок
    path = f"messages/{parent_message.message_id}"
    if message.content_type == 'photo':
        raw = message.photo[2].file_id
        name = raw + ".jpg"
        file_info = bot.get_file(raw)
        downloaded_file = bot.download_file(file_info.file_path)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(f'{path}/photo.jpg', 'wb') as f:
            f.write(downloaded_file)

    bot.send_message(
        message.from_user.id,
        f'Ваша претензия передана на анализ юристам. Спасибо большое за Ваше обращение!',
        reply_markup=markup
    )


bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть