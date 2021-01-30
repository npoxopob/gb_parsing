import re
from urllib.parse import urljoin
import scrapy
import pymongo


def __get_author(self, response):
    resp = response.xpath('//body/script[contains(text(), "window.transitState = decodeURIComponent")]/text()')
    return urljoin("https://youla.ru/user/", re.findall(rec, resp))


class AutoyuolaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    css_query = {
        "brands": "div.TransportMainFilters_block__3etab a.blackLink",
        "pagination": "div.Paginator_block__2XAPy a.Paginator_button__u1e7D",
        "ads": "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu.blackLink",
    }

    rec = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")

    data_query = {
        "title": lambda resp: resp.css("div.AdvertCard_advertTitle__1S1Ak::text").get(),
        "price": lambda resp: float(resp.css('div.AdvertCard_price__3dDCr::text').get().replace("\u2009", '')),
        "year_out": lambda resp: resp.css(
            'div.AdvertSpecs_data__xK2Qx[data-target="advert-info-year"] a.blackLink::text').get(),
        "mileage": lambda resp: resp.css(
            'div.AdvertSpecs_data__xK2Qx[data-target="advert-info-mileage"]::text').get(),
        "body_type": lambda resp: resp.css(
            'div.AdvertSpecs_data__xK2Qx[data-target="advert-info-bodyType"] a.blackLink::text').get(),
        "transmission": lambda resp: resp.css(
            'div.AdvertSpecs_data__xK2Qx[data-target="advert-info-transmission"]::text').get(),
        "engine": lambda resp: resp.css(
            'div.AdvertSpecs_data__xK2Qx[data-target="advert-info-engineInfo"]::text').get(),
        "color": lambda resp: resp.css(
            'div.AdvertSpecs_data__xK2Qx[data-target="advert-info-color"]::text').get(),
        "drive_type": lambda resp: resp.css(
            'div.AdvertSpecs_data__xK2Qx[data-target="advert-info-driveType"]::text').get(),
        "engine_power": lambda resp: resp.css(
            'div.AdvertSpecs_data__xK2Qx[data-target="advert-info-enginePower"]::text').get(),
        "vin_code": lambda resp: resp.css(
            'div.AdvertSpecs_data__xK2Qx[data-target="advert-info-vinCode"]::text').get(),
        "is_custom": lambda resp: resp.css(
            'div.AdvertSpecs_data__xK2Qx[data-target="advert-info-isCustom"]::text').get(),
        "owners": lambda resp: resp.css(
            'div.AdvertSpecs_data__xK2Qx[data-target="advert-info-owners"]::text').get(),
        "description_full": lambda resp: resp.css(
            'div.AdvertCard_descriptionInner__KnuRi[data-target="advert-info-descriptionFull"]::text').get(),
        "author": lambda resp: urljoin("https://youla.ru/user/",
                                       re.findall(re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar"),
                                                  resp.xpath(
                                                      '//body/script[contains(text(), "window.transitState = decodeURIComponent")]/text()'
                                                  ).get())),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def parse(self, response, **kwargs):
        brands_links = response.css(self.css_query["brands"])
        yield from self.gen_task(response, brands_links, self.brand_parse)

    def brand_parse(self, response):
        # pagination_links = response.css(self.css_query["pagination"])
        # yield from self.gen_task(response, pagination_links, self.brand_parse)
        ads_links = response.css(self.css_query["ads"])
        yield from self.gen_task(response, ads_links, self.ads_parse)

    def ads_parse(self, response):
        data = {}
        for key, selector in self.data_query.items():
            try:
                data[key] = selector(response)
            except (ValueError, AttributeError):
                continue
        self.db_client['gb_parse'][self.name].insert_one(data)

    @staticmethod
    def gen_task(response, link_list, callback):
        for link in link_list:
            yield response.follow(link.attrib["href"], callback=callback)
