import re
from urllib.parse import urljoin

from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from .items import AutoyuolaItem, HHVacancyItem


def get_author_id(item):
    re_str = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
    result = re.findall(re_str, item)
    return result


def get_author_url(item):
    base_url = "https://youla.ru/user/"
    return urljoin(base_url, item)


def clear_unicode(value):
    return value.replace("\u2009", "")


def in_float(value):
    try:
        return float(value)
    except ValueError:
        return None


def get_specification(item):
    tag = Selector(text=item)
    name = tag.xpath('//div[contains(@class, "AdvertSpecs_label")]/text()').get()
    value = tag.xpath('//div[contains(@class, "AdvertSpecs_data")]//text()').get()
    return {name: value}


def specifications_output(values):
    result = {}
    for itm in values:
        result.update(itm)
    return result


class AutoyuolaLoader(ItemLoader):
    default_item_class = AutoyuolaItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = MapCompose(clear_unicode, in_float)
    price_out = TakeFirst()
    author_in = MapCompose(get_author_id, get_author_url)
    author_out = TakeFirst()
    specifications_in = MapCompose(get_specification)
    specifications_out = specifications_output


class HHVacancyLoader(ItemLoader):
    default_item_class = HHVacancyItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    description_in = "".join
    description_out = TakeFirst()
    salary_in = "".join
    salary_out = TakeFirst()
