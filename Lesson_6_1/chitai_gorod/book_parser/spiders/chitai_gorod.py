# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from chitai_gorod.book_parser.items import BookParserItem


class ChitaiGorodSpider(scrapy.Spider):
    name = 'chitai_gorod'
    allowed_domains = ['www.chitai-gorod.ru']

    def __init__(self, search):
        self.start_urls = [f'https://www.chitai-gorod.ru/search/result/?q={search}']

    def parse(self, response: HtmlResponse):
        # Ссылка на следующую страницу.
        next_page = None
        is_rigth_button = response.xpath("//div[@class='pagination']/a[@class='pagination-item']/i/text()").extract_first()[-1]
        if is_rigth_button == 'keyboard_arrow_right':
            next_page = response.xpath("//div[@class='pagination']/a[@class='pagination-item']/i/../@href").extract_first()
        books_links = response.xpath("//div[@class='product-card__info']/a/@href").extract()

        for link in books_links:
            yield response.follow(link, callback=self.chitai_gorod_parse)
        yield response.follow(next_page, callback=self.parse)  # Необходимо корректно завершить поиск когда страницы закончатсяения поиска

    def chitai_gorod_parse(self, response: HtmlResponse):
        book_data = {}
        price = []
        book_data['name'] = response.xpath("//h1/text()").extract_first()
        book_data['author'] = response.xpath("//a[@class='link product__author']/text()").extract_first()
        book_data['author_href'] = response.xpath("//a[@class='link product__author']/@href").extract_first()

        book_data['picture'] = response.xpath("//picture[@slot='pictures']/source[2]/@srcset").extract()  # - путь к картинкам.
        # goods_data['parameters'] = response.xpath("//uc-variants//span[@slot='axis']").extract()  # -- параметры выбора.[словарь].
        price.append(response.xpath("//uc-pdp-price-view[@class='primary-price']/span[@slot='price']/text()").extract_first())
        price.append(response.xpath("//uc-pdp-price-view[@class='primary-price']/span[@slot='currency']/text()").extract_first())
        price.append(response.xpath("//uc-pdp-price-view[@class='primary-price']/span[@slot='unit']/text()").extract_first())
        book_data['raiting'] = response.xpath("//div[@class='sp-summary-rating-value']/span[@itemprop='ratingValue']/text()").extract_first()
        book_data['reviewCount'] = response.xpath(
            "//div[@class='sp-summary-rating-description']/span[@itemprop='reviewCount']/text()").extract_first()
        book_data['price'] = price
        book_data['characteristics'] = response.xpath("//section[@id='nav-characteristics']//uc-pdp-section-layout//dl/div")

        book_data['url'] = response.url
        yield BookParserItem(book_data)
