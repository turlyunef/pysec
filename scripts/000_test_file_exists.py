#Получить содержимое файла:
file_content = instance.get_file("/home/env.json")
print("File content: ", file_content)

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

