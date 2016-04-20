# coding=gbk

from Searcher import Searcher
from selenium import webdriver
import SysConfig
from PIL import Image


class FirefoxSearcher(Searcher):

    screenshot_offset_x = 0
    screenshot_offset_y = 0

    def __init__(self):
        super(FirefoxSearcher, self).__init__()

    def build_driver(self):
        build_result = 0
        self.driver = webdriver.Firefox()
        self.set_timeout_config()
        for i in xrange(SysConfig.max_try_times):
            if self.wait_for_load_start_url():
                break
            else:
                if i == SysConfig.max_try_times:
                    build_result = 1
        return build_result

    def download_validate_image(self, image_element, save_path):
        self.driver.get_screenshot_as_file(save_path)
        left = self.screenshot_offset_x + image_element.location['x']
        top = self.screenshot_offset_y + image_element.location['y']
        right = self.screenshot_offset_x + image_element.location['x'] + image_element.size['width']
        bottom = self.screenshot_offset_y + image_element.location['y'] + image_element.size['height']
        image = Image.open(save_path)
        image = image.crop((left, top, right, bottom))
        image.save(save_path)


if __name__ == '__main__':
    searcher = FirefoxSearcher()
    searcher.build_driver()
