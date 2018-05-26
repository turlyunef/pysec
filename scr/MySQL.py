import pymysql.cursors
_env = None #Хранение параметров для подключения к целевому хосту по SSH

# Класс тнаспрота MySQL
class MySQL:
    #Конструктор:
    def __init__(self, transport_name, host, port, login, password):
        self.transport_name = transport_name
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.connect()
        
    def connect(self, db = 'sadb', charset = 'utf8', unix_socket = False):
        try:
            self.connection = pymysql.connect(host= self.host,
                                 user = self.login,
                                 port = self.port,
                                 password = self.password,
                                 db = db,
                                 charset = charset,
                                 cursorclass = pymysql.cursors.DictCursor,
                                 unix_socket = unix_socket)
        except pymysql.err.OperationalError:
            print("Ошибка подключения к MySQL docker-контейнеру")

    #Выполнить команду, указанную в аргументе sql    
    def sqlexec(self, sql):
        print("\nВыполнение команды {} через транспорт MySQL".format(sql))
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
            self.connection.commit()
            result = cursor.fetchone()
            print("Результат выполнения команды: ", result)
        except Exception as value:
            print("Ошибка выполнения команды через транспорт MySQL.")
            print("Причина отказа выполнения команды: {}".format(value))
        else:
            return result

    def close(self):
        self.connection.close()
