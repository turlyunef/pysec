#Прочитать файл:
file_content = instance.get_file_through_exec("/home/env.json")


#Обработать содержимое и выдать значение для статуса:
if file_content != None:
    status = 1
    response = "Файл существует"
else:
    status = 2
    response = "Файл отсутствует"

#Добавить запись в таблицу scandata:
data.add_control(int(script[0:3]), status, response, datetime_before)
