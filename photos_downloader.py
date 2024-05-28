import os
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import keyboard
import piexif
from PIL import Image

# creating global immutable dictionaries of the months in case I accidentally try to chang it

hebrew_months = {
    "בינו'": "01",
    "בפבר'": "02",
    "במרץ": "03",
    "באפר'": "04",
    "במאי": "05",
    "ביוני": "06",
    "ביולי": "07",
    "באוג'": "08",
    "בספט'": "09",
    "באוק'": "10",
    "בנוב'": "11",
    "בדצמ'": "12"
}

english_months = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sept": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12"
}



def make_directory(path, directory_name="Google Photos"):
    """
    :param path: complete path of the directory the user want to create that directory
    :param directory_name: the name of the directory the user want to call it.
    :return: If the directory been created properly.
    """

    # creating the complete path of the new directory
    complete_path = path + "\\" + directory_name

    if (not directory_exists(complete_path)):
        os.mkdir(fr"{complete_path}")
        print(f'The directory "{directory_name}" was created successfully in the chosen directory')
        return complete_path

    return "-1"


def directory_exists(directory_path):
    if os.path.isdir(directory_path):
        print(f"The directory '{directory_path}' exists.")
        return True
    return False


def get_language(driver, url):
    """
    Moving to the next image and the go back, only then the date are visible in the HTMLand we can determine if the
    dates are in hebrew or english.

    :param driver: chrome webdriver we're working on
    :param url: the url of the first photo we want to download
    :return: the language the profile is using.
    """
    element = driver.find_element('tag name', 'body')
    time.sleep(0.3)
    element.send_keys(Keys.ARROW_LEFT)
    time.sleep(0.5)
    if driver.current_url == url:
        element.send_keys(Keys.ARROW_RIGHT)
        time.sleep(0.5)
        element.send_keys(Keys.ARROW_LEFT)
        return "english"
    else:
        element.send_keys(Keys.ARROW_RIGHT)
        time.sleep(0.5)
        return "hebrew"


def move_to_next_photo(driver, direction):
    """
    moving to the next photo.
    :param driver: chrome webdriver
    :param direction: the direction of the next photo (according to the language)
    """
    element = driver.find_element('tag name', 'body')
    time.sleep(0.3)
    if direction == "right":
        element.send_keys(Keys.ARROW_RIGHT)
    else:
        element.send_keys(Keys.ARROW_LEFT)
    time.sleep(0.3)


def get_file_name(date, language):
    """

    :param date: the date of the photo as a String
    :param language: the language the date is written.
    :return: the name of the current photo in this format - YYYY.MM.DD, to be able to sort by name in the directory.
    """
    # Split the text into an array by spaces
    date = date.replace('\u200F', '')
    date_as_array = date.split()
    date_as_array = [word.replace(',', '') for word in date_as_array]
    day = date_as_array[4]
    if language == "hebrew":
        month = hebrew_months.get(date_as_array[5])
    else:
        month = english_months.get(date_as_array[5])
    year = date_as_array[6]
    time = date_as_array[7]
    file_name = year + ":" + month + ":" + day + " " + time
    return file_name


def save_image_as(name, directory_path, driver, element):
    actions = ActionChains(driver)
    actions.context_click(element).perform()

    keyboard.send('v')

    # Optional: handle the "Save As" dialog if necessary
    time.sleep(1)  # Adjust delay as needed for dialog to appear
    keyboard.write(name)
    keyboard.send('alt+d')
    # input the right directory
    keyboard.write(directory_path)  # C:\Users\galev\OneDrive\Desktop
    time.sleep(0.1)
    keyboard.send('enter')
    time.sleep(0.5)
    for i in range(9):
        keyboard.send('tab')
        time.sleep(0.1)
    keyboard.send('enter')
    time.sleep(0.1)


def set_metadata(file_path, date_str):
    exif_dict = piexif.load(file_path)
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str.encode("utf-8")
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = date_str.encode("utf-8")
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_path)


def crawler(url, download_all_photos=True, number_of_photos= 10):
    # initializing parameters and the webdriver and unable google restriction to log in (restriction due to identification of webdriver that runs through selenium)

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
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
        print(driver.execute_script("return navigator.userAgent;"))

    # entering the photo we got from the user.
    driver.get(url)

    # Waiting until the user correctly logged-in and letting the driver sleep and not overload the cpu.
    while driver.current_url != url:
        time.sleep(0.2)

    Language = get_language(driver, url)

    if Language == "english":
        Direction = "right"
    else:
        Direction = "left"


    # if(download_all_photos):
    #     while True:
    #         #TODO: make a break statment if after moving to the next photo we are still in the same url.
    #         pass
    #
    # else:
    #     for i in range(number_of_photos):
    #         #TODO: function that download and save it in the right directory.
    # # Find the div element by XPath
    div_element = driver.find_element(By.XPATH, "//div[@aria-live='assertive']")

    # Extract the innerHTML of the div element
    div_text = div_element.get_attribute("innerHTML")

    file_date = get_file_name(div_text, Language)
    file_name = file_date.replace(':', "_")
    element = driver.find_element('tag name', 'body')
    path_str = "C:\\Users\\galev\\OneDrive\\Desktop"
    save_image_as(file_name, path_str, driver, element)
    set_metadata(path_str+"\\"+file_name, file_date)
    move_to_next_photo(driver, Direction)

    # # Use pyautogui to select "Save Image As"
    # pyautogui.press('v')  # or adjust to the appropriate key for "Save Image As"
    #
    # # Optional: handle the "Save As" dialog if necessary
    # time.sleep(1)  # Adjust delay as needed for dialog to appear
    # pyautogui.typewrite("desired_filename.png")  # Change to your desired filename


    while True:
        time.sleep(0.5)


if __name__ == '__main__':
    crawler("https://photos.google.com/photo/AF1QipPG5bUkHMsthrvYUWJSTFsJ9WhFJY2GWYVsY0Kz")

