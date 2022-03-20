import random
import sqlite3
import time
import random
import telebot

bd = sqlite3.connect('user.db', check_same_thread=False)
sql = bd.cursor()

conn = sqlite3.connect('promo.db', check_same_thread=False)
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS promo(
    id INT,
    promo TEXT,
    value INT
)""")
conn.commit()

bot = telebot.TeleBot("5242417371:AAFNa0bLKBgc4repVmCZxUA0IahQlWSR7aU", parse_mode=None)

def announcement_promo():
    rough_promo = cur.execute(f"SELECT * FROM promo WHERE id = 1").fetchone()
    announcement = f'Промокод дня!\nВведите промокод {rough_promo[1]} и получите {rough_promo[2]}$ на свой игровой счёт'
    bot.send_message(-1001766749889, announcement)

def promo():
    while True:
        current_time = f'{time.gmtime()[3]}:{time.gmtime()[4]}'
        if current_time == '10:0':
            sql.execute(f"UPDATE user SET daily_promo={False}")
            bd.commit()
            promocode = ''
            for i in range(5):
                promocode = promocode + random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'))
            promo_value = random.randint(75, 200)

            cur.execute(f"DELETE FROM promo WHERE id = 1")
            cur.execute(f"INSERT INTO promo VALUES (?,?,?)", (1, promocode, promo_value))
            conn.commit()

            sql.execute(f"UPDATE user SET daily_promo={True}")
            bd.commit()

            announcement_promo()
            time.sleep(100)
        else: time.sleep(30)

if __name__ == "__main__":
    promo()