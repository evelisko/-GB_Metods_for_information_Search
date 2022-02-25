from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from pymongo import MongoClient

letters_list = []
chrome_options = Options()
chrome_options.add_argument('start-maximized')  # --headless
# chrome_options.add_argument('headless') #Режим без интерфейса
driver = webdriver.Chrome('./chromedriver.exe', options=chrome_options)
# driver.implicitly_wait(15)
driver.get('https://mail.ru/')

try:
    user_id_inbox = driver.find_element_by_id('mailbox:login')
    user_id_inbox.send_keys('study.ai_172@mail.ru')
    user_id_inbox.send_keys(Keys.ENTER)

    user_pass_inbox = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'mailbox:password')))
    user_pass_inbox.send_keys('NextPassword172')
    user_pass_inbox.send_keys(Keys.ENTER)
except Exception as  ex:
    print(f'ошибка при входе в почту:{ex}')
    driver.quit()
    exit()

mails_href = [] # список в который будем складывать ссылки на страницы наших писем.
page_count = 0
end_of_page = False
mail_id_list = []
last_letter = None
while end_of_page == False:
    letters = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'js-tooltip-direction_letter-bottom')))
    if letters[-1] != last_letter:
        for letter in letters:
            mail_id = letter.get_attribute('data-uidl-id')
            if mail_id not in mail_id_list:
                mail_id_list.append(mail_id)
                mail_href = letter.get_attribute('href')
                mails_href.append(mail_href)
        page_count += 1
        last_letter = letters[-1]
    actions = ActionChains(driver)
    actions.key_down(Keys.ARROW_DOWN)
    actions.perform()
    try: # Проверяем наличие этого элемента. если он опявился значит мы достигли конца страницы
        driver.find_element_by_class_name('list-letter-spinner')
        end_of_page = True
    except:
        end_of_page = False

print(f'Число сообщений: {len(mails_href)}')
print(page_count)

driver.implicitly_wait(10)

# Поочередно переходим на страницу каждого из писем и вытягиваем оттуда нужную нам информацию.
for index, href in enumerate(mails_href):
    try:
        letter_data = {}
        driver.get(href)

        letter = driver.find_element_by_class_name('layout__letter-content')
        letter_head = letter.find_element_by_tag_name('h2').text # Тема письма
        letter_author = driver.find_element_by_class_name('letter__author')
        author_name = letter_author.find_element_by_class_name('letter-contact')
        author_email = author_name.get_attribute('title')
        author_name = author_name.text
        letter_date = letter_author.find_element_by_class_name('letter__date').text
        letter_body = driver.find_element_by_class_name('letter-body')
        l_body = letter_body.find_elements_by_tag_name('span')
        if len(l_body) == 0:
            l_body.append(letter_body.find_element_by_tag_name('div'))
        letter_text = ''
        for i in l_body:
            t = ''
            try:
                t = i.text
            except:
                print('Ошибка ')
            letter_text += t

        letter_data['head'] = letter_head
        letter_data['author_name'] = author_name
        letter_data['author_email'] = author_email
        letter_data['date'] = letter_date
        letter_data['text'] = letter_text
        letters_list.append(letter_data)

        print("", end="\r")
        print(f'Писем прочитано: {index + 1}', end=" ")
    except:
        print(f'Ошибка')
print('')

df = pd.DataFrame(letters_list)
df.to_csv('lettres.csv', index=False)

print('Записываем полученный результат в БД.')
client = MongoClient('localhost', 27017)
db = client['lettres']
db.lettres.delete_many({})
db.lettres.insert_many(letters_list)

print('Программа завершена')
driver.quit()
