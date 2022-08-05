import telebot
import datetime
import sql_base as sql
import diagram as dia
import time
from telebot import types
import re

bot = telebot.TeleBot('5389340325:AAGB0Ddka7EbAB13iU1PWQgZjhupKF7dO4M')


# Период статистики
def stat_tipe(tipstat: str):
    tekdat = datetime.date.today()
    tekmoun = tekdat.month
    d1 = 0
    d2 = 0
    textdat = ''
    if tipstat == '1':
        d1 = datetime.date(2022, int(tekmoun - 1), 1)
        d2 = datetime.date(2022, int(tekmoun), 1)
        textdat = 'прошлый месяц'
    elif tipstat == '2':
        d1 = datetime.date(2022, int(tekmoun), 1)
        d2 = datetime.date(2022, int(tekmoun + 1), 1)
        textdat = 'текущий месяц'
    elif tipstat == '3':
        tek1 = tekdat - datetime.timedelta(days=7 + tekdat.weekday())
        tek2 = tekdat - datetime.timedelta(days=tekdat.weekday())
        d1 = datetime.date(2022, tek1.month, tek1.day)
        d2 = datetime.date(2022, tek2.month, tek2.day)
        textdat = 'прошлую неделю'
    elif tipstat == '4':
        tek1 = tekdat - datetime.timedelta(days=tekdat.weekday())
        tek2 = tekdat + datetime.timedelta(days=7 - tekdat.weekday())
        d1 = datetime.date(2022, tek1.month, tek1.day)
        d2 = datetime.date(2022, tek2.month, tek2.day)
        textdat = 'текущую неделю'
    return d1, d2, textdat


# Тестовый пользователь
def test_user(userid: int):
    if userid == 90205749:
        userid = 12345  # 12345   185983928
    else:
        pass
    return userid


# Очистка от эмоджи
def del_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001F9FE"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


# Нажали старт (Основное окно)
@bot.message_handler(commands=['start'])
def start_message(message):
    firstname = message.from_user.first_name
    userid = test_user(message.from_user.id)
    lastname = message.from_user.last_name
    login = message.from_user.username
    print(firstname, userid, lastname, login)
    # {'id': 90205749, 'is_bot': False, 'first_name': 'Andrew', 'username': 'ASveshnikoff', 'last_name': None,
    #  'language_code': 'en', 'can_join_groups': None, 'can_read_all_group_messages': None,
    #  'supports_inline_queries': None, 'is_premium': None, 'added_to_attachment_menu': None}
    if sql.facecontrol(userid) == 0:
        sql.sql_insert_users(userid, firstname, lastname, login)

    glavmess = f'Привет, {firstname}! Я @YouMoney25 - твой персональный финансовый бот. Я помогу тебе контролировать ' \
               f'твои расходы! '
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Внести расход', callback_data='rasx'))
    markup.add(types.InlineKeyboardButton(text='Статистика', callback_data='static'))
    markup.add(types.InlineKeyboardButton(text='Настройки', callback_data='option'))
    markup.add(types.InlineKeyboardButton(text='Информация', callback_data='info'))
    bot.send_message(message.chat.id, glavmess, parse_mode='html')
    bot.send_message(message.chat.id, 'Выбери действие:', parse_mode='html', reply_markup=markup)


# Главное меню
@bot.callback_query_handler(func=lambda call: call.data.startswith('mainmenu'))
def mainmenu(call):
    mess = 'Выбери действие:'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Внести расход', callback_data='rasx'))
    markup.add(types.InlineKeyboardButton(text='Статистика', callback_data='static'))
    markup.add(types.InlineKeyboardButton(text='Настройки', callback_data='option'))
    markup.add(types.InlineKeyboardButton(text='Информация', callback_data='info'))
    # markup.add(rasx,stat,option,info)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=mess,
                          parse_mode='html', reply_markup=markup)


# Внести Расход Список категорий
@bot.callback_query_handler(func=lambda call: call.data.startswith('rasx'))
def input_rash(call):
    userid = test_user(call.message.chat.id)
    mess = 'Выбери категорию:'
    cat = sql.sql_takecat_list(userid=userid)
    markup = types.InlineKeyboardMarkup()
    if not cat:
        mess = '😔Категории отсутствуют!\n' \
               'Для того чтобы внести расход нужно всего 3 шага:\n' \
               '1. Добавить категорию\n' \
               '2. Добавить подкатегорию\n' \
               '3. Внести сумму расхода'
        markup.add(types.InlineKeyboardButton(text='➕ Добавить категорию', callback_data='newc'))
    else:
        for row in cat:
            markup.add(types.InlineKeyboardButton(text=row[1], callback_data=f'cat__{row[0]}__{row[1]}'))
    back = types.InlineKeyboardButton(text='🔝 Главное меню', callback_data='mainmenu')
    markup.add(back)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=mess,
                          parse_mode='html', reply_markup=markup)


