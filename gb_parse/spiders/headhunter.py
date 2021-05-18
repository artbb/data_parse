"""
Источник https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113
вакансии удаленной работы.
Задача: Обойти с точки входа все вакансии и собрать след данные:
1. название вакансии
2. оклад (строкой от до или просто сумма)
3. Описание вакансии
4. ключевые навыки - в виде списка названий
5. ссылка на автора вакансии
Перейти на страницу автора вакансии,
собрать данные:
1. Название
2. сайт ссылка (если есть)
3. сферы деятельности (списком)
4. Описание
Обойти и собрать все вакансии данного автора.
"""
import scrapy
import re
import pymongo
from gb_parse.items import GbParseItem


class HhruSpider(scrapy.Spider):
	name = 'hhru'
	allowed_domains = ['hh.ru']
	start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

	#прохожу все страницы в вакансиях, передаю каждую страницу дальше в обработку
	def parse(self, response):
		pag_link = response.xpath('//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href')
		for p_link in pag_link:
			yield response.follow(p_link, callback = self.links_parse)

	#получаю страницы из пагинации, в каждой ищу ссылки на вакансии, захожу в них и передаю в обработку
	def links_parse(self, response):
		vac_links = response.xpath('//div[contains(@data-qa, "vacancy-serp__vacancy")]//a[@data-qa="vacancy-serp__vacancy-title"]/@href')
		for v_link in vac_links:
			yield response.follow(v_link, callback = self.vacancy_parse)

	#начинаю парсить каждую страницу
	def vacancy_parse(self, response):
		data_vac = {
			"title": response.xpath('//h1[@data-qa="vacancy-title"]/text()'),
			"salary": response.xpath('//p[@class="vacancy-salary"]/span/text()'),
			"description": response.xpath('//div[@data-qa="vacancy-description"]//text()'),
			"skills": response.xpath('//div[@class ="bloko-tag-list"]//div[contains(@data-qa, "skills-element")]/span[@data-qa="bloko-tag__text"]/text()'),
		"author": response.xpath('//a[@data-qa="vacancy-company-name"]/@href'),
		}
		#передаем данные в mongo
		mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
		db = mongo_client["test"]
		collection = db["hh_data"]
		collection.insert_one(data_vac)

	#берем страницу автора и передаем дальше в обработку
		for a_link in data_vac["author"]:
			yield response.follow(a_link, callback=self.author_parse)

	#парсинг страницы автора
	def author_parse(self, response):
		data_author = {
			"title": response.xpath('//span[@class="company-header-title-name"]/text()'),
			"site": response.xpath('//a[@class="g-user-content"]/@href'),
			"industry": [i for i in response.xpath('//div[@class="employer-sidebar-block"]//text()')],
			"description": response.xpath('//div[lass="g-user-content"]/text()')
		}

		#передаем данные в mongo
		mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
		db = mongo_client["test"]
		collection = db["hh_data"]
		collection.insert_one(data_author)