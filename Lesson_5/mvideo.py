from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from pymongo import MongoClient
import time

chrome_options = Options()
chrome_options.add_argument('start-maximized')  # --headless
driver = webdriver.Chrome('./chromedriver.exe', options=chrome_options)
driver.implicitly_wait(1)
driver.get('https://www.mvideo.ru/')

# Ищем список категорий товаров.
goods_categories = driver.find_elements_by_xpath("//div[@data-init='ajax-category-carousel']")
goods_category = goods_categories[1]
# for goods_category in goods_categories:
category_name = goods_category.find_element_by_xpath(".//div[@class='h2 u-mb-0 u-ml-xs-20 u-font-normal']").text
print(f'Категория тофаров : {category_name}' )
# Динамически заполняем все товары на полке.
# нажимаем на кнопку до тех пор пока она не исчезнет.
actions = ActionChains(driver)
actions.move_to_element(goods_category)
actions.perform()

is_next_page = True
i = 0
while is_next_page:
    time.sleep(0.2)
    next_btn = goods_category.find_element_by_css_selector("a.next-btn.sel-hits-button-next")
    # выделяем наш элемент. чтобы он стал доступным для загрузки.
    actions.move_to_element(next_btn)
    actions.click()
    actions.perform()
    try:
        goods_category.find_element_by_css_selector("a.next-btn.sel-hits-button-next.disabled")
        print('Все страницы просмотрены')
        is_next_page = False
    except:
        i += 1
        print(i)

# Получаем информацию о товарах.
products = goods_category.find_elements_by_class_name("gallery-list-item")
products_list = []
for product in products:
    product_info = {}
    p = product.find_element_by_tag_name('a')
    product_href = p.get_attribute('href')
    product_name = p.get_attribute('data-track-label')
    price = product.find_element_by_class_name('c-pdp-price__current').text
    product_info['name'] = product_name
    product_info['price'] = price
    product_info['href'] = product_href
    products_list.append(product_info)

df = pd.DataFrame(products_list)
df.to_csv('mvideo.csv', index=False)

print('Записываем полученный результат в БД.')
client = MongoClient('localhost', 27017)
db = client['mvideo_goods']
db.mvideo_goods.delete_many({})
db.mvideo_goods.insert_many(products_list)

print('Программа завершена')
driver.quit()


