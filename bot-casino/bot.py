#5242417371:AAFNa0bLKBgc4repVmCZxUA0IahQlWSR7aU
#V 1.3.1

import sqlite3
import telebot
from telebot import types
import random
import time


conn = sqlite3.connect('promo.db', check_same_thread=False)
cur = conn.cursor()

bd = sqlite3.connect('user.db', check_same_thread=False)
sql = bd.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS user(
    username TEXT,
    login TEXT,
    cash REAL,
    bid REAL,
    daily_promo BOOL
)""")
bd.commit()

bot = telebot.TeleBot("5242417371:AAFNa0bLKBgc4repVmCZxUA0IahQlWSR7aU", parse_mode=None)

@bot.message_handler(commands=['start'])
def print_hi(message):
    bot.send_message(message.from_user.id, f'Здравствуйте, {message.from_user.first_name}!\nНапишите /help, чтобы посмотреть список возможных комманд')

@bot.message_handler(commands=['help'])
def print_help(message):
    bot.send_message(message.from_user.id, f'Список команд:\n/start - Запустить бота\n/reg - Зарегистрироваться\n/play - Начать игру\n/cash - Проверить баланс\n/promo - Ввести промокод\n\nУдачи🍀🍀🍀')

@bot.message_handler(commands=['reg'])
def register(message):
    sql.execute(f"SELECT login FROM user WHERE login = '{message.from_user.id}'")
    if sql.fetchone() is None:
        sql.execute(f"INSERT INTO user VALUES (?,?,?,?,?)", (message.from_user.username, message.from_user.id, 100, 0, True))
        bd.commit()
        bot.send_message(message.from_user.id, f'Вы успешно зарегистрировались\nВы получили 100$ за регистрацию\nВведите /play для начала игры')
    else:
        sql.execute(f"UPDATE user SET username='{message.from_user.username}' WHERE login = '{message.from_user.id}'")
        bd.commit()
        bot.send_message(message.from_user.id, f'Ваш аккаунт уже был зарегистрирован ранее.\nВаши данные обновлены!\nВведите /play для начала игры')

@bot.message_handler(commands=['money'])
def deposit_money(message):
    sql.execute(f"UPDATE user SET cash=cash+100 WHERE login = '{message.from_user.id}'")
    bd.commit()
    bot.send_message(message.from_user.id, 'Вам добавленно 100$')

@bot.message_handler(commands=['cash'])
def check_cash(message):
    if sql.execute(f"SELECT login FROM user WHERE login = '{message.from_user.id}'").fetchone() is not None:
        cash = sql.execute(f"SELECT cash FROM user WHERE login = '{message.from_user.id}'").fetchone()[0]
        bot.send_message(message.from_user.id, f'Ваш капитал составляет {cash}$')
    else: bot.send_message(message.from_user.id, 'Вы не зерегистрированы.\nВведите /reg для регистрации.')

@bot.message_handler(commands=['promo'])
def enter_promo(message):
    if sql.execute(f"SELECT login FROM user WHERE login = '{message.from_user.id}'").fetchone() is not None:
        if sql.execute(f"SELECT daily_promo FROM user WHERE login = '{message.from_user.id}'").fetchone()[0] == True:
            bot.send_message(message.from_user.id, 'Введите промокод')
            bot.register_next_step_handler(message, check_promo)
        else: bot.send_message(message.from_user.id, 'Вы уже ввели ежедневный промокод.\nПовторите попытку завтра')
    else: bot.send_message(message.from_user.id, 'Вы не зерегистрированы.\nВведите /reg для регистрации.')

def check_promo(message):
    print('[+]')
    promo = str(message.text)
    if promo == cur.execute(f"SELECT promo FROM promo WHERE id = 1").fetchone()[0]:
        value = cur.execute(f"SELECT value FROM promo WHERE promo = '{promo}'").fetchone()[0]
        sql.execute(f"UPDATE user SET cash=cash+{value} WHERE login = '{message.from_user.id}'")
        sql.execute(f"UPDATE user SET daily_promo={False} WHERE login = '{message.from_user.id}'")
        bd.commit()
        bot.send_message(message.from_user.id, f'На ваш счёт добавлено {value}$!\nПриятной игры')


@bot.message_handler(commands=['play'])
def play_motd(message):
    if sql.execute(f"SELECT login FROM user WHERE login = '{message.from_user.id}'").fetchone() is not None:
        keyword = types.InlineKeyboardMarkup()
        keyword_headsortails = types.InlineKeyboardButton(text='Рулетка', callback_data='roulette')
        keyword.add(keyword_headsortails)
        bot.send_message(message.from_user.id, text='Выберите игру:', reply_markup=keyword)
    else: bot.send_message(message.from_user.id, 'Вы не зерегистрированы.\nВведите /reg для регистрации.')

@bot.callback_query_handler(func=lambda call: call.data == 'roulette')
def roulette(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, 'Вы выбрали игру "Рулетка"\nПри выигрыше вы зарабатываете вложенную сумму, а при проигрыше теряете всю ставку')
    bot.send_message(call.message.chat.id, 'Введите ставку')
    bot.register_next_step_handler(call.message, roulette2)

def roulette2(message):
    bid = float(message.text)
    sql.execute(f"UPDATE user SET bid={bid} WHERE login = '{message.from_user.id}'")
    if bid <= sql.execute(f"SELECT cash FROM user WHERE login = '{message.from_user.id}'").fetchone()[0]:
        keyword = types.InlineKeyboardMarkup()

        keyword_low = types.InlineKeyboardButton(text='Малые', callback_data='low')
        keyword_high = types.InlineKeyboardButton(text='Большие', callback_data='high')
        keyword.add(keyword_low, keyword_high)

        keyword_read = types.InlineKeyboardButton(text='Красное', callback_data='red')
        keyword_black = types.InlineKeyboardButton(text='Чёрное', callback_data='black')
        keyword.add(keyword_read, keyword_black)

        keyword_even = types.InlineKeyboardButton(text='Чётное', callback_data='even')
        keyword_odd = types.InlineKeyboardButton(text='Нечётное', callback_data='odd')
        keyword.add(keyword_even, keyword_odd)

        keyword_dozen1 = types.InlineKeyboardButton(text='1я Дюжина', callback_data='dozen1')
        keyword_dozen2 = types.InlineKeyboardButton(text='2я Дюжина', callback_data='dozen2')
        keyword_dozen3 = types.InlineKeyboardButton(text='3я Дюжина', callback_data='dozen3')
        keyword.add(keyword_dozen1, keyword_dozen2, keyword_dozen3)

        keyword_column1 = types.InlineKeyboardButton(text='1я Колонна', callback_data='column1')
        keyword_column2 = types.InlineKeyboardButton(text='2я Колонна', callback_data='column2')
        keyword_column3 = types.InlineKeyboardButton(text='3я Колонна', callback_data='column3')
        keyword.add(keyword_column1, keyword_column2, keyword_column3)

        keyword_snake = types.InlineKeyboardButton(text='Змеиная ставка', callback_data='snake')
        keyword.add(keyword_snake)

        img = open('roulette_frz.png', 'rb')
        bot.send_photo(message.from_user.id, photo=img, caption='Выберите вариант ставки', reply_markup=keyword)

    else: bot.send_message(message.from_user.id, 'У вас недостаточно средств')

@bot.callback_query_handler(func=lambda call: True)
def heads_or_tails_head(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    keyword = types.InlineKeyboardMarkup()
    keyword_headsortails = types.InlineKeyboardButton(text='Играть ещё раз', callback_data='roulette')
    keyword.add(keyword_headsortails)
    bid = sql.execute(f"SELECT bid FROM user WHERE login = '{call.from_user.id}'").fetchone()[0]
    result = random.randint(0, 36)
    bot.send_message(call.message.chat.id, 'Ставки сделаны, ставок больше нет!\nВращаем рулетку...')
    time.sleep(3)
    bot.send_message(call.message.chat.id, f'Шарик остановился на числе {result}!')

    if call.data == 'low':
        if result <=18 and result > 0:
            bot.send_message(call.message.chat.id, text='Вы выиграли!', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash+{bid} WHERE login = '{call.from_user.id}'")
        else:
            bot.send_message(call.message.chat.id, text='Вы проиграли :(', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash-{bid} WHERE login = '{call.from_user.id}'")
        sql.execute(f"UPDATE user SET bid=0 WHERE login = '{call.from_user.id}'")
        bd.commit()

    elif call.data == 'high':
        if result >18 and result <= 36:
            bot.send_message(call.message.chat.id, text='Вы выиграли!', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash+{bid} WHERE login = '{call.from_user.id}'")
        else:
            bot.send_message(call.message.chat.id, text='Вы проиграли :(', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash-{bid} WHERE login = '{call.from_user.id}'")

    elif call.data == 'red':
        if result == 1 or result == 3 or result == 5 or result == 7 or result == 9 or result == 12 or result == 14 or result == 16 or result == 18 or result == 19 or result == 21 or result == 23 or result == 25 or result == 27 or result == 30 or result == 32 or result == 34 or result == 36:
            bot.send_message(call.message.chat.id, text='Вы выиграли!', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash+{bid} WHERE login = '{call.from_user.id}'")
        else:
            bot.send_message(call.message.chat.id, text='Вы проиграли :(', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash-{bid} WHERE login = '{call.from_user.id}'")

    elif call.data == 'black':
        if result == 2 or result == 4 or result == 6 or result == 8 or result == 10 or result == 11 or result == 13 or result == 15 or result == 17 or result == 20 or result == 22 or result == 24 or result == 26 or result == 28 or result == 29 or result == 31 or result == 33 or result == 35:
            bot.send_message(call.message.chat.id, text='Вы выиграли!', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash+{bid} WHERE login = '{call.from_user.id}'")
        else:
            bot.send_message(call.message.chat.id, text='Вы проиграли :(', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash-{bid} WHERE login = '{call.from_user.id}'")

    elif call.data == 'even':
        if result % 2 == 0:
            bot.send_message(call.message.chat.id, text='Вы выиграли!', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash+{bid} WHERE login = '{call.from_user.id}'")
        else:
            bot.send_message(call.message.chat.id, text='Вы проиграли :(', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash-{bid} WHERE login = '{call.from_user.id}'")

    elif call.data == 'odd':
        if result % 2 != 0:
            bot.send_message(call.message.chat.id, text='Вы выиграли!', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash+{bid} WHERE login = '{call.from_user.id}'")
        else:
            bot.send_message(call.message.chat.id, text='Вы проиграли :(', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash-{bid} WHERE login = '{call.from_user.id}'")

    elif call.data == 'dozen1':
        if result >= 1 and result <= 12:
            bot.send_message(call.message.chat.id, text='Вы выиграли!', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash+{bid} WHERE login = '{call.from_user.id}'")
        else:
            bot.send_message(call.message.chat.id, text='Вы проиграли :(', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash-{bid} WHERE login = '{call.from_user.id}'")

    elif call.data == 'dozen2':
        if result >= 13 and result <= 24:
            bot.send_message(call.message.chat.id, text='Вы выиграли!', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash+{bid} WHERE login = '{call.from_user.id}'")
        else:
            bot.send_message(call.message.chat.id, text='Вы проиграли :(', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash-{bid} WHERE login = '{call.from_user.id}'")

    elif call.data == 'dozen3':
        if result >= 25 and result <= 36:
            bot.send_message(call.message.chat.id, text='Вы выиграли!', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash+{bid} WHERE login = '{call.from_user.id}'")
        else:
            bot.send_message(call.message.chat.id, text='Вы проиграли :(', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash-{bid} WHERE login = '{call.from_user.id}'")

    elif call.data == 'column1':
        if result == 1 or result == 4 or result == 7 or result == 10 or result == 13 or result == 16 or result == 19 or result == 22 or result == 25 or result == 28 or result == 31 or result == 34:
            bot.send_message(call.message.chat.id, text='Вы выиграли!', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash+{bid} WHERE login = '{call.from_user.id}'")
        else:
            bot.send_message(call.message.chat.id, text='Вы проиграли :(', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash-{bid} WHERE login = '{call.from_user.id}'")

    elif call.data == 'column2':
        if result == 2 or result == 5 or result == 8 or result == 11 or result == 14 or result == 17 or result == 20 or result == 23 or result == 26 or result == 29 or result == 32 or result == 35:
            bot.send_message(call.message.chat.id, text='Вы выиграли!', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash+{bid} WHERE login = '{call.from_user.id}'")
        else:
            bot.send_message(call.message.chat.id, text='Вы проиграли :(', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash-{bid} WHERE login = '{call.from_user.id}'")

    elif call.data == 'column3':
        if result == 3 or result == 6 or result == 9 or result == 12 or result == 15 or result == 18 or result == 21 or result == 24 or result == 27 or result == 30 or result == 33 or result == 36:
            bot.send_message(call.message.chat.id, text='Вы выиграли!', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash+{bid} WHERE login = '{call.from_user.id}'")
        else:
            bot.send_message(call.message.chat.id, text='Вы проиграли :(', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash-{bid} WHERE login = '{call.from_user.id}'")

    elif call.data == 'snake':
        if result == 1 or result == 5 or result == 9 or result == 12 or result == 14 or result == 16 or result == 19 or result == 23 or result == 27 or result == 30 or result == 32 or result == 34:
            bot.send_message(call.message.chat.id, text='Вы выиграли!', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash+{bid} WHERE login = '{call.from_user.id}'")
        else:
            bot.send_message(call.message.chat.id, text='Вы проиграли :(', reply_markup=keyword)
            sql.execute(f"UPDATE user SET cash=cash-{bid} WHERE login = '{call.from_user.id}'")

    else: bot.send_message(call.message.chat.id, f'Уважаемый пользователь, вариант ответа \"{call.data}\" не имеет должного продолжения.\nВозможно, данная функция находится в разработке.\nЕсли вы считаете, что произошла ошибка - обратитесь к администрации.\n\nБлагодарим за понимание!')

    sql.execute(f"UPDATE user SET bid=0 WHERE login = '{call.from_user.id}'")
    bd.commit()

# def notify_promo():
#     rough_promo = cur.execute(f"SELECT * FROM promo WHERE id = 1").fetchone()
#     announcement = f'Промокод дня!/nВведите промокод `{rough_promo[1]}` используя команду /promo и получите **{rough_promo[2]}$** на свой счёт'
#     bot.send_message(-1001766749889, announcement)

def main():
    bot.infinity_polling()

if __name__ == "__main__":
    main()