import json
import importlib
from scr.Exceptions import UnknownTransport, AuthError, UnknownTransportError
from scr.Exceptions import TransportConnectionError, UnknownStatus, AddControlError, ControlListError
from scr.SSH import SSH
from scr.MySQL import MySQL

_env = None #Хранение параметров для подключения к целевому хосту по SSH

#Десериализует _env
def get_env():
    try:
        with open('env.json','r') as flow:
            env = json.load(flow)
    except FileNotFoundError:
        raise AuthError()
    return env

#Возвращает параметры для подключения к целевой системе на основе _env
#для вывода в отчет
def get_transport_settings(transport_name):
    global _env
    try:
        if not _env:
            _env = get_env()#Подгружаем _env из файла 'env.json'
        host = _env['host']
        port = _env['transports'][transport_name]['port']
        login = _env['transports'][transport_name]['login']
    except AuthError:
        raise AuthError()
    except KeyError:        
        raise AuthError()
    else:
        return host, port, login

#Возвращает при необходимости нужные параметры для подключения к целевой системе на основе _env
def get_connection_settings(transport_name, host = None, port = None, login = None, password = None):
    global _env
    try:
        if not _env:
            _env = get_env() #Подгружаем _env из файла 'env.json'
        if host == None: host = _env['host']
        if port == None: port = _env['transports'][transport_name]['port']
        if login == None: login = login = _env['transports'][transport_name]['login']
        if password == None: password = _env['transports'][transport_name]['password']
    except AuthError:
        raise AuthError()
    except KeyError:        
        raise AuthError()
    else:
        return host, port, login, password

#Возвращает instance транспорта SSH
def get_transport(transport_name, host = None, port = None, login = None,
                  password = None):
    try:
        #Взять host, port, login, password из файла 'env.json' в зависимости от их содержимого:
        host, port, login, password = get_connection_settings(transport_name, host, port, login, password)
    except UnknownTransport as value: #Выбрасывается, если нет транспорта, указанного в аргументе вызова функции get_transport
        print("Транспорта ", value, " не существует")
        return None
    except AuthError: #Выбрасывается при неверной структуре файла env.json
        print ("Невозможно извлечь параметры для подключения из файла 'env.json', нарушена структура файла")
        return None
    try:
        transport_instance = getattr(importlib.import_module("scr."+transport_name), transport_name)(transport_name, host, port, login, password)
    except TypeError:
        print ("Ошибка извлечения инстанса с переданными аргументами класса")
        return None
    except ModuleNotFoundError:
        print("Модуля ", transport_name, " не существует")
        return None
    else:
        return transport_instance
