import telebot
import random
from database import Database
from datetime import datetime, date
import time
from buttons import *
import os
from dotenv import load_dotenv, find_dotenv
from roulette_data import sectors, all_nums, pack, first12, second12, third12
import requests

load_dotenv(find_dotenv())

ADMIN_ID = int(os.getenv('USER_ID'))
db = Database('Bot/users.db')
bot = telebot.TeleBot(os.getenv('TOKEN'))


@bot.message_handler(commands=['register'])
def reg(message):
    user_id = message.from_user.id
    if not db.user_exists(user_id):
        db.add_user(user_id)
        msg = bot.reply_to(message, "Укажите желаемый никнейм.")
        bot.register_next_step_handler(msg, register)
    else:
        bot.send_message(user_id, 'Вы уже зарегестрированы!')
        bot.send_message(message.chat.id, f'Привет, {db.get_nickname(user_id)}, выбери игру!', reply_markup=main_menu())


@bot.message_handler(commands=['start', 'help'])
def start(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Добро пожаловать в ботяру с играми, для регистрации пропишите /register')


@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, 'Привет, господин!', reply_markup=admin_menu())
    else:
        bot.send_message(message.from_user.id, 'У вас нет прав администратора! Идите на хуй')


@bot.message_handler(commands=['get_admin_contact'])
def send_admin_contact(message):
    bot.send_contact(chat_id=message.from_user.id, phone_number='+79120810518', first_name='Artyomlbch')


@bot.message_handler(commands=['balance'])
def get_user_balance(message):
    try:
        return bot.send_message(message.from_user.id, f'Ваш баланс: {db.get_balance(message.from_user.id)}р')
    except Exception as ex:
        print(ex)


@bot.message_handler(commands=['roulette'])
def roulette_info(message: dict[str:str]) -> None:
    photo = open('casino-roulette-table-illustration-green-gambling-roulette-table-numbers-90513337.jpg', 'rb')
    bot.send_photo(message.chat.id, photo)
    bot.send_message(message.from_user.id, 'Информация!!!\nДля ставки на число пишите: /roulettenum [ставка] [число]'
                                           '\nДля ставки на сектор пишите: /roulettesec [ставка] [1 или 2 или 3]'
                                           '\nДля ставки на цвет пишите: /rouletteclr [ставка] [r или b]')


@bot.message_handler(commands=['roulettenum'])
def roulette_number(message):
    if len(message.text.split()) == 1:
        return bot.send_message(message.from_user.id, 'Аргументы пиши.')
    try:
        bet = int(message.text.split()[1])
        num = int(message.text.split()[2])
        if num not in range(0, 37):
            raise ValueError

        def win(rand_num):
            bot.send_message(message.from_user.id, f"И выпадает **** {rand_num} ****")
            db.add_balance(message.from_user.id, bet * 35)
            bot.send_message(message.from_user.id,
                             f"Вы выиграли: {bet * 35}р. Баланс: {db.get_balance(message.from_user.id)}p")

        db.min_balance(message.from_user.id, bet)
        rand_num = random.choice(all_nums)
        bot.send_message(message.from_user.id, 'Рулетка крутится...')
        if num == rand_num:
            win(rand_num)
            db.add_win(message.from_user.id)
        else:
            bot.send_message(message.from_user.id, f"И выпадает **** {rand_num} ****")
            bot.send_message(message.from_user.id, f"Вы проиграли. Ваш баланс: {db.get_balance(message.from_user.id)}р")
            db.add_lose(message.from_user.id)
    except ValueError:
        bot.send_message(message.from_user.id, 'Неподходящее число')
    except Exception as ex:
        print(ex)
        bot.send_message(message.from_user.id, 'Чтобы пополнить баланс пропишите Пополнить баланс')


