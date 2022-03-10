import telebot
from telebot import types
import sqlite3

import main
print('Start')
bot = telebot.TeleBot("5129327876:AAEqHGv5mrFEYmU1edRbqKp93im6LCF0HF0")
db = sqlite3.connect('main.db', check_same_thread=False)
sql = db.cursor()


sql.execute("""CREATE TABLE IF NOT EXISTS main (
    id INT PRIMARY KEY,
    name TEXT,
    type TEXT,
    size TEXT,
    price_for_all INT,
    price_for_trainers INT,
    number_in_storage INT
)""")

db.commit()


a = 0
now_index = 0
admin_flag = False
trainer_flag = False

with db:
    sql.execute("SELECT * FROM main")
    rows = sql.fetchall()


# Функция, обрабатывающая команду /start
@bot.message_handler(commands=['start', '752102', 'trainer'])
def commands(message):
    global admin_flag, trainer_flag
    admin_flag, trainer_flag = False, False

    if message.text == '/trainer':
        bot.send_message(message.chat.id, 'Приветствую вас в панели тренера!')

        global trainer_keyboard
        trainer_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        show_button = 'Показать склад'
        search_button = 'Поиск по cкладу'
        trainer_keyboard.add(show_button, search_button)
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                         reply_markup=trainer_keyboard)
        trainer_flag = True

    elif message.text == '/start':
        bot.send_message(message.from_user.id, 'Привет!')

        global user_keyboard
        user_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        show_button = 'Показать склад'
        search_button = 'Поиск по cкладу'
        user_keyboard.add(show_button, search_button)
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                         reply_markup=user_keyboard)

    elif message.text == '/752102':
        bot.send_message(message.chat.id, 'Приветствую вас в панели администратора!')
        admin_flag = True

        global main_keyboard
        main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = 'Добавить'
        button2 = 'Изменить'
        button3 = 'Показать склад'
        button4 = 'Удалить'
        search_button = 'Поиск по cкладу'
        main_keyboard.add(button1, button2, button3, button4, search_button)
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                         reply_markup=main_keyboard)


@bot.message_handler(content_types=['text'])
def buttons_handler(message):
    global back_keyboard
    back_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = 'Назад'
    button_clear = 'Очистить все'


    if message.text == 'Добавить' and admin_flag:
        back_keyboard.add(button_back)
        bot.send_message(message.chat.id,
                         'Введите название товара:',
                         reply_markup=back_keyboard)

        bot.register_next_step_handler(message, add_name)

    elif message.text == 'Удалить' and admin_flag:
        back_keyboard.add(button_back, button_clear, 'Удалить товар')
        bot.send_message(message.chat.id, 'Нажмите "Очистить все", если хотите удалить все со склада. Нажмите "Удалить товар", если хотите удалить 1 товар со склада.',
                         reply_markup=back_keyboard)

        bot.register_next_step_handler(message, clear_storage)

    elif message.text == 'Показать склад':
        with db:
            sql.execute("SELECT * FROM main")
            rows = sql.fetchall()

            if len(rows) == 0:
                bot.send_message(message.chat.id, 'Склад пустой')
            elif admin_flag or trainer_flag:
                ans = '---------------'
                for i in range (len(rows)):
                    ans += f'\n{i+1}) {rows[i][1]}\n Размер: {rows[i][3]}\n Тип: {rows[i][2]}\n Количество: {rows[i][6]}\n Цена для всех: {rows[i][4]}\n Цена для тренеров: {rows[i][5]}\n'
                    ans += '---------------'
                bot.send_message(message.chat.id, ans)

            else:
                ans = '---------------'

                for i in range(len(rows)):
                    ans += f'\n{i + 1}) {rows[i][1]}\n Размер: {rows[i][3]}\n Тип: {rows[i][2]}\n Количество: {rows[i][6]}\n Цена: {rows[i][4]}\n'
                    ans += '---------------'
                bot.send_message(message.chat.id, ans)


    elif message.text == 'Изменить' and admin_flag:
        with db:
            sql.execute("SELECT * FROM main")
            rows = sql.fetchall()

        if len(rows) != 0:

            global edit_keyboard
            edit_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_copy = 'Копировать товар'
            button_edit = 'Изменить'
            edit_keyboard.add(button_copy, button_edit, button_back)
            bot.send_message(message.chat.id, 'Выберите, интересующий вас вопрос',
                                 reply_markup=edit_keyboard)
            bot.register_next_step_handler(message, edit_storage)

        else:
            bot.send_message(message.chat.id, 'Склад пуст')

    elif message.text == 'Поиск по cкладу':
        with db:
            sql.execute("SELECT * FROM main")
            rows = sql.fetchall()

        if len(rows) == 0:
            bot.send_message(message.chat.id, 'Склад пустой')
        else:
            button1 = 'Назад'
            back_keyboard.add(button1)
            bot.send_message(message.chat.id, 'Введите название или тип товара: ',
                             reply_markup=back_keyboard)

            bot.register_next_step_handler(message, search_on_storage)



