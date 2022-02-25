import datetime
import re

import requests
from lxml import html
from pymongo import MongoClient

yandex_news = 'https://yandex.ru/news/?from=tabbar'
lenta_news = 'https://lenta.ru/'
mail_news = 'https://news.mail.ru/?from=menu'

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

mounths = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября',
           'декабря']


def mail_news_info(href):
    response = requests.get(href, headers=header)
    dom = html.fromstring(response.text)
    items = dom.xpath("//div[@class ='breadcrumbs breadcrumbs_article js-ago-wrapper']/*/span")

    date_time = items[0].xpath(".//span[@class='note__text breadcrumbs__text js-ago']/@datetime")[0]
    source = items[1].xpath(".//a[@class='link color_gray breadcrumbs__link']/@href")[0]
    return source, date_time


def lenta_time_date_converter(date_time_text):
    date_time = None
    try:
        date_time_text = date_time_text.replace(', ', '')
        tmp_array = date_time_text.strip(' ')
        tmp_array = tmp_array.split(' ')
        day_ = int(tmp_array[1])
        mounth_ = mounths.index(tmp_array[2]) + 1
        year_ = int(tmp_array[3])
        tmp_time = tmp_array[0].split(':')
        hour_ = int(tmp_time[0])
        minutes_ = int(tmp_time[1])
        date_time = datetime.datetime(year_, mounth_, day_, hour_, minutes_)
        # print(date_time)
    except Exception as ex:
        print(f'lenta_date_converter: {ex}')
    return date_time


def yandex_time_date_converter(date_time_text, is_yesterday):
    date_time = None
    try:
        tmp_time = date_time_text.split(':')
        hour_ = int(tmp_time[0].strip())
        minutes_ = int(tmp_time[1].strip())
        date_ = datetime.date.today()
        date_time = datetime.datetime(date_.year, date_.month, date_.day, hour_, minutes_)
        if is_yesterday:
            date_time = date_time - datetime.timedelta(1)
    except Exception as ex:
        print(f'yandex_date_converter: {ex}')
    return date_time


def mail_time_date_converter(date_time_text):
    date_time = None
    try:
        indT = date_time_text.index('T')
        ind_plus = date_time_text.index('+')
        date_ = date_time_text[0:indT]
        time_ = date_time_text[indT + 1:ind_plus]
        deltaTme_ = date_time_text[ind_plus + 1:]
        tmp_date = date_.split('-')
        year_ = int(tmp_date[0])
        mounth_ = int(tmp_date[1])
        day_ = int(tmp_date[2])

        tmp_time = time_.split(':')
        hour_ = int(tmp_time[0])
        minutes_ = int(tmp_time[1])
        seconds_ = int(tmp_time[2])

        tmp_time = deltaTme_.split(':')
        d_hour_ = int(tmp_time[0])
        d_minutes_ = int(tmp_time[1])

        date_time = datetime.datetime(year_, mounth_, day_, hour_, minutes_, seconds_)
        delta_time = datetime.timedelta(hours=d_hour_, minutes=d_minutes_)
        date_time = date_time + delta_time

    except Exception as ex:
        print(f'mail_date_converter: ex')
    return date_time


def request_to_mail_ru():
    news_list = []
    try:
        response = requests.get(mail_news, headers=header)
        dom = html.fromstring(response.text)
        items = dom.xpath("//ul[@class='list list_type_square list_half js-module']/li")
        for item in items:  # нужно еще отделно обработать заголовок новости.
            news = {}
            news_href = item.xpath("./a/@href")[0]
            if news_href.find('https://') == -1:
                news_href = 'https://news.mail.ru' + news_href
            news_name = item.xpath("./a/text()")
            news_source, date_time_text = mail_news_info(news_href)
            news['date'] = mail_time_date_converter(date_time_text)
            news['name'] = news_name[0].replace('\xa0', ' ')
            news['href'] = news_href
            news['source'] = news_source
            news_list.append(news)
    except Exception as ex:
        print(f'request_to_mail_ru {ex}')
    return (news_list)


# Получаем данные с сайта.
def request_to_lenta_ru():
    news_list = []
    try:
        response = requests.get(lenta_news, headers=header)
        dom = html.fromstring(response.text)

        items = dom.xpath("//section[@class='row b-top7-for-main js-top-seven']/div[@class='span4']/div")
        for item in items[1:-1]:  # нужно еще отделно обработать заголовок новости.
            news = {}
            news_href = 'https://lenta.ru' + item.xpath("./a/@href")[0]
            news_name = item.xpath("./a/text()")
            news_date = item.xpath("./a/time/@datetime")
            news['name'] = news_name[0].replace('\xa0', ' ')
            news['href'] = news_href
            news['date'] = lenta_time_date_converter(news_date[0])
            news['source'] = 'lenta.ru'
            news_list.append(news)
    except Exception as ex:
        print(f'request_to_lenta_ru {ex}')
    return (news_list)


def request_to_yandex():  # Берем новости из разряда "Интерессное"
    news_list = []
    try:
        response = requests.get(yandex_news, headers=header)
        dom = html.fromstring(response.text)

        categories = dom.xpath("//div[@class = 'page-content__cell']//a[contains(@class,'link link_theme_normal"
                               " rubric-label rubric-label_top_')]/text()")[5:]

        print(f'Виды категорий повостей на yandex.ru/news:')
        print(categories)
        index = categories.index('Интересное') + 2
        print(f'Индекс выбранной категории: {index}')
        items = dom.xpath(
            f"//div[@class = 'page-content__cell'][{index}]//table[@class='stories-set__items']//td[@class='stories-set__item']")
        for item in items:
            news = {}
            news_name = item.xpath(".//div[@class='story__topic']//h2[@class='story__title']/a/text()")
            news_source = item.xpath(".//div[@class='story__info']/div[@class='story__date']/text()")[0]
            news_href = item.xpath(".//div[@class='story__topic']//h2[@class='story__title']/a/@href")
            is_yesterday = False
            if news_source.find('вчера') != -1:
                news_source = news_source.replace('вчера', '')
                is_yesterday = True
            news_time = re.findall(r'\d{2}:\d{2}', news_source)[0]
            news_source = news_source.replace(news_time, '')
            news['date'] = yandex_time_date_converter(news_time, is_yesterday)
            news['name'] = news_name[0].replace('\xa0', ' ')
            news['href'] = 'https://yandex.ru' + news_href[0]
            news['source'] = news_source
            news_list.append(news)
    except Exception as ex:
        print(f'request_to_yandex {ex}')
    return (news_list)


lenta_news_list = request_to_lenta_ru()
print(f'Колличество новостей на lenta.ru : {len(lenta_news_list)}')
yandex_news_list = request_to_yandex()
print(f'Колличество новостей на yandex.ru/news : {len(yandex_news_list)}')
mail_news_list = request_to_mail_ru()
print(f'Колличество новостей на news/mail.ru : {len(mail_news_list)}')

# Записываем полученный результат в БД.
client = MongoClient('localhost', 27017)
db = client['yandex_news']
db = client['mail_news']
db = client['lenta_news']

# мы не ставим себе цели хранить все новости. вечно. поэтомы презаписываем новости актуальными
# при этом старые записи в таблицах подчищаются.
# перезаписываем повости.

db.yandex_news.delete_many({})
db.mail_news.delete_many({})
db.lenta_news.delete_many({})

db.yandex_news.insert_many(yandex_news_list)
db.mail_news.insert_many(mail_news_list)
db.lenta_news.insert_many(lenta_news_list)
