from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hh_ru import HhRuSpider


if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhRuSpider)

  # здесь можно в парамерах задать параметры поиска по вакансиям.

  # process.crawl(SjruSpider)
    process.start() # Запуск основного процесса в программе ...
    print('Программа завершена.')
