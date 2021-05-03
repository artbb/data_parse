import requests
from bs4 import BeautifulSoup
import datetime
import json
import pymongo

url = 'https://gb.ru/posts/'
url_base = 'https://gb.ru'

response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")

# распарсил и получил кол-во страниц со статьями:
pagination = soup.find('ul', attrs={"class": "gb__pagination"}).text
k = list(pagination)
m = k[k.index('…')+1:k.index('›')]
n = int(''.join(m))

# создал базу всех страниц со статьями:
urls = []
for k in range(1, n+1):
    urls.append(f"{url}?page={k}")

print(urls)

# создал базу всех ссылок на все статьи:
data_art = []
for ul in urls:
    response = requests.get(ul)
    soup = BeautifulSoup(response.text, "lxml")
    articles = soup.find_all(attrs={"class": "post-item__title"})
    for i in articles:
        data_art.append(f"{url_base}{i['href']}")

print(data_art)

# обрабатываю каждую статью сохраняя необходимые данные по заданию:
#data_all = {}
for st in data_art:
    st_response = requests.get(st)
    st_soup = BeautifulSoup(st_response.text, "lxml")

    title_text = st_soup.find("h1", attrs={"class": "blogpost-title"}).text

    img_text = st_soup.find(attrs={"class": "hidden", "itemprop": "image"}).text

    data_text = datetime.datetime.strptime(
        st_soup.find(attrs={"class": "text-md", "itemprop": "datePublished"}).get('datetime')[:10], '%Y-%m-%d')

    author_text = st_soup.find(attrs={"class": "text-lg", "itemprop": "author"}).text

    author_link = st_soup.find("a", attrs={"style": "text-decoration:none;"})['href']

    #парсим комментарии к статье (ключ-значение ФИО-body проблема с одинаковыми ФИО решил костылем через доп k_a)
    id_comment = st_soup.find('comments')['commentable-id']
    url_comment = requests.get(f'https://gb.ru/api/v2/comments?commentable_type=Post&commentable_id={id_comment}&order=desc').json()
    comments = {}
    k_a = []
    if len(url_comment)>0:
        url_comment = url_comment[0]
        def comments_json(url_comment):
            for k in url_comment.keys():
                if k == 'comment':
                    k_a.append(1)
                    comments.update({f"{url_comment[k]['user']['full_name']}_{k_a}": url_comment[k]['body']})
                    if len(url_comment[k]['children']) > 0:
                        url_len = url_comment[k]['children']
                        for el in url_len:
                            comments_json(el)

        comments_json(url_comment)

    data = {"url": st, "title": title_text, "img": img_text, "data": data_text, "author": author_text,
      "author link": author_link, "comment": comments}

    mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
    db = mongo_client["test"]
    collection = db["gb_posts"]
    collection.insert_one(data)

#проверено, в mongo все сохраняется и выводится, в т.ч. комментарии
#код конечно корявый и не ООП, надо дорабатывать, но в соответствии с заданием все парсится
