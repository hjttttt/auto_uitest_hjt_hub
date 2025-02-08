# Created by 黄景涛
# DATE 2024/8/19
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from utils.log_helper.logger import logger


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

    # 动作：等待n秒
    def key_sleep(self, sec: float = 2):
        time.sleep(float(sec))

    # 内置，查找元素
    def find_element(self, loc: str):
        """封装过的元素自动使用显示等待"""
        by_types = [By.CLASS_NAME, By.ID, By.NAME, By.LINK_TEXT, By.PARTIAL_LINK_TEXT]
        if loc.startswith(('.//', '//', '/')):
            by_type = By.XPATH
        elif loc.startswith(("#", ".")):
            by_type = By.CSS_SELECTOR
        else:
            for by_type in by_types:
                try:
                    el: WebElement = self.wait_for_element_visible(by_type, loc)
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
            el: WebElement = self.wait_for_element_visible(by_type, loc)
            tag_name = el.tag_name
            logger.info(f'【{el.tag_name}】定位成功')
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            return el
        except Exception as e:
            loc_error = f'元素【{loc}】，所有定位方式都没有定位成功！'
            logger.error(loc_error)
            raise Exception(loc_error)

    # 等待元素出现
    def key_sleep_until_ele(self, xpath_loc: str, timeout: int = 10):
        """
        :param xpath_loc: 定位参数
        :param timeout: 超时时间
        :return:
        """
        try:
            target_ele = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.XPATH, xpath_loc))
            )
        except TimeoutError:
            raise

        return target_ele

    # 内置，等待元素可见（不一定可点击）
    def wait_for_element_visible(self, by, locator):
        """
        :param self:
        :param by: 定位方式，eg. By.XPATH
        :param locator: 元素定位语句
        :return:
        """
        return WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located((by, locator)))

    def wait_element_appear_and_disappear(self, ele_loc: str, a_time: int = 2, d_time: int = 10):
        """
        元素先出现后消失（可用于loading的元素）
        :param ele_loc:
        :param a_time:
        :param d_time:
        :return:
        """
        try:
            # 等待 img 标签出现
            WebDriverWait(self.driver, a_time).until(
                EC.presence_of_element_located((By.XPATH, ele_loc))
            )
            # 等待 img 标签消失
            WebDriverWait(self.driver, d_time).until(
                EC.invisibility_of_element((By.XPATH, ele_loc))
            )
        except:
            pass

    # 动作：等待loading蒙层加载
    def key_sleep_until_unloading(self, loading_loc: str, timeout: int = 10):
        """
        :param loading_loc: loading蒙层定位参数
        :param timeout: 超时时间
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

        # loading蒙层定位器
        loading_locator = (By.XPATH, loading_loc)
        style_info = 'display: none;'
        try:
            WebDriverWait(self.driver, timeout).until(StyleContains(loading_locator, style_info))
        except TimeoutError:
            raise

    def wait_element_no_attr_value(self, ele: WebElement, attr_type: str, value: str, timeout: int = 10):
        """
        等待元素没有指定属性的指定值
        :param self:
        :param ele: WebElement元素
        :param attr_type: 标签元素的属性，eg:class属性、style属性
        :param value: 属性值
        :param timeout: 超时时间
        :return:
        """
        attr_types = ('class', 'style')
        if attr_type not in attr_types:
            raise Exception(f'元素不支持{attr_type}类型')

        # 自定义元素的加载消失条件
        class AttrContains:
            """ 是否包含属性值 """

            def __init__(self, element, val):
                self.ele = element
                self.attr_value = val

            def __call__(self, driver):
                return self.attr_value not in self.ele.get_attribute(attr_type)

        try:
            WebDriverWait(self.driver, timeout).until(AttrContains(ele, value))
        except TimeoutError:
            raise

    def key_wait_for_ele_status_recovery(self, initial_loc: str, loading_loc: str, timeout=10):
        """
        等待元素状态恢复，eg: 点击下载按钮，按钮处于loading态，直到文件保存窗口弹出后，恢复初始态
        :param initial_loc: 表示初始态的xpath
        :param loading_loc: 表示加载态的xpath
        :param timeout: 超时时长
        :return:
        """
        wait = WebDriverWait(self.driver, timeout)
        # 智能等待元素进入点击后的状态
        wait.until(EC.visibility_of_element_located((By.XPATH, loading_loc)))
        # 智能等待点击态的元素失效
        wait.until(EC.staleness_of(self.driver.find_element(By.XPATH, loading_loc)))
        # 智能等待初始态的元素出现
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, initial_loc)))
        except:
            pass
        logger.info(f'元素状态已恢复正常')