@bot.message_handler(commands=['roulettesec'])
def roulette_sec(message):
    if len(message.text.split()) == 1:
        return bot.send_message(message.from_user.id, 'Пиши аргументы.')
    try:
        bet = int(message.text.split()[1])
        num = int(message.text.split()[2])
        db.min_balance(message.from_user.id, bet)
        if num not in range(1, 4):
            raise ValueError
        bot.send_message(message.from_user.id, 'Рулетка крутится..')
        time.sleep(1)
        win_sector = random.choice([1, 2, 3])
        if num == win_sector:
            bot.send_message(message.from_user.id,
                             f'Выпал {win_sector} сектор, число **** {random.choice(sectors[num - 1])} ****')
            bot.send_message(message.from_user.id, f'Победа!! Вы выиграли {bet * 3}р.')
            db.add_balance(message.from_user.id, bet * 3)
            bot.send_message(message.from_user.id, f'Баланс: {db.get_balance(message.from_user.id)}p')
            db.add_win(message.from_user.id)
        else:
            bot.send_message(message.from_user.id,
                             f'Выпал {win_sector} сектор, число **** {random.choice(sectors[win_sector - 1])} ****')
            bot.send_message(message.from_user.id, f'Вы проиграли, ваш баланс: {db.get_balance(message.from_user.id)}р')
            db.add_lose(message.from_user.id)
    except ValueError:
        bot.send_message(message.from_user.id, 'Выбери сектор 1 - 3')
    except Exception as ex:
        print(ex)
        bot.send_message(message.from_user.id, f'Недостаточно средств, баланс: {db.get_balance(message.from_user.id)}p')


@bot.message_handler(commands=['send_message'])
def send_message_to_user(message):
    if len(message.text.split()) == 1:
        bot.send_message(message.from_user.id, "Чтобы отправить сообщение, напишите\n/send_message nickname message")
        return
    try:
        text = message.text.split()
        user = text[1]
        your_message = text[2]

        message_to_send = f"{db.get_nickname(message.from_user.id)} отправил вам сообщение:\n{your_message}"
        bot.send_message(db.get_id_by_nickname(user), message_to_send)
        bot.send_message(message.from_user.id, "Успешно!")
    except Exception as ex:
        print(ex)
        bot.send_message(message.from_user.id, "Такого пользователя нет.")


@bot.message_handler(commands=['rouletteclr'])
def roulette_clr(message):
    if len(message.text.split()) == 1:
        return bot.send_message(message.from_user.id, 'Аргументы пиши')
    clr = message.text.split()[2]
    bet = int(message.text.split()[1])
    numbersR, numbersB = {'❤️': [i for i in range(2, 38, 2)]}, {'🖤': [i for i in range(1, 36, 2)]}
    red_or_black = [numbersR, numbersB]

    def win(color: str):
        bot.send_message(message.from_user.id, f'{color} Выигрыш: {bet * 2}p')
        db.add_balance(message.from_user.id, bet * 2)
        bot.send_message(message.from_user.id, f'Баланс: {db.get_balance(message.from_user.id)}р')
        db.add_win(message.from_user.id)

    try:
        if clr == 'r':
            clr = '❤️'
        elif clr == 'b':
            clr = '🖤'
        else:
            raise ValueError
        db.min_balance(message.from_user.id, bet)
        for i, j in random.choice(red_or_black).items():
            bot.send_message(message.from_user.id, 'Рулетка крутится..')
            time.sleep(1)
            bot.send_message(message.from_user.id, f'****  {i}  {random.choice(j)}  {i}  ****')
            if i == '❤️' and clr == '❤️':
                win('Красное!')
            elif i == '🖤' and clr == '🖤':
                win('Черное!')
            else:
                bot.send_message(message.from_user.id, f'Вы проиграли :(')
                bot.send_message(message.from_user.id, f'Баланс: {db.get_balance(message.from_user.id)}р')
                db.add_lose(message.from_user.id)
            break
    except ValueError:
        bot.send_message(message.from_user.id, 'Введите r или b')
    except Exception as ex:
        print(ex)
        bot.send_message(message.from_user.id, f'Балик пополни, баланс: {db.get_balance(message.from_user.id)}р',
                         reply_markup=add_balance_menu())


def create_bj_cards():
    cards = {"2": 2,
             "3": 3,
             "4": 4,
             "5": 5,
             "6": 6,
             "7": 7,
             "8": 8,
             "9": 9,
             "10": 10,
             "J": 10,
             "Q": 10,
             "K": 10,
             "T": 11}

    return cards

