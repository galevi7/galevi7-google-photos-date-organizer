import os
import shutil
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import keyboard
import piexif
import pyperclip

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

ready_files = {}


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

    if not directory_exists(complete_path):
        os.mkdir(fr"{complete_path}")
        return complete_path

    return "-1"


def directory_exists(directory_path):
    if os.path.isdir(directory_path):
        # print(f"The directory '{directory_path}' exists.")
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
    # driver.get('https://www.google.com')
    #TODO: check hebrew and english and return the language according to that.
    # Use JavaScript to retrieve the browser language
    language = driver.execute_script("return navigator.language || navigator.userLanguage;")
    print(f"Browser Language: {language}")
    if language[0:2] == "en":
        return "english"

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
    actions = ActionChains(driver)
    element = driver.find_element('tag name', 'body')
    time.sleep(0.3)
    actions.click(element).perform()
    time.sleep(0.3)
    if direction == "right":
        element.send_keys(Keys.ARROW_RIGHT)
    else:
        element.send_keys(Keys.ARROW_LEFT)
    time.sleep(0.3)


def delete_photo(driver):
    element = driver.find_element('tag name', 'body')
    element.click()
    time.sleep(0.5)
    element.send_keys(Keys.SHIFT+'#')
    time.sleep(2)
    driver.switch_to.active_element.send_keys(Keys.ENTER)
    time.sleep(2)


def get_file_size(file_details):
    size_start = file_details.find('(') + 1
    size_end = file_details.find(')', size_start)

    size_str = file_details[size_start:size_end].strip()  # Extract size string

    # Split size and unit
    size_value, size_unit = size_str.split(' ')
    size_value = float(size_value)
    size_unit = size_unit.upper()

    # Convert to MB if needed
    if size_unit == 'MB':
        return size_value
    elif size_unit == 'GB':
        return size_value * 1024
    else:
        return size_value / 1024



def is_video(driver):
    # Use single quotes for the XPATH string to avoid conflict with double quotes
    keyboard.send("i")
    time.sleep(0.8)
    parent_element = driver.find_element(By.XPATH, '/html/body/div[1]')

    # Get the innerHTML or text content of the parent element
    parent_content = parent_element.text
    size = 0
    keyboard.send("i")
    time.sleep(0.8)
    # print(parent_content)
    # Check if the last 3 characters of the name are ".mp" (which could be for mp4, mp3, etc.)
    if ".mp4" in parent_content:
        size = get_file_size(parent_content)
        return True, size
    return False, size


def get_file_date_and_name(driver, language):
    """

    :param driver: google chrome driver
    :param language: the language the date is written.
    :return: file_date - the date and time the photo were taken.
             file_name -the name of the current photo in this format - YYYY_MM_DD HH:MM:SS.
    """

    # Find the div element by XPath
    div_element = driver.find_element(By.XPATH, "//div[@aria-live='assertive']")

    # Extract the innerHTML of the div element
    date = div_element.get_attribute("innerHTML")

    # Split the text into an array by spaces
    date = date.replace('\u200F', '')
    date_as_array = date.split()
    date_as_array = [word.replace(',', '') for word in date_as_array]
    day = date_as_array[4]
    month = hebrew_months.get(date_as_array[5].replace('׳', ""))
    if month is None:
        month = english_months.get(date_as_array[5].replace('׳', ""))
    year = date_as_array[6]
    exact_time = date_as_array[7]

    file_date = year + ":" + month + ":" + day + " " + exact_time
    file_name = day + "_" + month + "_" + year + " " + exact_time.replace(':', '_')
    return file_date, file_name


def check_file_name(name, directory_path, is_video):
    """
    Checks if this file is already exist, it's not efficient because I'm assuming that someone can add the same picture
    not on the same session, besides there's shouldn't be many pictures that are taken at the same exact time!
    :param name: file name
    :param directory_path: the complete path of the directory the file should be in if he exists
    :return: original name if the file doesn't exist, modified name with counter of that date.
    """
    if is_video:
        suffix = ".mp4"
    else:
        suffix = ".jpg"
    file_path = directory_path + "\\" + name #+ suffix
    image_count = 0
    while os.path.isfile(file_path):
        image_count += 1
        file_path = directory_path + "\\" + name + f"({image_count})" #+ suffix
    if image_count == 0:
        return name
    return name + f"({image_count})"


def save_image_as(name, directory_path, driver, element):
    actions = ActionChains(driver)
    actions.context_click(element).perform()
    time.sleep(1)
    keyboard.send('v')
    time.sleep(2)
    keyboard.write(name)
    time.sleep(0.8)
    keyboard.send('alt+d')
    time.sleep(0.8)
    keyboard.send('ctrl+c')
    time.sleep(0.8)
    if pyperclip.paste() == directory_path:
        keyboard.send('enter')
        time.sleep(0.7)
        keyboard.send('enter')
        time.sleep(0.7)
    else:
    # input the right directory
        keyboard.write(directory_path)
        time.sleep(0.65)
        keyboard.send('enter')
        time.sleep(0.65)
        keyboard.send('enter')
        time.sleep(0.65)
        keyboard.send('enter')
        time.sleep(0.65)
        keyboard.send('enter')
        time.sleep(0.7)


