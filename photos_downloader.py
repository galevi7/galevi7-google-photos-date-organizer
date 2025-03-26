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
import multiprocessing


###### global parameteres for general usage ######


class PhotosDownloader:

    def __init__(self, url, directory_path, older_photos=True, download_all_photos=True,
                 number_of_photos=5, delete=False):
        self.url = url
        self.directory_path = directory_path
        self.older_photos = older_photos
        self.download_all_photos = download_all_photos
        self.number_of_photos = number_of_photos
        self.delete = delete
        self.driver = None

    # creating global immutable dictionaries of the months for transferring month suffix into month number.
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

    shared_counter = multiprocessing.Value('i', 0)

    ########## functions for general usage and potential features ##########

    def make_directory(self, path, directory_name="Google Photos"):
        """
        :param path: complete path of the directory the user want to create that directory
        :param directory_name: the name of the directory the user want to call it.
        :return: If the directory been created properly.
        """

        # creating the complete path of the new directory
        complete_path = path + "\\" + directory_name

        if not self.directory_exists(complete_path):
            os.mkdir(fr"{complete_path}")
            return complete_path

        return "-1"

    def directory_exists(self, path):
        if os.path.isdir(path):
            return True
        return False

    ########### functions for usage of 1st process - downloading and collect data ###########

    def move_to_next_photo(self, direction):
        """
        moving to the next photo.
        param direction: the direction of the next photo (according to the language)
        """
        actions = ActionChains(self.river)
        element = self.driver.find_element('tag name', 'body')
        time.sleep(0.3)
        actions.click(element).perform()
        time.sleep(0.3)
        if direction == "right":
            element.send_keys(Keys.ARROW_RIGHT)
        else:
            element.send_keys(Keys.ARROW_LEFT)
        time.sleep(0.3)

    def delete_photo(self, driver):
        element = driver.find_element('tag name', 'body')
        element.click()
        time.sleep(0.5)
        element.send_keys(Keys.SHIFT + '#')
        time.sleep(2)
        driver.switch_to.active_element.send_keys(Keys.ENTER)
        time.sleep(2)


    def get_file_date_and_name(self):

        """
        param language: the language the date is written.
        :return: file_date - the date and time the photo were taken.
                 file_name -the name of the current photo in this format - YYYY_MM_DD HH:MM:SS.
        """

        # Find the div element by XPath
        div_element = self.driver.find_element(By.XPATH, "//div[@aria-live='assertive']")

        # Extract the innerHTML of the div element
        date = div_element.get_attribute("innerHTML")

        # Split the text into an array by spaces
        date = date.replace('\u200F', '')
        date_as_array = date.split()
        date_as_array = [word.replace(',', '') for word in date_as_array]
        day = date_as_array[4]
        month = self.hebrew_months.get(date_as_array[5].replace('׳', ""))
        if month is None:
            month = self.english_months.get(date_as_array[5].replace('׳', ""))
        year = date_as_array[6]
        exact_time = date_as_array[7]

        file_date = year + ":" + month + ":" + day + " " + exact_time
        file_name = day + "_" + month + "_" + year + " " + exact_time.replace(':', '_')
        return file_date, file_name

    def check_file_name(self, name, path):
        """
        Checks if this file is already exist, it's not efficient because I'm assuming that someone can add the same picture
        not on the same session, besides there's shouldn't be many pictures that are taken at the same exact time!
        :param name: file name
        :param path: the complete path of the directory the file should be in if he exists    :return: original name if the file doesn't exist, modified name with counter of that date.
        """
        file_path = path + "\\" + name
        image_count = 0
        while os.path.isfile(file_path):
            image_count += 1
            file_path = path + "\\" + name + f"({image_count})"
        if image_count == 0:
            return name
        return name + f"({image_count})"

    def download_and_collect_data(self, download_directory):
        """
        The function unify and uses all the functions that we use for downloading the files, creating directories,
        getting the dates in the right order.
        :param driver: chrome driver
        :param language: the Language of the driver (english/hebrew)
        :param download_directory: the main directory that all the subdirectories will be created in
        :return: current_directory
        """
        element = self.driver.find_element('tag name', 'body')
        time.sleep(1)
        file_date, file_name = self.get_file_date_and_name()
        year = file_date[0:4]
        month = file_date[5:7]
        directory_name = year + "." + month
        designated_directory_path = self.directory_path + "\\" + directory_name
        # checking if this date exist
        # saving according to file format
        element.send_keys('i')
        time.sleep(0.8)
        parent_element = self.driver.find_element(By.XPATH, '/html/body/div[1]')
        # Get the innerHTML or text content of the parent element
        parent_content = parent_element.text
        element.send_keys(Keys.SHIFT + 'd')
        element.send_keys('i')
        # Check if the last 3 characters of the name are ".mp" (which could be for mp4, mp3, etc.)
        # is_video = ".mp4" in parent_content
        parent_text = parent_content.split("\n")

        for line in parent_text:
            if line[-3:] in ["jpg", "JPG", "jpeg", "JPEG"]:  # Common photo formats
                original_name = line
                break
            elif line[-3:] in ["png", "PNG"]:  # Common lossless photo format
                original_name = line
                break
            elif line[-3:] in ["gif", "GIF"]:  # Animated/static image
                original_name = line
                break
            elif line[-4:] in ["heic", "HEIC", "heif", "HEIF"]:  # Modern photo formats
                original_name = line
                break
            elif line[-3:] in ["webp", "WEBP"]:  # Web-friendly photo format
                original_name = line
                break
            elif line[-3:] in ["bmp", "BMP"]:  # Older bitmap format
                original_name = line
                break
            elif line[-3:] in ["tif", "TIF", "tiff", "TIFF"]:  # High-quality images
                original_name = line
                break
            elif line[-3:] in ["mp4", "MP4"]:  # Most common video format
                original_name = line
                break
            elif line[-3:] in ["mov", "MOV"]:  # Apple video format
                original_name = line
                break
            elif line[-3:] in ["avi", "AVI"]:  # Video format
                original_name = line
                break
            elif line[-3:] in ["mkv", "MKV"]:  # Versatile video format
                original_name = line
                break
            elif line[-4:] in ["flv", "FLV"]:  # Flash video
                original_name = line
                break
            elif line[-3:] in ["3gp", "3GP"]:  # Mobile-friendly format
                original_name = line
                break
            elif line[-4:] in ["webm", "WEBM"]:  # Open-source web format
                original_name = line
                break
            elif line[-4:] in ["mts", "MTS", "m2ts", "M2TS"]:  # AVCHD formats
                original_name = line
                break

        file_name = self.check_file_name(original_name, download_directory)

        return original_name, file_name, file_date, designated_directory_path

    def set_direction(self, language):
        """
        A function that sets the direction we're scrolling the photos.
        param language: the Language of the driver (english/hebrew)
        :return: the Direction.
        """
        if language == "hebrew":
            if self.older_photos:
                return "left", "right"
            else:
                return "right", "left"
        else:
            if self.older_photos:
                return "right", "left"
            else:
                return "left", "right"

    def get_download_directory(self, driver, language):
        driver.get('chrome://settings/downloads')
        element = driver.find_element('tag name', 'settings-ui')
        time.sleep(1)
        shadow_root = self.get_shadow_root(driver, element)
        shadow_root_text = shadow_root.find_element(By.CSS_SELECTOR, "#main").text
        text_as_array = shadow_root_text.split('\n')
        if language == "english":
            path_index = text_as_array.index('Location') + 1
        else:
            path_index = text_as_array.index('מיקום') + 1
        return text_as_array[path_index]

    def get_shadow_root(self, driver, element):
        return driver.execute_script('return arguments[0].shadowRoot', element)

    def init_driver(self):
        # initializing parameters and the webdriver and unable google restriction to log in
        # (restriction due to identification of webdriver that runs through selenium)

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
        return driver

    def init_crawler_and_download_dir(self):
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

        time.sleep(0.5)
        download_directory = self.get_download_directory(driver, "hebrew")
        driver.quit()
        return download_directory

    ##### the main function for the 1st process ####
    def crawler(self, file_list, username="", password="", finished_iterate_photos=None):
        # initializing parameters and the webdriver and unable google restriction to log in
        # (restriction due to identification of webdriver that runs through selenium)

        self.driver = self.init_driver()

        # entering the photo we got from the user.
        download_directory = self.get_download_directory(driver)
        time.sleep(0.5)
        self.driver.get(self.url)
        if username and password:
            keyboard.write(username)
            time.sleep(0.5)
            keyboard.send('enter')
            time.sleep(10)
            keyboard.write(password)
            time.sleep(0.5)
            keyboard.send('enter')
            time.sleep(15)
        # Waiting until the user correctly logged-in and letting the driver sleep and not overload the cpu.
        while driver.current_url != self.url:
            time.sleep(0.1)

        # moving back and forth to reveal data
        Direction, opposite_direction = self.set_direction("hebrew", self.older_photos)
        self.move_to_next_photo(driver, Direction)
        self.move_to_next_photo(driver, opposite_direction)

        # in case the user chooses to download all the photos from the photo he chose.
        if self.download_all_photos:
            previous_url = self.url
            current_url = None
            while previous_url != current_url:
                previous_url = current_url

                file_data_tuple = self.download_and_collect_data(driver, "hebrew", download_directory)
                file_list.append(file_data_tuple)
                time.sleep(1)
                if self.delete:
                    self.delete_photo(driver)
                    time.sleep(2)
                    if not self.older_photos:
                        previous_url = driver.current_url
                        time.sleep(0.5)
                        self.move_to_next_photo(driver, Direction)
                        time.sleep(2)
                else:
                    self.move_to_next_photo(driver, Direction)
                    time.sleep(1)
                current_url = driver.current_url

        # in case that the user chose to download a certain number of photos.
        else:
            previous_url = self.url
            current_url = None
            for i in range(self.number_of_photos):

                if previous_url == current_url:
                    break

                previous_url = current_url

                file_data_tuple = self.download_and_collect_data(driver, "hebrew", download_directory)
                file_list.append(file_data_tuple)
                if self.delete:
                    self.delete_photo(driver)
                    if not self.older_photos:
                        previous_url = driver.current_url
                        self.move_to_next_photo(driver, Direction)
                        time.sleep(0.5)
                else:
                    self.move_to_next_photo(driver, Direction)
                    time.sleep(1)
                current_url = driver.current_url
        finished_iterate_photos.value = True
        print("finished_iterate_photos.value: ", finished_iterate_photos.value)
        print("finished 1st process")
        driver.quit()

    ### those functions are for single process (not in use) ###

    ########### functions for usage of 2nd process - continusely checking if the file fully downloaded ###########

    def check_download(self, ready_files_queue, file_list, download_dir_path,
                       finished_iterate_photos, finished_download):
        i = 0
        while (not finished_iterate_photos.value) or (len(file_list) > 0):

            if len(file_list) > 0:

                # file_data_tuple = (original_name, file_name, file_date, designated_directory_path)
                file_data_tuple = file_list.pop(0)
                original_name = file_data_tuple[0]
                file_name = file_data_tuple[1]
                file_date = file_data_tuple[2]
                designated_directory_path = file_data_tuple[3]
                file_full_path = download_dir_path + "\\" + original_name
                if os.path.isfile(file_full_path):
                    print(f"{file_name} were added to the queue!!!")
                    print(len(file_list))
                    ready_files_queue.put((file_full_path, file_name, file_date, designated_directory_path))
                else:
                    file_list.append(file_data_tuple)
        print("finished 2nd process")
        finished_download.value = True

    ################ functions for the 3rd process ####################
    def rename_and_move(self, ready_files_queue, finished_download):
        """
        the function rename the original name of the file to the date the photo were taken.
        """
        while (not finished_download.value) or (not ready_files_queue.empty()):
            # file_data_tuple = (file_full_path, file_name, file_date, designated_directory_path)
            if not ready_files_queue.empty():
                file_data_tuple = ready_files_queue.get()
                file_full_path = file_data_tuple[0]
                file_name = file_data_tuple[1]
                file_date = file_data_tuple[2]
                designated_directory_path = file_data_tuple[3]
                if not self.directory_exists(designated_directory_path):
                    os.mkdir(fr"{designated_directory_path}")
                if file_full_path[-3:] == "mp4":
                    suffix = ".mp4"
                else:
                    suffix = ".jpg"
                file_name = self.check_file_name(file_name + suffix, designated_directory_path)
                new_name_path = designated_directory_path + "\\" + file_name + suffix
                # need to do logs here!!!
                print("before move")
                shutil.move(file_full_path, new_name_path)
                print(f"is the file still exist in the original path: {os.path.isfile(file_full_path)}")
                # shutil.move(fr'{downloads_directory + file_name}', directory_path)
                self.set_metadata(new_name_path, file_date)

    # setting the date of the picture to be the actual time the photo was taken

    def set_metadata(self, file_path, date_str):
        """
        setting the metadata of the file to the original date the photo were taken
        :param file_path: the path of the photo/video
        :param date_str: the original date as a string
        """
        exif_dict = piexif.load(file_path)
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str.encode("utf-8")
        exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = date_str.encode("utf-8")
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, file_path)

    def process(self):

        with multiprocessing.Manager() as manager:
            # Create a shared integer using the manager
            shared_counter = manager.Value('i', 0)
            finished_iterate_photos = manager.Value('b', False)
            finished_download = manager.Value('b', False)
            ready_files_queue = manager.Queue()
            file_list = manager.list()
            username = os.getenv("username")
            password = os.getenv("password")
            # Create and start the processes
            download_dir_path = self.init_crawler_and_download_dir()

            crawler_process = multiprocessing.Process(target=self.crawler,
                                                      args=(self.file_list, username, password,
                                                            finished_iterate_photos))

            download_check_process = multiprocessing.Process(target=self.check_download,
                                                             args=(
                                                                 ready_files_queue, file_list, download_dir_path,
                                                                 finished_iterate_photos, finished_download))

            rename_and_move_process = multiprocessing.Process(target=self.rename_and_move,
                                                              args=(ready_files_queue, finished_download))

            crawler_process.start()
            download_check_process.start()
            rename_and_move_process.start()

            crawler_process.join()
            download_check_process.join()
            rename_and_move_process.join()


if __name__ == '__main__':
    # make_directory("C:\\Users\\galev\\OneDrive\\Desktop")
    # path_str = "C:\\Users\\galev\\OneDrive\\Desktop\\Google Photos"
    # url = "https://photos.google.com/photo/AF1QipM7fvdLw3E9a8b-j-8AsER3HBK-iIPBTRkbKiFj"
    # directory_path = "C:\\Users\\galev\\OneDrive\\Desktop\\Google Photos"
    # older_photos = True
    # download_all_photos = False
    # number_of_photos = 5
    # delete = False
    print("")
