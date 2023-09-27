from telebot import types

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Игры')
    button2 = types.KeyboardButton('Проверить баланс')
    button3 = types.KeyboardButton('Профиль')
    button4 = types.KeyboardButton('Перевести')
    markup.add(button1, button2, button3, button4)

    return markup

def games_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Больше/меньше')
    button2 = types.KeyboardButton('Кости')
    button3 = types.KeyboardButton('Рандом кости')
    button4 = types.KeyboardButton('Рулетка')
    button5 = types.KeyboardButton('Выйти')
    markup.add(button1, button2, button3, button4, button5)

    return markup

def check_balance():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Пополнить баланс')
    button2 = types.KeyboardButton('Вывести деньги')
    button3 = types.KeyboardButton('Играть')
    markup.add(button1, button2, button3)

    return markup

def add_balance_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Пополнить баланс')
    button2 = types.KeyboardButton('Выйти')
    markup.add(button1, button2)

    return markup

def dice_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Изменить ставку')
    button2 = types.KeyboardButton('Выйти')
    markup.add(button1, button2)

    return markup

def dice_buttons():
    inline = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('1', callback_data='1')
    item2 = types.InlineKeyboardButton('2', callback_data='2')
    item3 = types.InlineKeyboardButton('3', callback_data='3')
    item4 = types.InlineKeyboardButton('4', callback_data='4')
    item5 = types.InlineKeyboardButton('5', callback_data='5')
    item6 = types.InlineKeyboardButton('6', callback_data='6')
    inline.add(item1, item2, item3, item4, item5, item6)

    return inline

def profile_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Выйти')
    button2 = types.KeyboardButton('Статистика')
    button3 = types.KeyboardButton('Сменить ник')
    markup.add(button1, button2, button3)

    return markup

def quit_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Выйти')
    markup.add(button1)

    return markup

def bet_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('100')
    button2 = types.KeyboardButton('500')
    button3 = types.KeyboardButton('1000')
    markup.add(button1, button2, button3)

    return markup

def admin_menu():
    inline = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Посмотреть пользователей', callback_data='wu')
    item2 = types.InlineKeyboardButton('Разослать сообщение всем', callback_data='sa')
    item3 = types.InlineKeyboardButton('Разослать сообщение пользователю', callback_data='sto')
    item4 = types.InlineKeyboardButton('Выдать себе 50.000р', callback_data='mny')
    inline.add(item1, item2, item3, item4)

    return inline