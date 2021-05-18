
"""
Источник https://www.avito.ru/krasnodar/kvartiry/prodam
Город можно сменить
задача обойти пагинацию и подразделы квартир в продаже.
Собрать данные:
URL
Title
Цена
Адрес (если доступен)
Параметры квартиры (блок под фото)
Ссылку на автора

Дополнительно но не обязательно вытащить телефон автора
"""
import scrapy
import re
import pymongo
from gb_parse.items import GbParseItem
from gb_parse.loaders import AvitoLoader


class Avito_Flat(scrapy.Spider):
	name = 'avitoflat'
	allowed_domains = ['avito.ru']
	start_urls = ['https://www.avito.ru/krasnodar/kvartiry/prodam']

	#прохожу все страницы в вакансиях, передаю каждую страницу дальше в обработку
	def parse(self, response):
		pag_link = response.xpath('//a[@class="pagination-page"]/@href')
		for p_link in pag_link:
			yield response.follow(p_link, callback = self.links_parse)

	#получаю страницы из пагинации, в каждой ищу ссылки на вакансии, захожу в них и передаю в обработку
	def links_parse(self, response):
		flat_links = response.xpath('//a[contains(@class, "iva-item-sliderLink")]/@href')
		for f_link in flat_links:
			yield response.follow(f_link, callback = self.flat_parse)

	#начинаю парсить каждую страницу
	def flat_parse(self, response):

		parametrs = []
		for itm in response.xpath('//li[@class="item-params-list-item"]').extract():
			itm1 = itm.replace('<li class="item-params-list-item"> <span class="item-params-label">', '')
			itm2 = itm1.replace('</span>', '')
			itm3 = itm2.replace('</li>', '')
			parametrs.append(itm3)


		try:
			author = response.xpath('//a[contains(@title, "Нажмите, чтобы перейти в профиль")]/@href').extract()[0]
		except:
			author = 'Автора нет'


		data_flat = {
			"URL": response.url,
			"Title": response.xpath('//span[@class="title-info-title-text"]/text()').extract(),
			"Price": int(re.findall('[0-9]+', re.findall('itemPrice\D+[0-9]+', response.xpath('//script[contains(text(),"itemPrice")]').extract()[0])[0])[0]),
			"Adress": response.xpath('//div[@itemprop="address"]//span/text()').extract(),
			"Parametrs": parametrs,
			"Author": author,

		}
		mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
		db = mongo_client["test"]
		collection = db["avito_data"]
		collection.insert_one(data_flat)