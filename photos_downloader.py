import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def make_directory_on_desktop(path, directory_name="Google Photos"):
    """
    :param path: complete path of the directory the user want to create that directory
    :param directory_name: the name of the directory the user want to call it.
    :return: If the directory been created properly.
    """

    # creating the complete path of the new directory
    complete_path = path + "\\" + directory_name

    if(not directory_exists(complete_path)):
        os.mkdir(fr"{complete_path}")
        print(f'The directory "{directory_name}" was created successfully in the chosen directory')
        return complete_path

    return "-1"

def directory_exists(directory_path):
    if os.path.isdir(directory_path):
        print(f"The directory '{directory_path}' exists.")
        return True
    return False


def crawler(url, profile_directory):
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={profile_directory}")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    while True:
        continue



if __name__ == '__main__':
    user_path = "C:\\Users\\galev\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
    crawler("https://photos.google.com/photo/AF1QipPG5bUkHMsthrvYUWJSTFsJ9WhFJY2GWYVsY0Kz", user_path)
