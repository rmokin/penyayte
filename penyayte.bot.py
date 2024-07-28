import os
import telebot
from telebot import types
import logging
import json
import sys
import  uuid

logger = logging.getLogger(__file__)
bot = None

DEFAULT_SETTINGS={
    "log":{
        "level": logging.INFO,
        "format": "%(name)s %(asctime)s %(levelname)s %(message)s",
    },
    "telegram":{
        "token": "***",
	}
}

class Scenario:
    def __init__(self, bot, steps=[]):
        self.__bot = bot
        self.__steps = steps

    def init(self):
        """
        for step in self.__steps:
            step.init()


        @self.__bot.message_handler(commands=['start'])
        def start_func(message):
            markup = types.InlineKeyboardMarkup()
            rus = types.InlineKeyboardButton('Русский 🇷🇺', callback_data='rus')
            eng = types.InlineKeyboardButton('English 🇬🇧', callback_data='eng')
            markup.row(rus, eng)
            self.__bot.send_message(message.chat.id, 'Please, choose the language you want to continue in below again 👇',
                             reply_markup=markup)

        """

        @self.__bot.message_handler()
        def message_handler(call):
            text = call.text
            step = self.__find_step_by_text__(text)
            if step:
                self.__bot.send_message(call.from_user.id, step.message, reply_markup=step.markup)
            else:
                logger.info(f"Undefined message:{text}")


        @self.__bot.callback_query_handler(func=lambda callback: True)
        def handle(call):
            self.__bot.send_message(call.message.chat.id, 'Data: {}'.format(str(call.data)))
            self.__bot.answer_callback_query(call.id)

    def __find_step_by_text__(self, text):
        for step in self.__steps:
            if step.message == text or step.command == text:
                return step

class ScenarioStep:
    def __init__(self, message="", buttons=[], command="", name=""):
        self._markup = types.InlineKeyboardMarkup()
        self._message = message
        self._buttons = buttons
        self._command = command
        self._name = name or str(uuid.uuid4())
        if len(self._buttons):
            self._markup.row(*[button.type for button in self._buttons])

    @property
    def markup(self):
        return self._markup

    @property
    def message(self):
        return self._message

    @property
    def command(self):
        return self._command







class StepButton:
    def __init__(self, text, url=None, name=None):
        self._text = text
        self._url = url
        self._name = name or str(uuid.uuid4())
        self._callback = self._name if self._url is None else None
        self._type = types.InlineKeyboardButton(self._text, self._url, self._callback)

    @property
    def type(self):
        return self._type



"""
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
        msg = bot.send_message(message.from_user.id, '(Шаг 1/3) Пожалуйста, укажите: Фамилию Имя Отчество', reply_markup=markup)
        bot.register_next_step_handler(msg, step_after_input_name, message)
    elif message.text == 'Изменить: Фамилию Имя Отчество':
        pass
    elif message.text == 'Правила сайта':
        bot.send_message(message.from_user.id, 'Прочитать правила сайта вы можете по ' + '[ссылке](https://habr.com/ru/docs/help/rules/)', parse_mode='Markdown')

    elif message.text == 'Правила по оформлению претензий':
        bot.send_message(message.from_user.id, 'Подробно про советы по оформлению претензий можно ознакомится по ' + '[ссылке](https://petition.rospotrebnadzor.ru/petition/)', parse_mode='Markdown')
    else:
        start(message)

@bot.message_handler(content_types=['text'])
def step_after_input_name(message, parent_message):

    path = f"messages/{parent_message.message_id}"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f'{path}/name.txt', 'w', encoding='utf-8') as f:
        f.write(message.text)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Продолжить: (Шаг 2/3) описать претензию')
    btn3 = types.KeyboardButton('Изменить: Фамилию Имя Отчество')
    markup.add(btn1, btn3)
    bot.send_message(message.from_user.id, f"{message.text}, cпасибо!", reply_markup=markup)



    msg = bot.send_message(message.from_user.id, 'Пришлите, пожалуйста, фотографии Вашей проблемы', reply_markup=markup)
    bot.register_next_step_handler(msg, step_add_photo, parent_message)

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
"""

def settings(path='config.json'):
    global logger, SETTINGS, DEFAULT_SETTINGS

    SETTINGS = {**DEFAULT_SETTINGS}
    loaded_settings = {}
    try:
        if os.path.isfile(path):
            with open(path) as f:
                loaded_settings = json.load(f)
        else:
            logger.debug(f"Can't find config. Use defaults")
    except Exception as e:
        logger.critical(f"Can't load config. Error: {str(e)}")
        sys.exit(1)
    else:
        SETTINGS.update(loaded_settings)
        SETTINGS["log"]["level"] = int(SETTINGS["log"]["level"])
        if SETTINGS["log"]["level"] < 10:
            SETTINGS["log"]["level"] = logging.NOTSET
        elif 10 <= SETTINGS["log"]["level"] < 20:
            SETTINGS["log"]["level"] = logging.DEBUG
        elif 20 <= SETTINGS["log"]["level"] < 30:
            SETTINGS["log"]["level"] = logging.INFO
        elif 30 <= SETTINGS["log"]["level"] < 40:
            SETTINGS["log"]["level"] = logging.WARNING
        elif 40 <= SETTINGS["log"]["level"] < 50:
            SETTINGS["log"]["level"] = logging.ERROR
        else:
            SETTINGS["log"]["level"] = logging.CRITICAL

        logger.setLevel(SETTINGS["log"]["level"])
        log_formatter = logging.Formatter(SETTINGS["log"]["format"])

        log_file_handler = logging.FileHandler(f"{os.path.basename(__file__)}.log", mode='a')
        log_file_handler.setFormatter(log_formatter)
        logger.addHandler(log_file_handler)

        log_console_handler = logging.StreamHandler()
        log_console_handler.setFormatter(log_formatter)
        logger.addHandler(log_console_handler)

def main():
    global SETTINGS, bot
    logger.info(f"Loading settings")
    settings('config.json')
    logger.info(f"Init telegram bot")
    logger.debug(f"token: {SETTINGS['telegram']['token']}")
    try:
        bot = telebot.TeleBot(SETTINGS['telegram']['token'])
    except Exception as e:
        logger.critical(f"Can't init telegram bot. Error: {str(e)}")
        sys.exit(1)

    scenario = Scenario(
        bot,
        [
            ScenarioStep(
                "👋 Привет! Я бот-помошник, совместно с группой компетентных юристов, помогу Вам корректно оформить претензию и направить её по надлежащему адресу",
                [
                    StepButton(
                        "Оформить претензию?"
                    ),
                    StepButton(
                        "Правила по оформлению",
                        "https://petition.rospotrebnadzor.ru/petition/"
                    ),
                ],
                "/start"
            )
        ]
    )

    scenario.init()

    logger.info(f"Staring read messages")
    bot.polling(none_stop=True, interval=0)
    logger.info(f"Stopping read messages")

if __name__ == '__main__':
    main()
