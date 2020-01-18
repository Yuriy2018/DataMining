from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from avito_parse import settings
from avito_parse.spiders.avito import AvitoSpider

if __name__=='__main__':
    scr_settings = Settings()
    scr_settings.setmodule(settings)
    process = CrawlerProcess(settings=scr_settings)
    process.crawl(AvitoSpider)
    process.start()