# Статистика
@bot.callback_query_handler(func=lambda call: call.data.startswith('static'))
def statistika(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=f'Прошлый месяц', callback_data=f'stat__1'))
    markup.add(types.InlineKeyboardButton(text=f'Текущий месяц', callback_data=f'stat__2'))
    markup.add(types.InlineKeyboardButton(text=f'Прошлая неделя', callback_data=f'stat__3'))
    markup.add(types.InlineKeyboardButton(text=f'Текущая неделя', callback_data=f'stat__4'))
    markup.add(types.InlineKeyboardButton(text='🔝 Главное меню', callback_data=f'mainmenu'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=f'Выбери период:', parse_mode='html', reply_markup=markup)


# Вывод статистики по категориям
@bot.callback_query_handler(func=lambda call: call.data.startswith('stat__'))
def stat_po_cat(call):
    tipstat = call.data.split("__")
    datestat = stat_tipe(tipstat[1])
    userid = test_user(call.message.chat.id)
    sumcat = sql.sql_takesumcat(userid=userid, d1=str(datestat[0]), d2=str(datestat[1]))
    labels = ()
    sizes = []
    explode = ()
    markup = types.InlineKeyboardMarkup()
    if not sumcat:
        mess = 'Для отображение статистики внесите расход.'
        markup.add(types.InlineKeyboardButton(text='Внести расход', callback_data=f'rasx'))
    else:
        for row in sumcat:
            markup.add(types.InlineKeyboardButton(text=f'{row[1]}: {row[2]} руб',
                                                  callback_data=f'statart__{row[0]}__{row[1]}__{tipstat[1]}'))
            labels += (del_emoji(row[1]),)
            sizes.append(row[2])
            explode += (0.01,)
        mess = f'Сумма расходов за {datestat[2]}: {sum(sizes)} рублей.\nДетализация по категориям:'
        dia.circle_diag(userid, labels, sizes, explode, datestat[2])
        img = open(f'{userid}_png.png', 'rb')
        bot.send_photo(call.message.chat.id, img)
    markup.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data=f'static'))
    bot.send_message(chat_id=call.message.chat.id,
                     text=mess,
                     parse_mode='html', reply_markup=markup)


# Вывод статистики по подкатегориям
@bot.callback_query_handler(func=lambda call: call.data.startswith('statart__'))
def stat_po_art(call):
    catl = call.data.split("__")
    datestat = stat_tipe(catl[3])
    mess = f'Cумма расходов за {datestat[2]} по категории {catl[2]}:'
    userid = test_user(call.message.chat.id)
    art = sql.sql_takesumart_list(userid=userid, cat=catl[1], d1=str(datestat[0]), d2=str(datestat[1]))
    labels = ()
    sizes = []
    explode = ()
    markup = types.InlineKeyboardMarkup()
    for row in art:
        markup.add(types.InlineKeyboardButton(text=f'{row[1]}: {row[2]} руб', callback_data=f'00000000'))
        labels += (row[1],)  # убрать эмоджи
        sizes.append(row[2])
        explode += (0.01,)
    print(labels)
    dia.circle_diag(userid, labels, sizes, explode, datestat[2])
    markup.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data=f'stat__{catl[3]}'))
    img = open(f'{userid}_png.png', 'rb')
    bot.send_photo(call.message.chat.id, img)
    bot.send_message(chat_id=call.message.chat.id, text=mess, parse_mode='html',
                     reply_markup=markup)


