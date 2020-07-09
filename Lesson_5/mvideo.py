import pprint as pprint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from lxml import html
from pymongo import MongoClient

chrome_options = Options()
chrome_options.add_argument('start-maximized')  # --headless
driver = webdriver.Chrome('./chromedriver.exe', options=chrome_options)
driver.implicitly_wait(1)
driver.get('https://www.mvideo.ru/')


# выбираем катер=горию  товар дня.


# Ищем список категорий товаров.
goods_categories = driver.find_elements_by_xpath("//div[@data-init='ajax-category-carousel']")
for goods_category in goods_categories:
    category_name = goods_category.find_element_by_xpath(".//div[@class='h2 u-mb-0 u-ml-xs-20 u-font-normal']").text
    print(f'Категория тофаров : {category_name}' )
    # Динамически заполняем все товары на полке.
    # нажимаем на кнопку до тех пор пока она не исчезнет.
    actions = ActionChains(driver)
    actions.move_to_element(goods_category)
    actions.perform()

    next_btn = goods_category.find_element_by_css_selector("a.next-btn.sel-hits-button-next")
    # выделяем наш элемент. чтобы он стал доступным для загрузки.
    actions.move_to_element(next_btn).click()
    actions.perform()
    # #
    # next_btn.click() #узнаем можн ли по ней кликнуть



# sml = driver.find_element_by_xpath(".//div[@class='gallery-layout sel-hits-block']")
# st=goods_categories.find_element_by_xpath("./div[@class='section']//a[@class='next-btn sel-hits-button-next']")
# next-btn sel-hits-button-next
# next-btn sel-hits-button-next disabled # Ищем вот этот элемент.
# class="section"
print('Программа завершена')
# driver.quit()
