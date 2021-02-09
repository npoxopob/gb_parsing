import scrapy
from gb_parse.loaders import AutoyuolaLoader


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    css_query = {
        "brands": "div.TransportMainFilters_block__3etab a.blackLink",
        "pagination": "div.Paginator_block__2XAPy a.Paginator_button__u1e7D",
        "ads": "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu.blackLink",
    }

    data_xpath = {
        "title": "//div[@data-target='advert-title']/text()",
        "price": "//div[@data-target='advert-price']/text()",
        "images": "//figure[contains(@class, 'PhotoGallery_photo')]//img/@src",
        "description": "//div[@data-target='advert-info-descriptionFull']/text()",
        "specifications": '//h3[contains(text(), "Характеристики")]/../div/div[contains(@class, "AdvertSpecs_row")]',
        "author": '//body/script[contains(text(), "window.transitState = decodeURIComponent")]/text()',
    }

    def parse(self, response, **kwargs):
        brands_links = response.css(self.css_query["brands"])
        yield from self.gen_task(response, brands_links, self.brand_parse)

    def brand_parse(self, response):
        pagination_links = response.css(self.css_query["pagination"])
        yield from self.gen_task(response, pagination_links, self.brand_parse)
        ads_links = response.css(self.css_query["ads"])
        yield from self.gen_task(response, ads_links, self.ads_parse)

    def ads_parse(self, response):
        loader = AutoyuolaLoader(response=response)
        loader.add_value("url", response.url)

        for key, selector in self.data_xpath.items():
            loader.add_xpath(key, selector)

        yield loader.load_item()

    @staticmethod
    def gen_task(response, link_list, callback):
        for link in link_list:
            yield response.follow(link.attrib["href"], callback=callback)