# Настройки
@bot.callback_query_handler(func=lambda call: call.data.startswith('option'))
def option(call):
    glavmess = 'Меню настроек:'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Редактировать категории', callback_data='сustomiz'))
    # markup.add(types.InlineKeyboardButton(text='Настройка уведомлений', callback_data='reminder'))
    markup.add(types.InlineKeyboardButton(text='🔝 Главное меню', callback_data='mainmenu'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=glavmess,
                          parse_mode='html', reply_markup=markup)


# Редактировать категории
@bot.callback_query_handler(func=lambda call: call.data.startswith('сustomiz'))
def option(call):
    userid = test_user(call.message.chat.id)
    cat = sql.sql_takecat_list(userid=userid)
    markup = types.InlineKeyboardMarkup()
    mess = f'Редактирование категорий:\n✏ - редактировать\n❌ - удалить'
    for row in cat:
        catbut = types.InlineKeyboardButton(text=row[1], callback_data='0')
        changebut = types.InlineKeyboardButton(text='✏', callback_data=f'сust__changecat__{row[0]}__{row[1]}')
        delbut = types.InlineKeyboardButton(text='❌', callback_data=f'сust__dlcat__{row[0]}__{row[1]}')
        markup.add(catbut, changebut, delbut)
    markup.add(types.InlineKeyboardButton(text='➕ Добавить новую', callback_data='newc'))
    back = types.InlineKeyboardButton(text='🔙 Назад', callback_data='option')
    markup.add(back)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=mess,
                          parse_mode='html', reply_markup=markup)


# Редактирование подкатегорий
@bot.callback_query_handler(func=lambda call: call.data.startswith('сust__changecat__'))
def cust_change(call):
    cangecat = call.data.split("__")
    print(f'All = {cangecat}')
    mess = f'Категория: {cangecat[3]}\nИзменение подкатегорий:\n✏ - переименовать\n❌ - удалить'
    userid = test_user(call.message.chat.id)
    art = sql.sql_takeart_list(userid=userid, cat=cangecat[2])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Переименовать категорию', callback_data=f'renamecat__{cangecat[2]}'))
    for row in art:
        artbut = types.InlineKeyboardButton(text=row[1], callback_data='0')
        changebut = types.InlineKeyboardButton(text='✏',
                                               callback_data=f'сust__renameart__{row[0]}__{row[1]}__{cangecat[2]}__'
                                                             f'{cangecat[3]}')
        delbut = types.InlineKeyboardButton(text='❌',
                                            callback_data=f'сust__delart__{row[0]}__{row[1]}__{cangecat[2]}__'
                                                          f'{cangecat[3]}')
        markup.add(artbut, changebut, delbut)
    markup.add(types.InlineKeyboardButton(text=f'➕ Добавить подкатегорию',
                                          callback_data=f'newart__{cangecat[2]}__{cangecat[3]}'))
    back = types.InlineKeyboardButton(text='🔙 Назад', callback_data='сustomiz')
    markup.add(back)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=mess,
                          parse_mode='html', reply_markup=markup)


# Переименовать подкатегорию  all ['сust', 'renameart', '12', 'Топливо', '2', 'Автомобиль']
@bot.callback_query_handler(func=lambda call: call.data.startswith('сust__renameart__'))
def rename_art(call):
    art = call.data.split("__")
    mess = 'Введите новое название подкатегории:'
    ctn = bot.send_message(call.message.chat.id, mess, parse_mode='html', reply_markup=None)
    bot.register_next_step_handler(ctn, rename_art_sql, art)


def rename_art_sql(message, value):
    art = value
    if message.content_type == 'text':
        nameart = message.text
        sql.sql_rename_art(nameart=nameart, artid=art[2])
        mess = f'Переименовал категорию на {nameart}\nЧто делаем дальше?'
        print(mess)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Редактировать категорию',
                                              callback_data=f'сust__changecat__{art[4]}__{art[5]}'))
        markup.add(types.InlineKeyboardButton(text='🔝 Главное меню', callback_data='mainmenu'))
        bot.send_message(message.from_user.id, mess, reply_markup=markup)
    else:
        datt = bot.send_message(message.chat.id, 'Не понимаю тебя. Напиши новое название подкатегории:')
        bot.register_next_step_handler(datt, rename_art_sql, art)


# Настройки - подтверждение удаления подкатегории
@bot.callback_query_handler(func=lambda call: call.data.startswith('сust__delart__'))
def cust_del_art(call):
    delart = call.data.split("__")
    mess = f'Удалить подкатегорию категорию {delart[3]}?'
    markup = types.InlineKeyboardMarkup()
    da = types.InlineKeyboardButton(text='Да',
                                    callback_data=f'deleteart__{delart[2]}__{delart[3]}__{delart[4]}__{delart[5]}')
    net = types.InlineKeyboardButton(text='Нет', callback_data=f'сust__changecat__{delart[4]}__{delart[5]}')
    markup.add(da, net)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=mess,
                          parse_mode='html', reply_markup=markup)


