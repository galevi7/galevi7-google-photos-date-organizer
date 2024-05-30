import os
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import keyboard
import piexif

# creating global immutable dictionaries of the months in case I accidentally try to change it

hebrew_months = {
    "בינו": "01",
    "בפבר": "02",
    "במרץ": "03",
    "באפר": "04",
    "במאי": "05",
    "ביוני": "06",
    "ביולי": "07",
    "באוג": "08",
    "בספט": "09",
    "באוק": "10",
    "בנוב": "11",
    "בדצמ": "12"
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

year_month_directory_dict = {}

duplicate_dates = {}

# TODO: function for setting direction or change some code so the user can pick the direction (older photos or new ones)

# TODO: consider adding feature of downloading in time window between dd/mm/yyyy-dd/mm/yyyy


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


def get_file_date_and_name(driver, language):
    """

    :param driver: google chrome driver
    :param language: the language the date is written.
    :return: file_date - the date and time the photo were taken.
             file_name -the name of the current photo in this format - YYYY_MM_DD HH:MM:SS.
    """

    # # Find the div element by XPath
    div_element = driver.find_element(By.XPATH, "//div[@aria-live='assertive']")

    # Extract the innerHTML of the div element
    date = div_element.get_attribute("innerHTML")

    # Split the text into an array by spaces
    date = date.replace('\u200F', '')
    date_as_array = date.split()
    date_as_array = [word.replace(',', '') for word in date_as_array]
    day = date_as_array[4]
    if language == "hebrew":
        month = hebrew_months.get(date_as_array[5].replace('׳', ""))
    else:
        month = english_months.get(date_as_array[5].replace('׳', ""))
    year = date_as_array[6]
    time = date_as_array[7]

    file_date = year + ":" + month + ":" + day + " " + time
    file_name = day + "_" + month + "_" + year + " " + time.replace(':', '_')

    return file_date, file_name


def check_file_name(name, directory_path):
    """
    Checks if this file is already exist (rare, but its happens)
    :param name: file name
    :param directory_path: the complete path of the directory the file should be in if he exists
    :return: original name if the file doesn't exist, modified name with counter of that date.
    """
    file_path = directory_path + "\\" + name + ".jpg"
    if os.path.isfile(file_path):
        same_date_counter = duplicate_dates.get(name, None)
        if same_date_counter is None:
            duplicate_dates[name] = 2
            name = name + "(1)"
        else:
            name = name + "(" + str(same_date_counter) + ")"
            duplicate_dates[name] = same_date_counter + 1
    return name


def save_image_as(name, directory_path, driver, element, is_new_month):
    actions = ActionChains(driver)
    actions.context_click(element).perform()
    time.sleep(0.7)
    keyboard.send('v')
    time.sleep(1)
    keyboard.write(name)
    if is_new_month:
        keyboard.send('alt+d')
        # input the right directory
        keyboard.write(directory_path)  # C:\Users\galev\OneDrive\Desktop
        time.sleep(0.3)
        keyboard.send('enter')
        time.sleep(1)
        for i in range(9):
            keyboard.send('tab')
            time.sleep(0.6)
        keyboard.send('enter')
    else:
        keyboard.send('enter')
    time.sleep(0.65)


def set_metadata(file_path, date_str):
    exif_dict = piexif.load(file_path)
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str.encode("utf-8")
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = date_str.encode("utf-8")
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_path)


def download_and_save_image(driver, Language, directory_path, Direction, current_directory):
    """
    The function unify and uses all the functions that we use for downloading the files, creating directories,
    getting the dates and etc, in the right order.
    :param driver: chrome driver
    :param Language: the Language of the driver (english/hebrew)
    :param directory_path: the main directory that all the sub-directories will be created in
    :param Direction: the direction of the next photo (older photos or newer).
    :param current_directory: the directory we saved in last time.
    """
    file_date, file_name = get_file_date_and_name(driver, Language)
    year = file_date[0:4]
    month = file_date[5:7]
    months_set = year_month_directory_dict.get(year, None)

    if months_set is None:
        year_month_directory_dict[year] = {month}
        directory_name = year + "." + month
        current_directory = make_directory(directory_path, directory_name)
        is_new_month = True

    elif not month in months_set:
        months_set.add(month)
        directory_name = year + "." + month
        current_directory = make_directory(directory_path, directory_name)
        is_new_month = True
    else:
        is_new_month = False

    element = driver.find_element('tag name', 'body')
    # checking if this date exist
    file_name = check_file_name(file_name, current_directory)

    save_image_as(file_name, current_directory, driver, element, is_new_month)
    time.sleep(0.3)
    set_metadata(current_directory + "\\" + file_name + ".jpg", file_date)
    time.sleep(0.5)
    move_to_next_photo(driver, Direction)
    time.sleep(0.5)
    return current_directory





def crawler(url, directory_path, download_all_photos=True, number_of_photos=10):
    # initializing parameters and the webdriver and unable google restriction to log in
    # (restriction due to identification of webdriver that runs through selenium)

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

    keyboard.write('galevi403')
    time.sleep(0.5)
    keyboard.send('enter')
    time.sleep(10)
    keyboard.write('Gal140921Tehila')
    time.sleep(0.5)
    keyboard.send('enter')
    time.sleep(0.5)

    # Waiting until the user correctly logged-in and letting the driver sleep and not overload the cpu.
    while driver.current_url != url:
        time.sleep(0.2)

    Language = get_language(driver, url)

    if Language == "english":
        Direction = "right"
    else:
        Direction = "left"

    current_directory = None

    # in case the user chooses to download all the photos from the photo he chose.
    if(download_all_photos):
        previous_url = url
        current_url = None
        while previous_url != current_url:
            previous_url = current_url
            current_directory = download_and_save_image(driver, Language, directory_path, Direction, current_directory)
            current_url = driver.current_url


    # in case that the user chose to download a certain number of photos.
    else:
        current_directory = None
        previous_url = url
        current_url = None
        for i in range(number_of_photos):

            if previous_url == current_url:
                break

            previous_url = current_url
            current_directory = download_and_save_image(driver, Language, directory_path, Direction, current_directory)
            current_url = driver.current_url


    driver.quit()


if __name__ == '__main__':
    path_str = "C:\\Users\\galev\\OneDrive\\Desktop\\Google Photos"
    crawler("https://photos.google.com/photo/AF1QipMRlIuPvTMqWv1LFN1IDrHwfhNA2-AOS_q6YGDu", path_str)

