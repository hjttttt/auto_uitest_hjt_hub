# Created by 黄景涛
# DATE: 2024/9/29

import logging
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_mixin import BaseMiXin
from utils.log_helper.logger import logger


class EleAssert(BaseMiXin):

    def key_assert_text_in_ele(self, actual_msg_loc, expect, timeout=5):
        """
        断言元素文本是否包含预期字符串
        :param actual_msg_loc: 目标元素定位
        :param expect: 预期字符串
        :param timeout: 超时时间
        :return: bool
        """
        is_success = False
        try:
            msg_ele = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, actual_msg_loc)))
        except TimeoutError:
            pass
        else:
            content = msg_ele.text
            if expect in content:
                is_success = True
        assert is_success is True, f'元素的实际文本内容为【{content}】, 不包含【{expect}】'

    def key_assert_no_error_message(self, error_message_loc, error_content: str = None, timeout=5):
        """
        断言无报错标签及错误内容
        :param error_message_loc: 错误信息元素定位
        :param error_content: 错误消息
        :param timeout: 超时时间
        :return:
        """
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, error_message_loc)))
            # 查找错误信息元素
            error_element = self.driver.find_element(By.XPATH, error_message_loc)

            error_msg = f"断言失败。存在报错，报错内容：{error_element.text}"
            if error_content is None:
                assert False, error_msg
            else:
                if error_content in error_element.text:
                    assert False, error_msg
                else:
                    logger.info('警告：存在报错，但不是预期报错信息，请核对')
        except TimeoutException:
            assert True

    def key_assert_list_is_null(self, expect_ele_loc: str):
        """
        断言数据列表无数据，以出现空占位图为依据
        :param expect_ele_loc: 期望出现的ele元素
        :return:
        """
        try:
            expect_ele = self.driver.find_element(By.XPATH, expect_ele_loc)
            logger.info(f'断言捕获的元素空占位信息：{expect_ele.text}')
            assert True
        except NoSuchElementException:
            assert False, '列表不为空，无空占位信息'
        except TimeoutException:
            assert False, '查询空占位元素超时'

    def key_assert_no_element(self, ele_loc: str):
        """
        断言不存在某个元素
        :param ele_loc: 预期不存在的元素
        :return: bool
        """
        try:
            expect_ele = self.driver.find_element(By.XPATH, ele_loc)
        except NoSuchElementException:
            assert True
        else:
            assert False, f'元素【{expect_ele.text}】被发现存在'

    def key_assert_4(self):
        ...

    def key_assert_5(self):
        ...
