"""
Обойти все марки авто и зайти на странички объявлений
Собрать след стуркутру и сохранить в БД Монго
Название объявления
Список фото объявления (ссылки)
Список характеристик
Описание объявления
ссылка на автора объявления
дополнительно попробуйте вытащить телефона
"""
import re
import scrapy
import pymongo

class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']



## для parse... получение через response css ссылок и их запуск
    def _get_follow(self, response, selector, callback):
        for link in response.css(selector):
            url = link.attrib['href']
            yield response.follow(url, callback=callback)
######

#### парсим стартовую страницу и находим ссылки всех брендов
    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response,
            ".TransportMainFilters_brandsList__2tIkv .ColumnItemList_column__5gjdt a.blackLink",
            self.brand_parse,
        )

## после того как нашли ссылку бренда парсим каждую страницу пагинации
    def brand_parse(self, response):
        yield from self._get_follow(
            response, ".Paginator_block__2XAPy a.Paginator_button__u1e7D", self.brand_parse
        )
        yield from self._get_follow(
            response,
            "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu.blackLink",
            self.car_parse,
        )
#       pag_link = response.css("Paginator_block__2XAPy a.Paginator_button__u1e7D")
#       for link in pag_link:
#           url = link.attrib['href']
#           yield response.follow(url, callback = self.brand_parse)
############################



## проходим внутри каждого бренда по всей пагинации, заходим на кажду страницу и сохраняем данные
    def car_parse(self, response):

        #поиск информации об авторе. зашит в скрипты, нужно их распарсить по декодеру
        for script in response.css("script"):
            try:
                if "window.transitState = decodeURIComponent" in script.css("::text").extract_first():
                    j = "phones" # телефон, name/ но что-то корректное не отображается
                    result = re.findall(j, script.css("::text").extract_first())
            except TypeError:
                'ошибка автор'


        data = {
            "url": response.url,
            "title": response.css("div.AdvertCard_advertTitle__1S1Ak::text").get(),

            #берем src у каждой картинки в _36e_r
            #(в документации альтернативно можно через .xpath('@src'))

            "photos": [pict.attrib.get("src") for pict in
                       response.css("figure.PhotoGallery_photo__36e_r img")],

            # идем в div __2FEH и далее внутрь в ljPcX где берем название х-ки (напр год) _2JHnS и
            #значение _xK2Qx
            #https://auto.youla.ru/advert/used/geely/emgrand_ec7/prv--360c216b634c07a7/
            #в некоторых объявлениях описание с ссылкой, в ха-ках несколько типов _xK2Qx (с ссылкой и без)

            "chars": [
                {"char_name": chars.css(".AdvertSpecs_label__2JHnS::text").extract_first(),
                 "char_value": chars.css(".AdvertSpecs_data__xK2Qx::text").extract_first()
                 or chars.css(".AdvertSpecs_data__xK2Qx a::text").extract_first()
                 } for chars in
                response.css("div.AdvertCard_specs__2FEHc .AdvertSpecs_row__ljPcX")
            ],

            #текст объявления полный в _KnuRi class="AdvertCard
            "descriptions": response.css(
                ".AdvertCard_descriptionInner__KnuRi::text"
            ).extract_first(),

            "author": result

        }
        mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
        db = mongo_client["test"]
        collection = db["youla_data"]
        collection.insert_one(data)


