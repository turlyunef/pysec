import os
import sqlite3
import json
from datetime import datetime
import importlib

from scr.transports import get_transport
from scr.DB import execute_bd_command, copy_to_control, add_control, close_data_base
from scr.reporting import print_report
from scr.Exceptions import ControlDataError


#Создание таблицы control
execute_bd_command ("CREATE TABLE control(id INTEGER PRIMARY KEY, descr TEXT, request TEXT, descr_short TEXT)")
#где:
#id - идентификатор проверки (456 и т.д.)
#descr - описание проверки 
#request - требование проверки (Файл существует и т.д.)
#descr_short - короткое описание проверки

#Копирование всех данных из файла control.json в таблицу control
copy_to_control()

#Создание таблицы scandata
execute_bd_command ("CREATE TABLE scandata(id INTEGER PRIMARY KEY, status TEXT, response TEXT, datetime_from_run TEXT, lasting TEXT)")
#где:
#id - идентификатор проверки (456 и т.д.)
#response - ответ на request (Файл отсутствует, файл существует и т.д.)
#datetime - дата и время начала выполнения проверки
#lasting - продолжительность выполнения проверки

#Создание таблицы transports
execute_bd_command ("CREATE TABLE transports(id INTEGER PRIMARY KEY AUTOINCREMENT, transport TEXT)")
#где:
#id - автонумерация
#transport - название используемого транспорта


#Создать или подгрузить транспорт SSH:
from scr.transports import get_transport
instance_SSH = get_transport("SSH")

#Создать транспорт MySQL:
instance_MySQL = get_transport("MySQL")

    
#Чтение имен всех файлов в папке scripts:
scripts_listdir = os.listdir('./scripts')
#Удалить из списка не скрипты:
try:
    for value in scripts_listdir:
        if value.startswith('__'):
            scripts_listdir.remove(value)
except:
    pass
print("Список всех скриптов в папке scripts:\n", scripts_listdir)

#Запуск пошагово всех скриптов в папке scripts:
for script in scripts_listdir:
    if script.endswith('.py'):
        print ("\nЗапуск скрипта {}".format (script[0:-3]))
        datetime_before = datetime.now()
        try:
            importlib.import_module('scripts.'+script[0:-3])
        except TransportError as value:
            print("Ошибка транспорта. Команда не выполнена по причине: ", value)
        except Exception as value:
            #Добавление записи со статусом STATUS_EXCEPTION в таблицу scandata:
            add_control(int(script.split("_")[0]), 5, "Ответ на запрос не получен", datetime_before)
            print("Ошибка запуска модуля: ", value)
        
#Создание отчета
try:
    print_report()
except ControlDataError:
    print("Ошибка генерации отчета, в файле \"control.json\" отсутствуют все записи для скриптов в папке scripts")

#Закрытие БД:
close_data_base()

#Закрытие соединения с целевым хостом через SSH-сервер:
try:
    instance_SSH.close()
except AttributeError or NameError:
    print("Соединение с целевым хостом через SSH-сервер не создавалось, ошибка закрытия инстанса транспорта")

#Закрытие соединения с целевым хостом через MySQL:
try:
    instance_MySQL.close()
except AttributeError or NameError:
    print("Соединение с целевым хостом через MySQL не создавалось, ошибка закрытия инстанса транспорта")

print("Выполнение завершено")
