import paramiko
import json

#Клиент для подключения к целевому хосту через SSH:
client = paramiko.SSHClient()
#Добавляем ключ сервера в список известных хостов — файл .ssh/known_hosts.
#Если при соединении с сервером ключа в нем не найдено, то по умолчанию ключ «отбивается» и вызввается SSHException
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

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
  
    #Выполняет подключение к целевому хосту
    def connect(self, client_name):
        try:
            print ("Попытка подключения к %s:%d" % (self.host, self.port))
            client_name.connect(hostname = self.host, username = self.login, password = self.password, port = self.port)
        except paramiko.ssh_exception.AuthenticationException:
            print ("Ошибка аутентификации к целевому хосту \"%s\" через %s-соединение, проверьте логин и пароль" % (self.host, self.transport_name))
            raise TransportConnetionError()
        except paramiko.ssh_exception.NoValidConnectionsError:
            print ("Unable to connect to port %d on %s" % (self.port, self.host))
            raise TransportConnetionError()
        except Error_get_connection_settings: #Если не удалось прочитать файл env.json
            raise TransportConnetionError()
        except Exception:
            print("Неизвестная ошибка, подключение к \"%s\" не установлено" % self.host)
            raise TransportConnetionError()
        else:
            print("Подключено к %s:%d" % (self.host, self.port))

    #Закрывает подключение к целевому хосту
    def close_connection(self, client_name):
        try:
            if False: #!!!Исключение не реализовано, поискать проверки на наличие установленного соединения с SSH сервером
                 raise TransportConnectionError(self.host)
        except TransportConnetionError as value:
            print("Отсутствует соединение с целевым хостом ", value)
        else:
            client_name.close() #Закрыть соединение с целевым хостом
    
    #Выполняет комманду на целевом хосте
    def exec_(self, command):
        try:
            self.connect(client) #Подключиться к целевому хосту
        except TransportConnetionError:
            pass
        else:
            try:
                #Выполнить команду command:
                print ("Попытка выполнения команды %s" % command)
                stdin, stdout, stderr = client.exec_command(command)
                #Записать результат в results:
                results = stdout.read()
                error = stdout.read()
                print ("results:", results, "error:",error) 
                if results != b'' and results != '':
                    print(results) #Вывод результата на экран 
                else:
                    error = stdout.read()
                    raise TransportError(error)
            except TransportError as value:
                if error !='' and error != b'':
                    print("Команда не выполнена по причине: ", value)
                else:
                    print("Команда не найдена")
            except FileNotFoundError or IOError:
                raise TransportError(error)
        finally:
            self.close_connection(client) #Закрыть соединение
  
    #Возвращает содержимое файла
    #Способ 1 (через SFTP)
    def get_file(self, path): 
        try:            
            transport = paramiko.Transport((self.host, self.port))
            transport.connect(username = self.login, password = self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            file_content = sftp.file(path, mode = 'r').read()
            self.close_connection(transport)
        except FileNotFoundError or IOError:
            print("Файла \"%s\" не существует" % path.split('/')[-1])
            return None
        except Exception:
            print("Ошибка")
        else:
            return file_content


    #Возвращает содержимое файла (Не работает)
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
            instance.exec_('cd %s' % folder)
            instance.exec_('cat %s' % file_name)
        except TransportError:
            print("Файла \"%s\" не существует" % file_name)
            return None
        except Exception:
            print("Неизвестная ошибка")
        else:
            return file_content
        
#Десериализует _env
def get_env():
    global _env
    if not _env:
        with open('env.json','r') as flow:
            _env = json.load(flow)
        

#Возвращает при необходимости нужные параметры для подключения к целевой системе на основе _env
def get_connection_settings(host = None, port = None, login = None, password = None):
    get_env() # Подгрузить _env из файла 'env.json'
    try:
        if host == None: host = _env['host']
        if port == None: port = _env['transports']['SSH']['port']
        if login == None: login = login = _env['transports']['SSH']['login']
        if password == None: password = _env['transports']['SSH']['password']
    except KeyError:        
        raise Error_get_connection_settings()
    else:
        return host, port, login, password

#Возвращает instance транспорта
def get_transport(transport_name, host = None, port = None, login = None,
                  password = None):
    try:
        if transport_name == "SSH":
            #Взять host, port, login, password из файла 'env.json' в зависимости от их содержимого:
            host, port, login, password = get_connection_settings(host, port, login, password)
            
        else:
            raise UnknownTransport(transport_name)
    except UnknownTransport as value: #Выбрасывается, если нет транспорта, указанного в аргументе вызова функции get_transport
        print("Транспорта ", value, " не существует")
        #return None
    except Error_get_connection_settings: #Выбрасывается при неверной структуре файла env.json
        print ("Невозможно извлечь параметры для подключения из файла 'env.json', нарушена структура файла")
        #return None
    return SSH(transport_name, host, port, login, password)
