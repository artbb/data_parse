import re
from urllib.parse import urljoin

from scrapy.loader import ItemLoader
from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose

class AvitoLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_out = TakeFirst()
    adress_out = TakeFirst()
    parametrs_out = TakeFirst()
    author_out = TakeFirst()