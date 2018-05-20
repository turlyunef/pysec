#Выполнить команды:

try:
    instance2.sqlexec('''CREATE TABLE `users` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `email` varchar(255) COLLATE utf8_bin NOT NULL,
        `password` varchar(255) COLLATE utf8_bin NOT NULL,
        PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
            AUTO_INCREMENT=1 ;''')
except Exception as value:
    print("Ошибка создания таблицы users в БД: ", value)
    
try:    
    instance2.sqlexec("INSERT INTO `users` (`email`, `password`) VALUES ('webmaster@python.org', 'very-secret')")
except Exception as value:
    print("Ошибка добавления записи в таблицу users в БД", value)
try:
    file_content = instance2.sqlexec("SELECT `id`, `password` FROM `users` WHERE `email`='webmaster@python.org'")
except Exception as value:
    print("Ошибка чтения записи в таблице users в БД", value)

#Обработать содержимое и выдать значение для статуса:
if file_content != None:
    status = 1
    response = "Команда выполнена корректно"
else:
    status = 2
    response = "Команда не выполнена"

#Добавить запись в таблицу scandata:
data.add_control(int(script[0:3]), status, response, datetime_before)

#Добавить отметку об использовании транспорта MySQL в БД:
data.add_values_to_DB('transports (transport)', "\'MySQL\'")