# Удаление подкатегории
@bot.callback_query_handler(func=lambda call: call.data.startswith('deleteart__'))
def cust_delartsql(call):
    delart = call.data.split("__")
    # userid = test_user(call.message.chat.id)
    sql.sql_delart(art=delart[1])
    mess = f'Подкатегория {delart[2]} удалена!'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Редактировать категорию',
                                          callback_data=f'сust__changecat__{delart[3]}__{delart[4]}'))
    markup.add(types.InlineKeyboardButton(text='🔝 Главное меню', callback_data='mainmenu'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=mess,
                          parse_mode='html', reply_markup=markup)


# Настройки - подтверждение удаления категории
@bot.callback_query_handler(func=lambda call: call.data.startswith('сust__dlcat__'))
def cust_delcat(call):
    delcat = call.data.split("__")
    mess = f'Удалить категорию {delcat[3]}?'
    markup = types.InlineKeyboardMarkup()
    da = types.InlineKeyboardButton(text='Да', callback_data=f'deletecat__{delcat[2]}__{delcat[3]}')
    net = types.InlineKeyboardButton(text='Нет', callback_data=f'сustomiz')
    markup.add(da, net)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=mess,
                          parse_mode='html', reply_markup=markup)


# Удаление категории
@bot.callback_query_handler(func=lambda call: call.data.startswith('deletecat__'))
def cust_delcatsql(call):
    delcat = call.data.split("__")
    userid = test_user(call.message.chat.id)
    sql.sql_delcat(userid=userid, cat=delcat[1])
    mess = f'Категория {delcat[2]} удалена!'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Редактировать категории', callback_data='сustomiz'))
    markup.add(types.InlineKeyboardButton(text='🔝 Главное меню', callback_data='mainmenu'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=mess,
                          parse_mode='html', reply_markup=markup)


# Добавление новой подкатегории
@bot.callback_query_handler(func=lambda call: call.data.startswith('newart__'))
def newart(call):
    nwart = call.data.split("__")
    print(nwart)
    mess = f'Алгоритм тебе знаком!\nНапиши мне название подкатегории, которую необходимо добавить.\n' \
           f'Например:\n' \
           f'🛒 Продукты, 🧾 Ком. платежи и т.д'
    ctn = bot.send_message(call.message.chat.id, mess, parse_mode='html', reply_markup=None)
    bot.register_next_step_handler(ctn, inputart, nwart)


def inputart(message, value):
    nwart = value
    if message.content_type == 'text':
        nameart = message.text
        userid = test_user(message.from_user.id)
        print(nwart[1])
        artid = sql.sql_insert_art(nameart=nameart, namecat=nwart[1], userid=userid)
        mess = f'Добавил подкатегорию: {nameart} в категорию: {nwart[2]}!\n' \
               f'Теперь ты можешь внести расход или добавить еще одну подкатегорию.'
        markup = types.InlineKeyboardMarkup()
        print(f'art__{artid[0]}__{nameart}')
        markup.add(types.InlineKeyboardButton(text='Внести расход', callback_data=f'art__{artid[0]}__{nameart}'))
        markup.add(
            types.InlineKeyboardButton(text='➕ Добавить подкатегорию', callback_data=f'newart__{nwart[1]}__{nwart[2]}'))
        markup.add(types.InlineKeyboardButton(text='🔝 Главное меню', callback_data='mainmenu'))
        bot.send_message(message.from_user.id, mess, reply_markup=markup)
    else:
        datt = bot.send_message(message.chat.id, 'Не понимаю тебя. Напиши новое название категории:')
        bot.register_next_step_handler(datt, inputart, nwart)


# Добавление новой категории
@bot.callback_query_handler(func=lambda call: call.data.startswith('newc'))
def new_cat(call):
    mess = f'Отправь мне название категории, которую необходимо добавить.\n' \
           f'В имени можно использовать эмоджи.\n' \
           f'Например:\n🏠Дом, 🚙Автомобиль и т.д.\n'
    ctn = bot.send_message(call.message.chat.id, mess, parse_mode='html', reply_markup=None)
    bot.register_next_step_handler(ctn, input_cat)


def input_cat(message):
    if message.content_type == 'text':
        namecat = message.text
        userid = test_user(message.from_user.id)
        catid = sql.sql_insert_cat(namecat=namecat, userid=userid)
        print(catid[0], type(catid))
        mess = f'Отлично, категорию {namecat} я добавил!\n' \
               f'Отредактировать её ты всегда сможешь в настройках.\n' \
               f'Теперь давай добавим в неё подкатегории:'
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(text='➕ Добавить подкатегорию', callback_data=f'newart__{catid[0]}__{namecat}'))
        # markup.add(types.InlineKeyboardButton(text='Редактировать категории', callback_data='сustomiz'))
        markup.add(types.InlineKeyboardButton(text='🔝 Главное меню', callback_data='mainmenu'))
        bot.send_message(message.from_user.id, mess, reply_markup=markup)
    else:
        datt = bot.send_message(message.chat.id, 'Не понимаю тебя. Напиши название категории:')
        bot.register_next_step_handler(datt, input_cat)


