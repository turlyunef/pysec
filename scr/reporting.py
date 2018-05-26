from jinja2 import Template, Environment, PackageLoader, FileSystemLoader, select_autoescape
from collections import Counter
from datetime import datetime
from collections import namedtuple
from scr.transports import get_transport_settings, get_transport
from scr.Exceptions import ControlDataError, TransportError
from scr.DB import get_data_from_table, get_transport_info_list
 
#Создать отчет сканирования, на входе таблица "scandata", "control" и база данных data_base
def print_report():

    #Подгрузка содержимого таблиц из базы данных
    scandata = get_data_from_table("scandata")
    control = get_data_from_table("control")

    print("\nГенерация отчета сканирования")

    #Переменная окружения для модуля создания pdf-отчета
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    #Счетчик проверок:
    counter = Counter()

    #Пустые листы для создания namedtuple для дальнейшего рендеринга шаблона index.html:
    id_list = []
    status_list = []
    response_list = []
    datetime_from_run_list = []
    lasting_list = []

    descr_list = []
    request_list = []
    descr_short_list = []

    counter_key_list = []
    counter_value_list = []

    #Вычислить количество проверок по статусам:
    for (id_, status, response, datetime_from_run, lasting) in scandata:
        id_list.append(id_)
        status_list.append(status)
        response_list.append(response)
        datetime_from_run_list.append(datetime_from_run)
        lasting_list.append(lasting)
        
        counter[status] +=1

    #Общее количество проверок:
    sum_status = sum(counter.values()) 

    #Дата и время генерации отчета:
    date_time_report = str(datetime.now())[:-7]
    
    for (id_, descr, request, descr_short) in control:
        descr_list.append(descr)
        request_list.append(request)
        descr_short_list.append(descr_short)

    #Подсчет и вывод количества проверок по статусам:
    for key in counter:
        print("Проверок, завершившихся статусом %s: %s" % (key, counter[key]))
        counter_key_list.append(key)
        counter_value_list.append(counter[key])
        
    #Вывод количества проверок
    print  ("Общее количество проверок: ", sum_status)

    #namedtuple для рендеринга html (данные по результатам работы со scandata)
    Data = namedtuple('scandata','id_,status,response,datetime_from_run,lasting,descr,request,descr_short')
    data = [Data(id_, status, response, datetime_from_run, lasting, descr, request, descr_short) \
            for id_,status,response,datetime_from_run,lasting,descr,request,descr_short in zip(id_list, status_list, response_list,datetime_from_run_list,\
                                                                     lasting_list,descr_list, request_list, descr_short_list)]

    # Проверка, совпадает ли количество проверок со сгенерированным namedtuple Data
    # Может не совпадать, если в файле control.json нет всех описаний проверок для используемых в папке scripts
    if len(data)!=sum_status:
        raise ControlDataError()
      
    #namedtuple для рендеринга html (данные по результатам работы со счетчиком проверок)
    Counter_data = namedtuple('counter_data','counter_key,counter_value')
    counter_data = [Counter_data(counter_key,counter_value) for counter_key,counter_value in zip(counter_key_list,counter_value_list)]

    system_summary = "Не получена" #хранение информации о целевой системе для внесения в отчет
    try:
        #Создать или подгрузить транспорт SSH:
        instance_SSH = get_transport("SSH")

        #Получение информации о целевой системе для внесения в отчет:
        system_summary = str(instance_SSH.exec_("cat /etc/lsb-release"), encoding='utf8')
    except TransportError as value:
        print("Ошибка транспорта. Получение информации о целевой системе для внесения в отчет не выполнено по причине: ", value)
    except AttributeError as value:
        print("Ошибка транспорта. Получение информации о целевой системе для внесения в отчет не выполнено по причине: ", value)
    #Получение информации об используемых транспортах из БД, таблицы transport:
    transport_info_list = get_transport_info_list()
    
    #Рендеринг html

    try:
        tpl = env.get_template('index.html')
    except:
        print("Файл 'index.html' отсутствует в папке 'templates'")
    else:
        rendered_html = tpl.render(data = data, \
                                   date_time_report = date_time_report,\
                                   sum_status = sum_status,\
                                   counter_data = counter_data,\
                                   system_summary = system_summary,\
                                   transport_info = transport_info_list)
        
    #Создание PDF
    try:
        from weasyprint import HTML, CSS
        
    except:
        print("Ошибка использования библиотеки weasyprint, PDF-файл не создан. \nСм. отчет в HTML-файле \"Report.html\" в папке \"out\"")
        f = open('./out/Report.html', 'w', encoding='utf8')
        for index in rendered_html:
            f.write(index)
        f.close()
    else:
        whtml = HTML(string=rendered_html.encode('utf8')) 
        wcss = CSS(filename='./templates/style.css')
        whtml.write_pdf('./out/Report.pdf',stylesheets=[wcss])
