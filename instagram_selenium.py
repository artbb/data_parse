"""
Источник instgram
Задача авторизованным пользователем обойти список произвольных тегов,
Сохранить структуру Item олицетворяющую сам Tag (только информация о теге)
Сохранить структуру данных поста, Включая обход пагинации. (каждый пост как отдельный item, словарь внутри node)
Все структуры должны иметь след вид
date_parse (datetime) время когда произошло создание структуры
data - данные полученые от инстаграм
Скачать изображения всех постов и сохранить на диск
"""

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime


def parse_insta():
    url = "https://www.instagram.com/"

    #прокси когда совсем не пускал
    #options = webdriver.ChromeOptions()
    #options.add_argument('--proxy-server=socks5://' + '41.217.219.53:31398')

    browser = webdriver.Chrome()

    # функция подмены хедеров (когда инстаграм начал ограничивать время)
    def interceptor(request):
        del request.headers['Referer']  # удалем старые
        request.headers['Referer'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'

    # добавляем новые
    browser.request_interceptor = interceptor

    # запускаем браузер с новыми хедерами
    browser.get(url)

    #жду подгрузки всех форм для корректной атворизации
    wait = WebDriverWait(browser, 5)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "EPjEi")))

    u_name = browser.find_element_by_name("username")
    u_name.send_keys("artemiyb1")
    u_pwd = browser.find_element_by_name("password")
    u_pwd.send_keys("Bere3!k0v123")
    u_pwd.submit()

    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "olLwo")))
    # жду подгрузки страницы, чтобы авторизация не слетела

    xpath1 = '//div[contains(@class, "Igw0E")]/a[contains(@href, "hashtags")]'
    h1_url = browser.find_element_by_xpath(xpath1)
    print(h1_url.get_attribute('href'))
    h1_url.click()


    xpath2 = '//li[contains(@class, "LGb3y")]/a[contains(@href, "1")]' #здесь можно сделать выбор произвольного 0-10
    h2_url = browser.find_element_by_xpath(xpath2)
    print(h2_url.get_attribute('href'))
    h2_url.click()

    xpath3 = '//li[contains(@class, "LGb3y")]/a[contains(@href, "1-0")]' #здесь можно сделать выбор произвольного 0-0-10-10
    h3_url = browser.find_element_by_xpath(xpath3)
    print(h3_url.get_attribute('href'))
    h3_url.click()

    xpath4 = '//li[contains(@class, "LGb3y")]/a[contains(@href, "f")]' #здесь можно сделать выбор произвольного тега с любой буквой
    h4_url = browser.find_element_by_xpath(xpath4)
    print(h4_url.get_attribute('href'))
    h4_url.click()

    #итоговые данные парсинга
    instagram_parse = []
    pic_itm = 0  # вспомогательная переменная учета кол-ва картинок на странице

    # общая структура тега
    tag_str = {}
    #записываем время
    tag_str.update({'time_now': datetime.now()})
    # имя тега
    tag_name = browser.find_element_by_class_name("_7UhW9").text
    tag_str.update({'tag_name': tag_name})
    # логотип тега
    tag_logo = browser.find_element_by_class_name("_7A2D8").get_attribute('src')
    tag_str.update({'tag_logo': tag_logo})
    # кол-во публикаций
    tag_amount = browser.find_element_by_class_name("g47SY ").text
    tag_str.update({'tag_amount_el': tag_amount})

    # добавляем общую структуру тега в единый массив
    instagram_parse.append(tag_str)

#######################################################################
    #с 1по 9 - это лучшие, далее с 10 по 21 (12 штук) - новые, потом нужно нажать скролл и снова


    def parse_pict(): #функция парсинга выбранной картинки
        tag_picture = {}
        # добавляем автора картинки:
        tag_p_author = browser.find_element_by_class_name("sqdOP").text
        tag_picture.update({'picture_author': tag_p_author})

        # добавляем описание картинки
        tag_p_describe = browser.find_element_by_class_name('FFVAD').get_attribute('alt')
        tag_picture.update({'picture_describe': tag_p_describe})

        # добавляем кол-во лайков картинки (либо просмотров если видео по тегу vcOH2)
        # tag_p_likes = browser.find_element_by_class_name("zV_Nj").text
        # tag_picture.update({'picture_likes': tag_p_likes})

        # добавляем все данные по картинки в общий массив
        instagram_parse.append(tag_picture)
        xpath10 = '//div[contains(@class, "Igw0E")]/button[contains(@class, "wpO6b")]'
        browser.find_element_by_xpath(xpath10).click() #закрываем окно

    def pict_next(): #функция обхода всех картинок на странице
        xpath5 = '//div[contains(@class, "v1Nh3")]/a[contains(@href, "p")]'
        pic_url = browser.find_elements_by_xpath(xpath5)
        len_xpath5 = len(pic_url)
        pic_itm = 0

        while pic_itm < len_xpath5:
            pic_url = browser.find_elements_by_xpath(xpath5)
            pic_url[pic_itm].click()
            parse_pict()
            # идем на след картинку
            pic_itm+=1

    #скроллим страницу пока не будет конца и запускаем скрипты на исполнение
    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        pict_next()


parse_insta()