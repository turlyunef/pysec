import json
import sqlite3
from scr.Exceptions import UnknownTransport, TransportError, AuthError, UnknownTransportError
from scr.Exceptions import TransportConnectionError, UnknownStatus, AddControlError
from scr.Exceptions import ControlListError
from scr.transports import get_transport_settings
from datetime import datetime

_data_base_instance = None #Хранение инстанса базы данных SQLite
_control_list = None #Хранение содержимого файла control.json (инфо о проверках)

#Десериализует 'control.json' и вносит данные в _control_list
def get_control_list():
    global _control_list
    if not _control_list:
        try:
            with open('control.json', 'r', encoding='utf-8-sig') as flow: 
                _control_list = json.load(flow, encoding='utf-8-sig')
        except FileNotFoundError:
            raise ControlListError()

#Получение данных из файла control.json в переменную _control_list:
get_control_list()

#Класс для сохранения информации об использованных транспортах (хост порт и логин)
class Transport_info:
    pass

#Класс базы данных
class DB:
    
    #Словарь с наименованиями статусов для записи в таблицу scandata по результатам проверки:
    status_dict = {1 : 'STATUS_COMPLIANT', 2: 'STATUS_NOT_COMPLIANT',
                           3: 'STATUS_NOT_APPLICABLE', 4: 'STATUS_ERROR', 5: 'STATUS_EXCEPTION'}
    #Конструктор:
    def __init__(self):
        #Открытие БД в памяти:
        self.db = sqlite3.connect(':memory:') 
        #Создание курсора БД:
        self.db_cursor = self.db.cursor()
          
        
    #Добавить запись values в таблицу table 
    def add_values_to_DB(self, table, values):
        self.db_cursor.execute ("INSERT INTO {} VALUES ({})".format(table, values))
        self.db.commit()


    #Кодирует строку в число (Для передачи в БД ' и других знаков препинания в описании комплаенса)
    def text_to_bits(text):
        bits = bin(int.from_bytes(text.encode('utf-8'), 'big'))[2:]
        return int(bits.zfill(8 * ((len(bits) + 7) // 8)),2)


    #Декодирует строку из числа (Для передачи в БД ' и других знаков препинания в описании комплаенса)
    def text_from_bits(bits, encoding='utf-8'):
        return bits.to_bytes((bits.bit_length() + 7) // 8, 'big').decode('utf-8')


    #(Отладочная функция)
    #Получить все таблицы из базы данных в виде списка и вывести все данные на экран
    def get_all_table_from_DB():
        self.db_cursor.execute("SELECT name from sqlite_master WHERE type = 'table'")
        tables = list()
        for table in db_cursor:
            tables.append(table)

        for table in tables:
            print(table)
            self.db_cursor.execute("SELECT * FROM {}".format(table[0]))
            print(self.db_cursor.fetchall())
        
        return tables


    #Получить данные с индексом idx комплаенса по его id из таблицы control:
    def get_from_control(self, idx, id_):
        try:
            self.db_cursor.execute('SELECT * FROM control WHERE id=?', (str(id_),))
            data = DB.text_from_bits(int((self.db_cursor.fetchall()[0][idx])))
        except IndexError:
            print("Запись %s отсутствует в таблице control" % id_)
        except sqlite3.OperationalError:
            print("Таблицы не существует")
        return data

            
    
#-------------------------------------------------------------------------------------------------
#
def get_data_base_instance():
    global _data_base_instance
    if not _data_base_instance:
        _data_base_instance = DB()

get_data_base_instance()

#
def execute_bd_command(command):
    global _data_base_instance ####
    _data_base_instance.db_cursor.execute(command)


#Копирование всех данных из файла control.json в таблицу control:
def copy_to_control():
    global _data_base_instance ####
    for values in _control_list:
        execute_bd_command ("INSERT INTO control VALUES ({}, \'{}\', \'{}\', \'{}\')".format(int(values[0]), \
                                                                                                     DB.text_to_bits(values[1]),\
                                                                                                     DB.text_to_bits(values[2]),\
                                                                                                     DB.text_to_bits(values[3])))
    _data_base_instance.db.commit()

#Добавить запись в таблицу scandata по результатам выполнения скрипта:
def add_control (id_, status, response, datetime_before):
    global _data_base_instance ####
    if status in DB.status_dict.keys():
        values = "{},\'{}\',\'{}\',\'{}\',\'{}\'".format(id_,\
                                                            DB.text_to_bits(str(DB.status_dict[status])),\
                                                            DB.text_to_bits(response),\
                                                            str(datetime_before)[0:-7],\
                                                            str(datetime.now()-datetime_before))
            
        _data_base_instance.add_values_to_DB('scandata (id, status, response, datetime_from_run, lasting)', values)
    elif (status not in DB.status_dict.keys()):
        raise UnknownStatus()
    else:
        raise AddControlError()

#Получить все данные в виде списка из таблицы:
def get_data_from_table(table):
    global _data_base_instance ####
    execute_bd_command("SELECT * FROM {}".format(table))
    tables_new=[] #Вспомогательный список для извлечения из БД и декодирования строк таблицы
    for value in _data_base_instance.db_cursor:
        value_new=list(value) # Извлекаем все элементы записей в таблице
        if (table != "transports"):
            value_new[1]=DB.text_from_bits(int(value[1])) #Декодируем из числа текстовую строку
            value_new[2]=DB.text_from_bits(int(value[2])) #Декодируем из числа текстовую строку
        if (table == "control"):
            value_new[3]=DB.text_from_bits(int(value[3])) #Декодируем из числа текстовую строку
        tables_new.append(value_new) #Добавляем все записи во вспомогательную таблицу
    return tables_new



#Получение информации об используемых транспортах:
#Возвращает список инстансов, внутри которых хранятся хост, порт и логин для транспортов
def get_transport_info_list():
    global _data_base_instance

    
    transport_info_list = []  #Хранит список инстансов класса Transport_info
    transport_list = [] #Хранит список имен транспортов, чтобы не выгружать повторные имена, на тот случай
    #если создадут несколько инстансов одного и того же транспорта в модуле transports 
    
    #Извлечение всех транспортов, которые были использованы:
    
    transport_name_list = get_data_from_table('transports')
    
    #Перебор всех транспортов, которые были использованы:
    for value in transport_name_list:
        #Если имя транспорта не в списке имен транспортов:
        if value[1] not in transport_list:
            transport_list.append(value[1]) #Добавление имени транспорта в список имен транспортов
            transport_info = Transport_info() #Создание инстанса для хранения информации об транспорте
            transport_info.name = value[1] #внести имя в инстанс
            transport_info.host, transport_info.port , transport_info.login = \
                                    get_transport_settings(value[1]) #Получить хост порт и логин для данного транспорта
            transport_info_list.append(transport_info) #добавить инстанс транспорта в их спосок
    return transport_info_list 

#Добавить отметку об использовании транспорта в БД:
#Используется в функции get_transport(), в модуле transports. При создании инстанса транспорта, в БД падает запись
def set_transport_list(transport_name):
    global _data_base_instance ####
    _data_base_instance.add_values_to_DB('transports (transport)', "\'{}\'".format(transport_name))
    
    
def close_data_base():
    global _data_base_instance ####
    _data_base_instance.db.close()