def search_on_storage(message):

    if message.text == 'Назад':
        if admin_flag:
            bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                             reply_markup=main_keyboard)
        else:
            bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                             reply_markup=user_keyboard)

    else:
        ans = '---------------'
        search_querry = str(message.text).lower()
        j = 1
        with db:
            sql.execute("SELECT * FROM main")
            rows = sql.fetchall()

        if trainer_flag or admin_flag:
            for i in range (len(rows)):
                if search_querry == str(rows[i][1]) or search_querry == str(rows[i][2]):
                    ans += f'\n{j}) {rows[i][1]}\n Размер: {rows[i][3]}\n Тип: {rows[i][2]}\n Количество: {rows[i][6]}\n Цена для всех: {rows[i][4]}\n Цена для тренеров: {rows[i][5]}\n'
                    ans += '---------------'
                    j += 1


        elif trainer_flag == False:
            with db:
                sql.execute("SELECT * FROM main")
                rows = sql.fetchall()

            for i in range(len(rows)):
                if search_querry == str(rows[i][1]) or search_querry == str(rows[i][2]):
                    ans += f'\n{j}) {rows[i][1]}\n Размер: {rows[i][3]}\n Тип: {rows[i][2]}\n Количество: {rows[i][6]}\n Цена: {rows[i][4]}\n'
                    ans += '---------------'
                    j += 1


        if ans == '---------------':
            bot.send_message(message.chat.id, 'Товара с таким названием или типом не найдено')
            if admin_flag:
                bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                                 reply_markup=main_keyboard)
            else:
                bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                                 reply_markup=user_keyboard)

        else:
            bot.send_message(message.chat.id, ans)
            if admin_flag:
                bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                                 reply_markup=main_keyboard)
            else:
                bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                                 reply_markup=user_keyboard)




def add_name(message):
    if message.text != 'Назад':
        global name_add
        name_add = message.text
        #sql.execute(f"INSERT INTO main (name) VALUES ('{name_add}')")
        #db.commit()

        bot.send_message(message.chat.id, f'Введите размер для {name_add}:')
        bot.register_next_step_handler(message, add_size)


    else:
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                         reply_markup=main_keyboard)

def add_size(message):
    global a

    if message.text != 'Назад':
        global size_add
        size_add = message.text

        #sql.execute(f"INSERT INTO main (size) VALUES ('{message.text}')")
        #db.commit()

        bot.send_message(message.chat.id, f'Введите тип {name_add}:')
        bot.register_next_step_handler(message, add_type)

    else:
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                         reply_markup=main_keyboard)


def add_type(message):
    global a

    if message.text != 'Назад':
        global type_add
        type_add = message.text

        #sql.execute(f"INSERT INTO main (type) VALUES ('{message.text}')")
        #db.commit()

        bot.send_message(message.chat.id, f'Введите количество {name_add}:')
        bot.register_next_step_handler(message, add_number_in_storage)

    else:
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                         reply_markup=main_keyboard)

def add_number_in_storage(message):
    global a

    if message.text != 'Назад':
        global number_add
        number_add = message.text

        #sql.execute(f"INSERT INTO main (number_in_storage) VALUES ('{message.text}')")
        #db.commit()

        bot.send_message(message.chat.id, f'Введите цену {name_add}, которая будет видна всем:')
        bot.register_next_step_handler(message, add_price_for_all)

    else:
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                         reply_markup=main_keyboard)


def add_price_for_all(message):
    global a

    if message.text != 'Назад':
        global price_for_all_add
        price_for_all_add = message.text

        #sql.execute(f"INSERT INTO main (price_for_all) VALUES ('{message.text}')")
        #db.commit()

        bot.send_message(message.chat.id, f'Введите цену {name_add}, которая будет видна тренерам:')
        bot.register_next_step_handler(message, add_price_for_trainers)

    else:
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                         reply_markup=main_keyboard)

