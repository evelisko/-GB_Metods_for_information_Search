# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter import ItemAdapter
from pymongo import MongoClient


# Здесь располагается все логика анализа полученных данных.
#
# class JobparserPipeline(object):
#     def process_item(self, item, spider):
#         return item



    # Получаем данные по вакнсиям.
class JobparserPipeline(object):

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.mongo_base = self.client.vacansy_db

    def del_dublicate(self,args):
        s = []
        for i in args:
            if i == ', ' or i not in s:
                s.append(i)
        return s

    def selary_analizer(self,selary_txt):  # возвращает массив содержащий значение зарбплаты.
        min_selary = None
        max_selary = None
        money_type = None
        selary_desc = None
        symbols = ['от', 'до']
        if selary_txt != [] and 'По договорённости' not in selary_txt and 'з/п не указана' not in selary_txt:  # 'проверяем наличие символов в строке'
            selary_array = list(map(lambda x: x.strip(' '), selary_txt))
            if selary_array[0] == symbols[0] and selary_array[2] == symbols[1]:
                min_selary = int(selary_array[1].replace('\xa0', ''))
                max_selary = int(selary_array[3].replace('\xa0', ''))
            elif selary_array[0] == symbols[0]:  # от
                min_selary = int(selary_array[1].replace('\xa0', ''))
            elif selary_array[0] == symbols[1]:  # до
                max_selary = int(selary_array[1].replace('\xa0', ''))
            else:  # до
                max_selary = int(selary_array[0].replace('\xa0', ''))

            ind = selary_array.index('')
            if ind > 0:
                money_type = selary_array[ind + 1]
            if selary_array[-1] != money_type:
                selary_desc = selary_array[-1]

        return [min_selary, max_selary, money_type, selary_desc]
        # Производим разбор вакансии, приводим данные в порядок.
    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        # if spider.name == 'hh_ru':
        vacancy_data = {}
        vacancy_data['name'] = item['name']
        vacancy_data['company_name'] = ''.join(item['company_name'])
        vacancy_data['company_href'] = f"https://izhevsk.hh.ru{item['company_href'][0]}"
        vacancy_data['company_location'] = ''.join(self.del_dublicate(item['company_location']))
        vacancy_data['connection_info'] = ' '.join(list(map(lambda x: x.replace('\xa0', ' '), self.del_dublicate(item['connection_info']))))
        # этот способ не сохраняет последовательность элементов в списке.
        vacancy_data['publication_date'] = item['publication_date'][1].replace('\xa0', ' ')
        # list(map(lambda x: x.replace('\xa0', ' '), vacancy['publication_date']))
        vacancy_data['skils'] = item['skils']

        vacancy_data['salary_min'], vacancy_data['salary_max'], vacancy_data['salary_currency'], \
                                                 vacancy_data['salary_desc'] = self.selary_analizer(item['salary'])
        vacancy_data['experience'] = item['experience']


        collection.insert_one(vacancy_data)

        return vacancy_data

    def __del__(self):
        self.client.close()

##########################################################################

# 2020-07-14 20:08:15 [scrapy.core.scraper] DEBUG: Scraped from <200 https://izhevsk.hh.ru/vacancy/36818329?query=Embedded%20developer>
# {'company_href': ['/employer/25'],
#  'company_location': ['Василеостровская',
#                       ', ',
#                       'Санкт-Петербург',
#                       ', 13-я линия В.О., 14'],
#  'company_name': 'T-Systems RUS',
#  'connection_info': [],
#  'experience': 'не требуется',
#  'name': 'Senior Frontend developer (MIF)',
#  'publication_date': ['Вакансия опубликована ',
#                       '15\xa0июня\xa02020',
#                       ' в ',
#                       'Санкт-Петербурге'],
#  'salary': ['з/п не указана'],
#  'skils': []}
##########################################################################
# {'company_href': ['/employer/76989'],
#  'company_location': ['Санкт-Петербург', ', ', 'Московская'],
#  'company_name': 'Арбат-Невский',
#  'connection_info': ['Кукушкина Елена Александровна',
#                      '+7\xa0(921)\xa03152354',
#                      '+7\xa0(921)\xa03152354',
#                      'e.kukushkina@arbat-nevskiy.ru'],
#  'experience': 'более 6 лет',
#  'name': 'Разработчик С++/инженер-программист С++',
#  'publication_date': ['Вакансия опубликована ',
#                       '15\xa0июня\xa02020',
#                       ' в ',
#                       'Санкт-Петербурге'],
#  'salary': ['от ', '120\xa0000', ' до ', '180\xa0000', ' ', 'руб.', ' на руки'],
#  'skils': ['Linux',
#            'SVN',
#            'Разработка ПО',
#            'Qt',
#            'SIP',
#            'C++',
#            'GUL',
#            'cmake',
#            'инженер-программист',
#            'программирование',
#            'Bash']}