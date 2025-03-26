import unittest
from photos_downloader import *
import bcrypt

download_directory = init_crawler_and_download_dir()
directory_path = r'C:\Users\galev\OneDrive\Documents\GitHub\galevi7-google-photos-date-organizer\tests\download_test'
url = "https://photos.google.com/photo/AF1QipOb2hHHTJN9PSeZ--6vZ61-iETxpK6I4qWVf0H5"

class MyTestCase(unittest.TestCase):


    def test_download_and_collect_data(self):
        driver = init_driver()
        result_tuple = download_and_collect_data(driver, "hebrew", directory_path)
        driver.quit()
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    username = "photos.organizer.test"
    password = "Test!!!Test"

    # unittest.main()
