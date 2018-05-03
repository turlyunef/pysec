#Создать транспорт SSH:
instance = get_transport("SSH")
#Получить содержимое файла:
file_content = instance.get_file("/home/env.json")
#Обработать содержимое и выдать значение для статуса:
if file_content != None: status = 1
else: status = 2

#Добавить запись в таблицу scandata:
add_control(000, status)


