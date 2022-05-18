from sh3ll import IS
import selenium.common.exceptions
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import ActionChains
import loader


url = ""
options = Options()
options.set_preference("javascript.enabled", False)  # Yoinks js from the site
options.headless = False
app = IS(name="Quizlet Bot", prefix="QBot>")


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
    ctx.progress_bar.progress(2)  # PROGRESS
    print("\r", ctx.progress_bar, end="")
    sleep(1.0)
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
            action_chains.drag_and_drop(t, d).perform() # PROGRESS
            ctx.progress_bar.progress(2)
            print("\b" * len(str(ctx.progress_bar)), end="")
        except selenium.common.exceptions.NoSuchElementException:
            pass

    sleep(2.0)
    driver.close()
    print(ctx.progress_bar)


app.run()