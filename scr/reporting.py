from jinja2 import Template, Environment, PackageLoader, FileSystemLoader, select_autoescape
from collections import Counter
from datetime import datetime
from collections import namedtuple

def print_report(scandata, control):
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    counter = Counter()
    id_list = []
    status_list = []
    response_list = []
    datetime_from_run_list = []
    lasting_list = []

    descr_list = []
    request_list = []
    descr_short_list = []

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

    #Вывод количества проверок по статусам:
    for key in counter:
        print("Проверок, завершившихся статусом %s: %s" % (key, counter[key]))
    #Вывод количества проверок
    print  ("Общее количество проверок: ", sum_status)

    


    Data = namedtuple('scandata','id_,status,response,datetime_from_run,lasting,descr,request,descr_short')
    data = [Data(id_, status, response, datetime_from_run, lasting,descr, request, descr_short) \
            for id_,status,response,datetime_from_run,lasting,descr,request,descr_short in zip(id_list, status_list, response_list,datetime_from_run_list,\
                                                                     lasting_list,descr_list, request_list, descr_short_list)]


    #Рендеринг html

    try:
        tpl = env.get_template('index.html')
    except:
        print("Файл 'index.html' отсутствует в папке 'templates'")
    else:
        rendered_html = tpl.render(data = data, date_time_report = date_time_report)
        
    #Создание PDF
    try:
        from weasyprint import HTML, CSS
        
    except:
        print("Ошибка weasyprint, PDF-файл не создан, см. HTML: Report.html")
        f = open('./out/Report.html', 'w', encoding='utf8')
        for index in rendered_html:
            f.write(index)
        f.close()
    else:
        whtml = HTML(string=rendered_html.encode('utf8')) 
        wcss = CSS(filename='./templates/style.css')
        whtml.write_pdf('./out/Report.pdf',stylesheets=[wcss])
