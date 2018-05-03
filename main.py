import os
import sqlite3
import json
from SSH import *


# Класс исключения при отсутствии транспорта
class UnknownTransport(Exception): pass

# Класс исключения при остутвии комманды или файла
class TransportError(Exception): pass 

# Класс исключения в случае ошибок подключения
class TransportConnetionError(Exception): pass

# Класс исключения в случае неверной структуры в файле env.json
class Error_get_connection_settings(Exception): pass

# Класс исключения при использовании номера неизвестного статуса
class UnknownStatus(Exception): pass

# Класс исключения при ошибке добавления записи функцией add_control
class AddControlError(Exception): pass

_control_list = None #Хранение данных для таблицы control базы данных tables.db

#Десериализует _control_list
def get_control_list():
    global _control_list
    if not _control_list:
        with open('control.json','r') as flow:
            _control_list = json.load(flow)


#Добавить запись values в таблицу table 
def add_values_to_DB(table, values):
    db_cursor.execute ("INSERT INTO {} VALUES ({})".format(table, values))
    db.commit()


#Кодирует строку в число (Для передачи в БД ' и других знаков препинания в описании комплаенса)
def text_to_bits(text):
    bits = bin(int.from_bytes(text.encode('utf-8'), 'big'))[2:]
    return int(bits.zfill(8 * ((len(bits) + 7) // 8)),2)


#Декодирует строку из числа (Для передачи в БД ' и других знаков препинания в описании комплаенса)
def text_from_bits(bits, encoding='utf-8'):
    return bits.to_bytes((bits.bit_length() + 7) // 8, 'big').decode('utf-8')


#Получить все таблицы из базы данных в виде списка и вывести все данные на экран (не используется)
def get_all_table_from_DB():
    db_cursor.execute("SELECT name from sqlite_master WHERE type = 'table'")
    tables = list()
    for table in db_cursor:
        tables.append(table)

    for table in tables:
        print(table)
        db_cursor.execute("SELECT * FROM {}".format(table[0]))
        print(db_cursor.fetchall())
    
    return tables


#Получить описание комплаенса по его id из таблицы control:
def get_descr_from_control(id_):
    try:
        db_cursor.execute('SELECT * FROM control WHERE id=?', (str(id_),))
        _ = db_cursor.fetchall()[0][1]
    except IndexError:
        print("Запись %s отсутствует в таблице control" % id_)
    except sqlite3.OperationalError:
        print("Таблицы не существует")
    else:
        return _        

        
#Добавить запись в таблицу scandata по результатам выполнения скрипта:
def add_control (id_, status):
    descr = get_descr_from_control(id_)
    status_dict = {1 : 'STATUS_COMPLIANT', 2: 'STATUS_NOT_COMPLIANT',
                       3: 'STATUS_NOT_APPLICABLE', 4: 'STATUS_ERROR', 5: 'STATUS_EXCEPTION'}
    if descr != None and status in status_dict.keys():
        values = "\'{}\',\'{}\'".format(descr, str(status_dict[status]))
        add_values_to_DB('scandata (descr, status)', values)
    elif (status not in status_dict.keys()):
        raise UnknownStatus()
    else:
        raise AddControlError()

#Получить все данные в виде списка из таблицы:
def get_data_from_table(table):
    db_cursor.execute("SELECT * FROM {}".format(table))
    tables_new=[]
    for value in db_cursor:
        value_new=list(value)
        value_new[1]=text_from_bits(int(value[1]))
        tables_new.append(value_new)
    print(tables_new)
    return tables_new

#Открытие БД в памяти:
db = sqlite3.connect(':memory:')
db_cursor = db.cursor()

#Создание таблицы control и scandata
db_cursor.execute ("""
CREATE TABLE control(id INTEGER PRIMARY KEY, descr TEXT)
""")

db_cursor.execute ("""
CREATE TABLE scandata(id INTEGER PRIMARY KEY AUTOINCREMENT, descr TEXT, status TEXT)
""")

#Получение данные из файла control.json:
get_control_list()

#Копирование всех данных из файла control.json в таблицу control:
for values in _control_list:
    db_cursor.execute ("INSERT INTO control VALUES ({}, \'{}\')".format(int(values[0]), text_to_bits(values[1])))
    db.commit()

#Чтение имен всех файлов в папке scripts:
scrips_listdir = os.listdir('./scripts')

for script in scrips_listdir:
    if script.endswith('.py'):
        print ("Runing {}".format (script[:-3]))
        try:
            exec(open('./scripts/{}'.format(script)).read())
        except:
            #Добавление записи со статусом STATUS_EXCEPTION в таблицу scandata:
            add_control(int(script[0:3]), 5)
        
#Чтение содержимого таблицы scandata:
print("Table scandata:")
get_data_from_table("scandata")
db.close()




