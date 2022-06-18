# импортируем все нужные библиотеки
import codecs  # потому что слетала кодировка
import json  # потому что словарь в формате json
import telebot  # непосредственно библиотека для работы с ботом
from telebot import *

bot = telebot.TeleBot('1152483061:AAEb3U5qdlkuh_6oV9oplfCctZK6ERpvczE')

# открываем json файл и вытаскиваем оттуда всю информацию
f = codecs.open("game.json", "r", "utf_8")
js = f.read()
f.close()
game = json.loads(js)

# тема - название раздела, который будет изучаться
# блок - какое-то количество вопросов, объединённых одним заданием
# задание - то, что нужно сделать (выбрать, написать, вставить пропуск и т.д.)
# вопрос - то, на что пользователю нужно каким-то образом ответить

steps = {}  # словарь вида id - тема - [номер блока, номер вопроса], чтобы сохранять прогресс пользователя

# записываем все названия тем в список
names = []  # 0 - Артикли, 1 - Существительные, 2- Степени сравнения прилагательных, 3 - Предлоги,
for name in game["themes"]:  # 4 - Использование времён, 5 - Пассивный залог, 6 - Инфинитивы, 7 - Причастие,
    n = game["themes"][name]["name"]  # 8- Герундий, 9 - Сложное дополнение, 10 - Сложное подлежащее,
    names.append(n)  # 11 - Условные предложения, 12 - Модальные глаголы

# записываем все отклики на нажатие кнопок в список
call_backs = []
for call_back in game["themes"]:
    c = game["themes"][call_back]["call_back"]
    call_backs.append(c)

# кастомная клавиатура
q_keyboard = types.ReplyKeyboardMarkup(False, True)  # создаём подходящий объект
q_keyboard.row('Нужна помощь.')  # добавляем в неё кнопки
q_keyboard.row("Я не знаю. Покажи ответ.")
q_keyboard.row("Выбрать другую тему.")
keyboard_end = types.InlineKeyboardMarkup()  # кнопка, которая появляется после решения всех заданий блока
key_end = types.InlineKeyboardButton(text="\ud83c\udf6a", callback_data="end")
keyboard_end.add(key_end)


# обработка команды /start, кнопки с выбором темы
@bot.message_handler(commands=['start'])
def themes(m):
    cid = m.chat.id
    steps[cid] = {}  # создаём словарь для хранения прогресса каждого пользователя
    for back in game["themes"]:  # в каждой теме ставим 0 номер блока и 0 номер вопроса по умолчанию
        call = game["themes"][back]["call_back"]
        steps[cid][call] = [0, 0]
    keyboard = types.InlineKeyboardMarkup()  # формируем выпадающие кнопки
    for i in range(13):
        key = types.InlineKeyboardButton(text=names[i], callback_data=call_backs[i])
        keyboard.add(key)
    bot.send_message(cid, text='Выберите раздел, который хотите отточить:', reply_markup=keyboard)


# те же кнопки с выбором темы, но уже для использования внутри основного цикла
def for_themes(cid):
    keyboard = types.InlineKeyboardMarkup()
    for i in range(13):
        key = types.InlineKeyboardButton(text=names[i], callback_data=call_backs[i])
        keyboard.add(key)
    bot.send_message(cid, text='Выберите раздел, который хотите отточить:',
                     reply_markup=keyboard)


# что происходит, когда получаем какое-либо сообщение
@bot.message_handler(content_types=['text'])
def message_in(message):
    cid = message.chat.id
    guess_what_to_do(cid, message.text)


# обработка команды /help
@bot.message_handler(commands=['help'])
def help1(message):
    bot.send_message(message.chat.id, 'Напиши "/start"')


# функция, которая выдаёт вопросы
def give_question(cid):
    tema = steps[cid]['current']  # steps[cid]['current'] = answer.data, то есть, текущая тема, на которой пользователь
    question = steps[cid][tema][1]  # получаем номер вопроса
    block = steps[cid][tema][0]  # получаем номер блока
    if question == len(game['themes'][tema]['questions'][block]['question']):
        question = 0  # обнуляем внутри условного оператора
        steps[cid][tema][1] = 0  # обнуляем в глобальной переменной
        block += 1
        steps[cid][tema][0] += 1
    if block == len(game['themes'][tema]['questions']):
        bot.send_message(cid, "Вы ответили на все имеющиеся вопросы по данной теме. Возьмите печеньку:)",
                         reply_markup=keyboard_end)  # закончили всю тему - получите печеньку
        return
    bot.send_message(cid, game['themes'][tema]['questions'][block]['task'] + '\n\n' +
                     game['themes'][tema]['questions'][block]['question'][question], reply_markup=q_keyboard)


# функция, которая проверяет ответы
def guess_what_to_do(cid, answer):
    tema = steps[cid]['current']  # steps[cid]['current'] = answer.data, то есть, текущая тема, на которой пользователь
    block = steps[cid][tema][0]  # получаем номер блока
    question = steps[cid][tema][1]  # получаем номер вопроса
    # проверяем на соответствие, не обращая внимание на регистр
    if answer.lower().rstrip('.') != (game['themes'][tema]['questions'][block]['answer']
                                      [question].lower().rstrip('.')):
        # проверям на соответствие надписям на кнопках кастомной клавиатуры
        if answer == "Нужна помощь.":
            bot.send_message(cid, game['themes'][tema]['questions'][block]['help'])
            bot.send_message(cid,
                             "Попробуйте ещё раз." + "\n" + game['themes'][tema]['questions'][block]
                             ['task'] + '\n\n' + game['themes'][tema]['questions'][block]['question']
                             [question], reply_markup=q_keyboard)

        elif answer == "Я не знаю. Покажи ответ.":
            bot.send_message(cid,
                             'Правильный ответ:' + '\n\n' + game['themes'][tema]['questions'][block]['answer']
                             [question])
            steps[cid][tema][1] += 1
            give_question(cid)
        elif answer == "Выбрать другую тему.":
            for_themes(cid)
        else:
            bot.send_message(cid,
                             'Вы ошиблись. Попробуйте ещё раз.' + '\n' + game['themes'][tema]
                             ['questions'][block]['task'] + '\n\n' + game['themes'][tema]['questions'][block]
                             ['question'][question], reply_markup=q_keyboard)
    else:
        bot.send_message(cid, 'Вы абсолютно правы!')
        steps[cid][tema][1] += 1  # молодец и ответили правильно
        give_question(cid)


# обработкий нажатий на кнопку выбора темы после запуска бота
@bot.callback_query_handler(func=lambda call: True)
def optionals(m):
    cid = m.message.chat.id
    if m.data == "end":  # после выдачи печеньки
        for_themes(cid)
    else:  # после выбора темы
        steps[cid]['current'] = m.data
        give_question(cid)


bot.polling(none_stop=True, interval=0)
