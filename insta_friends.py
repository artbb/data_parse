"""
Источник Интсаграмм

На вход программе подяется 2 имени пользователя
Задача программы найти самую короткую цепоччку рукопожатий между этими пользователями

рукопожатием считаем только взаимоподписанных пользовтаелей
---------------------------------------------------------------------------------------
Алгоритм:
1. Ищем всех взаимных друзей пользователя 1 и 2 сохраняем в базу:
{1: [x1, x2, x3...]}
{2: [y1, y2, y3...]}

смотрим есть ли среди 1[] какой-либо из y.
если нет, то идем дальше:

у каждого друга сохраняем в базу его взаимных друзей (второе рукопожатие)
{
x1: [x11, x12, x13...],
x2: [x21, x22, x23...],
x3: [x31, x32, x33...],
}

И смотрим ли среди x1[], x2[] и т.д... какой-либо из y если нет, то идем дальше:

у каждого друга друга сохраняем в базу его взаимных друзей (третье рукопожатие)
{
x11:[x111, x112, x113],
x12:[x111, x112, x113],
x13:[x111, x112, x113],
x21:[x111, x112, x113],
x23:[x111, x112, x113],
x23:[x111, x112, x113],
.....
}

И смотрим ли среди  x11[], x12[],....какой-либо из y если нет, то идем дальше:

Если есть, то строим цепочку 2 - y3 - x13 - x1 - 1

"""
from random import randint

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import numpy as np


url = "https://www.instagram.com/garikkharlamov/"
browser = webdriver.Chrome()
browser.get(url)

#логинимся
xpath1 = '//button[contains(@class, "sqdOP")]'
h1_url = browser.find_element_by_xpath(xpath1)
h1_url.click()

u_name = browser.find_element_by_name("username")
u_name.send_keys("ЛОГИН")
u_pwd = browser.find_element_by_name("password")
u_pwd.send_keys("ПАРОЛЬ")
u_pwd.submit()

wait = WebDriverWait(browser, 5)
wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "olLwo")))

#отказываемся сохранить пароль
xpath2 = '//button[contains(@class, "sqdOP yWX7d")]'
h2_url = browser.find_element_by_xpath(xpath2)
h2_url.click()


wait = WebDriverWait(browser, 5)
wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "_4bSq7")))

#ищем подписки
h3_url = find_element_by_link_text("подписок")
h3_url.click()

names_following = []
names_followers = []
def following():  # функция обхода всех подписок
    xpath5 = '//a[contains(@class, "FPmhX")]'
    name_p = browser.find_elements_by_xpath(xpath5)
    len_xpath5 = len(name_p)
    name_itm = 0
    while name_itm < len_xpath5:
        name_p_name = browser.find_elements_by_xpath(xpath5).text
        names_following.append(name_p_name)
        name_itm += 1


#ищем подписчиков
h4_url = find_element_by_link_text("подписчиков")
h4_url.click()
def followers():  # функция обхода всех подписок
    xpath5 = '//a[contains(@class, "FPmhX")]'
    name_p = browser.find_elements_by_xpath(xpath5)
    len_xpath5 = len(name_p)
    name_itm = 0
    while name_itm < len_xpath5:
        name_p_name = browser.find_elements_by_xpath(xpath5).text
        names_followers.append(name_p_name)
        name_itm += 1

#сравниваем имена и сохраняем единый массив
id1 = np.intersect1d(names_following, names_followers)


################################################################################################
# Таким образом загружая двух пользователей получаем список их взаимных друзей

# Далее запуская эту же функцию мы можем проходить по их друзьям.


### Далее пример кода алгоритма графов поиска кратчайшего пути по списку смежностей

id1 = [49, 34] #это пример друзей пользователя 1
id2 = [4, 15, 5, 3] #это пример друзей пользователя 2

data_friends = []
list_friends = []
df_spam = []

def next_friend(): # это заглушка функции сбора друзей друга
    next_fr = [randint(0, 200) for _ in range(3)]
    return next_fr