def save_video_as(name, directory_path, driver, video_size):
    actions = ActionChains(driver)
    keyboard.send('shift+d')
    time.sleep(1)
    keyboard.send('ctrl+j')

    time.sleep(10)
    time.sleep(0.8)
    for i in range(5):
        keyboard.send('tab')
        time.sleep(2)
    keyboard.send('enter')
    time.sleep(2)
    keyboard.press_and_release('f2')
    time.sleep(2)
    keyboard.write(name)
    time.sleep(2)
    keyboard.send('enter')
    time.sleep(2)
    keyboard.send('ctrl+x')
    time.sleep(2)
    keyboard.send('alt+d')
    time.sleep(2)
    # input the right directory
    keyboard.write(directory_path)
    time.sleep(2)
    keyboard.send('enter')
    time.sleep(2)
    keyboard.send('ctrl+v')
    time.sleep(2)
    keyboard.send('alt+f4')
    time.sleep(2)
    keyboard.send('ctrl+w')
    time.sleep(2)


# setting the date of the picture to be the actual time the photo was taken.
def set_metadata(file_path, date_str):
    exif_dict = piexif.load(file_path)
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str.encode("utf-8")
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = date_str.encode("utf-8")
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_path)


def download_and_save_file(driver, language, directory_path, video_size, is_video=False):
    """
    The function unify and uses all the functions that we use for downloading the files, creating directories,
    getting the dates and etc, in the right order.
    :param video_size: video size in MB
    :param driver: chrome driver
    :param language: the Language of the driver (english/hebrew)
    :param directory_path: the main directory that all the sub-directories will be created in
    :param is_video: is the file is video
    :return: current_directory
    """
    file_date, file_name = get_file_date_and_name(driver, language)
    year = file_date[0:4]
    month = file_date[5:7]
    directory_name = year + "." + month
    current_directory = directory_path + "\\" + directory_name

    if not directory_exists(current_directory):
        os.mkdir(fr"{current_directory}")

    element = driver.find_element('tag name', 'body')
    # checking if this date exist
    file_name = check_file_name(file_name, current_directory)
    # saving according to file format
    if is_video:
        save_video_as(file_name, current_directory, driver, video_size)
    else:
        save_image_as(file_name, current_directory, driver, element)
    time.sleep(1)
    set_metadata(current_directory + "\\" + file_name + ".jpg", file_date)
    time.sleep(0.5)
    # if delete:
    #     delete_photo()
    #     time.sleep(0.35)
    # move_to_next_photo(driver, direction)
    # time.sleep(0.5)
    return current_directory


def rename_and_move(downloads_directory, original_name):
    file_tuple = ready_files.get(original_name)
    file_name = file_tuple[0]
    directory_path = file_tuple[1]
    is_video = file_tuple[2]
    file_date = file_tuple[3]
    if not directory_exists(directory_path):
        os.mkdir(fr"{directory_path}")
    file_name = check_file_name(file_name, directory_path, is_video)
    old_name_path = downloads_directory + "\\" + original_name
    if is_video:
        suffix = ".mp4"
    else:
        suffix = ".jpg"
    new_name_path = directory_path + "\\" + file_name + suffix
    shutil.move(old_name_path, new_name_path)
    # shutil.move(fr'{downloads_directory + file_name}', directory_path)
    set_metadata(new_name_path, file_date)


def download_and_collect_data(driver, language, directory_path):
    """
    The function unify and uses all the functions that we use for downloading the files, creating directories,
    getting the dates and etc, in the right order.
    :param driver: chrome driver
    :param language: the Language of the driver (english/hebrew)
    :param directory_path: the main directory that all the subdirectories will be created in
    :return: current_directory
    """
    element = driver.find_element('tag name', 'body')
    time.sleep(1)
    file_date, file_name = get_file_date_and_name(driver, language)
    year = file_date[0:4]
    month = file_date[5:7]
    directory_name = year + "." + month
    designated_directory_path = directory_path + "\\" + directory_name
    # checking if this date exist
    # file_name = check_file_name(file_name, designated_directory_path)
    # saving according to file format
    element.send_keys('i')
    time.sleep(0.8)
    parent_element = driver.find_element(By.XPATH, '/html/body/div[1]')
    # Get the innerHTML or text content of the parent element
    parent_content = parent_element.text
    element.send_keys(Keys.SHIFT + 'd')
    element.send_keys('i')
    # Check if the last 3 characters of the name are ".mp" (which could be for mp4, mp3, etc.)
    is_video = ".mp4" in parent_content
    parent_text = parent_content.split("\n")
    if is_video:
        for line in parent_text:
            if line[-3:] == "mp4":
                original_name = line
                break
    else:
        for line in parent_text:
            if line[-3:] == "jpg":
                original_name = line
                break

    ready_files[original_name] = (file_name, designated_directory_path, is_video, file_date)
    time.sleep(0.5)

    return original_name


