import sys
import argparse
import mysql.connector
import settings
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def wait_for_load(selector):
    delay = 30  # seconds
    try:
        element = WebDriverWait(driver, delay).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, selector)))
    except TimeoutException:
        print("Loading took too much time!")


def go_to_next_page():
    driver.find_element_by_css_selector("a[oldtitle='next page']").click()


def get_irns_on_page(list):
    wait_for_load("td[aria-describedby='gridForsearch_pane_IRN']")
    irn_on_page_list = driver.find_elements_by_css_selector("td[aria-describedby='gridForsearch_pane_IRN']")
    for irn in irn_on_page_list:
        list.append(irn.text)


def save_list_to_file(file_name, list):
    f = open(file_name, "w+")
    for num in list:
        f.write(num + "\n")
    f.close()


def get_site_nums():
    f = open("irns.txt", "r")
    parsed_irns = f.read().split('\n')
    parsed_irns = filter(None, parsed_irns)
    f.close()
    return parsed_irns


def get_database_nums(start_date, end_date):
    link = mysql.connector.connect(**settings.MYSQL_CONFIG)
    cursor = link.cursor()
    query = "SELECT INTREGN FROM TOSN WHERE (INTREGD BETWEEN '{start_date}' AND '{end_date}')"\
        .format(start_date=start_date, end_date=end_date)
    cursor.execute(query)
    tms_in_db = cursor.fetchall()
    trademarks_in_db = []
    for x in tms_in_db:
        trademarks_in_db.append(x[0])
    cursor.close()
    link.close()
    return trademarks_in_db


arguments_parser = argparse.ArgumentParser()
arguments_parser.add_argument('-df', default='*') # date_from
arguments_parser.add_argument('-dt', default='*') # date_to
arguments_parser.add_argument('-p', default='1')
namespace = arguments_parser.parse_args(sys.argv[1:])

date_from = namespace.df
date_to = namespace.dt
start_page = int(namespace.p)

# parse data
# driver options
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument('blink-settings=imagesEnabled=false')


driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.get(settings.SEARCH_URL)
driver.find_element_by_css_selector("a#advancedModeLink").click()
driver.find_element_by_css_selector("input#RD_input").send_keys(date_from + " TO " + date_to + Keys.ENTER)
wait_for_load('select#rowCount1')
driver.find_element_by_css_selector("select#rowCount1").click()
driver.find_element_by_css_selector("option[value='" + str(settings.PAGE_SIZE) + "']").click()
wait_for_load('div.pageCount')
current_page_num = int(driver.find_element_by_css_selector("input#skipValue1").get_attribute("value"))
current_page_object = driver.find_element_by_css_selector("input#skipValue1")

if current_page_num != start_page:
    current_page_object.clear()
    current_page_object.send_keys(str(start_page) + Keys.ENTER)
    wait_for_load('div.pageCount')

total_pages_element = driver.find_element_by_css_selector("div.pageCount").text.split(' ')
total_pages = int(total_pages_element[1])
irn_list = []
page_counter = 1
try:
    for page in range(start_page - 1, total_pages - 1):
        get_irns_on_page(irn_list)
        page_counter = page
        go_to_next_page()
    get_irns_on_page(irn_list)
except Exception:
    print("Parser stops with params: -df " + date_from + " -dt " + date_to + " -p " + str(page_counter))
finally:
    driver.quit()
    save_list_to_file("irns.txt", irn_list)


# compare with current database
site_nums = get_site_nums()
db_nums = get_database_nums(date_from, date_to)
site_nums_set = set(site_nums)
db_nums_set = set(db_nums)
diff = site_nums_set - db_nums_set

save_list_to_file("diff.txt", diff)

