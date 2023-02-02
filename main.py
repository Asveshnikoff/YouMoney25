import telebot
import datetime
import time
import sql_base as sql
import diagram as dia
from telebot import types
import re
import constant as const

bot = telebot.TeleBot(const.token)


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
        userid = 90205749  # 12345   185983928
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


# Разбитие списка на равные чести
def generator_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


# Проверка длины списка
def prov_dlin(i, dlin):
    if i < 0:
        i = 0
    elif i > dlin:
        i = dlin
    else:
        i = i
    return i


# Нажали старт (Основное окно)
@bot.message_handler(commands=['start'])
def start_message(message):
    firstname = message.from_user.first_name
    userid = test_user(message.from_user.id)
    lastname = message.from_user.last_name
    login = message.from_user.username
    # bot.answer_callback_query(message.chat.id, "START!!!")
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
    markup.add(types.InlineKeyboardButton(text=f'Все расходы', callback_data=f'AllRash__0'))
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
        mess = f'Данные по расходам за {datestat[2]} отсутствуют.\nДля отображение внесите расход.'
        markup.add(types.InlineKeyboardButton(text='Внести расход', callback_data=f'rasx'))
    else:
        for row in sumcat:
            markup.add(types.InlineKeyboardButton(text=f'{row[1]}: {row[2]} руб',
                                                  callback_data=f'statcat__{row[0]}__{row[1]}__{tipstat[1]}'))
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
@bot.callback_query_handler(func=lambda call: call.data.startswith('statcat__'))
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
        markup.add(types.InlineKeyboardButton(text=f'{row[1]}: {row[2]} руб',
                                              callback_data=f'statart__{row[0]}__{row[1]}__'
                                                            f'{catl[3]}__0__{catl[1]}__{catl[2]}'))
        labels += (row[1],)
        sizes.append(row[2])
        explode += (0.01,)
    print(labels)
    dia.circle_diag(userid, labels, sizes, explode, datestat[2])
    markup.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data=f'stat__{catl[3]}'))
    img = open(f'{userid}_png.png', 'rb')
    bot.send_photo(call.message.chat.id, img)
    bot.send_message(chat_id=call.message.chat.id, text=mess, parse_mode='html',
                     reply_markup=markup)


# Вывод перечня всех расходов
@bot.callback_query_handler(func=lambda call: call.data.startswith('AllRash__'))
def stat_allrash(call):
    rashcall = call.data.split("__")
    userid = test_user(call.message.chat.id)
    allrash = sql.sql_allrash(userid=userid)
    allrash1 = list(generator_list(allrash, 8))
    i = prov_dlin(int(rashcall[1]), len(allrash1) - 1)
    mess = f'Детализация расходов.\n' \
           f'Выбери для редактирования.'
    markup = types.InlineKeyboardMarkup()
    if len(allrash1) != 1:
        butdown = types.InlineKeyboardButton(text=f'<<<',
                                             callback_data=f'AllRash__{i - 1}')
        butup = types.InlineKeyboardButton(text=f'>>>',
                                           callback_data=f'AllRash__{i + 1}')
        markup.add(butdown, butup)
        mess += f'\nСтраница {i + 1} из {len(allrash1)}:'
    for row in allrash1[i]:
        markup.add(types.InlineKeyboardButton(text=f'{row[1]} руб. от {row[2]} {row[4]}/{row[5]}',
                                              callback_data=f'chanoneart__{row[0]}__{row[1]}__{row[2]}'))
    markup.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data=f'static'))
    bot.send_message(chat_id=call.message.chat.id, text=mess, parse_mode='html', reply_markup=markup)


