import json
import time
import typing
import datetime
import requests
from urllib.parse import urljoin
import bs4
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session, mapper


class GbBlogParse:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/90.0.4430.93 Safari/537.36"}
    __parse_time = 0

    def __init__(self, start_url, url_base="https://gb.ru", delay=0.1):
        self.start_url = start_url
        self.url_base = url_base
        self.delay = delay
        self.data_art = set()
        self.urls = []
        self.all_comments = []
        self.tags = []

    def _get_response(self, url):
        next_time = self.__parse_time + self.delay
        while True:
            if next_time > time.time():
                time.sleep(next_time - time.time())
            response = requests.get(url, headers=self.headers)
            self.__parse_time = time.time()
            if response.status_code == 200:
                return response
            time.sleep(self.delay)

    def get_soup(self, url):
        response = self._get_response(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        return soup

    def pagination(self):
        pagination = self.get_soup(self.start_url).find('ul', attrs={"class": "gb__pagination"}).text
        k = list(pagination)
        m = k[k.index('…') + 1:k.index('›')]
        n_pag = int(''.join(m))
        return n_pag

    def _all_tags(self):
        t = self.get_soup(self.start_url).find_all(attrs={"class": "posts-nav-btn"})
        for i in t:
            self.tags.append({"name":i.text, "tag_url":f"{self.url_base}{i['href']}"})


    def l_urls(self):
        for k in range(1, 1 + 1):  #!(1, self.pagination() + 1)! для ускорения тестирования только 1 страница, заменить
            self.urls.append(f"{self.start_url}?page={k}")

    def link_art(self):
        self.l_urls()
        for ul in self.urls:
            articles = self.get_soup(ul).find_all(attrs={"class": "post-item__title"})
            for i in articles:
                self.data_art.add(f"{self.url_base}{i['href']}") #

#Суть основного парсера и СОХРАНЕНИЯ В БАЗУ:
    # в отдельный set сохраняю все статьи со всех страниц пагинэйшена
    # далее прохожусь по каждой статье и собираю нужные данные
    # внутри есть функция для парсинга комментариев:
    # к каждой статье собираю все даные по комментам в требуемой форме и сохраняю в массив
    # ИТОГО: все данные передаю в sql базу на этапе обработки каждой статьи (создание структуры базы там же)
# РЕЗУЛЬТАТ: все передается и отрабатывается, данные сохраняются.
    # ПРОБЛЕМЫ:
    # 1. по вашему коду там якобы могут словари подгружаться в базу и все должно работать.
    # НО в документации я так и не нашел, чтобы можно было подгружать словари одним массивом.
    # в моем коде я загружаю отдельными данными
    # Просьба (1) описать ВОЗМОЖНОСТЬ загрузить данные в базу одним массивом - как это сделать на моем примере
    # 2. Не понятно как делать select и прочие запросы
    # хотел обработать tag чтобы не было ошибки с добавлением не уникальных (т.е. вначале select и проверка есть
    # ли такой уже в базе, если такого нет, то добавляем)
    # Просьба (2) написать на примере моего кода как можно такой select выпонить
    # 3. JOIN запросы
    # для связи comment to comment хотел сделать через join по столбцам id_comment и parent_id + root_comment_id
    # не знаю как. Читал про SessionContext или Flask, реализовать не удалось, думаю есть более простой алгоритм.
    # Просьба (3) на основе моего кода показать как это можно было сделать JOIN запросом применительно к комментариям
    # 4. Алхимия не работает.
    # На уроке было сказано, что под капотом SQLAlchemy вся алхимия зашита и все связи корректно добавляются.
    # у мееня связи не создались! Посмотрел итоговую созданную таблицу в Dbeaver - связей нет.
    # Просьба (4) прокомментировать почему связи не организовались.
    # (в ручную делать все понятно как, а что там под капотом, и почему не сработало в "автомате" - не могу понять)

    def data_parser(self):
        for st in self.data_art:
            st_soup = self.get_soup(st)

            title_text = st_soup.find("h1", attrs={"class": "blogpost-title"}).text
            img_text = st_soup.find(attrs={"class": "hidden", "itemprop": "image"}).text
            data_text = datetime.datetime.strptime(
                st_soup.find(attrs={"class": "text-md", "itemprop": "datePublished"}).get('datetime'), '%Y-%m-%dT%H:%M:%S%z')
            author_text = st_soup.find(attrs={"class": "text-lg", "itemprop": "author"}).text
            author_link = self.url_base+st_soup.find("a", attrs={"style": "text-decoration:none;"})['href']
            tags_text = [tag.text for tag in st_soup.find_all("a", attrs={"class": "small"})]

            id_comment_st = self.get_soup(st).find('comments')['commentable-id']
            json_comment = requests.get(
                    f'https://gb.ru/api/v2/comments?commentable_type=Post&commentable_id={id_comment_st}&order=desc').json()

            elk = json_comment
            idc = id_comment_st

            all_comments = []

            def comments_json(el, id):
                for kk in el:
                    if isinstance(kk, dict):
                        for k in kk.keys():
                            a_comment = {}
                            if k == 'comment':
                                a_comment.update({'id_article': id,  # ul параметр мегафункции парсера
                                                  'id_comment': kk[k]['id'],
                                                  'parent_id': kk[k]['parent_id'],
                                                  'root_comment_id': kk[k]['root_comment_id'],
                                                  'user name': kk[k]['user']['full_name'],
                                                  'body comment': kk[k]['body']
                                                  })
                                all_comments.append(a_comment)
                                if len(kk[k]['children']) > 0:
                                    i_len = [kk[k]['children']]
                                    for elem in i_len:
                                        comments_json(elem, idc)

            comments_json(el=elk, id=idc)

            data_all = {"url": st, "title": title_text, "img": img_text, "data": data_text, "author": author_text,
                    "author link": author_link, "tags": tags_text, "id_com_art": idc, "comments": all_comments}

            Base = declarative_base()

            class Post(Base):
                __tablename__ = "post"
                id = Column(Integer, primary_key=True)
                title = Column(String(250))
                url = Column(String)
                id_com_art = Column(Integer)
                author_id = Column(Integer, ForeignKey("author.id"))
                author = relationship("Author", backref="posts")
                def __init__(self, title, url, id_com_art):
                    self.title = title
                    self.url = url
                    self.id_com_art = id_com_art


            tag_post = Table(
                "tag_post",
                Base.metadata,
                Column("post_id", Integer, ForeignKey("post.id")),
                Column("tag_id", Integer, ForeignKey("tag.id")),
            )

            class Author(Base):
                __tablename__ = "author"
                id = Column(Integer, primary_key=True)
                a_url = Column(String)
                a_name = Column(String(350))
                def __init__(self, a_url, a_name):
                    self.a_url = a_url
                    self.a_name = a_name

            class Comments(Base):
                __tablename__ = "comments"
                id = Column(Integer, primary_key=True)
                id_comment = Column(Integer)
                id_article = Column(Integer)
                parent_id = Column(Integer)
                root_comment_id = Column(Integer)
                user_name = Column(String(350))
                body_comment = Column(String(350))
                def __init__(self, id_comment, id_article, parent_id, root_comment_id, user_name, body_comment):
                    self.id_comment = id_comment
                    self.id_article = id_article
                    self.parent_id = parent_id
                    self.root_comment_id = root_comment_id
                    self.user_name = user_name
                    self.body_comment = body_comment

            class Tag(Base):
                __tablename__ = "tag"
                id = Column(Integer, primary_key=True)
                t_url = Column(String)
                t_name = Column(String(350))
                posts = relationship(Post, secondary=tag_post, backref="tags")
                def __init__(self, t_url, t_name):
                    self.t_url = t_url
                    self.t_name = t_name



            Base.metadata.create_all(bind=engine)

            data_post = Post(title_text, st, idc)
            data_author = Author(author_link, author_text)

            session = Session(bind=engine)

            for ta in self.tags:
                t_url = ta['tag_url']
                t_name = ta['name']

                data_tags = Tag(t_url, t_name)
                session.add(data_tags)


            for com in all_comments:
                id_comment = com['id_comment']
                id_article = com['id_article']
                parent_id = com['parent_id']
                root_comment_id = com['root_comment_id']
                user_name = com['user name']
                body_comment = com['body comment']

                data_comments = Comments(id_comment, id_article, parent_id, root_comment_id, user_name, body_comment)
                session.add(data_comments)


            session.add(data_post)
            session.add(data_author)

            session.commit()
            session.close()



if __name__ == "__main__":
    parser = GbBlogParse("https://gb.ru/posts")
    engine = create_engine('sqlite:///gb_parse_posts.db')
    parser._all_tags()
    parser.link_art()
    parser.data_parser()



