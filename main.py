from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

options = webdriver.ChromeOptions()


options.add_argument("--headless")
# options.add_argument("--disable-gpu")
options.add_argument('blink-settings=imagesEnabled=false')


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

date_from = '2019-03-01'
date_to = '2019-03-05'

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
