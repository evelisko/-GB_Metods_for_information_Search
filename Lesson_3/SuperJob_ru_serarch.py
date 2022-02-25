from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import json
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
        selary_txt = selary_txt.replace('/месяц', '')
        selary_array = selary_txt.split(' ')
        money_type = selary_array[-1].rstrip('.')

        if selary_array[0] == symbols[0]: # от
            min_selary = selary_array[1] + selary_array[2]
        elif (selary_array[0] == symbols[1]):  # до
            max_selary = selary_array[1] + selary_array[2]
        elif (len(symbols) < 4):  # до
            max_selary = selary_array[0] + selary_array[1]
        else:                                                       # -
            min_selary = selary_array[0] + selary_array[1]
            max_selary = selary_array[2] + selary_array[3]

    return [min_selary, max_selary, money_type]


header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'charset': 'utf-8'
}


main_link = 'https://russia.superjob.ru/vacancy/search/'
text = 'C%2B%2B%20Developer' #'Machine%20Learning%20Engineer'
page = 1
vacancy = []
is_next_page = True  # Флаг поназываюций что есть еще страницы.
# Выполняем переход на следующую страницу.
# Может существовать как минимум одна страница с запросом.

while (is_next_page == True):
    response = requests.get(f'{main_link}?keywords={text}&page={page}', headers=header).text

    soup = bs(response, 'lxml')

    btn_next = soup.findAll('span', {'class': "qTHqo _1mEoj _2h9me DYJ1Y _2FQ5q _2GT-y"})
    if 'Дальше' == btn_next[-1].getText():
        print(f'Cтраница {page}')
        page += 1
    else:
        print(f'Cтраница {page}')
        is_next_page = False

    vacancy_hrefs = soup.find('script',
                              {'type': "application/ld+json"}).string  # Преобразуем полученное значчение в  json.

    v_links = json.loads(vacancy_hrefs)
    v_link_list = []
    for v_link in v_links['itemListElement']:
        v_link_list.append(v_link['url'])


    # Последовательно загружаем сайты с описанием вакансии и считываем с него информацию.
    i = 0
    for v_link in v_link_list:
        i += 1
        print(i, end=" ")
        vacancy_data = {}
        try:
            v_response = requests.get(v_link, headers=header).text
            # print(v_response)
            v_soup = bs(v_response, 'lxml')
            vs = v_soup.find('div', {'class': '_3Qutk'})
            vsk = vs.find_next('div', {'class': '_3MVeX'})
            vacancy_name = vsk.contents[1].getText()
            # Ссылка на вакансию.
            vk_href = v_link
            selary_txt = vsk.contents[4].getText()
            # Город расположения.
            vk_location = vsk.contents[2].getText()

            vs2 = vs.find_next('div', {'class': '_3zucV undefined'})
            # Название фирмы.
            vk_employer_id = None
            vk_employer = vs2.find('a', {'class': 'icMQ_'})
            if vk_employer is not None:
                vk_employer_id = 'https://russia.superjob.ru' + vk_employer['href']
                vk_employer = vk_employer.getText()
            else:
                vk_employer = vs.find('span', {'class': '_3mfro _1hP6a _2JVkc _2VHxz'}).getText()

            min_selary, max_selary, money_type = selary_analizer(selary_txt)
            vacancy_data['name'] = vacancy_name
            vacancy_data['employer'] = vk_employer
            vacancy_data['location'] = vk_location
            vacancy_data['min_selary'] = min_selary
            vacancy_data['max_selary'] = max_selary
            vacancy_data['money_type'] = money_type
            # vacancy_data['publicatin_date'] = vacancy_date # не смог найти где дата публикации указана.
            vacancy_data['href'] = vk_href
            vacancy_data['employer_id'] = vk_employer_id
            vacancy_data['source'] = 'https://russia.superjob.ru'
            vacancy.append(vacancy_data)
        except Exception as ex:
            print("")
            print('Ошибка при анализе вакансии ', ex)

    print(' ')


# pprint(vacancy)

df = pd.DataFrame(vacancy)

df.to_csv('SJ_1C_Vacansies.csv', index=False)
