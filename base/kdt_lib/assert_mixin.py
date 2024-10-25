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

from .base_mixin import BaseMiXin


class EleAssert(BaseMiXin):

    def key_assert_text_in_ele(self, actual_msg_loc, expect):
        is_success = False
        try:
            msg_ele = self.key_sleep_until_ele(actual_msg_loc)
        except TimeoutError:
            pass
        else:
            content = msg_ele.text
            if expect in content:
                is_success = True
        assert is_success is True, f'元素的文本内容不包含【{expect}】'
