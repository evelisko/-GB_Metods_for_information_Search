import re

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs


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
            min_selary = re.findall(r'\d{1,8}', selary_array[1] + selary_array[2])[0]
        elif selary_array[0] == symbols[1]:  # до
            max_selary = re.findall(r'\d{1,8}', selary_array[1] + selary_array[2])[0]
        elif (len(selary_array) < 4):  # до
            max_selary = re.findall(r'\d{1,8}', selary_array[0] + selary_array[1])[0]
        else:  # -
            min_selary = re.findall(r'\d{1,8}', selary_array[0] + selary_array[1])[0]
            max_selary = re.findall(r'\d{1,8}', selary_array[2] + selary_array[3])[0]

    return [min_selary, max_selary, money_type]


header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'charset': 'utf-8'
}
main_link = 'https://izhevsk.hh.ru/search/vacancy?L_is_autosearch=false&area=113&clusters=true&enable_snippets=true'
text = 'C++ Developer'  # 'Machine+Learning+Engineer'
page = 0
vacancy = []
i = 0
is_next_page = True  # Флаг поназываюций что есть еще страницы.
# Выполняем переход на следующую страницу.
# Может существовать как минимум одна страница с запросом.
new_vacancy = 0
while is_next_page == True:
    response = requests.get(f'{main_link}&text={text}&page={page}', headers=header).text
    soup = bs(response, 'lxml')

    btn_next = soup.find('a', {'class': "HH-Pager-Controls-Next"})
    # print("", end="\r")
    if btn_next != None:
        # print(f'Cтраница {page + 1}')
        page += 1
    else:
        # print(f'Cтраница {page + 1}')
        is_next_page = False

    vacancy_block = soup.find('div', {'class': 'vacancy-serp'})
    divs = vacancy_block.findChildren(recursive=False)


    for vk in divs:
        vacancy_data = {}
        # print(i, end=" ")
        try:
            if vk.attrs['class'][0] == 'vacancy-serp-item':  # Проверка на то не являетс яли даггый тег рекламой.
                i += 1
                vacancy_name = vk.find('div', {'class': 'vacancy-serp-item__info'})
                if vacancy_name is not None:
                    vacancy_name = vacancy_name.getText()
                else:
                    print(f'{i} vacancy_name')
                # Ссылка на вакансию.
                vacancy_id = None
                vk_href = vk.find('a', {'class': 'bloko-link HH-LinkModifier'})
                if vk_href is not None:
                    vk_href = vk_href['href']
                    vacancy_id = re.findall(r'\d{1,8}', vk_href)[0]
                else:
                    print(f'{i} vk_href')
                # Нужно создать функцию для разбиения строки. на составляющие.
                min_selary, max_selary, money_type = None, None, None
                selary_txt = vk.find('div', {'class': 'vacancy-serp-item__sidebar'})
                if selary_txt is not None:
                    selary_txt = selary_txt.getText()
                    min_selary, max_selary, money_type = selary_analizer(selary_txt)
                else:
                    print(f'{i} selary_txt')
                # Название фирмы.
                vk_employer = vk.find('a', {'data-qa': "vacancy-serp__vacancy-employer"})
                if vk_employer is not None:
                    vk_employer = vk_employer.getText()
                else:
                    print(f'{i} vk_employer')
                vk_employer_id = vk.find('a', {'data-qa': "vacancy-serp__vacancy-employer"})
                if vk_employer_id is not None:
                    vk_employer_id = 'https://izhevsk.hh.ru' + vk_employer_id['href']
                else:
                    print(f'{i} vk_employer_id')
                # Город расположения.
                vk_location = vk.find('span', {'data-qa': "vacancy-serp__vacancy-address"})
                if vk_location is not None:
                    vk_location = vk_location.getText()
                else:
                    print(f'{i} vk_location')
                # Дата публикации.
                vacancy_date = vk.find('span', {'data-qa': "vacancy-serp__vacancy-date"})
                if vacancy_date is not None:
                    vacancy_date = vacancy_date.getText()
                else:
                    print(f'{i} vacancy_date')

                if min_selary is not None:
                    min_selary = float(min_selary)

                if max_selary is not None:
                    max_selary = float(max_selary)
                new_vacancy += 1

                if new_vacancy < i:
                    print(f'разница {new_vacancy} {i}')
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
                vacancy_data['vacancy_id'] = vacancy_id
                vacancy.append(vacancy_data)
        except Exception as ex:
            print("")
            print(f'{i}: Ошибка при анализе вакансии', ex)
        print("", end="\r")
        print(f'Найдено вакансий: {i}   Новых вакансий : {new_vacancy}', end=" ")
# print(f'Новых вакансий : {new_vacancy}')
print(f'Страниц :{page + 1}')
# print(f'Ошибок: {errors}' )
print(' ')
# pprint(vacancy)

# сохраняем полученный результат в csv файл.

df = pd.DataFrame(vacancy)

df.to_csv('HH_ML_Vacansies.csv', index=False)
