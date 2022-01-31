"""
    Примечание. Если идет поток ошибок, то скорее всего это Ошибка 429 Too Many Requests.
"""
from time import sleep

import openpyxl
import requests
from bs4 import BeautifulSoup


def connection(url):
    """
    Получаем документ
    Отключил проверку сертификатов из-за ошибок при подключении к сайту.
    """
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def suppliers_scrap(site):
    """ Собираем все наименования и сслыки на каждого поставщика """
    suppliers = {}
    try:
        for link in site.find('tbody').find_all('a'):
            suppliers[link.text.strip()] = link["href"]
    except AttributeError:
        print('Метод имеется и работает. В потоке вызывается ошибка.')
    finally:
        return suppliers


def supplier_data_scrap(site):
    """ Собираем все данные каждого поставщика """
    try:
        raw_table = site.find_all(class_='table table-striped')
        table = raw_table[0].find_all('tr') + raw_table[2].find_all('tr')
        hdr = [''.join([header.text for header in pg.find_all('th')]) for pg in table]
        bdy = [''.join([body.text.strip() for body in pg.find_all('td')]) for pg in table]
        data = dict(zip(hdr, bdy))
        return data
    except IndexError:
        print('О руководителе и организации. В большом потоке вызывает ошибку.')
    finally:
        pass


def supplier_full_address(site):
    try:
        raw_table = site.find_all(class_='table table-striped')
        address = raw_table[3].find_all('tr')
        hdr_address = [[header.text for header in addr.find_all('th')][:3] for addr in address]
        bdy_address = [[body.text.strip() for body in addr.find_all('td')][:3] for addr in address]
        data = dict(zip(hdr_address[0], bdy_address[1]))
        return data
    except IndexError:
        print('Адрес. В большом потоке вызывается ошибка.')
    finally:
        pass


def full_data(part_1, part_2):
    """ Объединяет два словаря с данными в один """
    try:
        return part_1 | part_2
    except TypeError:
        print("Полные данные. В большом потоке вызывается ошибка")
    finally:
        pass


def fill_xlsx_file(data, b_sheet, row):
    """ Заполняем таблицу данными """
    try:
        b_sheet[f'A{row}'].value = data["Наименование на рус. языке"]
        b_sheet[f'B{row}'].value = data["БИН участника"]
        b_sheet[f'C{row}'].value = data["ФИО"]
        b_sheet[f'D{row}'].value = data["ИИН"]
        b_sheet[f'E{row}'].value = data['Страна'].capitalize() + ", " + data["Полный адрес(рус)"]
    except TypeError:
        print("В большом потоке вызывается ошибка")
    finally:
        pass


records = 20
row_p = 2
book = openpyxl.Workbook()
sheet = book.active
sheet['A1'].value = 'Наименование организации'
sheet['B1'].value = 'БИН организации'
sheet['C1'].value = 'ФИО руководителя'
sheet['D1'].value = 'ИИН руководителя'
sheet['E1'].value = 'Полный адрес'
for pg in range(1, 23):
    page = connection(f"https://www.goszakup.gov.kz/ru/registry/rqc?count_record={records}&page={pg}")
    supplier_links = suppliers_scrap(page)
    print(len(supplier_links), pg)
    for supp_name, supp_link in supplier_links.items():
        print(supp_link, supp_name, sep='\t')
        sleep(1)    # для того чтобы не выходила Ошибка 429
        page = connection(supp_link)
        raw_data = supplier_data_scrap(page)
        full_address = supplier_full_address(page)
        fill_xlsx_file(full_data(raw_data, full_address), sheet, row_p)
        row_p += 1
    book.save('Hello.xlsx')

book.close()
