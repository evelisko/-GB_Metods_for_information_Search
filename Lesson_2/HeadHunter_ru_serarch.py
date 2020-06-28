from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import pandas as pd


def selary_analizer(selary_txt):  # возвращает массив содержащий значение зарбплаты.
    min_selary = None
    max_selary = None
    money_type = None
    symbols = ['от', 'до']
    # print(selary_txt)
    if selary_txt != '' and selary_txt != 'По договорённости':  # 'проверяем наличие символов в строке'
        selary_txt = selary_txt.replace('—\xa0', '')
        selary_txt = selary_txt.replace('-', ' ')
        selary_txt = selary_txt.replace('\xa0', ' ')
        selary_txt = selary_txt.replace('./месяц', '')
        selary_array = selary_txt.split(' ')
        money_type = selary_array[-1].rstrip('.')

        if selary_array[0] == symbols[0]:  # от
            min_selary = selary_array[1] + selary_array[2]
        elif selary_array[0] == symbols[1]:  # до
            max_selary = selary_array[1] + selary_array[2]
        elif (len(symbols) < 4):  # до
            max_selary = selary_array[0] + selary_array[1]
        else:  # -
            min_selary = selary_array[0] + selary_array[1]
            max_selary = selary_array[2] + selary_array[3]

    return [min_selary, max_selary, money_type]


header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'charset': 'utf-8'
}
main_link = 'https://izhevsk.hh.ru/search/vacancy?L_is_autosearch=false&area=113&clusters=true&enable_snippets=true'
text = 'C%2B%2B+Developer'  # 'Machine+Learning+Engineer'
page = 0
vacancy = []
is_next_page = True  # Флаг поназываюций что есть еще страницы.
# Выполняем переход на следующую страницу.
# Может существовать как минимум одна страница с запросом.

while is_next_page == True:
    response = requests.get(f'{main_link}&text={text}&page={page}', headers=header).text
    soup = bs(response, 'lxml')

    btn_next = soup.find('a', {'class': "HH-Pager-Controls-Next"})
    print("", end="\r")
    if btn_next != None:
        print(f'Cтраница {page + 1}')
        page += 1
    else:
        print(f'Cтраница {page + 1}')
        is_next_page = False

    vacancy_block = soup.find('div', {'class': 'vacancy-serp'})
    divs = vacancy_block.findChildren(recursive=False)

    i = 0
    for vk in divs:
        vacancy_data = {}
        i += 1
        print(i, end=" ")
        try:
            if vk.attrs['class'][0] != 'serp-special':  # Проверка на то не являетс яли даггый тег рекламой.
                vacancy_name = vk.find('div', {'class': 'vacancy-serp-item__info'}).getText()
                # Ссылка на вакансию.
                vk_href = vk.find('a', {'class': 'bloko-link HH-LinkModifier'})['href']
                # Нужно создать функцию для разбиения строки. на составляющие.
                selary_txt = vk.find('div', {'class': 'vacancy-serp-item__sidebar'}).getText()
                # Название фирмы.
                vk_employer = vk.find('a', {'data-qa': "vacancy-serp__vacancy-employer"}).getText()
                vk_employer_id = 'https://izhevsk.hh.ru' + vk.find('a', {'data-qa': "vacancy-serp__vacancy-employer"})[
                    'href']
                # Город расположения.
                vk_location = vk.find('span', {'data-qa': "vacancy-serp__vacancy-address"}).getText()
                # Дата публикации.
                vacancy_date = vk.find('span', {'data-qa': "vacancy-serp__vacancy-date"}).getText()

                min_selary, max_selary, money_type = selary_analizer(selary_txt)

                vacancy_data['name'] = vacancy_name
                vacancy_data['employer'] = vk_employer
                vacancy_data['location'] = vk_location
                vacancy_data['min_selary'] = min_selary
                vacancy_data['max_selary'] = max_selary
                vacancy_data['money_type'] = money_type
                # vacancy_data['publicatin_date'] = vacancy_date
                vacancy_data['href'] = vk_href
                vacancy_data['employer_id'] = vk_employer_id
                vacancy_data['source'] = 'https://hh.ru/'
                vacancy.append(vacancy_data)
        except Exception as ex:
            print("")
            print('Ошибка при анализе вакансии ', ex)
    print(' ')
# pprint(vacancy)

# сохраняем полученный результат в csv файл.

df = pd.DataFrame(vacancy)

df.to_csv('HH_ML_Vacansies.csv', index=False)