# Вывод детализации по подкатегории одной    ['statart', '1', 'Ипотека', '1', '1']
@bot.callback_query_handler(func=lambda call: call.data.startswith('statart__'))
def stat_po_oneart(call):
    artone = call.data.split("__")
    datestat = stat_tipe(artone[3])
    userid = test_user(call.message.chat.id)
    oneart = sql.sql_takesumoneart_list(userid=userid, artid=artone[1], d1=str(datestat[0]), d2=str(datestat[1]))
    oneart1 = list(generator_list(oneart, 7))
    i = prov_dlin(int(artone[4]), len(oneart1) - 1)
    mess = f'Детализация расходов за {datestat[2]} по подкатегории {artone[2]}.\n' \
           f'Выбери для редактирования.'
    markup = types.InlineKeyboardMarkup()
    if len(oneart1) != 1:
        butdown = types.InlineKeyboardButton(text=f'<<<',
                                             callback_data=f'statart__{artone[1]}__{artone[2]}__{artone[3]}__{i - 1}__'
                                                           f'{artone[5]}__{artone[6]}')
        butup = types.InlineKeyboardButton(text=f'>>>',
                                           callback_data=f'statart__{artone[1]}__{artone[2]}__{artone[3]}__{i + 1}__'
                                                         f'{artone[5]}__{artone[6]}')
        markup.add(butdown, butup)
        mess += f'\nСтраница {i + 1} из {len(oneart1)}:'
    for row in oneart1[i]:
        if row[3] is None:
            komm = ''
        else:
            komm = f'({row[3]})'
        markup.add(types.InlineKeyboardButton(text=f'{row[1]} руб. от {row[2]} {komm}',
                                              callback_data=f'chanoneart__{row[0]}__{row[1]}__{row[2]}'))
    markup.add(
        types.InlineKeyboardButton(text='🔙 Назад',
                                   callback_data=f'statcat__{artone[5]}__{artone[6]}__{artone[3]}'))
    bot.send_message(chat_id=call.message.chat.id, text=mess, parse_mode='html', reply_markup=markup)


# Кнопки редактирование строки расхода
@bot.callback_query_handler(func=lambda call: call.data.startswith('chanoneart__'))
def change_oneart(call):
    oneart = call.data.split("__")
    print(oneart)
    mess = f'Расход на {oneart[2]} руб. от {oneart[3]}\nКомментарий:'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=f'Изменить сумму', callback_data=f'changesumoneart__{oneart[1]}'))
    markup.add(types.InlineKeyboardButton(text=f'Изменить комментарий', callback_data=f'changekommoneart__{oneart[1]}'))
    markup.add(types.InlineKeyboardButton(text=f'Удалить', callback_data=f'deletesumoneart__{oneart[1]}'))
    # markup.add(types.InlineKeyboardButton(text='🔙 Назад', callback_data=f'statart__1__🏠Ипотека__1__1'))
    bot.send_message(chat_id=call.message.chat.id, text=mess, parse_mode='html', reply_markup=markup)
    # нужно исправить назад


# Кнопка удалить выбранный расход
@bot.callback_query_handler(func=lambda call: call.data.startswith('deletesumoneart__'))
def delete_oneart(call):
    oneart = call.data.split("__")
    mess = 'Расход удален!'
    print(oneart)
    userid = test_user(call.message.chat.id)
    sql.sql_deloneart(userid, oneart[1])
    bot.send_message(chat_id=call.message.chat.id, text=mess, parse_mode='html', reply_markup=None)


# Кнопка редактировать комментарий выбранного расход    changekommoneart__
@bot.callback_query_handler(func=lambda call: call.data.startswith('changekommoneart__'))
def changekomm_oneart(call):
    oneart = call.data.split("__")
    mess = 'Введите новый комментарий расхода:'
    datt = bot.send_message(call.message.chat.id, mess, parse_mode='html', reply_markup=None)
    bot.register_next_step_handler(datt, sqlchangekomm_oneart, oneart)


