#Прочитать файл:
file_content = instance.get_file_through_exec("/home/en2v.json")


#Обработать содержимое и выдать значение для статуса:
if file_content != None:
    status = 1
    response = "Файл существует"
else:
    status = 2
    response = "Файл отсутствует"

#Добавить запись в таблицу scandata:
data.add_control(int(script[0:3]), status, response, datetime_before)

#Добавить отметку об использовании транспорта SSH в БД:
data.add_values_to_DB('transports (transport)', "\'SSH\'")
