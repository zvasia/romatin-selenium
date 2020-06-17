import sys
import argparse
import mysql.connector
from datetime import datetime

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def create_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-df', default='*') # date_from
    parser.add_argument('-dt', default='*') # date_to

    return parser


arguments_parser = create_argument_parser()
namespace = arguments_parser.parse_args(sys.argv[1:])

date_from = namespace.df
date_to = namespace.dt

# parse data
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument('blink-settings=imagesEnabled=false')
start_time = datetime.now()


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


driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

SEARCH_URL = 'https://www3.wipo.int/madrid/monitor/en'

PAGE_SIZE = 100

driver.get(SEARCH_URL)
driver.find_element_by_css_selector("a#advancedModeLink").click()
driver.find_element_by_css_selector("input#RD_input").send_keys(date_from + " TO " + date_to + Keys.ENTER)
wait_for_load('select#rowCount1')
driver.find_element_by_css_selector("select#rowCount1").click()
driver.find_element_by_css_selector("option[value='100']").click()
wait_for_load('div.pageCount')

page_counter = driver.find_element_by_css_selector("div.pageCount").text.split(' ')
total_pages = int(page_counter[1])
irn_list = []
for page in range(total_pages - 1):
    get_irns_on_page(irn_list)
    go_to_next_page()
get_irns_on_page(irn_list)
driver.quit()

f = open("irns.txt", "w+")
for num in irn_list:
    f.write(num + "\n")
f.close()


# compare with current database
config = {
    'user': 'root',
    'password': 'root',
    'port': '8889',
    'host': '127.0.0.1',
    'database': 'romarin',
    'raise_on_warnings': True,
}


def get_site_nums():
    f = open("irns.txt", "r")
    parsed_irns = f.read().split('\n')
    parsed_irns = filter(None, parsed_irns)
    f.close()
    return parsed_irns


def get_database_nums(start_date, end_date):
    link = mysql.connector.connect(**config)
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


site_nums = get_site_nums()
db_nums = get_database_nums(date_from, date_to)
site_nums_set = set(site_nums)
db_nums_set = set(db_nums)
diff = site_nums_set - db_nums_set


f = open("diff.txt", "w+")
for num in diff:
    f.write(num + "\n")
f.close()

