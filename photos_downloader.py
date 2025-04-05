import os
import shutil
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        self.download_dir_path = None

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
        actions = ActionChains(self.driver)
        element = self.driver.find_element('tag name', 'body')
        time.sleep(0.3)
        actions.click(element).perform()
        time.sleep(0.3)
        if direction == "right":
            element.send_keys(Keys.ARROW_RIGHT)
        else:
            element.send_keys(Keys.ARROW_LEFT)
        time.sleep(0.3)

    def delete_photo(self):
        element = self.driver.find_element('tag name', 'body')
        element.click()
        time.sleep(0.5)
        element.send_keys(Keys.SHIFT + '#')
        time.sleep(2)
        self.driver.switch_to.active_element.send_keys(Keys.ENTER)
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

    def check_file_name(self, name, path, suffix):
        """
        Checks if this file is already exist, it's not efficient because I'm assuming that someone can add the same picture
        not on the same session, besides there's shouldn't be many pictures that are taken at the same exact time!
        :param name: file name
        :param suffix: the suffix of the file
        :param path: the complete path of the directory the file should be in if he exists    :return: original name if the file doesn't exist, modified name with counter of that date.
        """
        file_path = path + "\\" + name
        image_count = 0
        suffix_length = len(suffix)
        while os.path.isfile(file_path):
            image_count += 1
            file_path = path + "\\" + name[:len(name)-1-suffix_length] + f" ({image_count})" + name[len(name)-1-suffix_length:]
        if image_count == 0:
            return name
        return name[:len(name)-1-suffix_length] + f" ({image_count})" + name[len(name)-1-suffix_length:]

    def download_and_collect_data(self):
        """
        The function unify and uses all the functions that we use for downloading the files, creating directories,
        getting the dates in the right order.
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


        valid_extensions = {
            "jpg", "jpeg", "png", "gif", "heic", "heif", "webp", "bmp",
            "tif", "tiff", "mp4", "mov", "avi", "mkv", "flv", "3gp",
            "webm", "mts", "m2ts"
        }
        original = ""
        s = ""
        for line in parent_text:
            _, ext = os.path.splitext(line)  # Extract extension
            ext = ext.lstrip(".").lower()  # Remove the leading dot and normalize case
            if ext in valid_extensions:
                original = line
                s = ext  # Use the actual file extension as the suffix
                break

        # original_name = self.check_file_name(original_name, self.download_dir_path, suffix)

        return [original, file_name, file_date, designated_directory_path, s]

    def get_language(self):
        """
        A function that gets the language of the driver.
        :return: the language of the driver.
        """
        element = self.driver.find_element('tag name', 'html')
        language = element.get_attribute('lang')
        return language

    def set_direction(self, language):
        """
        A function that sets the direction we're scrolling the photos.
        param language: the Language of the driver (english/hebrew)
        :return: the Direction.
        """
        if language == "iw":
            if self.older_photos:
                return "left", "right"
            else:
                return "right", "left"
        else:
            if self.older_photos:
                return "right", "left"
            else:
                return "left", "right"

    def get_download_directory(self):
        self.driver.get('chrome://settings/downloads')
        element = self.driver.find_element('tag name', 'settings-ui')
        time.sleep(1)
        shadow_root = self.get_shadow_root(element)
        shadow_root_text = shadow_root.find_element(By.CSS_SELECTOR, "#main").text
        text_as_array = shadow_root_text.split('\n')
        # if language == "english":
        #     path_index = text_as_array.index('Location') + 1
        # else:
        path_index = text_as_array.index('מיקום') + 1
        return text_as_array[path_index]

    def get_shadow_root(self, element):
        return self.driver.execute_script('return arguments[0].shadowRoot', element)

    def init_crawler_and_download_dir(self):
        # initializing parameters and the webdriver and unable google restriction to log in
        # (restriction due to identification of webdriver that runs through selenium)

        options = webdriver.ChromeOptions()
        # options.add_argument("user-data-dir=C:\\Users\\galev\\AppData\\Local\\Google\\Chrome\\User Data")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--lang=he")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--mute-audio")
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Initializing a list with two Useragents
        useragentarray = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        ]

        for i in range(len(useragentarray)):
            # Setting user agent iteratively as Chrome 108 and 107
            self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": useragentarray[i]})
            # print(driver.execute_script("return navigator.userAgent;"))

        time.sleep(0.5)
        self.download_dir_path = self.get_download_directory()
        return self.download_dir_path

    def safe_crawler(self, file_list, finished_iterate_photos, error_queue, shared_download_path,
                     finished_download):
        """Wrapper for crawler to catch exceptions and send them to the queue."""
        try:
            self.crawler(file_list, shared_download_path, finished_iterate_photos, finished_download)
        except Exception as ex:
            if self.driver:
                self.driver.quit()
            error_queue.put(str(ex))

    ##### the main function for the 1st process ####
    def crawler(self, file_list, shared_download_path, finished_iterate_photos, finished_download):
        # initializing parameters and the webdriver and unable google restriction to log in
        # (restriction due to identification of webdriver that runs through selenium)
        self.init_crawler_and_download_dir()
        shared_download_path.value = self.download_dir_path
        # entering the photo we got from the user.
        time.sleep(0.5)
        self.driver.get(self.url)

        # Waiting until the user correctly logged-in and letting the driver sleep and not overload the cpu.
        timeout = 120  # 2 minutes
        start_time = time.time()

        while self.driver.current_url != self.url:
            if time.time() - start_time > timeout:
                raise Exception("Timed out: Failed to reach the expected URL within 2 minutes."
                                " Please check your internet connection or the email address and try again.")
            time.sleep(0.1)

        if "Error 404" in self.driver.title:
            raise Exception("The photo you entered is not available or does not exist. Please try again.")

        try:
            self.driver.minimize_window()  # Minimize browser
            self.driver.set_window_position(-10000, 0)  # Move it off-screen
        except Exception as e:
            raise Exception(f"Failed to make browser uninterrupted: {str(e)}")

        # moving back and forth to reveal data
        Direction, opposite_direction = self.set_direction(self.get_language())
        self.move_to_next_photo(Direction)
        self.move_to_next_photo(opposite_direction)
        if self.driver.current_url != self.url:
            self.move_to_next_photo(Direction)
            time.sleep(1)

        # in case the user chooses to download all the photos from the photo he chose.
        if self.download_all_photos:
            previous_url = self.url
            current_url = None
            while previous_url != current_url:
                previous_url = current_url

                file_data_tuple = self.download_and_collect_data()
                file_list.append(file_data_tuple)
                time.sleep(1)
                if self.delete:
                    if file_data_tuple[-1] == "mp4":
                        time.sleep(3)
                    self.delete_photo()
                    time.sleep(1)
                    if not self.older_photos:
                        previous_url = self.driver.current_url
                        time.sleep(0.5)
                        self.move_to_next_photo(Direction)
                        time.sleep(2)
                else:
                    self.move_to_next_photo(Direction)
                    time.sleep(1)
                current_url = self.driver.current_url

        # in case that the user chose to download a certain number of photos.
        else:
            previous_url = self.url
            current_url = None
            for i in range(self.number_of_photos):

                if previous_url == current_url:
                    break

                previous_url = current_url

                file_data_tuple = self.download_and_collect_data()
                file_list.append(file_data_tuple)
                if self.delete:
                    if file_data_tuple[-1] == "mp4":
                        time.sleep(3)
                    self.delete_photo()
                    time.sleep(1)
                    if not self.older_photos:
                        previous_url = self.driver.current_url
                        self.move_to_next_photo(Direction)
                        time.sleep(0.5)
                else:
                    self.move_to_next_photo(Direction)
                    time.sleep(1)
                current_url = self.driver.current_url
        finished_iterate_photos.value = True
        time.sleep(5)
        print("finished_iterate_photos.value: ", finished_iterate_photos.value)
        print("finished 1st process")
        while not finished_download.value:
            time.sleep(1)
        self.driver.quit()

    ### those functions are for single process (not in use) ###

    ########### functions for usage of 2nd process - continusely checking if the file fully downloaded ###########

    def check_download(self, ready_files_queue, file_list,
                       finished_iterate_photos, finished_download, shared_download_path):

        last_activity_time = time.time()  # Start timer

        while (not finished_iterate_photos.value) or (len(file_list) > 0):

            if len(file_list) > 0 and shared_download_path.value:
                last_activity_time = time.time()  # Reset timer

                # Process file
                file_data_tuple = file_list.pop(0)
                original_name = file_data_tuple[0]
                file_name = file_data_tuple[1]
                file_date = file_data_tuple[2]
                designated_directory_path = file_data_tuple[3]
                suffix = file_data_tuple[4]
                file_full_path = shared_download_path.value + "\\" + original_name

                if os.path.isfile(file_full_path):
                    print(f"{file_name} were added to the queue!!!")
                    print(len(file_list))
                    ready_files_queue.put((file_full_path, file_name, file_date, designated_directory_path, suffix))
                else:
                    file_list.append(file_data_tuple)

            # Stop if nothing happens for 150 seconds
            if time.time() - last_activity_time > 150:
                print("Timeout reached: No activity in check_download for 150 seconds. Stopping.")
                break

        print("Finished 2nd process")
        finished_download.value = True
        print("finished_download.value: ", finished_download.value)
        time.sleep(3)

    ################ functions for the 3rd process ####################
    def rename_and_move(self, ready_files_queue, finished_download):
        last_activity_time = time.time()  # Start timer

        while (not finished_download.value) or (not ready_files_queue.empty()):

            if not ready_files_queue.empty():
                last_activity_time = time.time()  # Reset timer

                # Process file
                file_data_tuple = ready_files_queue.get()
                file_full_path = file_data_tuple[0]
                file_date = file_data_tuple[2]
                designated_directory_path = file_data_tuple[3]
                suffix = file_data_tuple[4]
                file_name = file_data_tuple[1] + "." + suffix

                if not self.directory_exists(designated_directory_path):
                    os.mkdir(fr"{designated_directory_path}")

                file_name = self.check_file_name(file_name, designated_directory_path, suffix)
                new_name_path = designated_directory_path + "\\" + file_name

                print("before move")
                shutil.move(file_full_path, new_name_path)
                print(f"is the file still exist in the original path: {os.path.isfile(file_full_path)}")

                self.set_metadata(new_name_path, file_date)

            # Stop if nothing happens for 300 seconds
            if time.time() - last_activity_time > 250:
                print("Timeout reached: No activity in rename_and_move for 150 seconds. Stopping.")
                break

        print("Finished renaming and moving files")

    # setting the date of the picture to be the actual time the photo was taken

    def set_metadata(self, file_path, date_str):
        """
        setting the metadata of the file to the original date the photo were taken
        :param file_path: the path of the photo/video
        :param date_str: the original date as a string
        """

        # Convert the date_str format 'YYYY:MM:DD HH:MM:SS' to 'YYYY-MM-DD HH:MM:SS'
        formatted_date_str = date_str.replace(":", "-", 2)

        # Convert the formatted string to a Unix timestamp
        timestamp = time.mktime(time.strptime(formatted_date_str, "%Y-%m-%d %H:%M:%S"))

        # Update the file's creation and modification dates using os.utime
        os.utime(file_path, (timestamp, timestamp))

        print(f"Updated file {file_path} with new date: {date_str}")

    def start(self):

        with multiprocessing.Manager() as manager:
            # Create a shared integer using the manager
            finished_iterate_photos = manager.Value('b', False)
            finished_download = manager.Value('b', False)
            ready_files_queue = manager.Queue()
            file_list = manager.list()
            shared_download_path = manager.Value('download', '')
            error_queue = manager.Queue()

            # Create and start the processes

            crawler_process = multiprocessing.Process(target=self.safe_crawler,
                                                      args=(file_list,
                                                            finished_iterate_photos, error_queue,
                                                            shared_download_path, finished_download))

            download_check_process = multiprocessing.Process(target=self.check_download,
                                                             args=(
                                                                 ready_files_queue, file_list,
                                                                 finished_iterate_photos, finished_download,
                                                                 shared_download_path))

            rename_and_move_process = multiprocessing.Process(target=self.rename_and_move,
                                                              args=(ready_files_queue, finished_download))
            processes = [crawler_process, download_check_process, rename_and_move_process]

            # Start all processes
            for process in processes:
                process.start()

            try:
                # Monitor the error queue while processes are running
                while any(p.is_alive() for p in processes):
                    if not error_queue.empty():
                        error_message = error_queue.get()
                        raise RuntimeError(error_message)
                    time.sleep(0.1)

            finally:
                # Ensure all processes are terminated if an error occurs
                for process in processes:
                    process.terminate()
                    process.join()


if __name__ == '__main__':
    # make_directory("C:\\Users\\galev\\OneDrive\\Desktop")
    # path_str = "C:\\Users\\galev\\OneDrive\\Desktop\\Google Photos"
    # url = "https://photos.google.com/photo/AF1QipM7fvdLw3E9a8b-j-8AsER3HBK-iIPBTRkbKiFj"
    # directory_path = "C:\\Users\\galev\\OneDrive\\Desktop\\Google Photos"
    # older_photos = True
    # download_all_photos = False
    # number_of_photos = 5
    # delete = False
    pd = PhotosDownloader(r"https://photos.google.com/photo/AF1QipOYNN6jR-lqIKUC4dnJgp9uNnWVvjRnvYPA5jMN",
                          r"C:\Users\galev\OneDrive\Desktop\Google Photos", True, False, 5, True)
    try:
        pd.start()
    except Exception as e:
        print(str(e))
    finally:
        print("finished")
