from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from goods_parser import settings
from goods_parser.spiders.leroy_merlin import LeroyMerlinSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroyMerlinSpider, search='Лампа эдисона')  # Параметры поискового запроса.
    process.start()
    print('Программа завершена.')
