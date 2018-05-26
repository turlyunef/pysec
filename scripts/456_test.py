from datetime import datetime
datetime_before = datetime.now()

import sys
sys.path.append('../')
import os
from scr.SSH import SSH
from scr.DB import DB, add_control
from scr.transports import get_transport

#Создать или подгрузить транспорт SSH:
instance = get_transport("SSH")

#Прочитать файл:
file_content = instance.get_file_through_exec("/home/enErrorv.json")

#Обработать содержимое и выдать значение для статуса:
if file_content != None:
    status = 1
    response = "Файл существует"
else:
    status = 2
    response = "Файл отсутствует"

#Добавить запись в таблицу scandata:
name_module = os.path.basename(__file__)
id_ = (name_module.split("_"))[0]
add_control(int(id_), status, response, datetime_before)
