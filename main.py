import os
import sqlite3
import json
from datetime import datetime
import importlib

from scr.transports import get_transport #Возвращает instance транспорта
from scr.DB import DB
from scr.reporting import print_report
from scr.Exceptions import ControlDataError

#Создать транспорт SSH:
instance = get_transport("SSH")

#Создать транспорт MySQL:
instance2 = get_transport("MySQL")

#Создать базу данных
data = DB()


#Создание таблицы control
data.db_cursor.execute ("CREATE TABLE control(id INTEGER PRIMARY KEY, descr TEXT, request TEXT, descr_short TEXT)")
#где:
#id - идентификатор проверки (456 и т.д.)
#descr - описание проверки 
#request - требование проверки (Файл существует и т.д.)
#descr_short - короткое описание проверки


#Создание таблицы scandata
data.db_cursor.execute ("CREATE TABLE scandata(id INTEGER PRIMARY KEY, status TEXT, response TEXT, datetime_from_run TEXT, lasting TEXT)")
#где:
#id - идентификатор проверки (456 и т.д.)
#response - ответ на request (Файл отсутствует, файл существует и т.д.)
#datetime - дата и время начала выполнения проверки
#lasting - продолжительность выполнения проверки

#Создание таблицы transports
data.db_cursor.execute ("CREATE TABLE transports(id INTEGER PRIMARY KEY AUTOINCREMENT, transport TEXT)")
#где:
#id - автонумерация
#transport - название используемого транспорта

#Копирование всех данных из файла control.json в таблицу control:
for values in data.control_list:
    data.db_cursor.execute ("INSERT INTO control VALUES ({}, \'{}\', \'{}\', \'{}\')".format(int(values[0]), \
                                                                                             DB.text_to_bits(values[1]),\
                                                                                             DB.text_to_bits(values[2]),\
                                                                                             DB.text_to_bits(values[3])))
    data.db.commit()
    
#Чтение имен всех файлов в папке scripts:
scripts_listdir = os.listdir('./scripts')
print("Список всех скриптов в папке scripts:\n", scripts_listdir)
#Запуск пошагово всех скриптов в папке scripts:
for script in scripts_listdir:
    if script.endswith('.py'):
        print ("\nЗапуск скрипта {}".format (script[:-3]))
        datetime_before = datetime.now()
        try:
            #exec(open('./scripts/{}'.format(script), encoding='utf-8').read())
            importlib.import_module('scripts.'+script)
        except Exception as value:
            #Добавление записи со статусом STATUS_EXCEPTION в таблицу scandata:
            data.add_control(int(script[0:3]), 5, "Ответ на запрос не получен", datetime_before)
            print("Ошибка: ", value)
        
#Создание отчета
try:
    print_report(data.get_data_from_table("scandata"), data.get_data_from_table("control"), instance, data)
except ControlDataError:
    print("Ошибка генерации отчета, в файле \"control.json\" отсутствуют все записи для скриптов в папке scripts")

#Закрытие БД:
data.db.close()

#Закрытие соединения с целевым хостом через SSH-сервер:
try:
    instance.close()
except AttributeError or NameError:
    print("Соединение с целевым хостом через SSH-сервер не создавалось, ошибка закрытия инстанса транспорта")

#Закрытие соединения с целевым хостом через MySQL:
try:
    instance2.close()
except AttributeError or NameError:
    print("Соединение с целевым хостом через MySQL не создавалось, ошибка закрытия инстанса транспорта")
