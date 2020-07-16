# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from goods_parser.items import GoodsParserItem


class LeroyMerlinSpider(scrapy.Spider):
    name = 'leroy_merlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        # Ссылка на следующую страницу.
        next_page = response.xpath("//div[@class='next-paginator-button-wrapper']/a/@href").extract_first()
        # Ссылки на страницы с вакансиями.
        goods_links = response.xpath(
            "//div[contains(@class,'plp-card-list-inner')]//div[@class='product-name']/a/@href").extract()
        # Собираем все вакансии на странице
        for link in goods_links:
            yield response.follow(link, callback=self.goods_parse)
        yield response.follow(next_page, callback=self.parse)  # Переход на следующую страницу.

    def goods_parse(self, response: HtmlResponse):
        goods_data = {}
        price = []
        goods_data['name'] = response.xpath("//h1[@class='header-2']/text()").extract_first()
        goods_data['picture'] = response.xpath("//picture[@slot='pictures']/source[2]/@srcset").extract_first()  # - путь к картинкам.
        # goods_data['parameters'] = response.xpath("//uc-variants//span[@slot='axis']").extract()  # -- параметры выбора.[словарь].
        price.append(response.xpath("//uc-pdp-price-view[@class='primary-price']/span[@slot='price']/text()").extract())
        price.append(response.xpath("//uc-pdp-price-view[@class='primary-price']/span[@slot='currency']/text()").extract())
        price.append(response.xpath("//uc-pdp-price-view[@class='primary-price']/span[@slot='unit']/text()").extract())
        goods_data['price'] = price
        goods_data['characteristics'] = response.xpath("//section[@id='nav-characteristics']//uc-pdp-section-layout//dl/div").extract()
        goods_data['url'] = response.url
        yield GoodsParserItem(goods_data)
        GoodsParserItem

    # def goods_parse(self, response: HtmlResponse):  # Парсинг конкретно вакансии
    #     vacancy_data = {}
    #     vacancy_data['name'] = response.css('h1::text').extract_first()
    #     vacancy_data['salary'] = response.xpath("//span[@class='bloko-header-2 bloko-header-2_lite']/text()").extract()
    #     vacancy_data['experience'] = response.xpath("//span[@data-qa = 'vacancy-experience']/text()").extract_first()
    #     vacancy_data['skils'] = response.xpath("//div[@class ='bloko-tag bloko-tag_inline']//text()").extract()
    #     vacancy_data['company_name'] = response.xpath("//a[@data-qa='vacancy-company-name']/*/text()").extract()
    #     vacancy_data['company_href'] = response.xpath("//a[@data-qa='vacancy-company-name']/@href").extract()
    #     vacancy_data['company_location'] = response.xpath("//p[@data-qa='vacancy-view-location']//text()").extract()
    #     # company_description =
    #     vacancy_data['publication_date'] = response.xpath("//p[@class='vacancy-creation-time']/text()").extract()
    #     vacancy_data['connection_info'] = response.xpath("//div[@class='vacancy-contacts__body']//text()").extract()
    #     # vacancy - title
    #     yield GoodsParserItem(vacancy_data)

# name = response.xpath("//h1/span/text()").extract_first()
# photos = response.xpath("//div[contains(@class,'gallery-img-wrapper')]/div/@data-url").extract()
# yield AvitoparserItem(name=name,photos=photos)

# //picture[@slot='pictures']/source[2]/@srcset - путь к картинкам.
#
# //h1[@class='header-2']/text() - название.
#
# //uc-variants//span[@slot='axis'] -- параметры выбора.
#
# //uc-variants/uc-variant-card[@slot='variants']/a -- параметры. но, есть несколько разных категорий. из них нужно делать выбор.
#
# //uc-variants[2]/uc-variant-card[@slot='variants']/a -- выбор по индексам делать будем.
#
# //uc-pdp-price-view[@class='primary-price'] - цена.
#
# //section[@id='nav-characteristics']//uc-pdp-section-layout//dl/div -- Характеристики.