def sqlchangekomm_oneart(message, value):
    art = value
    userid = test_user(message.from_user.id)
    kom = message.text
    if message.content_type == 'text':
        sql.sql_changekommoneart(oneart=art[1], userid=userid, komm=kom)
        mess = f'Изменил комментарий на {kom}'
        bot.send_message(message.from_user.id, mess, reply_markup=None)
    else:
        datt = bot.send_message(message.chat.id, 'Комментарий должен быть текстом. Повтори ввод:')
        bot.register_next_step_handler(datt, sqlchangekomm_oneart, art)


# Кнопка редактировать сумму выбранного расход    sql_deloneart
@bot.callback_query_handler(func=lambda call: call.data.startswith('changesumoneart__'))
def changesumoneart__(call):
    oneart = call.data.split("__")
    mess = 'Введите новую сумму расхода:'
    datt = bot.send_message(call.message.chat.id, mess, parse_mode='html', reply_markup=None)
    bot.register_next_step_handler(datt, sqlchangesumm_oneart, oneart)


def sqlchangesumm_oneart(message, value):
    art = value
    userid = test_user(message.from_user.id)
    summ = message.text
    if message.content_type == 'text' and summ.isdigit() and int(summ) > 0:
        sql.sql_changesummoneart(oneart=art[1], userid=userid, summa=summ)
        mess = f'Изменил сумму на {summ} руб.'
        bot.send_message(message.from_user.id, mess, reply_markup=None)
    else:
        datt = bot.send_message(message.chat.id, 'Сумма должена быть целым числом больше 0! Повтори ввод:')
        bot.register_next_step_handler(datt, sqlchangesumm_oneart, art)


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
        changebut = types.InlineKeyboardButton(text='✏', callback_data=f'сust__chancat__{row[0]}__{row[1]}')
        delbut = types.InlineKeyboardButton(text='❌', callback_data=f'сust__dlcat__{row[0]}__{row[1]}')
        markup.add(catbut, changebut, delbut)
    markup.add(types.InlineKeyboardButton(text='➕ Добавить новую', callback_data='newc'))
    back = types.InlineKeyboardButton(text='🔙 Назад', callback_data='option')
    markup.add(back)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=mess,
                          parse_mode='html', reply_markup=markup)


# Редактирование подкатегорий
@bot.callback_query_handler(func=lambda call: call.data.startswith('сust__chancat__'))
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
                                              callback_data=f'сust__chancat__{art[4]}__{art[5]}'))
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
    net = types.InlineKeyboardButton(text='Нет', callback_data=f'сust__chancat__{delart[4]}__{delart[5]}')
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
                                          callback_data=f'сust__chancat__{delart[3]}__{delart[4]}'))
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
    mess = f'Напиши сумму затрат в подкатегории {art[2]}.\nЧерез пробел можешь указать комментарий.'
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
    summkomm = message.text
    summkomm = summkomm.split(" ", 1)
    print(summkomm)
    try:
        komm = summkomm[1]
    except IndexError:
        komm = ''
    if message.content_type == 'text' and summkomm[0].isdigit() and int(summkomm[0]) > 0:
        hide_markup = types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, '👍', reply_markup=hide_markup)
        now = str(datetime.datetime.now())
        rash = sql.sql_insert_rashod(artid=art[1], userid=userid, summa=summkomm[0], datenow=now, komment=komm)
        mess = f'Добавил {summkomm[0]}руб. на {art[2]}.\nКомментарий: {komm}'
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Редактировать',
                                              callback_data=f'chanoneart__{rash[0]}__{rash[1]}__{rash[2]}'))
        markup.add(types.InlineKeyboardButton(text='🔝 Главное меню', callback_data='mainmenu'))
        bot.send_message(message.from_user.id, mess, reply_markup=markup)
    else:
        datt = bot.send_message(message.chat.id,
                                'Сумма должена быть целым числом больше 0!'
                                ' Через пробел можешь указать комментарий. Повтори ввод:')
        bot.register_next_step_handler(datt, input_rasx, art)


# Запуск \ перезапуск бота
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(3)
            print(str(e))
