import paramiko
from scr.Exceptions import TransportError


# Класс транспорта SSH
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
            print ("Попытка подключения к SSH-серверу через сокет %s: %d" % (self.host, self.port))
            client_name.connect(hostname = self.host, username = self.login, password = self.password, port = self.port)
        except paramiko.ssh_exception.AuthenticationException:
            print ("Ошибка аутентификации к целевому хосту \"%s\" через %s-соединение, проверьте логин и пароль" % (self.host, self.transport_name))
            
        except paramiko.ssh_exception.NoValidConnectionsError:
            print ("Не удается подключиться к порту %d на хосте %s" % (self.port, self.host))
        except Exception as value:
            print("Ошибка, подключение к SSH-серверу через хост \"%s\" не установлено" % (self.host, value))
        else:
            print("Подключено к SSH-серверу через сокет %s: %d" % (self.host, self.port))

    #Выполняет комманду на целевом хосте
    def exec_(self, command):
        try:
            #Выполнить команду command:
            print ("Выполнение на целевой системе команды: \"%s\"" % command)
            if self.client == None:
                raise TransportError(error)
            stdin, stdout, stderr = self.client.exec_command(command)
            #Записать результат в results:
            results = stdout.read()
            error = stderr.read()
            if results != b'' and results != None:
                return results
            else:
                error = stderr.read()
                raise TransportError(error)
        except FileNotFoundError or IOError:
            raise TransportError(error)
            return None

    #Закрыть клиент
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
            print("Содержимое файла: ", file_content)
            return file_content


    #Возвращает содержимое файла
    #Способ 2 (через отправку команд функцией exec_)
    def get_file_through_exec(self, path): 
        try:            
            #Удалить лишние пробелы в указанном пользователем пути:
            path = path.rstrip()
            path = path.lstrip()
            #Извлечь имя файла и папки в указанном пути:
            file_name,folder = path.rsplit('/', 1)

            #Передать команду целевому хосту на чтение файла:
            file_content = self.exec_('cat %s' % path)
        except TransportError as value:
            print("Не удалось прочитать файл \"%s\", %s" % (file_name, value))
            return None
        except Exception as value:
            print("Ошибка: ", value)
        else:
            print("Содержимое файла: ", file_content)
            return file_content