@bot.message_handler(commands=['blackjack'])
def blackjack(message):
    if len(message.text.split()) != 2:
        bot.send_message(message.from_user.id, "Введите подходящую сумму.")
        return

    try:
        sum_to_play = int(message.text.split()[1])
        if (db.get_balance(message.from_user.id) - sum_to_play) < 0:
            bot.send_message(message.from_user.id, "Недостаточно средств.")
            return

        cards = create_bj_cards()

        db.set_bet(message.from_user.id, sum_to_play)
        db.min_balance(message.from_user.id, sum_to_play)

        first_player_card, first_dealer_card = random.choice(list(cards.keys())), random.choice(list(cards.keys()))
        second_player_card = random.choice(list(cards.keys()))
        player_value = 12 if first_player_card + second_player_card == "TT" else (cards[first_player_card] +
                                                                                  cards[second_player_card])
        dealer_value = cards[first_dealer_card]

        db.add_played(message.from_user.id)
        bot.send_message(message.from_user.id, f"Your cards: |{first_player_card}| |{second_player_card}| Value: {player_value}\n"
                                                    f"Dealer cards: |{first_dealer_card}| |X| Value: {dealer_value}",
                                                    reply_markup=blackjack_menu())
    except Exception as ex:
        bot.send_message(message.from_user.id, "Введите валидную сумму.")
        print(ex)


@bot.callback_query_handler(lambda query: query.data == 'stand')
def bj_stand(call):
    user_id = call.from_user.id

    player_message, dealer_message = call.message.text.split("\n")[0].split(), call.message.text.split("\n")[1].split()
    player_value, dealer_value = int(player_message[-1]), int(dealer_message[-1])
    cards = create_bj_cards()

    prev_cards = list()
    prev_cards.append(dealer_message[2])

    while dealer_value < 21 and dealer_value < player_value:
        card = random.choice(list(cards.keys()))
        if card == "T":
            dealer_value += 1 if dealer_value + 11 > 21 else 11
        else:
            dealer_value += cards[card]
        prev_cards.append(f'|{card}|')

    new_message = (f'{" ".join(player_message)}\n'
                   f'Dealer cards: {" ".join(prev_cards)} Value: {dealer_value}')

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_message)

    if player_value < dealer_value <= 21:
        bot.send_message(user_id, f"You lost!\nYour balance: {db.get_balance(user_id)}")
        db.add_lose(user_id)
    elif dealer_value == player_value:
        db.add_balance(user_id, db.get_bet(user_id))
        bot.send_message(user_id, f"Draw! Your balance: {db.get_balance(user_id)}")
    else:
        if player_value == 21:
            db.add_balance(user_id, (db.get_bet(user_id) * 2.5))
        else:
            db.add_balance(user_id, (db.get_bet(user_id) * 2))

        bot.send_message(user_id, f"You win!!! Your balance: {db.get_balance(user_id)}")
        db.add_win(user_id)

    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(lambda query: query.data == 'hit')
def bj_hit(call, is_doubled=False):
    player_message, dealer_message = call.message.text.split()[:-6], call.message.text.split()[-6:]

    cards = create_bj_cards()
    new_card = random.choice(list(cards.keys()))
    if new_card == "T":
        new_value = int(player_message[-1]) + 1 if int(player_message[-1]) + 11 > 21 else int(player_message[-1]) + 11
    else:
        new_value = int(player_message[-1]) + cards[new_card]

    prev_cards = []
    i = 2
    while player_message[i] != "Value:":
        prev_cards.append(player_message[i])
        i += 1

    prev_cards.append(f"|{new_card}|")
    new_message = (f'Your cards: {" ".join(prev_cards)} Value: {new_value}\n'
                   f'{" ".join(dealer_message)}')

    if new_value > 21:
        new_message = (f'Your cards: {" ".join([i for i in prev_cards])} Value: {new_value}\n'
                       f'{" ".join(dealer_message)}')

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_message)
        bot.send_message(call.from_user.id, f"You lost!\nYour balance: {db.get_balance(call.from_user.id)}")
        db.add_lose(call.from_user.id)
        bot.answer_callback_query(callback_query_id=call.id)
    else:
        if is_doubled:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_message,
                                  reply_markup=bj_stand_menu())
            bot.answer_callback_query(callback_query_id=call.id)

        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_message,
                                  reply_markup=blackjack_menu())
            bot.answer_callback_query(callback_query_id=call.id)

