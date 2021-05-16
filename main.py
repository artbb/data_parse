from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.headhunter import HhruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule('gb_parse.settings') #импорт модуля settings
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(HhruSpider) #передаем class паука
    #убрал автоюлу
    crawler_process.start()

#    process.crawl(HhRuSpider, vacancy=vacancy)
#    process.crawl(SuperjobRuSpider, vacancy=vacancy)