def set_direction(language, older_photos):
    """
    A function that sets the direction we're scrolling the photos.
    :param language: the Language of the driver (english/hebrew)
    :param older_photos: is the user wants to download photos that were taken before that photo
    :return: the Direction.
    """
    if language == "hebrew":
        if older_photos:
            return "left", "right"
        else:
            return "right", "left"
    else:
        if older_photos:
            return "right", "left"
        else:
            return "left", "right"


def get_download_directory(driver, language):
    driver.get('chrome://settings/downloads')
    element = driver.find_element('tag name', 'settings-ui')
    time.sleep(1)
    shadow_root = get_shadow_root(driver, element)
    shadow_root_text = shadow_root.find_element(By.CSS_SELECTOR, "#main").text
    text_as_array = shadow_root_text.split('\n')
    if language == "english":
        path_index = text_as_array.index('Location') + 1
    else:
        path_index = text_as_array.index('מיקום') + 1
    return text_as_array[path_index]
    #TODO: finish and check this in hebrew and in english that I get the path right



def get_shadow_root(driver, element):
    return driver.execute_script('return arguments[0].shadowRoot', element)

def crawler(url, directory_path, older_photos=True, download_all_photos=True, number_of_photos=10, delete=False,
            username="", password=""):
    # initializing parameters and the webdriver and unable google restriction to log in
    # (restriction due to identification of webdriver that runs through selenium)

    options = webdriver.ChromeOptions()
    # options.add_argument("user-data-dir=C:\\Users\\galev\\AppData\\Local\\Google\\Chrome\\User Data")
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

    # entering the photo we got from the user.
    # download_directory = get_download_directory(driver)
    time.sleep(0.5)
    driver.get(url)

    keyboard.write(username)
    time.sleep(0.5)
    keyboard.send('enter')
    time.sleep(10)
    keyboard.write(password)
    time.sleep(0.5)
    keyboard.send('enter')
    time.sleep(15)
    # language = get_language(driver, url)
    download_directory = get_download_directory(driver, "hebrew")
    time.sleep(0.5)
    driver.get(url)
    # Waiting until the user correctly logged-in and letting the driver sleep and not overload the cpu.
    while driver.current_url != url:
        time.sleep(0.1)

    # Language = get_language(driver, url)

    # moving back and forth to reveal data
    Direction, opposite_direction = set_direction("hebrew", older_photos)
    move_to_next_photo(driver, Direction)
    move_to_next_photo(driver, opposite_direction)


    # in case the user chooses to download all the photos from the photo he chose.
    if download_all_photos:
        previous_url = url
        current_url = None
        while previous_url != current_url:
            previous_url = current_url
            is_file_video, video_size = is_video(driver)
            # if is_video(driver):
            #     move_to_next_photo(driver, Direction)
            #     time.sleep(1)
            #     current_url = driver.current_url
            #     continue

            # download_and_save_file(driver, Language, directory_path, video_size, is_file_video)
            download_and_collect_data(driver, "hebrew", directory_path)
            time.sleep(1)
            if delete:
                delete_photo(driver)
                time.sleep(2)
                if not older_photos:
                    previous_url = driver.current_url
                    time.sleep(2)
                    move_to_next_photo(driver, Direction)
                    time.sleep(2)

            current_url = driver.current_url

    # in case that the user chose to download a certain number of photos.
    else:
        previous_url = url
        current_url = None
        for i in range(number_of_photos):

            if previous_url == current_url:
                break

            previous_url = current_url
            # if is_video(driver):
            #     number_of_photos += 1
            #     move_to_next_photo(driver, Direction)
            #     time.sleep(1)
            #     current_url = driver.current_url
            #     continue

            # is_file_video, video_size = is_video(driver)
            # download_and_save_file(driver, Language, directory_path, video_size, is_file_video)
            original_name = download_and_collect_data(driver, "hebrew", directory_path)
            if delete:
                delete_photo(driver)
                if not older_photos:
                    previous_url = driver.current_url
                    move_to_next_photo(driver, Direction)
                    time.sleep(0.5)
            rename_and_move(download_directory, original_name)
            current_url = driver.current_url

    driver.quit()


if __name__ == '__main__':
    make_directory("C:\\Users\\galev\\OneDrive\\Desktop")
    path_str = "C:\\Users\\galev\\OneDrive\\Desktop\\Google Photos"
    crawler("https://photos.google.com/photo/AF1QipMGBthVpcukeZsSbjQzvZtCde9M8QvSQxmGKAH4", path_str,
            True, False, 3, True, 'galevi403', 'Gal140921Tehila')
