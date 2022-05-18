from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time


def get_terms(url):
    options = Options()
    options.set_preference("javascript.enabled", False)  # Yoinks js from the site
    options.headless = True

    driver = webdriver.Firefox(options=options)

    driver.get(url)
    time.sleep(2.0)
    driver.execute_script("window.stop();")
    html = driver.page_source
    driver.close()

    soup = BeautifulSoup(html, 'html.parser')

    # TermText notranslate lang-en
    tmp = [element.text for element in soup.find_all("span", class_="TermText notranslate lang-en")]
    for element in soup.find_all("span", class_="TermText notranslate lang-math"):
        tmp.append(element.text)

    terms = {}
    for i in range(0, len(tmp) - 2, 2):
        terms[tmp[i]] = tmp[i + 1]

    return terms
