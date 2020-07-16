# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


def del_dublicate(self, args):
    s = []
    for i in args:
        if i == ', ' or i not in s:
            s.append(i)
    return s


def selary_analizer(self, selary_txt):  # возвращает массив содержащий значение зарбплаты.
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
    vacancy_data['connection_info'] = ' '.join(
        list(map(lambda x: x.replace('\xa0', ' '), self.del_dublicate(item['connection_info']))))
    # этот способ не сохраняет последовательность элементов в списке.
    vacancy_data['publication_date'] = item['publication_date'][1].replace('\xa0', ' ')
    # list(map(lambda x: x.replace('\xa0', ' '), vacancy['publication_date']))
    vacancy_data['skils'] = item['skils']

    vacancy_data['salary_min'], vacancy_data['salary_max'], vacancy_data['salary_currency'], \
    vacancy_data['salary_desc'] = self.selary_analizer(item['salary'])
    vacancy_data['experience'] = item['experience']

    collection.insert_one(vacancy_data)

    return vacancy_data


def get_charactercstic(item):
    charactercstic = {}

    return charactercstic


class DataBasePipeline:  # Складываемсчитанные с сайта данные в БД.
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.mongo_base = self.client.goods_db

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        goods_atr = {}
        goods_atr['name'] = item['name']
        goods_atr['parameters'] = item['parameters']
        goods_atr['price'] = item['price']
        goods_atr['characteristics'] = get_charactercstic(item['characteristics'])
        goods_atr['url'] = item['url']
        # '.join(list(map(lambda x: x.replace('\xa0', ' '), del_dublicate(item['connection_info']))))
        collection.insert_one(goods_atr)
        return goods_atr

    # -----------------
    # loader.add_xpath('name', "//h1[@class='header-2']/text()")
    # loader.add_xpath('parameters', "//uc-variants//span[@slot='axis']")  # -- параметры выбора.
    # # //uc-variants/uc-variant-card[@slot='variants']/a -- параметры. но, есть несколько разных категорий. из них нужно делать выбор.
    # # //uc-variants[2]/uc-variant-card[@slot='variants']/a -- выбор по индексам делать будем.
    # loader.add_xpath('price', "//uc-pdp-price-view[@class='primary-price']")  # - цена.
    # loader.add_xpath('characteristics', "//section[@id='nav-characteristics']//uc-pdp-section-layout//dl/div")
    # loader.add_value('url', response.url)
    # -----------------------

    def __del__(self):
        self.client.close()


########################################################################################################################
class GoodsParserPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['picture']:
            for img in item['picture']:
                try:
                    img_path = img
                    yield scrapy.Request(img_path, meta=item)
                except Exception as e:
                    print(e)

    # def file_path(self, request, response=None, info=None):
    #     item = request.meta
    #     return 'dir1/dir2/file.ext'

    def item_completed(self, results, item, info):
        if results:
            item['picture'] = [itm[1] for itm in results if itm[0]]
        return item
