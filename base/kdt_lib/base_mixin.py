# Created by 黄景涛
# DATE 2024/8/19

import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from utils.logger.custom_logger import logger
from utils.screenshot.picture_util import save_png


class BaseMiXin:
    def __init__(self, driver, timeout=10):
        self.driver: WebDriver = driver
        self.timeout = timeout

    # 内置，获取关键字函数
    def get_kw_method(self, key):
        f = getattr(self, f'key_{key}', None)
        if not f:
            raise AttributeError(f'不存在关键字:{key}')
        return f

    # 内置，等待元素出现
    def wait_for_element(self, by, locator):
        """
        :param self:
        :param by: 定位方式，eg. By.XPATH
        :param locator: 元素定位语句
        :return:
        """
        return WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable((by, locator)) or EC.visibility_of_element_located((by, locator))
        )

    # 内置，查找元素
    def find_element(self, loc: str):
        "封装过的元素自动使用显示等待"
        by_types = [By.CLASS_NAME, By.ID, By.NAME, By.LINK_TEXT, By.PARTIAL_LINK_TEXT]
        if loc.startswith(('.//', '//', '/')):
            by_type = By.XPATH
        elif loc.startswith(("#", ".")):
            by_type = By.CSS_SELECTOR
        else:
            for by_type in by_types:
                try:
                    el: WebElement = self.wait_for_element(by_type, loc)
                    tag_name = el.tag_name
                except:
                    continue
                else:
                    logger.info(f'【{el.tag_name}】定位成功')
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)  # 元素滚动到视图的正中间
                    return el
            else:
                by_type = By.XPATH
        try:
            el: WebElement = self.wait_for_element(by_type, loc)
            tag_name = el.tag_name
            logger.info(f'【{el.tag_name}】定位成功')
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            return el
        except Exception as e:
            loc_error = f'元素【{loc}】，所有定位方式都没有定位成功！'
            logger.error(loc_error)
            raise Exception(loc_error)

    # 动作：等待n秒
    @classmethod
    def key_sleep(cls, sec: float = 2):
        time.sleep(float(sec))

    # 等待元素出现
    def key_sleep_until_ele(self, xpath_loc: str, timeout: int = 10, instance=None):
        """
        :param xpath_loc: 定位参数
        :param timeout: 超时时间
        :param instance: 所在的Test类实例
        :return:
        """
        # 加载前，保存截屏
        save_png(instance)

        try:
            target_ele = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.XPATH, xpath_loc))
            )
        except TimeoutError:
            raise

        return target_ele

    # 动作：等待loading蒙层加载
    def key_sleep_until_unloading(self, loading_loc: str, timeout: int = 10, instance=None):
        """
        :param loading_loc: loading蒙层定位参数
        :param timeout: 超时时间
        :param instance: 所在的Test类实例
        :return:
        """

        class StyleContains:
            """ style中是否包含某个值 """

            def __init__(self, locator, text):
                self.locator = locator
                self.text = text

            def __call__(self, driver):
                element = driver.find_element(*self.locator)
                return self.text in element.get_attribute("style")

        # 加载前，保存截屏
        save_png(instance)

        # loading蒙层定位器
        loading_locator = (By.XPATH, loading_loc)
        style_info = 'display: none;'
        try:
            WebDriverWait(self.driver, timeout).until(StyleContains(loading_locator, style_info))
        except TimeoutError:
            raise
