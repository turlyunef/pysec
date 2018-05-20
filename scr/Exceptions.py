# Класс исключения при отсутствии транспорта
class UnknownTransport(Exception): pass

# Класс исключения при остутвии комманды или файла
class TransportError(Exception): pass

# Класс исключения в случае неверной структуры в файле env.json
# или его отсутствия
class AuthError(TransportError): pass

# Класс исключения при неизвестной ошибке подключения
class UnknownTransportError(Exception): pass

# Класс исключения в случае ошибок подключения
class TransportConnectionError(Exception): pass

# Класс исключения при использовании номера неизвестного статуса
class UnknownStatus(Exception): pass

# Класс исключения при ошибке добавления записи функцией add_control
class AddControlError(Exception): pass

# Класс исключения при остутвии файла control.json
class ControlListError(Exception): pass
