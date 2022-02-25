# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhRuSpider(scrapy.Spider):
    name = 'hh_ru'
    allowed_domains = ['hh.ru']
    # start_urls = ['http://hh.ru/']
    # start_urls = ['https://izhevsk.hh.ru/search/vacancy?L_is_autosearch=false&area=113&clusters=true&enable_snippets=true&text=C%2B%2B+Developer']
    start_urls = [
        'https://izhevsk.hh.ru/search/vacancy?clusters=true&enable_snippets=true&text=Embedded+developer&L_save_area=true&area=113&from=cluster_area&showClusters=true']

    # spider = FollowAllSpider(domain=domain)
    # spider.start_urls = ['http://google.com']


    def parse(self, response:HtmlResponse):
        # Ссылка на следующую страницу.
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        # Ссылка на страницу с вакансией.
        vacansy_links = response.css('a.bloko-link.HH-LinkModifier::attr(href)').extract()
        # Собираем все вакансии на странице
        for link in vacansy_links:
            yield response.follow(link, callback=self.vacansy_parse)

        yield response.follow(next_page, callback=self.parse)

    def vacansy_parse(self, response: HtmlResponse):
        vacancy_data = {}
        vacancy_data['name'] = response.css('h1::text').extract_first()
        vacancy_data['salary'] = response.xpath("//span[@class='bloko-header-2 bloko-header-2_lite']/text()").extract()
        vacancy_data['experience'] = response.xpath("//span[@data-qa = 'vacancy-experience']/text()").extract_first()
        vacancy_data['skils'] = response.xpath("//div[@class ='bloko-tag bloko-tag_inline']//text()").extract()
        vacancy_data['company_name'] = response.xpath("//a[@data-qa='vacancy-company-name']/*/text()").extract()
        vacancy_data['company_href'] = response.xpath("//a[@data-qa='vacancy-company-name']/@href").extract()
        vacancy_data['company_location'] = response.xpath("//p[@data-qa='vacancy-view-location']//text()").extract()
        # company_description =
        vacancy_data['publication_date'] = response.xpath("//p[@class='vacancy-creation-time']/text()").extract()
        vacancy_data['connection_info'] = response.xpath("//div[@class='vacancy-contacts__body']//text()").extract()
        # vacancy - title
        yield JobparserItem(vacancy_data)


    # def vacansy_parse(self, response:HtmlResponse):
    #     vacancy_data = {}
    #     name_vac = response.css('h1::text').extract_first()
    #     salary_vac = response.xpath("//span[@class='bloko-header-2 bloko-header-2_lite']/text()").extract()
    #     experience = response.xpath("//span[@data-qa = 'vacancy-experience']/text()").extract_first()
    #     skils = response.xpath("//div[@class ='bloko-tag bloko-tag_inline']//text()").extract()
    #     company_name = response.xpath("//a[@data-qa='vacancy-company-name']/*/text()").extract_first()
    #     company_href = response.xpath("//a[@data-qa='vacancy-company-name']/@href").extract()
    #     company_location = response.xpath("//p[@data-qa='vacancy-view-location']//text()").extract()
    #     # company_description =
    #     publication_date = response.xpath("//p[@class='vacancy-creation-time']/text()").extract()
    #     connection_info = response.xpath("//div[@class='vacancy-contacts__body']//text()").extract()
    #
    #  # vacancy - title
    #     yield JobparserItem(name=name_vac, salary=salary_vac)
    #
# span.bloko-tag__section.bloko-tag__section_text" data-qa="bloko-tag__text" style="" xpath="1">ASP.NET</span>