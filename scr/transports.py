import json
import importlib
from scr.Exceptions import UnknownTransport, AuthError, UnknownTransportError
from scr.Exceptions import TransportConnectionError, UnknownStatus, AddControlError, ControlListError
from scr.SSH import SSH
from scr.MySQL import MySQL


_env = None #Хранение параметров для подключения к целевому хосту
_transport_instances = {} #Хранение создаваемых инстансов транспортов 

#Десериализует _env
def get_env():
    global _env
    if not _env:
        try:
            with open('env.json','r') as flow:
                _env = json.load(flow)
        except FileNotFoundError:
            raise AuthError()
    return _env

#Возвращает параметры для подключения к целевой системе на основе файла _env
#для вывода в отчет данных по использованным транспортам
def get_transport_settings(transport_name):
    global _env
    global _transport_instances
    try:
        _env = get_env() #Подгружаем _env из файла 'env.json'
        host = _env['host']
        port = _env['transports'][transport_name]['port']
        login = _env['transports'][transport_name]['login']
    except AuthError:
        raise AuthError()
    except KeyError:        
        raise AuthError()
    else:
        return host, port, login

#Возвращает нужные параметры для подключения к целевой системе на основе _env
def get_connection_settings(transport_name, host = None, port = None, login = None, password = None):
    global _env  
    try:
        _env = get_env() #Подгружаем _env из файла 'env.json'
    except AuthError:
        raise AuthError()

    #Возврат нужных параметров из словаря _env:
    try:
        if host == None: host = _env['host']
        if port == None: port = _env['transports'][transport_name]['port']
        if login == None: login = login = _env['transports'][transport_name]['login']
        if password == None: password = _env['transports'][transport_name]['password']
    except KeyError:        
        raise AuthError()
    else:
        return host, port, login, password

#Возвращает instance транспорта
#Проверяет был ли ранее использован запрошенный транспорт по списку _transport_name_list
#Если был, вернет существующий инстанс, если нет, то сгенерирует новый
def get_transport(transport_name, host = None, port = None, login = None,
                  password = None):
    global _transport_instances
    #Проверка по списку "_transport_name_list", был ли уже запрошен указанный в "transport_name" транспорт:
    if transport_name not in _transport_instances.keys():
        try:
            #Взять host, port, login, password из файла 'env.json' в зависимости от их содержимого:
            host, port, login, password = get_connection_settings(transport_name, host, port, login, password)
        except UnknownTransport as value: #Выбрасывается, если нет транспорта, указанного в аргументе вызова функции get_transport
            print("Транспорта ", value, " не существует")
            return None
        except AuthError: #Выбрасывается при неверной структуре файла env.json
            print ("Невозможно извлечь параметры для подключения из файла 'env.json', нарушена структура файла")
            return None
        #Вызвать нужный модуль с классом транспорта по имени транспорта в "transport_name"
        try:
            instance = getattr(importlib.import_module("scr."+transport_name), transport_name)(transport_name, host, port, login, password)
        except TypeError:
            print ("Ошибка извлечения инстанса с переданными аргументами класса")
            return None
        except Exception as value:
            # примечание для проверяющего: Windows 10 вызывает исключение ModuleNotFoundError,
            # но под линуксом имя ModuleNotFoundError вызывает ошибку, поэтому вставил обобщенный Exception
            print("Модуль ", transport_name, " не существует, ошибка:", value)
            return None
        else:
            #Добавить созданный транспорт в словарь хранения транспортов:
            _transport_instances[transport_name] = instance

            #Добавить отметку об использовании транспорта в БД:
            from scr.DB import set_transport_list
            set_transport_list(transport_name)
            
            return instance

    #Если такой транспорт уже создавался, то вернуть его значение из словаря хранения транспортов:
    else:
        return _transport_instances[transport_name]