@bot.callback_query_handler(lambda query: query.data == 'bj_double')
def blackjack_double(call):
    user_id = call.from_user.id
    bet = db.get_bet(user_id)

    if (db.get_balance(user_id) - bet) < 0:
        bot.send_message(user_id, "Not enough money. Choose Hit/Stand")
        bot.answer_callback_query(callback_query_id=call.id)

    else:
        db.min_balance(user_id, bet)
        bj_hit(call, True)


@bot.message_handler(commands=['dice'])
def random_dice(message):
    def win(n):
        bot.send_message(user_id, f'Выпало {random_int}, вы выиграли {bet * n}р!')
        db.add_balance(user_id, (bet * n))
        db.add_win(user_id)
        return bot.send_message(user_id, f'Ваш баланс: {db.get_balance(user_id)}р')

    user_id = message.from_user.id
    random_int = random.randint(0, 1000)

    try:
        bet = int(message.text.split()[1])
        db.add_played(message.from_user.id)
        if db.get_balance(user_id) == 0 or not (db.min_balance(user_id, bet)):
            raise Exception
        if random_int == 777:
            bot.send_message(message.from_user.id, "777! Джекпот!!! 1000x")
            win(1000)

        if 500 < random_int < 800:
            win(2)
        elif 800 < random_int < 950:
            win(2.5)
        elif 950 <= random_int < 995:
            win(8)
        elif 995 < random_int <= 1000:
            win(200)
        else:
            bot.send_message(user_id, f'Выпало: {random_int}. Вы проиграли.')
            db.add_lose(user_id)
            return bot.send_message(user_id, f'Ваш баланс: {db.get_balance(user_id)}р')
    except ValueError:
        bot.send_message(user_id, 'Неправильно введена ставка!')
    except Exception as ex:
        print(ex)
        bot.send_message(user_id, 'Недостаточно средств')


@bot.callback_query_handler(lambda query: query.data == 'wu')
def adm(call):
    info = ''
    for nickname, balance in db.get_users_info():
        info += f'Никнейм: {nickname} ({balance}р)\n'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=info)
    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(lambda query: query.data == 'sa')
def send_all(call):
    msg = bot.reply_to(call.message, 'Введите сообщения для отправки')
    bot.register_next_step_handler(msg, send_msg_to_all)


@bot.callback_query_handler(lambda query: query.data == 'mny')
def give_money(call):
    db.add_balance(ADMIN_ID, 50000)
    t = f'Успешно! Ваш баланс: {db.get_balance(ADMIN_ID)}р'
    bot.edit_message_text(chat_id=ADMIN_ID, message_id=call.message.message_id, text=t)


@bot.callback_query_handler(lambda query: query.data == 'sto')
def send_all(call):
    msg = bot.reply_to(call.message, 'Введите ник пользователя и сообщения')
    bot.register_next_step_handler(msg, send_msg_to_user)


def send_msg_to_user(message):
    for user_id in db.get_users_id():
        nick, msg = message.text.split()
        if db.get_nickname(user_id) == nick:
            bot.send_message(user_id, msg)
            bot.send_message(ADMIN_ID, 'Успешно!')


def send_msg_to_all(message):
    for user_id in db.get_users_id():
        bot.send_message(user_id, message.text)
    else:
        bot.send_message(message.from_user.id, 'Успешно!')


dice_stickers = ['CAACAgIAAxkBAAEFeGFi7FH1VZBDWkawMiTMcUbZiYuLLQACixUAAu-iSEvcMCGEtWaZoCkE',
                 'CAACAgIAAxkBAAEFeGNi7FOAh1uE9P3dyTLjhCHQnHKawwACzxEAAlKRQEtOAAGmnvjK7y8pBA',
                 'CAACAgIAAxkBAAEFeGVi7FOJ-VF_UFHLLhlwdpf3sLsL-QACQBEAAiOsQUurmtw9CutR3ykE',
                 'CAACAgIAAxkBAAEFeGdi7FOVbDEy_3bBT1yQgIPOGdqBbQACcREAAuzsQUu1GqzW_T-jpCkE',
                 'CAACAgIAAxkBAAEFeGli7FOg0OoSKIrFdLyZ6jb2tHEAARkAAqEPAAJBtUFLbsHChM0BoSEpBA',
                 'CAACAgIAAxkBAAEFeGti7FOsaftdN19xvSiWnwABnpNFCFIAAvYNAAL3rUhLVg8sKkK3KGMpBA']


