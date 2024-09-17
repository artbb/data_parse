"""
Задача организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы
результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные
сохраняются в Json вайлы, для каждой категории товаров должен быть создан отдельный файл и содержать
товары исключительно соответсвующие данной категории.
пример структуры данных для файла:
нейминг ключей можно делать отличным от примера

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""
import json
import time
from pathlib import Path
import requests
from urllib.parse import urlparse


class Parse5ka:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/89.0.4389.128 Safari/537.36"
    }
    __parse_time = 0

    def __init__(self, start_url, cat_nms, save_path, delay=1):
        self.start_url = start_url
        self.save_path = save_path
        self.cat_nms = cat_nms
        self.delay = delay

    def run(self):
        for product in self._parse(self.start_url):
            file_path = self.save_path.joinpath(f"{cat_nms}.json")
            self.save(product, file_path)

    def _get_response(self, url):
        next_time = self.__parse_time + self.delay
        url = url.replace(urlparse(url).netloc, urlparse(self.start_url).netloc)
        while True:
            if next_time > time.time():
                time.sleep(next_time - time.time())
            response = requests.get(url, headers=self.headers)
            self.__parse_time = time.time()
            if response.status_code == 200:
                return response
            time.sleep(self.delay)

    def _parse(self, url):
        while url:
            response = self._get_response(url)
            data: dict = response.json()
            url = data.get("next")
            for product in data.get("results", []):
                product.update({'cat_name': cat_nms})
                yield product

    def save(self, data: dict, save_path):
        save_path.write_text(json.dumps(data, ensure_ascii=False))


def get_save_dir(dir_name):
    dir_path = Path(__file__).parent.joinpath(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path

cat_req = requests.get('https://5ka.ru/api/v2/categories/').json()
for cat in cat_req:
    if __name__ == "__main__":
        cat_id = cat['parent_group_code']
        cat_nms = cat['parent_group_name']
        url = f'https://5ka.ru/api/v2/special_offers/?categories={cat_id}'
        products_dir = get_save_dir("products")
        parser = Parse5ka(url, cat_nms, products_dir)
        parser.run()


