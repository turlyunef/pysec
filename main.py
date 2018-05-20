import os
import sqlite3
import json
from datetime import datetime

from scr.SSH import get_transport #Возвращает instance транспорта SSH
from scr.DB import DB
from scr.reporting import print_report


#Создать транспорт SSH:
instance = get_transport("SSH")

#Создать базу данных
data = DB()


#Создание таблицы control и scandata
data.db_cursor.execute ("CREATE TABLE control(id INTEGER PRIMARY KEY, descr TEXT, request TEXT, descr_short TEXT)")
#где:
#id - идентификатор проверки (456 и т.д.)
#descr - описание проверки 
#request - требование проверки (Файл существует и т.д.)
#descr_short - короткое описание проверки

data.db_cursor.execute ("CREATE TABLE scandata(id INTEGER PRIMARY KEY, status TEXT, response TEXT, datetime_from_run TEXT, lasting TEXT)")
#где:
#id - идентификатор проверки (456 и т.д.)
#response - ответ на request (Файл отсутствует, файл существует и т.д.)
#datetime - дата и время начала выполнения проверки
#lasting - продолжительность выполнения проверки

#Копирование всех данных из файла control.json в таблицу control:
for values in data.control_list:
    data.db_cursor.execute ("INSERT INTO control VALUES ({}, \'{}\', \'{}\', \'{}\')".format(int(values[0]), \
                                                                                             DB.text_to_bits(values[1]),\
                                                                                             DB.text_to_bits(values[2]),\
                                                                                             DB.text_to_bits(values[3])))
    data.db.commit()
    
#Чтение имен всех файлов в папке scripts:
scripts_listdir = os.listdir('./scripts')
print(scripts_listdir)
for script in scripts_listdir:
    if script.endswith('.py'):
        print ("Запуск скрипта {}".format (script[:-3]))
        datetime_before = datetime.now()
        try:
            exec(open('./scripts/{}'.format(script), encoding='utf-8').read())
        except Exception as value:
            #Добавление записи со статусом STATUS_EXCEPTION в таблицу scandata:
            data.add_control(int(script[0:3]), 5, "Ответ на запрос не получен", datetime_before)
            print("Ошибка: ", value)
        
#Создание отчета

print_report(data.get_data_from_table("scandata"), data.get_data_from_table("control"))

#Закрытие БД:
data.db.close()

#Закрыть соединение с целевым хостом через SSH-сервер:
instance.close()

