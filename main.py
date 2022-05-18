from selenium.webdriver.support.wait import WebDriverWait
from sh3ll import IS
import selenium.common.exceptions
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import loader
import pickle


url = ""
options = Options()
options.headless = False
app = IS(name="Quizlet-Bot", prefix="QBot>")


@app.command(name="url", help="Sets the url for the bot", category="set")
def set_url(ctx):
    global url
    url = str(ctx.parameters[0])
    print("~Set url to " + url + "\n")


@app.command(name="key", aliases=["answers", "k", "a"], help="Loads the answer key for the quizlet", category="load")
def load_key(ctx):
    if url == "":
        print("~Please set a url using 'set url __'")
        return

    key = loader.get_terms(url)
    print("-----------")
    for term in key:
        print(term + ": " + key[term])
    print("-----------\n")


@app.command(name="match", aliases=[], help="Automatically completes the match section for you.", progress=(1, 100))
def match(ctx):
    if url == "":
        print("~Please set a url using 'set url __'")
        return

    terms = loader.get_terms(url)
    ctx.progress_bar.end = 3 + len(terms)

    ctx.progress_bar.progress(1)
    print(ctx.progress_bar, end="")

    match_url = url[::-1][1:][url[::-1][1:].index("/"):][::-1] + "match/"

    driver = webdriver.Firefox(options=options)
    driver.get(match_url)

    for cookie in load_cookies():
        driver.add_cookie(cookie)

    ctx.progress_bar.progress(2)  # PROGRESS
    print("\r", ctx.progress_bar, end="")

    timeout = 10
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Start game')]")))
    except selenium.TimeoutException:
        print("Timed out waiting for page to load")

    driver.find_element(By.XPATH, "//span[contains(text(),'Start game')]").click()

    sleep(0.5)
    ctx.progress_bar.progress(2)  # PROGRESS
    print("\r", ctx.progress_bar, end="")

    for term in terms:
        print("\r", ctx.progress_bar, end="")
        definition = terms[term]

        try:
            t = driver.find_element(By.XPATH, f"//div[text()=\"{term}\"]")
            d = driver.find_element(By.XPATH, f"//div[text()=\"{definition}\"]")

            action_chains = ActionChains(driver)
            action_chains.drag_and_drop(t, d).perform()  # PROGRESS
            ctx.progress_bar.progress(2)
            print("\b" * len(str(ctx.progress_bar)), end="")
        except selenium.common.exceptions.NoSuchElementException:
            pass

    time = driver.find_element(By.CLASS_NAME, "MatchModeControls-currentTime").text
    print("\r" + "\b" * len(str(ctx.progress_bar)), end="")
    print("Finished in " + time + " seconds.")

    sleep(1.0)
    try:
        print(ctx.progress_bar)
        driver.close()
    except selenium.common.exceptions.WebDriverException:
        pass


@app.command(name="login", help="Lets you log in and save, so you can save your match results")
def login(ctx):
    driver = selenium.webdriver.Firefox()
    driver.get("https://quizlet.com")
    cont = input("Enter any key once you have signed in: ")
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
    driver.quit()


def load_cookies():
    return pickle.load(open("cookies.pkl", "rb"))

app.run()