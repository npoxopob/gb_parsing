import os
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.autoyuola import AutoyoulaSpider
from gb_parse.spiders.instagram import InstagramSpider

if __name__ == "__main__":
    tags = ['python', 'programming']
    load_dotenv('.env')
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(InstagramSpider, login=os.getenv('USERNAME'), password=os.getenv('ENC_PASSWORD'), tags=tags)
    crawler_process.start()
