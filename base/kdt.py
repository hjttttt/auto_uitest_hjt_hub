# Created by 黄景涛
# DATE 2024/7/18

import json
import os

import pytest

from webdriver_helper import get_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from config.settings import ROOT_PATH
from utils.auth.login_util import login
from base.kdt_lib.fields_mixin import FieldsMiXin
from base.kdt_lib.assert_mixin import EleAssert
from utils.logger.custom_logger import logger
from utils.screenshot.picture_util import save_png

with open(os.path.join(ROOT_PATH, 'config/config.json'), mode='r', encoding='utf8') as f:
    cfg = json.load(f)


def itf_login(username, password):
    """ 接口-登录 """
    login_url = cfg.get('login_info').get('login_url')
    return login(login_url, username, password)


def ui_login(driver):
    """ UI-登录 """
    login_msg = cfg.get('login_info')
    driver.get(login_msg['login_url'])
    kw = KeyWordLib(driver)
    kw.key_input(login_msg['user_input'], login_msg['username'])
    kw.key_input(login_msg['password_input'], login_msg['password'])
    kw.key_click(login_msg['login_button'])


class BaseDriver:
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, request):
        # 打开Chrome浏览器
        self.driver = get_webdriver()
        self.wait = WebDriverWait(self.driver, 10)  # 显示等待最多10s
        self.driver.maximize_window()
        # 在测试类中共享setup_class方法
        request.cls.driver = self.driver
        # 每执行一条用例前，自动登录
        ui_login(self.driver)
        yield
        # 关闭浏览器
        self.driver.quit()


class KeyWordLib(FieldsMiXin, EleAssert):

    # 动作：切换登录用户
    def key_switch_user(self, username, password, into_url=None):
        """
        :param self:
        :param username: 用户名
        :param password: 密码
        :param into_url: 需要进入的新页面
        :return:
        """
        # 获取用户cookie
        cookie = itf_login(username, password)
        # 刷新driver对象中的cookies
        self.driver.delete_all_cookies()
        for k, v in cookie.items():
            self.driver.add_cookie(dict(name=k, value=v))
        self.driver.refresh()

        if into_url is not None:
            self.key_get(into_url)

    # 动作：地址跳转
    def key_get(self, url):
        self.driver.get(url)

    # 动作：为指定的元素执行js代码
    def key_jscode(self, loc, code):
        ele = self.find_element(loc)
        self.driver.execute_script(code, ele)

    # 动作：点击
    def key_click(self, loc):
        """
        :param self:
        :param loc: 元素定位
        :return:
        """
        ele = self.find_element(loc)
        ele.click()

    # 动作：输入
    def key_input(self, loc, content=None):
        """
        :param self:
        :param loc: 输入框定位
        :param content: 输入内容
        :return:
        """
        ele = self.find_element(loc)
        ele.clear()
        if content is not None:
            ele.send_keys(content)

    # 动作：输入并回车查询
    def key_input_and_enter(self, loc, content=None):
        """
        :param self:
        :param loc: 输入框定位
        :param content: 输入内容
        :return:
        """
        ele = self.find_element(loc)
        ele.clear()
        if content is not None:
            ele.send_keys(content + Keys.ENTER)

    # 动作：hover下拉
    def key_select_with_hover(self, loc, option: str, instance=None):
        """
        :param loc:  定位参数
        :param option: 选项
        :param instance: 所在的Test类实例
        :return:
        """
        ele = self.find_element(loc)
        actions = ActionChains(self.driver)
        actions.move_to_element(ele).perform()

        # 截屏并保存PNG
        save_png(instance)

        # 选项面板
        ul_loc = "//div/ul[@class='bk-dropdown-list']"

        try:
            ul = self.find_element(ul_loc)
            lis = ul.find_elements(By.TAG_NAME, 'li')

            option = option.strip()
            for li in lis:
                if option in li.text:
                    li.click()
                    break
            else:
                not_find_error = f"未找到【{option}】"
                raise Exception(not_find_error)
        except:
            raise
        finally:
            width, height = ele.rect['width'], ele.rect['height']
            # 余量，单位：px，起到微调作用
            margin = 1
            offset_xy = (-(width // 2 + margin), (height // 2 + margin))
            actions.move_to_element_with_offset(ele, *offset_xy).perform()

    # 动作：切换浏览器窗口
    def key_switch_window(self, window_index):
        """
        切换浏览器窗口
        :param self:
        :param window_index: 窗口索引
        :return:
        """
        window_handles = self.driver.window_handles
        try:
            current_window = window_handles[int(window_index)]
        except:
            error_msg = f"索引为{window_index}的窗口不存在！"
            raise Exception(error_msg)
        self.driver.switch_to.window(current_window)

    # 动作：切换内嵌弹窗
    def key_switch_ifram(self, ifram_args):
        """
        切换内嵌弹窗
        :param self:
        :param ifram_args: ifram定位参数，如：xpath、class_name、id等
        :return:
        """
        ifram_ele = self.find_element(ifram_args)
        try:
            print(ifram_ele.tag_name)
        except:
            error_msg = f"ifram{ifram_ele}无法定位成功！"
            raise Exception(error_msg)
        self.driver.switch_to.frame(ifram_ele)


if __name__ == '__main__':
    ...