@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.text == 'Проверить баланс':
        bot.send_message(message.chat.id, f'Ваш баланс: {db.get_balance(message.from_user.id)}р')
        bot.send_message(message.chat.id, 'Что желаете сделать?', reply_markup=check_balance())

    elif message.text == 'artyomisthebest':
        db.add_balance(message.from_user.id, 10000)
        bot.send_message(message.from_user.id, 'Ваш баланс пополнен на 10.000р.')

    elif message.text == 'Перевести':
        msg = bot.send_message(message.from_user.id, 'Напишите ID и сумму (ID СУММА).')
        bot.register_next_step_handler(msg, send_money)

    elif message.text == 'Блэкджек':
        bot.send_message(message.from_user.id, "Чтобы играть в Blackjack, напишите команду: /blackjack [ставка]")

    elif message.text == 'Игры':
        user_id = message.from_user.id
        bot.send_message(user_id, 'Выбирайте', reply_markup=games_menu())

    elif message.text == 'Рулетка':
        user_id = message.from_user.id
        bot.send_message(user_id, 'Для информации об игре используйте команду /roulette', reply_markup=quit_menu())

    elif message.text == 'Сменить ник':
        user_id = message.from_user.id
        msg = bot.reply_to(message, 'Какой ник хочешь?')
        bot.register_next_step_handler(msg, change_nickname)

    elif message.text == 'Факт о числе':
        msg = bot.reply_to(message, 'Число?')
        bot.register_next_step_handler(msg, get_num_fact)

    elif message.text == 'Профиль':
        user_id = message.from_user.id

        bot.send_message(message.from_user.id, f'''{date.today().strftime("%B %d, %Y")}
        Ваш никнейм: {db.get_nickname(user_id)}
        Баланс: {db.get_balance(user_id)}р
        Ваш ID: {user_id}''', reply_markup=profile_menu())

    elif message.text == 'Рандом кости':
        bot.reply_to(message,
                     'Для игры используйте команду: /dice [ставка].\nВозможные выйгрыши(число: [500; 800] - 2x; [800; 950] - 2.5x, [950; 995] - 8x, [995; 1000] - 200x)')

    elif message.text == 'Выйти':
        bot.reply_to(message, 'Хорошо, выходим...', reply_markup=main_menu())

    elif message.text == 'Статистика':
        user_id = message.from_user.id

        if db.get_played(user_id) == 0:
            bot.send_message(user_id, f'''Игр сыграно: {db.get_played(user_id)}
                Выйгрыши/проигрыши: {db.get_win(user_id)}/{db.get_lose(user_id)}
                Процент побед: 0%''', reply_markup=quit_menu())
        else:
            bot.send_message(user_id, f'''Игр сыграно: {db.get_played(user_id)}
                            Выйгрыши/проигрыши: {db.get_win(user_id)}/{db.get_lose(user_id)}
                            Процент побед: {round(100 * (round(db.get_win(user_id) / db.get_played(user_id), 2)))}%''',
                             reply_markup=quit_menu())

    elif message.text == 'Пополнить баланс':
        msg = bot.reply_to(message, 'Введите сумму пополнения.')
        bot.register_next_step_handler(msg, add_blnc)

    elif message.text == 'Вывести деньги':
        msg = bot.reply_to(message, 'Введите сумму.')
        bot.register_next_step_handler(msg, min_blnc)

    elif message.text == 'Больше/меньше':
        user_id = message.from_user.id

        bet = bot.send_message(user_id, 'Введите ставку:')
        bot.register_next_step_handler(bet, more)

    elif message.text == 'Играть':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.reply_to(message, 'Выбирайте игру', reply_markup=games_menu())

    elif message.text == 'Кости':
        bot.send_message(message.from_user.id, 'Игра Кости!\nПравила очень просты:\nугадайте число от 1 до 6')

        msg = bot.reply_to(message, 'Выберите ставку', reply_markup=bet_menu())
        bot.register_next_step_handler(msg, dice)

    elif message.text == 'Изменить ставку':
        bot.send_message(message.from_user.id, 'Выберите', reply_markup=games_menu())

    else:
        bot.send_message(message.from_user.id, 'Я тебя не понимаю :((((')


