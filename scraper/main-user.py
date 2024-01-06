import pygsheets
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def open_gsheets(file_name):
    gdrive = pygsheets.authorize(service_file='credentials.json')
    sheet = gdrive.open(file_name)
    return sheet[0]

def get_user_list(gsheets):
    print("Fetching user list...")
    col = gsheets.get_col(17, include_tailing_empty=False)
    col_val = list(filter(None, col))

    col_lists = [eval(x) for x in col_val[1:]]
    user_list = [x[0][0] if x and x[0] else None for x in col_lists]
    all_users = list(set(user_list))

    return all_users

def get_scraped_user_list(gsheets):
    print("Fetching scraped user list...")
    col = gsheets.get_col(1, include_tailing_empty=False)
    col_val = list(filter(None, col))
    scraped_users = list(set(col_val[1:]))

    return scraped_users

def get_unscraped_user_list(all,scraped):
    print("Fetching unscraped user list...")
    all_users = get_user_list(open_gsheets(all))
    scraped_users = get_scraped_user_list(open_gsheets(scraped))
    unscraped_users = list(set(all_users) - set(scraped_users))

    return unscraped_users

def init_driver():
    driver = webdriver.Edge()

    return driver

def login(driver):

    login_url = 'https://www.parfumo.com/'
    driver.get(login_url)

    login_dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="login-btn"]'))
    )

    login_dropdown.click()

    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'username'))
    )
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'password'))
    )
    login_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/header/div[3]/div/form/div/button"))
    )

    username_input.send_keys() # Insert username here.
    password_input.send_keys() # Insert password here.

    login_button.click()

def init_get_i_have(driver,i_have_url,user):
    print("Fetching data for",user,"...")
    driver.get(i_have_url)
    driver.find_element(by='xpath', value='//*[@id="pf-form"]/div[1]/div[2]/a').click()

    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'war_list_item'))
        )
    except TimeoutException:
        pass

    try:
        perfume_divs = driver.find_elements(By.CLASS_NAME, value='war_list_item')
        i_have_perfumes = [perfume.text for perfume in perfume_divs]
        if not i_have_perfumes:
            i_have_perfumes = ""
    except Exception as e:
        i_have_perfumes = ""

    return i_have_perfumes

def get_i_have(driver,i_have_url,user):
    print("Fetching data for",user,"...")
    driver.get(i_have_url)

    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'war_list_item'))
        )
    except TimeoutException:
        pass

    try:
        perfume_divs = driver.find_elements(By.CLASS_NAME, value='war_list_item')
        i_have_perfumes = [perfume.text for perfume in perfume_divs]
        if not i_have_perfumes:
            i_have_perfumes = ""
    except Exception as e:
        i_have_perfumes = ""

    return i_have_perfumes

def get_i_had(driver,i_had_url):
    driver.get(i_had_url)

    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'war_list_item'))
        )
    except TimeoutException:
        pass

    try:
        perfume_divs = driver.find_elements(By.CLASS_NAME, value='war_list_item')
        i_had_perfumes = [perfume.text for perfume in perfume_divs]
        if not i_had_perfumes:
            i_had_perfumes = ""
    except Exception as e:
        i_had_perfumes = ""

    return i_had_perfumes

def get_wish_list(driver,wish_list_url):
    driver.get(wish_list_url)

    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'war_list_item'))
        )
    except TimeoutException:
        pass

    try:
        perfume_divs = driver.find_elements(By.CLASS_NAME, value='war_list_item')
        wish_list_perfumes = [perfume.text for perfume in perfume_divs]
        if not wish_list_perfumes:
            wish_list_perfumes = ""
    except Exception as e:
        wish_list_perfumes = ""

    return wish_list_perfumes

def get_watch_list(driver,watch_list_url):
    driver.get(watch_list_url)

    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'war_list_item'))
        )
    except TimeoutException:
        pass

    try:
        perfume_divs = driver.find_elements(By.CLASS_NAME, value='war_list_item')
        watch_list_perfumes = [perfume.text for perfume in perfume_divs]
        if not watch_list_perfumes:
            watch_list_perfumes = ""
    except Exception as e:
        watch_list_perfumes = ""

    return watch_list_perfumes

def get_tested(driver,tested_url):
    driver.get(tested_url)

    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'war_list_item'))
        )
    except TimeoutException:
        pass

    try:
        perfume_divs = driver.find_elements(By.CLASS_NAME, value='war_list_item')
        tested_perfumes = [perfume.text for perfume in perfume_divs]
        if not tested_perfumes:
            tested_perfumes = ""
    except Exception as e:
        tested_perfumes = ""

    return tested_perfumes

def init_crawl(user,driver,gsheets):
    i_have_url = 'https://www.parfumo.com/Users/'+user+'/Collection/I_have'
    i_had_url = 'https://www.parfumo.com/Users/'+user+'/Collection/I_had'
    wish_list_url = 'https://www.parfumo.com/Users/'+user+'/Collection/Wish_List'
    watch_list_url = 'https://www.parfumo.com/Users/'+user+'/Collection/Watch_List'
    tested_url = 'https://www.parfumo.com/Users/'+user+'/Collection/Tested'

    login(driver)
    i_have = init_get_i_have(driver,i_have_url,user)
    i_had = get_i_had(driver,i_had_url)
    wish_list = get_wish_list(driver,wish_list_url)
    watch_list = get_watch_list(driver,watch_list_url)
    tested = get_tested(driver,tested_url)

    row = [user,str(i_have[:199]),str(i_had[:199]),str(wish_list[:199]),str(watch_list[:199]),str(tested[:199])]

    gsheets.append_table(values=row, dimension='ROWS', overwrite=False)

    return row

def cont_crawl(user,driver,gsheets):
    i_have_url = 'https://www.parfumo.com/Users/'+user+'/Collection/I_have'
    i_had_url = 'https://www.parfumo.com/Users/'+user+'/Collection/I_had'
    wish_list_url = 'https://www.parfumo.com/Users/'+user+'/Collection/Wish_List'
    watch_list_url = 'https://www.parfumo.com/Users/'+user+'/Collection/Watch_List'
    tested_url = 'https://www.parfumo.com/Users/'+user+'/Collection/Tested'

    i_have = get_i_have(driver,i_have_url,user)
    i_had = get_i_had(driver,i_had_url)
    wish_list = get_wish_list(driver,wish_list_url)
    watch_list = get_watch_list(driver,watch_list_url)
    tested = get_tested(driver,tested_url)

    row = [user,str(i_have[:199]),str(i_had[:199]),str(wish_list[:199]),str(watch_list[:199]),str(tested[:199])]

    gsheets.append_table(values=row, dimension='ROWS', overwrite=False)

    return row

def main():
    unscraped_users = get_unscraped_user_list('parfumo-raw','parfumo-scrape-users') # GSheets for all users, GSheets for scraped users

    print(unscraped_users)

    if not unscraped_users:
        return

    gsheets = open_gsheets('parfumo-scrape-users') # GSheets for scraped users,
    driver = init_driver()
    init_crawl(unscraped_users[0],driver,gsheets)

    for i in unscraped_users[1:]:
        cont_crawl(i,driver,gsheets)

if __name__ == "__main__":
    main()