


# Выполнить вход в Instagram.
# пройти авторизацию. ВВести проль и логин. еще там какой-то пароль был.

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from insta_parser.spiders.instagram import InstagramSpider
from insta_parser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider)
    process.start()