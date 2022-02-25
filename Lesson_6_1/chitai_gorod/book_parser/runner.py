from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from chitai_gorod.book_parser import settings
from chitai_gorod.book_parser.spiders.chitai_gorod import ChitaiGorodSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(ChitaiGorodSpider, search='Машинное обучение')  # Параметры поискового запроса.
    process.start()
    print('Программа завершена.')