def register(message):
    user_id = message.from_user.id
    if db.get_signup(user_id) == 'setnickname':
        if len(message.text) > 15:
            bot.send_message(user_id, 'Ник не должен превышать 15 символов!')
        elif '@' in message.text or '/' in message.text:
            bot.send_message(message.chat.id, 'В вашем нике присутствует запрещенный символ!')
        else:
            db.set_nickname(user_id, message.text)
            db.set_signup(user_id, 'done')
            bot.send_message(user_id, 'Регистрация успешно завершена!')

            bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, выбери игру!',
                             reply_markup=main_menu())


def get_num_fact(message):
    response = requests.get(f'http://numbersapi.com/{message.text}/math')
    bot.send_message(message.from_user.id, response.text)


def change_nickname(message):
    try:
        db.set_nickname(message.from_user.id, message.text)
        bot.send_message(message.from_user.id, f'Успешно, теперь вы - {db.get_nickname(message.from_user.id)}')
    except Exception as ex:
        print(ex)


def add_blnc(message):
    try:
        amount = int(message.text)
        if amount <= 500000:
            db.add_balance(message.from_user.id, amount)
            bot.send_message(message.from_user.id, f'Успешно! Ваш баланс: {db.get_balance(message.from_user.id)}р')
        else:
            raise Exception
    except Exception as ex:
        print(ex)
        bot.send_message(message.from_user.id, 'Меньше 500.000р...')


def min_blnc(message):
    try:
        amount = int(message.text)
        db.min_balance(message.from_user.id, amount)
        bot.send_message(message.from_user.id, f'Успешно! Ваш баланс: {db.get_balance(message.from_user.id)}р')
    except Exception as ex:
        print(ex)
        bot.send_message(message.from_user.id, 'Вы хотите вывести слишком много денег.')


def more(message):
    try:
        db.set_bet(message.from_user.id, int(message.text))
        bot.reply_to(message, 'Хорошо, поехали!', reply_markup=dice_menu())
        msg = bot.send_message(message.from_user.id, 'Напишите любое число от 1 до 100')
        bot.register_next_step_handler(msg, moreLess)

    except Exception as ex:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Проверить баланс')
        button2 = types.KeyboardButton('Играть')
        markup.add(button1, button2)

        bot.send_message(message.from_user.id, 'Слишком большая ставка или неправильно введенное число!',
                         reply_markup=markup)


def send_money(message):
    try:
        if db.user_exists(int(message.text.split()[0])):
            id, summ = int(message.text.split()[0]), int(message.text.split()[1])
            db.add_balance(id, summ)
            db.min_balance(message.from_user.id, summ)
            bot.send_message(message.from_user.id, 'Деньги успешно переведены')
            bot.send_message(id, f'{db.get_nickname(message.from_user.id)} перевел Вам {summ}р')
        else:
            bot.send_message(message.from_user.id, 'ID или сумма введены неправильно')
    except Exception as ex:
        print(ex)
        bot.send_message(message.from_user.id, 'Что-то пошло не так (проверьте ID или сумму)')


def moreLess(message):
    inline = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(
        f'Больше >> {100 - int(message.text)}%/{round(100 / (100 - int(message.text)), 2)}x',
        callback_data='more')
    item2 = types.InlineKeyboardButton(
        f'Меньше << {100 - (100 - int(message.text))}%/{round(100 / int(message.text), 2)}x',
        callback_data='less')
    inline.add(item1, item2)

    bot.reply_to(message, f'{message.text}', reply_markup=inline)


def dice(message):
    try:
        db.set_bet(message.from_user.id, int(message.text))
        bot.reply_to(message, 'Хорошо, поехали!', reply_markup=dice_menu())
        bot.send_message(message.from_user.id, 'Выбирайте число', reply_markup=dice_buttons())

    except Exception as ex:

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Проверить баланс')
        button2 = types.KeyboardButton('Играть')
        markup.add(button1, button2)

        bot.send_message(message.from_user.id, 'Слишком большая ставка или неправильно введенное число!',
                         reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data in ['more', 'less'])
