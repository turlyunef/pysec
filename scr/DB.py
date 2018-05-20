import json
import sqlite3
from scr.Exceptions import UnknownTransport, TransportError, AuthError, UnknownTransportError
from scr.Exceptions import TransportConnectionError, UnknownStatus, AddControlError
from scr.Exceptions import ControlListError
from datetime import datetime

class DB:
    
    #Словарь с наименованиями статусов для записи в таблицу scandata по результатам проверки:
    status_dict = {1 : 'STATUS_COMPLIANT', 2: 'STATUS_NOT_COMPLIANT',
                           3: 'STATUS_NOT_APPLICABLE', 4: 'STATUS_ERROR', 5: 'STATUS_EXCEPTION'}

    #Десериализует _control_list
    def get_control_list(self):
        try:
            with open('control.json','r') as flow: 
                self.control_list = json.load(flow)
        except FileNotFoundError:
            raise ControlListError()
         

    #Конструктор:
    def __init__(self):
        #Открытие БД в памяти:
        self.db = sqlite3.connect(':memory:') 
        #Создание курсора БД:
        self.db_cursor = self.db.cursor()
        #Получение данные из файла control.json:
        self.get_control_list()

    
        
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


    #Получить данные с индексом what комплаенса по его id из таблицы control:
    def get_from_control(self, what, id_):
        try:
            self.db_cursor.execute('SELECT * FROM control WHERE id=?', (str(id_),))
            data = DB.text_from_bits(int((self.db_cursor.fetchall()[0][what])))
        except IndexError:
            print("Запись %s отсутствует в таблице control" % id_)
        except sqlite3.OperationalError:
            print("Таблицы не существует")
        return data

            
    #Добавить запись в таблицу scandata по результатам выполнения скрипта:
    def add_control (self, id_, status, response, datetime_before):
        if status in DB.status_dict.keys():
            values = "{},\'{}\',\'{}\',\'{}\',\'{}\'".format(id_,\
                                                             DB.text_to_bits(str(DB.status_dict[status])),\
                                                             DB.text_to_bits(response),\
                                                             str(datetime_before)[0:-7],\
                                                             str(datetime.now()-datetime_before))
            
            self.add_values_to_DB('scandata (id, status, response, datetime_from_run, lasting)', values)
        elif (status not in DB.status_dict.keys()):
            raise UnknownStatus()
        else:
            raise AddControlError()

    #Получить все данные в виде списка из таблицы:
    def get_data_from_table(self,table):
        self.db_cursor.execute("SELECT * FROM {}".format(table))
        tables_new=[] #Вспомогательный список для извлечения из БД и декодирования строк таблицы
        for value in self.db_cursor:
            value_new=list(value) # Извлекаем все элементы записей в таблице
            value_new[1]=DB.text_from_bits(int(value[1])) #Декодируем из числа текстовую строку
            value_new[2]=DB.text_from_bits(int(value[2])) #Декодируем из числа текстовую строку
            if (table == "control"):
                value_new[3]=DB.text_from_bits(int(value[3])) #Декодируем из числа текстовую строку
            tables_new.append(value_new) #Добавляем все записи во вспомогательную таблицу
        return tables_new
