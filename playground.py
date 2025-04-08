import time
import speedtest
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from photos_downloader import PhotosDownloader

if __name__ == '__main__':

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=he")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Initializing a list with two Useragents
    useragentarray = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    ]

    for i in range(len(useragentarray)):
        # Setting user agent iteratively as Chrome 108 and 107
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": useragentarray[i]})
        # print(driver.execute_script("return navigator.userAgent;"))

    time.sleep(0.5)

    driver.get("https://photos.google.com/trash/AF1QipPZMNBadDiTnbkWXCBKar5yC_uU1xpjqq48Dx3N")

    time.sleep(0.5)
    div_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/c-wiz/div[4]/c-wiz/div[1]/div[2]/div/span/div/div[1]/span/div").text