def parse_data(data_itm): # это функция итогового сбора крайтчайших друзей
    parse_key = list(data_itm.keys())[0]
    df_spam.append(parse_key)
    parse_value = list(data_itm.values())[0]
    if isinstance(parse_value, dict):
        parse_data(parse_value)


def base_friend(idx): #базовая функция поиска кратчайшкго пути до второго пользователя
    for friend in id2:
        if len(data_friends) == 0:
            if friend in idx:
                data_friends.append(friend)
        else:
            break

# итерация 1
base_friend(id1)

# итерация 2 - база
if len(data_friends) == 0:
    for friend in id1:
        f_of_f = {friend: next_friend()}
        list_friends.append(f_of_f)

# итерация 2 - действие
for fr in list_friends:
    fr_of_fr = list(fr.values())[0]
    base_friend(fr_of_fr)
    if len(data_friends) == 1:
        list_friends.pop(-1)
        print(f'id1 --> {list(fr.keys())[0]} --> {"-->".join([str(i) for i in data_friends])}--> id2')

# итерация 3 - база
if len(data_friends) == 0:
    len_lst = len(list_friends)
    spam = 0
    while spam < len_lst:
        for fr in list(list_friends[spam].values())[0]:
            f_of_f = {list(list_friends[spam].keys())[0]: {fr: next_friend()}}
            list_friends.append(f_of_f)
        spam+=1

# итерация 3 - действие
spam = len(id1)
while spam < len(list_friends) and len(data_friends) == 0:
    fr_of_fr = list(list(list_friends[spam].values())[0].values())[0]
    base_friend(fr_of_fr)
    if len(data_friends) == 1:
        parse_data(list_friends[spam])
        df_spam.extend(data_friends)
        print(f'id1 --> {"-->".join([str(i) for i in df_spam])} --> id2')
    spam += 1

print(list_friends)



# Здесь расписаны функции итерации до 3 рукопожатия, их можно более компаткно автоматизировать до
# любого значения итерации
# более общий пример:
"""
id1 = [[49, 34]]
id2 = [84, 115, 99]
len_first_id = len(id1[0])

id1_friends = []

data_friend = []

enum = 0
spam_general = 0

def next_friend():
    next_fr = [randint(0, 500) for _ in range(3)]
    return next_fr

def parse_data(data_itm):
    parse_key = list(data_itm.keys())[0]
    data_friend.append(parse_key)
    parse_value = list(data_itm.values())[0]
    if isinstance(parse_value, dict):
        parse_data(parse_value)

def search_friends(idx):
    global enum, spam_general, len_first_id, data_friend
    for friend in id2:
        if friend in idx[enum]:
            if len(id1_friends) == 0:
                return print(f'id1 --> {friend} --> id2')
                break
            else:
                parse_data(id1_friends[-1])
                data_friend.append(friend)
                return print(f'id1 --> {"-->".join([str(i) for i in data_friend])} --> id2')
                break

    if len(idx[spam_general])>0 and len(id1_friends) <= len_first_id:
        enum += 1
        friend_of_friend = next_friend()
        idx.append(friend_of_friend)
        id1_friends.append({idx[spam_general][0]: friend_of_friend})
        idx[spam_general].pop(0)

    elif len(idx[spam_general])>0:
        enum += 1
        friend_of_friend = next_friend()
        idx.append(friend_of_friend)
        id1_friends.append({list(id1_friends[0].keys())[0]:{idx[spam_general][0]: friend_of_friend}})
        idx[spam_general].pop(0)
    else:
        spam_general+=1
        enum += 1
        friend_of_friend = next_friend()
        idx.append(friend_of_friend)
        if len(list(id1_friends[0].values())[0]) <=1:
            id1_friends.pop(0)
        id1_friends.append({list(id1_friends[0].keys())[0]:{idx[spam_general][0]: friend_of_friend}})
        idx[spam_general].pop(0)



    #print(id1)
    print(id1_friends)

    search_friends(id1)

search_friends(id1)
"""