def add_price_for_trainers(message):
    global a

    if message.text != 'Назад':
        global price_for_trainers_add
        price_for_trainers_add = message.text

        sql.execute(f"INSERT INTO main (name, size, type, number_in_storage, price_for_all, price_for_trainers) VALUES ('{name_add}', '{size_add}', '{type_add}', '{number_add}', '{price_for_all_add}', '{price_for_trainers_add}')")
        db.commit()

        bot.send_message(message.chat.id, f'{name_add} успешно добален на склад')
        a += 1
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                         reply_markup=main_keyboard)
    else:
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                         reply_markup=main_keyboard)



def clear_storage(message):
    if message.text == 'Очистить все':
        sql.execute("DELETE FROM main WHERE id > 0")
        db.commit()

        bot.send_message(message.chat.id, 'Склад успешно очищен', reply_markup=main_keyboard)
    elif message.text == 'Удалить товар':

        with db:
            sql.execute("SELECT * FROM main")
            rows = sql.fetchall()

            if len(rows) == 0:
                bot.send_message(message.chat.id, 'Склад пустой')
            else:
                back_keyboard2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back_keyboard2.add('Назад')
                bot.send_message(message.chat.id, 'Выберите номер товара, данные о котором вы хотите удалить', reply_markup=back_keyboard2)
                bot.register_next_step_handler(message, delete_data)


    elif message.text == 'Назад':
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                         reply_markup=main_keyboard)
    else:
        bot.register_next_step_handler(message, clear_storage)


def delete_data(message):
     if message.text != 'Назад':
        with db:
            sql.execute("SELECT * FROM main")
            rows = sql.fetchall()

        if len(rows) == 0:
            bot.send_message(message.chat.id, 'Склад пуст')
        else:
            try:
                delete_index = int(message.text) - 1
                sql.execute(f"DELETE FROM main WHERE name = '{rows[delete_index][1]}' AND size = '{rows[delete_index][3]}' AND  type = '{rows[delete_index][2]}' AND  number_in_storage = '{rows[delete_index][6]}' AND price_for_all = '{rows[delete_index][4]}' AND  price_for_trainers = '{rows[delete_index][5]}'")
                bot.send_message(message.chat.id, f'Данные о товаре {rows[delete_index][1]} успешно удалены', reply_markup=main_keyboard)
                db.commit()
            except:
                bot.send_message(message.chat.id, f'Товара с номером {message.text} нет на складе', reply_markup=main_keyboard)
     else:
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре', reply_markup=main_keyboard)


def edit_storage(message):
    global edit_type
    edit_type = message.text
    if message.text == 'Изменить':
        back_keyboard.add('Назад')
        bot.send_message(message.chat.id, 'Выберите номер товара, данные о котором вы хотите редактировать', reply_markup=back_keyboard)
        bot.register_next_step_handler(message, find_index)

    elif message.text == 'Копировать товар':
        back_keyboard.add('Назад')
        bot.send_message(message.chat.id, 'Выберите номер товара, данные котрого вы хотите скопировать',
                         reply_markup=back_keyboard)
        bot.register_next_step_handler(message, find_index)

    elif message.text == 'Назад':
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                         reply_markup=main_keyboard)
    else:
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре')
        bot.register_next_step_handler(message, edit_storage)


