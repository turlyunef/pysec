# фреймворк pysec
# 
# Запуск:
# Через "python main", в окне при запуске выводятся ключевые события, результат работы скриптов
# 
# Протестирован на Ubuntu 16 и Windows 10
#
# Результат сохраняется в папке "out", 
# если произошел конфликт библиотеки jinja2, то сохранится только html, если все ок, то сохранятся pdf в папке "out"
# -----------------------------------------------------
# Все модули хранятся в пакете scr
# Структура и назначение модулей в пакете scr:
# 
# DB.py - отвечает за работу с базой данных SQLite
#
# Exceptions.py - собственные классы исключений
#
# MySQL.py - отвечает за класс транспорта MySQL
# SSH.py  - отвечает за класс транспорта SSH
#
# reporting.py - отвечает за создание отчета (pdf и html)
#
# transports.py - создает и хранит инстансы транспортов в единственном экземпляре
#
#-------------------------------------------------------
#запуск MySQL сервера
#docker run --name some-mariadb -p 127.0.0.1:43306:3306 -e MYSQL_ROOT_PASSWORD=pwd123 -e MYSQL_USER=sauser -e MYSQL_PASSWORD=sapassword -e MYSQL_DATABASE=sadb --rm mariadb:latest
#
#
# 
#
#
#
#
#
#
