import sqlite3


# Проверка пользователя SQL
def facecontrol(userid: int):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f'SELECT UserID FROM Users WHERE UserID ={userid}')
    us = sql.fetchone()
    print('user= ' + str(us))
    if us is None:
        print('Нету пользователя, добавляю')
        res = 0
    else:
        print('Есть пользователь')
        res = 1
    return res


# Добавление нового пользователя SQL
def sql_insert_users(userid: int, firstname: str, lastname: str, login: str):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    try:
        sql.execute('INSERT INTO Users (UserId, FirstName, LastName, Login) VALUES (?, ?, ?, ?);',
                    (userid, firstname, lastname, login))
        db.commit()
        rez = 'Добавлено'
    except:
        rez = 'Такой уже есть'
    db.close()
    return rez


# Получение списка категорий
def sql_takecat_list(userid: int):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f'SELECT catid, Name FROM Cat WHERE UserId = {userid} and Disable = 0')
    tt = sql.fetchall()
    db.close()
    return tt


# Получение списка подкатегорий
def sql_takeart_list(userid: int, cat: str):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f"""SELECT A.artid, A.name FROM Art A
                LEFT JOIN Cat C ON A.catid=C.catid      
                WHERE UserId = {userid} and C.catid = {cat} and A.disable = 0""")
    at = sql.fetchall()
    db.close()
    return at


# Добавление новой категории sql
def sql_insert_cat(namecat: str, userid: int):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute('INSERT INTO Cat (Name, UserID) VALUES (?, ?);', (namecat, userid))
    db.commit()
    sql.execute(f'select max(catid) from cat WHERE userid = {userid}')
    catid = sql.fetchone()
    db.close()
    return catid


# Добавление новой подкатегории sql
def sql_insert_art(nameart: str, namecat: str, userid: int):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute('INSERT INTO Art (Name, catid) VALUES (?, ?);', (nameart, namecat))
    db.commit()
    sql.execute(f'''select max(A.artid) from art A
                    left join Cat C on A.CatID = C.CatID
                    WHERE C.userid = {userid}''')
    artid = sql.fetchone()
    db.close()
    return artid


# Получение статистики по категориям sql
def sql_takesumcat(userid: int, d1: str, d2: str):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f'''select C.CatID, c.name, sum(R.Summa) as Summa from Rashod R
                left join Art A on R.ArtID = A.ArtID
                left join Cat C on A.CatID = C.CatID
                where  R.DateTime BETWEEN '{d1}' AND '{d2}'
                AND R.UserId = {userid} AND C.disable = 0 AND A.disable = 0 AND R.disable = 0
                group by C.CatID''')
    sumcat = sql.fetchall()
    # print(type(sumcat), '   ', sumcat)
    db.close()
    return sumcat


# Получение статистики по подкатегориям sql
def sql_takesumart_list(userid: int, cat: str, d1: str, d2: str):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f'''select R.ArtID, A.name, sum(R.Summa) as Summa from Rashod R
                left join Art A on R.ArtID = A.ArtID
                left join Cat C on A.CatID = C.CatID
                where  R.UserId = {userid} AND C.CatID = {cat} AND A.disable = 0 AND R.disable = 0
                AND R.DateTime BETWEEN '{d1}' AND '{d2}'
                group by R.ArtID''')
    sumart = sql.fetchall()
    db.close()
    return sumart


# Получение статистики по одной подкатегории
def sql_takesumoneart_list(userid: int, artid: str, d1: str, d2: str):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f'''select R.RashID, R.Summa, strftime('%d.%m.%Y %H:%M', R.DateTime) as DateTime, R.Komment
                    from Rashod R
                    left join Art A on R.ArtID = A.ArtID
                    left join Cat C on A.CatID = C.CatID
                    where  R.UserId = {userid} AND A.disable = 0 AND R.ArtID = {artid}  AND R.disable = 0
                    AND R.DateTime BETWEEN '{d1}' AND '{d2}'
                ''')
    sumoneart = sql.fetchall()
    db.close()
    return sumoneart


# Поличение списка всех расходов
def sql_allrash(userid: int):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f'''select R.RashID, R.Summa, strftime('%d.%m.%Y %H:%M', R.DateTime) as DateTime,
                                                            R.Komment, C.Name as Cat, A.Name as Art
                    from Rashod R
                    left join Art A on R.ArtID = A.ArtID
                    left join Cat C on A.CatID = C.CatID
                    where  R.UserId = {userid} AND A.disable = 0 AND R.disable = 0
                    order by 3 DESC
                ''')
    allrash = sql.fetchall()
    db.close()
    return allrash


# Удаление (проставление признака) категории sql
def sql_delcat(userid: int, cat: str):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f'''UPDATE cat SET Disable = 1 where UserId = {userid} and CatID = {cat}''')
    db.commit()
    db.close()


# Удаление (проставление признака) подкатегории sql
def sql_delart(art: str):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f'''UPDATE art SET Disable = 1 where ArtID = {art}''')
    db.commit()
    db.close()


# Удаление (проставление признака) выбранного расхода sql
def sql_deloneart(userid: int, oneart: str):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f'''UPDATE rashod SET Disable = 1 where UserId = {userid} and rashID = {oneart}''')
    db.commit()
    db.close()


# Редактирование суммы выбранного расхода sql
def sql_changesummoneart(userid: int, oneart: str, summa: int):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f'''UPDATE rashod SET Summa = {summa} where UserId = {userid} and rashID = {oneart}''')
    db.commit()
    db.close()


# Редактирование комментарий выбранного расхода sql
def sql_changekommoneart(userid: int, oneart: str, komm: str):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f'''UPDATE rashod SET Komment = '{komm}' where UserId = {userid} and rashID = {oneart}''')
    db.commit()
    db.close()


# Переименовать категорию sql
def sql_rename_cat(userid: int, catid: str, namecat: str):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f'''UPDATE cat SET Name = '{namecat}' where UserId = {userid} and CatID = {catid}''')
    db.commit()
    db.close()


#   Переименовать подкатегорию sql
def sql_rename_art(artid: str, nameart: str):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute(f'''UPDATE art SET Name = '{nameart}' where ArtID = {artid}''')
    db.commit()
    db.close()


# Добавление нового расхода sql
def sql_insert_rashod(artid: str, userid: int, summa: int, datenow: str, komment: str):
    db = sqlite3.connect('server.db')
    sql = db.cursor()
    sql.execute('INSERT INTO Rashod (UserID, ArtID, Summa, DateTime, Komment) VALUES (?, ?, ?, ?, ?);',
                (userid, artid, summa, datenow, komment))
    db.commit()
    sql.execute(f'''select max(RashID), summa, strftime('%d.%m.%Y %H:%M', DateTime) as DateTime from Rashod
                    WHERE userid = {userid} and ArtID = {artid}''')
    rashid = sql.fetchone()
    db.close()
    return rashid