# Переименовать категорию
@bot.callback_query_handler(func=lambda call: call.data.startswith('renamecat__'))
def rename_cat(call):
    cat = call.data.split("__")
    mess = 'Напиши новое название категории:'
    ctn = bot.send_message(call.message.chat.id, mess, parse_mode='html', reply_markup=None)
    bot.register_next_step_handler(ctn, input_cat, cat)


def rename_cat_sql(message, value):
    cat = value
    if message.content_type == 'text':
        namecat = message.text
        userid = test_user(message.from_user.id)
        sql.sql_rename_cat(namecat=namecat, userid=userid, catid=cat[1])
        mess = f'Переименовал категорию на {namecat}\nЧто делаем дальше?'
        print(mess)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Редактировать категории', callback_data='сustomiz'))
        markup.add(types.InlineKeyboardButton(text='🔝 Главное меню', callback_data='mainmenu'))
        bot.send_message(message.from_user.id, mess, reply_markup=markup)
    else:
        datt = bot.send_message(message.chat.id, 'Не понимаю тебя. Напиши новое название категории:')
        bot.register_next_step_handler(datt, rename_cat_sql, cat)


# Вывод списка подкатегорий
@bot.callback_query_handler(func=lambda call: call.data.startswith('cat'))
def answer(call):
    catl = call.data.split("__")
    print('all= ' + call.data)
    print('obrez= ' + catl[1])
    mess = 'Выбери подкатегорию:'
    userid = test_user(call.message.chat.id)
    art = sql.sql_takeart_list(userid=userid, cat=catl[1])
    markup = types.InlineKeyboardMarkup()
    if not art:
        mess = f'😔Подкатегории отсутствуют!\n' \
               f'Нужно добавить подкатегорию для внесения расхода.'
        markup.add(types.InlineKeyboardButton(text='➕ Добавить подкатегорию',
                                              callback_data=f'newart__{catl[1]}__{catl[2]}'))
    else:
        for row in art:
            markup.add(types.InlineKeyboardButton(text=row[1], callback_data=f'art__{row[0]}__{row[1]}'))
    markup.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data=f'rasx'))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.id, text=mess, parse_mode='html', reply_markup=markup)


# Фиксируем расход
@bot.callback_query_handler(func=lambda call: call.data.startswith('art__'))
def answer(call):
    art = call.data.split("__")
    print('all= ' + call.data)
    mess = f'Напиши сумму затрат в подкатегории {art[2]}:'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    but100 = types.InlineKeyboardButton(text='100')  # Последние введенные суммы по категории
    but200 = types.InlineKeyboardButton(text='200')
    but500 = types.InlineKeyboardButton(text='500')
    markup.add(but100, but200, but500)
    datt = bot.send_message(call.message.chat.id, mess, parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(datt, input_rasx, art)


# Добавление суммы расхода в подкатегорию
def input_rasx(message, value):
    art = value
    userid = test_user(message.from_user.id)
    summ = message.text
    if message.content_type == 'text' and summ.isdigit() and int(summ) > 0:
        now = str(datetime.datetime.now())
        sql.sql_insert_rashod(artid=art[1], userid=userid, summa=summ, datenow=now)
        mess = f'Добавил {summ}руб. на {art[2]}.'
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='🔝 Главное меню', callback_data='mainmenu'))
        bot.send_message(message.from_user.id, mess, reply_markup=markup)
    else:
        datt = bot.send_message(message.chat.id, 'Сумма должен быть целым числом больше 0, повтори ввод:')
        bot.register_next_step_handler(datt, input_rasx, art)


# Запуск \ перезапуск бота
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(3)
            print(str(e))
# bot.polling(none_stop=True)