def more_game(call):
    try:
        dig = int(call.message.text)
        random_int = random.uniform(0, 100)
        user_id = call.message.chat.id
        db.add_played(user_id)
        db.min_balance(user_id, db.get_bet(call.message.chat.id))
        if call.data == 'more':
            if random_int > dig:
                db.add_win(user_id)
                win = round(db.get_bet(user_id) * round(100 / (100 - int(dig)), 2))
                win_msg = bot.send_message(user_id, f'Выпало: {round(random_int, 3)}\nВаш выйгрыш: {win}р')
                db.add_balance(user_id, win)
                blnc_msg = bot.send_message(user_id, f'Ваш баланс: {db.get_balance(user_id)}р')

                time.sleep(2)
                bot.delete_message(win_msg.chat.id, win_msg.message_id)
                bot.delete_message(blnc_msg.chat.id, blnc_msg.message_id)

            else:
                db.add_lose(user_id)
                lose_msg = bot.send_message(user_id, f'Выпало: {round(random_int, 2)}\nВы проиграли :(')
                blnc_msg = bot.send_message(user_id, f'Ваш баланс: {db.get_balance(user_id)}р')

                time.sleep(2)
                bot.delete_message(lose_msg.chat.id, lose_msg.message_id)
                bot.delete_message(blnc_msg.chat.id, blnc_msg.message_id)
        else:
            if random_int < dig:
                db.add_win(user_id)
                win = db.get_bet(user_id) * round(100 / int(dig), 2)
                win_msg = bot.send_message(user_id, f'Выпало: {round(random_int, 3)}\nВаш выйгрыш: {win}р')
                db.add_balance(user_id, win)
                blnc_msg = bot.send_message(user_id, f'Ваш баланс: {db.get_balance(user_id)}р')

                time.sleep(2)
                bot.delete_message(win_msg.chat.id, win_msg.message_id)
                bot.delete_message(blnc_msg.chat.id, blnc_msg.message_id)

            else:
                db.add_lose(user_id)
                lose_msg = bot.send_message(user_id, f'Выпало: {round(random_int, 2)}\nВы проиграли :(')
                blnc_msg = bot.send_message(user_id, f'Ваш баланс: {db.get_balance(user_id)}р')

                time.sleep(2)
                bot.delete_message(lose_msg.chat.id, lose_msg.message_id)
                bot.delete_message(blnc_msg.chat.id, blnc_msg.message_id)
    except Exception as ex:
        print(ex)
        bot.send_message(user_id, 'Недостаточно средств, пополните баланс')

    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(lambda query: query.data in '123456')
def dice_game(call):
    try:
        user_id = call.message.chat.id
        db.min_balance(user_id, db.get_bet(call.message.chat.id))
        win_digit = random.randint(1, 6)
        dice_sticker = bot.send_sticker(call.message.chat.id, dice_stickers[win_digit - 1])
        db.add_played(user_id)
        time.sleep(3)
        if call.message:
            print(win_digit)
            if int(call.data) == win_digit:
                db.add_win(user_id)

                win = db.get_bet(user_id) * 6
                win_msg = bot.send_message(user_id, f'Вы угадали! Ваш выйгрыш: {win}р')
                db.add_balance(user_id, win)

                time.sleep(1)
                bot.delete_message(win_msg.chat.id, win_msg.message_id)
                bot.delete_message(dice_sticker.chat.id, dice_sticker.message_id)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f'Ваш баланс: {db.get_balance(user_id)}р',
                                      reply_markup=dice_buttons())
            else:
                db.add_lose(user_id)
                lose_msg = bot.send_message(user_id, f'Вы проиграли :(')

                time.sleep(1)
                bot.delete_message(lose_msg.chat.id, lose_msg.message_id)
                bot.delete_message(dice_sticker.chat.id, dice_sticker.message_id)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f'Ваш баланс: {db.get_balance(user_id)}р',
                                      reply_markup=dice_buttons())
    except Exception as ex:
        print(ex)
        bot.send_message(user_id, 'Недостаточно средств, пополните баланс')
    bot.answer_callback_query(callback_query_id=call.id)


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.infinity_polling()