def find_index(message):
    if message.text != "Назад":
        if edit_type == 'Изменить':
            try:
                global edit_index
                edit_index = int(message.text) - 1

                edit_keyboard2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button_column1 = 'Название'
                button_column2 = 'Размер'
                button_column3 = 'Тип'
                button_column4 = 'Количество'
                button_column5 = 'Цена для всех'
                button_column6 = 'Цена для тренеров'
                back_button = 'Назад'
                edit_keyboard2.add(button_column1, button_column2, button_column3, button_column4, button_column5,
                                   button_column6, back_button)

                bot.send_message(message.chat.id, 'Выберите столбец, данные в котором вы хотите редактировать',
                                 reply_markup=edit_keyboard2)
                print(message.text, edit_index)
                bot.register_next_step_handler(message, input_column)

            except:
                bot.send_message(message.chat.id, f'Товара с таким номером нет на складе', reply_markup=main_keyboard)

        elif edit_type == 'Копировать товар':
            try:
                with db:
                    sql.execute("SELECT * FROM main")
                    rows = sql.fetchall()

                now_index = int(message.text) - 1

                sql.execute(f"INSERT INTO main (name, type, size, price_for_all, price_for_trainers, number_in_storage) VALUES ('{rows[now_index][1]}', '{rows[now_index][2]}', '{rows[now_index][3]}', '{rows[now_index][4]}', '{rows[now_index][5]}', '{rows[now_index][6]}')")

                bot.send_message(message.chat.id, f'Данные товара успешно скопированы',
                                 reply_markup=main_keyboard)
                db.commit()

            except:
                bot.send_message(message.chat.id, f'Товара с таким номером нет на складе', reply_markup=main_keyboard)


    else:
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                         reply_markup=main_keyboard)

def input_column(message):
    if message.text != 'Назад':
        global num_of_column
        num_of_column = message.text
        bot.send_message(message.chat.id, 'Введите новое значение: ', reply_markup=back_keyboard)
        bot.register_next_step_handler(message, edit_info_storage)
    else:
        bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                     reply_markup=main_keyboard)

def edit_info_storage(message):
    with db:
        sql.execute("SELECT * FROM main")
        rows = sql.fetchall()

    if message.text != 'Назад':
        if num_of_column == 'Название':
            sql.execute(f"UPDATE main SET name = '{message.text}' WHERE name = '{rows[edit_index][1]}' AND size = '{rows[edit_index][3]}' AND  type = '{rows[edit_index][2]}' AND  number_in_storage = '{rows[edit_index][6]}' AND price_for_all = '{rows[edit_index][4]}' AND  price_for_trainers = '{rows[edit_index][5]}'")

        elif num_of_column == 'Размер':
            sql.execute(f"UPDATE main SET size = '{message.text}' WHERE name = '{rows[edit_index][1]}' AND size = '{rows[edit_index][3]}' AND  type = '{rows[edit_index][2]}' AND  number_in_storage = '{rows[edit_index][6]}' AND price_for_all = '{rows[edit_index][4]}' AND  price_for_trainers = '{rows[edit_index][5]}'")

        elif num_of_column == 'Тип':
            sql.execute(f"UPDATE main SET type = '{message.text}' WHERE name = '{rows[edit_index][1]}' AND size = '{rows[edit_index][3]}' AND  type = '{rows[edit_index][2]}' AND  number_in_storage = '{rows[edit_index][6]}' AND price_for_all = '{rows[edit_index][4]}' AND  price_for_trainers = '{rows[edit_index][5]}'")

        elif num_of_column == 'Количество':
            sql.execute(f"UPDATE main SET number_in_storage = '{message.text}' WHERE name = '{rows[edit_index][1]}' AND size = '{rows[edit_index][3]}' AND  type = '{rows[edit_index][2]}' AND  number_in_storage = '{rows[edit_index][6]}' AND price_for_all = '{rows[edit_index][4]}' AND  price_for_trainers = '{rows[edit_index][5]}'")

        elif num_of_column == 'Цена для всех':
            sql.execute(f"UPDATE main SET price_for_all = '{message.text}' WHERE name = '{rows[edit_index][1]}' AND size = '{rows[edit_index][3]}' AND  type = '{rows[edit_index][2]}' AND  number_in_storage = '{rows[edit_index][6]}' AND price_for_all = '{rows[edit_index][4]}' AND  price_for_trainers = '{rows[edit_index][5]}'")

        elif num_of_column == 'Цена для тренеров':
            sql.execute(f"UPDATE main SET price_for_trainers = '{message.text}' WHERE name = '{rows[edit_index][1]}' AND size = '{rows[edit_index][3]}' AND  type = '{rows[edit_index][2]}' AND  number_in_storage = '{rows[edit_index][6]}' AND price_for_all = '{rows[edit_index][4]}' AND  price_for_trainers = '{rows[edit_index][5]}'")

        db.commit()

        bot.send_message(message.chat.id, f'{num_of_column} успешно изменен на {message.text}')

    bot.send_message(message.chat.id, 'Выберите интересующий ваc вопрос на появившейся ниже клавиатуре',
                     reply_markup=main_keyboard)


bot.polling(none_stop=True, interval=0)
