# Created by 黄景涛
# DATE 2024/7/18

import logging
import json
import os
import time

import pytest

# from webdriver_helper import get_webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from urllib.parse import urljoin
from config.settings import ROOT_PATH
from base.login_util import login
from base.kdt_lib.fields_mixin import FieldsMiXin
from base.kdt_lib.inst_add_mixin import InstAttrMiXin
from base.kdt_lib.assert_mixin import EleAssert
from utils.log_helper.logger import logger
from utils.screenshot.picture_tool import save_png
from config.settings import cfg, get_environment_url


def itf_login(username, password):
    """ 接口-登录 """
    login_url = get_environment_url(cfg.get('login_info').get('login_url'))
    return login(login_url, username, password)


def ui_login(driver):
    """ UI-登录 """
    login_msg = cfg.get('login_info')
    login_url = get_environment_url(login_msg.get('login_url'))
    driver.get(login_url)
    kw = KeyWordLib(driver)
    kw.key_input(login_msg['user_input'], login_msg['username'])
    kw.key_input(login_msg['password_input'], login_msg['password'])
    kw.key_click(login_msg['login_button'])


class BaseDriver:
    service = Service(ChromeDriverManager().install())

    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, request):
        # 配置 Chrome 无头模式
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--window-size=1280,1024")
        # 打开Chrome浏览器
        # self.driver = get_webdriver(options=chrome_options)
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)  # 显示等待最多10s
        self.driver.maximize_window()
        request.cls.driver = self.driver

        ui_login(self.driver)
        yield
        # 测试完成后关闭浏览器
        self.driver.close()
        # self.driver.quit()


class KeyWordLib(FieldsMiXin, InstAttrMiXin, EleAssert):

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
    def key_get(self, url_route):
        url = get_environment_url(cfg.get('saas_base_url')) + url_route
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

    def key_click_brother(self, brother_ele_loc: str, parent_ele_type: str, self_loc: str):
        """
        通过定位兄弟节点，找到目标节点并点击
        :param brother_ele_loc: 兄弟节点的定位
        :param parent_ele_type: 父节点标签类型，eg: div
        :param self_loc: 自己的定位, eg: .//span[1]
        :return:
        """
        brother_ele = self.find_element(brother_ele_loc)
        parent_ele = brother_ele.find_element(By.XPATH, f'./parent::{parent_ele_type}')
        self_ele = parent_ele.find_element(By.XPATH, self_loc)
        self_ele.click()

    def key_hover_and_click(self, hover_loc, click_loc, instance=None):
        """
        hover到元素A上，并点击旁边的元素B
        :param hover_loc: hover的元素
        :param click_loc: 点击的元素
        :param instance:
        :return:
        """
        ele_1 = self.find_element(hover_loc)
        actions = ActionChains(self.driver)
        actions.move_to_element(ele_1).perform()

        # 截屏并保存PNG
        time.sleep(0.5)
        save_png(instance)

        ele_2 = self.find_element(click_loc)
        ele_2.click()

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
        time.sleep(0.5)
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
    def key_switch_iframe(self, iframe_args):
        """
        切换内嵌弹窗
        :param self:
        :param iframe_args: ifram定位参数，如：xpath、class_name、id等
        :return:
        """
        iframe_ele = self.find_element(iframe_args)
        try:
            print(iframe_ele.tag_name)
        except:
            error_msg = f"iframe{iframe_ele}无法定位成功！"
            raise Exception(error_msg)
        self.driver.switch_to.frame(iframe_ele)


if __name__ == '__main__':
    ...
