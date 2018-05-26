from datetime import datetime
datetime_before = datetime.now()

import sys
sys.path.append('../')
import os
from scr.MySQL import MySQL
from scr.DB import DB, add_control
from scr.transports import get_transport


#Создать транспорт MySQL:
instance = get_transport("MySQL")


#Выполнить команды:

instance.sqlexec('''CREATE TABLE `users` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `email` varchar(255) COLLATE utf8_bin NOT NULL,
    `password` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
        AUTO_INCREMENT=1 ;''')

instance.sqlexec("INSERT INTO `users` (`email`, `password`) VALUES ('webmaster@python.org', 'very-secret')")

file_content = instance.sqlexec("SELECT `id`, `password` FROM `users` WHERE `email`='webmaster@python.org'")

#Обработать содержимое и выдать значение для статуса:
if file_content != None:
    status = 1
    response = "Команда выполнена корректно"
else:
    status = 2
    response = "Команда не выполнена"

#Добавить запись в таблицу scandata:
name_module = os.path.basename(__file__)
id_ = (name_module.split("_"))[0]
add_control(int(id_), status, response, datetime_before)

