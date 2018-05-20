import paramiko
import json
from scr.Exceptions import UnknownTransport, TransportError, AuthError, UnknownTransportError
from scr.Exceptions import TransportConnectionError, UnknownStatus, AddControlError, ControlListError
from scr.transports import get_env

_env = None #Хранение параметров для подключения к целевому хосту по SSH

# Класс тнаспрота SSH
class SSH:
    #Конструктор:
    def __init__(self, transport_name, host, port, login, password):
        self.transport_name = transport_name
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        #Клиент для подключения к целевому хосту через SSH:
        self.client = paramiko.SSHClient()
        #Добавляем ключ сервера в список известных хостов — файл .ssh/known_hosts.
        #Если при соединении с сервером ключа в нем не найдено, то по умолчанию ключ «отбивается» и вызввается SSHException
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #Подключение к целевому хосту через SSH-сервер:
        self.connect(self.client)
    
  
    #Выполняет подключение к целевому хосту
    def connect(self, client_name):
        try:
            print ("Попытка подключения к %s:%d" % (self.host, self.port))
            client_name.connect(hostname = self.host, username = self.login, password = self.password, port = self.port)
        except paramiko.ssh_exception.AuthenticationException:
            print ("Ошибка аутентификации к целевому хосту \"%s\" через %s-соединение, проверьте логин и пароль" % (self.host, self.transport_name))
            
        except paramiko.ssh_exception.NoValidConnectionsError:
            print ("Unable to connect to port %d on %s" % (self.port, self.host))
        except Exception as value:
            print("Ошибка, подключение к \"%s\" не установлено" % (self.host, value))
        else:
            print("Подключено к %s:%d" % (self.host, self.port))

    #Выполняет комманду на целевом хосте
    def exec_(self, command):
        try:
            #Выполнить команду command:
            print ("Попытка выполнения команды %s" % command)
            stdin, stdout, stderr = self.client.exec_command(command)
            #Записать результат в results:
            results = stdout.read()
            error = stderr.read()
            if results != b'' and results != None:
                return results
            else:
                error = stderr.read()
                raise TransportError(error)
        except TransportError as value:
            if error != b'':
                print("Команда не выполнена по причине: ", value)
                return None
        except FileNotFoundError or IOError:
            raise TransportError(error)
            return None
    def close(self):
        self.client.close()
    #Возвращает содержимое файла
    #Способ 1 (через SFTP)
    def get_file(self, path): 
        try:            
            transport = paramiko.Transport((self.host, self.port))
            transport.connect(username = self.login, password = self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            file_content = sftp.file(path, mode = 'r').read()
            transport.close()
        except FileNotFoundError or IOError:
            print("Файла \"%s\" не существует" % path.split('/')[-1])
            return None
        except PermissionError:
            print("Отсутствует доступ к Файлу \"%s\"" % path.split('/')[-1])
            return None
        except Exception as value:
            print("Ошибка: ", value)
        else:
            return file_content


    #Возвращает содержимое файла
    #Способ 2 (через отправку команд функцией exec_)
    def get_file_through_exec(self, path): 
        try:            
            #Удалить лишние пробелы в указанном пользователем пути:
            path = path.rstrip()
            path = path.lstrip()
            #Извлечь имя файла и папки в указанном пути:
            file_name = path.split('/')[-1]
            folder = path[0:-len(file_name)]

            #Передать команду целевому хосту на чтение файла:
            file_content = self.exec_('cat %s' % path)
        except TransportError as value:
            print("Не удалось прочитать файл \"%s\", %s" % (file_name, value))
            return None
        except Exception as value:
            print("Ошибка: ", value)
        else:
            return file_content
        


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
    return SSH(transport_name, host, port, login, password)

