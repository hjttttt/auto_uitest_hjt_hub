# Created by 黄景涛
# DATE: 2024/10/29

import abc
import time

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from base.kdt_lib.local_mixin import LocalMiXin
from config.settings import ROOT_PATH
from utils.log_helper.logger import logger
from utils.screenshot.picture_tool import save_png

""" 组件库， 提供给关键字调用 """


class BasicComponent(LocalMiXin):
    """ 提供组件的公共属性和功能 """

    input_loc = None
    clear_icon_loc = None

    def hover(self, input_wrapper: WebElement):
        """ hover至输入框 """
        actions = ActionChains(self.driver)
        actions.move_to_element(input_wrapper).perform()

    def clear(self, input_wrapper: WebElement, clear_icon_loc):
        """ 清空输入框 """
        try:
            self.hover(input_wrapper)
            clear_icon = input_wrapper.find_element(By.XPATH, clear_icon_loc)
            clear_icon.click()
        except NoSuchElementException:
            logger.info('值本来就是空的，无需清空')
            pass

    # 收起下拉框
    def _back_up(self, select_ele):
        """ 收起下拉 """
        # 获取WebElement实例的宽、高
        width, height = select_ele.rect['width'], select_ele.rect['height']
        # 余量，单位：px，起到微调作用
        margin = 1
        offset_xy = (-(width // 2 + margin), (height // 2 + margin))
        actions = ActionChains(self.driver)
        # 光标移动到下拉框的左上角，然后单击
        actions.move_to_element_with_offset(select_ele, *offset_xy).click().perform()

    @classmethod
    def check_class_val(cls, element: WebElement, val) -> bool:
        """ class中是否有val值 """
        is_exist = element.get_attribute("class").find(val) != -1
        return is_exist

    @classmethod
    def check_style_val(cls, element: WebElement, val) -> bool:
        """ class中是否有style值 """
        style_val = element.get_attribute("style")
        if not style_val:
            is_exist = False
        else:
            is_exist = element.get_attribute("style").find(val) != -1
        return is_exist


class SingleChar(BasicComponent):
    """ 短字符 """

    input_loc = ".//div[1]/input"
    clear_icon_loc = ".//div[2]/i"

    def input_box(self, input_wrapper: WebElement, content=None):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param content: 输入内容
        :return:
        """
        input_ = input_wrapper.find_element(By.XPATH, self.input_loc)

        # 先尝试清空值
        self.clear(input_wrapper, self.clear_icon_loc)

        if content is not None:
            input_.send_keys(content)


class LongChar(SingleChar):
    """ 长字符 """
    input_loc = ".//div[1]/textarea"


class Int(BasicComponent):
    """ 数字 """
    input_loc = ".//div/input"

    def input_box(self, input_wrapper: WebElement, content=None):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param content: 输入内容
        :return:
        """
        input_ = input_wrapper.find_element(By.XPATH, self.input_loc)
        if content is not None:
            input_.clear()
            input_.send_keys(content)


class Float(Int):
    """ 浮点数 """


class Eum(BasicComponent):
    """ 枚举 """

    # 选项集
    options_ul_loc = '//div[@class="bk-options-wrapper"]/ul'
    # li元素
    lis_loc = './/li'

    def input_box(self, input_wrapper: WebElement, option=None, instance=None, auto_unfold=False):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param option: 枚举选项，eg: 1;  eg: 选项1
        :param instance: 所在的Test类实例
        :param auto_unfold: 是否自动展开
        :return:
        """
        # 检查是否自动展开
        if not auto_unfold:
            input_wrapper.click()
            self.key_sleep(0.5)

        # 截屏并保存PNG
        save_png(instance)

        try:
            ul_ele = self.find_element(self.options_ul_loc)
            lis = ul_ele.find_elements(By.XPATH, self.lis_loc)
            try:
                lis[int(option) - 1].click()
            except IndexError:
                raise Exception(f'选项索引【{option}】越界')
            except ValueError:
                for li in lis:
                    if option in li.text:
                        li.click()
                        break
                else:
                    raise Exception(f'选项【{option}】不存在！')
        except:
            raise


class List(Eum):
    """ 列表 """


class Date(SingleChar):
    """ 日期 """

    input_loc = ".//div/input"
    clear_icon_loc = ".//div/i"

    def input_box(self, input_wrapper: WebElement, content=None):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param content: 输入内容
        :return:
        """
        input_ = input_wrapper.find_element(By.XPATH, self.input_loc)

        # 先尝试清空值
        try:
            self.hover(input_wrapper)
            clear_icon = input_wrapper.find_element(By.XPATH, self.clear_icon_loc)
            clear_icon.click()
        except NoSuchElementException:
            logger.info('条件值本来就是空的，无需清空')
            pass

        if content is not None:
            cleaned_content = content.replace('"', '').replace('“', '')
            input_.send_keys(cleaned_content)


class DateTime(Date):
    """ 日期时间 """


class User_BK(BasicComponent):
    """ 用户 """

    clear_icon_loc = './/div/span[contains(@class, "bk-select-clear")]'
    # 下拉人员中的选项集
    options_ul_loc = '//div[@class="bk-options-wrapper"]/ul'
    # 搜索框
    search_input_loc = '//div[@class="bk-select-search-wrapper"]/input'

    def input_box(self, input_wrapper: WebElement, options=None, search_for: str = None, sleep_sec=2, instance=None,
                  auto_unfold=False):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param options: 多个选项， eg: product,hjt; eg: 1,2,3; eg: all
        :param search_for: 搜索关键词
        :param sleep_sec: 等待n秒
        :param instance: 所在的Test类实例
        :param auto_unfold: 是否自动展开
        :return:
        """
        # 先尝试清空值
        try:
            self.hover(input_wrapper)
            clear_icon = input_wrapper.find_element(By.XPATH, self.clear_icon_loc)
            clear_icon.click()
        except NoSuchElementException:
            logger.info('条件值本来就是空的，无需清空')
            pass

        # 等待下拉框可点击
        field = input_wrapper.find_element(By.TAG_NAME, 'div')
        self.wait_element_no_attr_value(field, attr_type='class', value="is-loading")

        # 检查是否自动展开
        if not auto_unfold:
            field.click()
        try:
            if search_for is not None:
                self.key_sleep(sleep_sec)
                # 内部搜索框对象
                input_ele = self.driver.find_element(By.XPATH, self.search_input_loc)
                input_ele.send_keys(search_for)
                self.key_sleep(sleep_sec)
                self.wait_element_no_attr_value(field, attr_type='class', value="is-loading")
                # 截屏并保存PNG
                save_png(instance)

            ul_ele = self.find_element(self.options_ul_loc)
            lis = ul_ele.find_elements(By.TAG_NAME, 'li')

            if options.strip() == 'all':
                target_lis = lis
            else:
                try:
                    idxs = [int(idx) - 1 for idx in options.strip().replace('，', ',').split(',')]
                    target_lis = [lis[i] for i in idxs]
                except ValueError:
                    option_names = [name.strip() for name in options.strip().replace('，', ',').split(',')]
                    target_lis = []
                    for name in option_names:
                        for li in lis:
                            if name in li.text:
                                target_lis.append(li)
                                break
                        else:
                            not_find_msg = f"【{name}】选项未找到，跳过勾选"
                            logger.info(not_find_msg)

            for li in target_lis:
                li.click()

            # 截屏并保存PNG
            save_png(instance)

        except:
            raise
        finally:
            self._back_up(input_wrapper)


class Organization(BasicComponent):
    """ 组织 """

    # 清空按钮
    clear_icon_loc = './/i[contains(@class, "select-clear")]'

    # 组织树
    tree_loc = '//div[@class="bk-select-dropdown-content"]/div[@class="bk-options-wrapper"]/ul/div[contains(@class, ' \
               '"bk-big-tree")]'
    # 搜索框
    search_input_loc = '//div[@class="bk-select-dropdown-content"]/div[@class="bk-select-search-wrapper"]/input'
    # 节点 - 勾选框
    radio_loc = './/div/span[@class="node-checkbox"]'
    # 节点 - 展开按钮
    expand_icon_loc = './/div/i[contains(@class, "node-folder-icon")]'

    def input_box(self, input_wrapper: WebElement, option_loc=None, search_for: str = None, is_expand='True',
                  instance=None, auto_unfold=False):
        """
        :param input_wrapper:  包囊组件的父级WebElement
        :param option_loc:  组织节点的定位
        :param search_for:  关键字搜索
        :param is_expand:  是否展开全部节点
        :param instance:  Test类的实例
        :param auto_unfold:  是否自动展开下拉框
        :return:
        """
        # 检查是否自动展开
        self.key_sleep(0.5)
        if not auto_unfold:
            input_wrapper.click()
            self.key_sleep(0.5)

        loading_loc = getattr(self, 'loading_loc', None)
        if loading_loc is not None:
            # 等待loading完成
            self.key_sleep_until_unloading(loading_loc)

        try:
            if search_for is not None:
                # 内部搜索框对象
                input_ele = self.driver.find_element(By.XPATH, self.search_input_loc)
                input_ele.send_keys(search_for)
                # 等待
                self.key_sleep(2)  # 必须2s以上，不然无法展开树
                # 截屏并保存PNG
                save_png(instance)
            else:
                raise Exception(f'search_for参数不能为空！')

            if is_expand.strip().lower() == 'true':
                # 展开组织树
                tree_ele = self.find_element(self.tree_loc)
                self.expanded_node_tree(tree_ele)
                # 截屏并保存PNG
                save_png(instance)

            # 勾选目标组织
            self.key_sleep(0.5)
            target_node_ele = self.driver.find_element(By.XPATH, option_loc)
            radio_box = target_node_ele.find_element(By.XPATH, self.radio_loc)
            if not self.check_class_val(radio_box, 'is-checked'):
                radio_box.click()
                # 截屏并保存PNG
                save_png(instance)
        except:
            raise

    def expanded_node_tree(self, tree_ele):
        """ 展开组织树 """
        while True:
            try:
                # 获取未展开的节点
                not_expanded_nodes = [node for node in tree_ele.find_elements(By.XPATH, './/div[contains(@id, '
                                                                                        '"bk-big-tree-")]') if
                                      not self.is_expanded(node)]
                if not not_expanded_nodes:
                    break

                # 循环处理每个节点展开
                for node in not_expanded_nodes:
                    self.node_expanded(node)
            except TimeoutException:
                raise

    def node_expanded(self, node: WebElement) -> None:
        """ 节点展开 """
        # 点击展开当前节点
        expand_icon = node.find_element(By.XPATH, self.expand_icon_loc)
        expand_icon.click()
        loading_loc = getattr(self, 'loading_loc', None)
        if loading_loc is not None:
            # 等待loading完成
            self.key_sleep_until_unloading(loading_loc)
        self.key_sleep(0.5)

    def is_expanded(self, node: WebElement) -> bool:
        """ 检查节点是否可展开 """
        # 父节点（已经展开过）或者叶子节点
        been_expanded_vals = ['is-expand', 'is-leaf']

        expanded_flag = any(self.check_class_val(node, val) for val in been_expanded_vals)
        return expanded_flag


class Bool(BasicComponent):
    """ 布尔 """

    input_loc = './/div[contains(@class, "bk-switcher")]'
    on_off = {'on': 'is-checked', 'off': 'is-unchecked'}

    def input_box(self, input_wrapper: WebElement, set_status: str, instance=None):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param set_status: 设置开关状态
        :param instance: 所在的Test类实例
        :return:
        """
        switch_ele = input_wrapper.find_element(By.XPATH, self.input_loc)

        # 截屏并保存PNG
        save_png(instance)

        # on_off参数校验
        set_status = set_status.strip().lower()
        if set_status not in self.on_off:
            raise Exception(f'【{set_status}】bool开关传值错误，请传入正确参数，参考：{tuple(self.on_off.keys())}')

        # 检查class值： is-checked, 开; is-unchecked, 关
        is_on = switch_ele.get_attribute("class").find(self.on_off.get('on')) != -1
        if is_on:
            current_status = 'on'
        else:
            current_status = 'off'

        # 若设置值与当前值不一致，则切换开关
        if set_status != current_status:
            switch_ele.click()

        # 截屏并保存PNG
        save_png(instance)


class TimeZone(BasicComponent):
    """ 时区 """

    # 下拉选项集
    options_ul_loc = '//div[@class="bk-options-wrapper"]/ul'
    # 搜索框
    search_input_loc = '//div[@class="bk-select-search-wrapper"]/input'
    # li元素
    lis_loc = './/li'

    # # 勾选框 - 废弃
    # check_loc = './/label[@class="bk-form-checkbox"]'

    def input_box(self, input_wrapper: WebElement, options=None, search_for: str = None, instance=None,
                  auto_unfold=False):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param options: 1个或多个选项，eg: 选项1,选项2; eg: 1,2; eg: all
        :param search_for: 关键词搜索
        :param instance: 所在的Test类实例
        :param auto_unfold: 是否自动展开
        :return:
        """

        # 检查是否自动展开
        if not auto_unfold:
            input_wrapper.click()
            self.key_sleep(0.5)

        if search_for is not None:
            # 内部搜索框对象
            input_ele = self.driver.find_element(By.XPATH, self.search_input_loc)
            input_ele.send_keys(search_for)
            self.key_sleep(1)
            # 截屏并保存PNG
            save_png(instance)

        try:
            ul_ele = self.find_element(self.options_ul_loc)
            lis = ul_ele.find_elements(By.XPATH, self.lis_loc)

            options = str(options)
            if options.strip() == 'all':
                target_lis = lis
            else:
                try:
                    idxs = [int(idx) - 1 for idx in options.strip().replace('，', ',').split(',')]
                    target_lis = [lis[i] for i in idxs]
                except ValueError:
                    option_names = [name.strip() for name in options.strip().replace('，', ',').split(',')]
                    target_lis = []
                    for name in option_names:
                        for li in lis:
                            if name in li.text:
                                target_lis.append(li)
                                break
                        else:
                            not_find_msg = f"【{name}】选项未找到，跳过勾选"
                            logger.info(not_find_msg)

            for li in target_lis:
                # li.find_element(By.XPATH, self.check_loc).click()     # 废弃
                li.click()
        except:
            raise
        finally:
            # 截屏并保存PNG
            save_png(instance)
            self._back_up(input_wrapper)


class BaseSelect(BasicComponent):
    """ 通用下拉框 """

    # 选项集面板
    options_ul_loc = '//div[@class="bk-options-wrapper"]/ul'
    # 搜索框
    search_input_loc = '//div[@class="bk-select-search-wrapper"]/input'
    # 清空icon
    clear_icon_loc = './/span[contains(@class, "bk-select-clear")]'
    # li元素
    lis_loc = './/li'

    def input_box(self, input_wrapper: WebElement, options=None, search_for=None, instance=None, auto_unfold=False):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param options: 选项，eg: 1;  eg: 选项1
        :param search_for: 搜索选项名称
        :param instance: 所在的Test类实例
        :param auto_unfold: 是否自动展开
        """
        # 检查是否自动展开
        if not auto_unfold:
            input_wrapper.click()
            time.sleep(0.5)

        # 截屏并保存PNG
        save_png(instance)

        # 搜索
        if search_for is not None:
            self.search(search_for)

        # 获取所有lis
        lis = self.get_lis()
        try:
            # 查找并处理options
            self.handle_options(options, lis, instance=instance)
        except:
            raise
        finally:
            self._back_up(input_wrapper)

    def search(self, search_for: str, sleep_sec: float = 0):
        """ 组件内搜索, 支持重写 """
        # 内部搜索框对象
        self.key_sleep(sleep_sec)
        search_input_ele = self.driver.find_element(By.XPATH, self.search_input_loc)
        search_input_ele.send_keys(search_for)
        self.key_sleep(sleep_sec)

    def get_lis(self):
        """ 获取所有的li, 支持重写 """
        ul_ele = self.find_element(self.options_ul_loc)
        lis = ul_ele.find_elements(By.XPATH, self.lis_loc)
        return lis

    def handle_options(self, options, lis, instance=None):
        """
        查找匹配的选项
        :param options: 目标选项列表
        :param lis: li元素列表
        :param instance: 所在的Test类实例
        :return:
        """
        if not len(lis):
            null_error = "搜索结果为空，或暂无选项"
            raise Exception(null_error)

        options = str(options).strip().replace('，', ',').split(',')
        n = len(options)
        if n == 1 and options[0] != 'all':
            # 单选项
            target_lis = self.match_one(options, lis)
            target_lis[0].click()
        else:
            # 多选项
            target_lis = self.match_many(options, lis)
            for li in target_lis:
                if self.check_class_val(li, 'is-selected'):
                    logger.info(f'{li.text}已被勾选，忽略')
                    continue
                li.click()
                # 截屏并保存PNG
                save_png(instance)

    @staticmethod
    def match_one(ops, lis):
        """单选项匹配"""
        op = ops[0]
        target_lis = []
        try:
            li = lis[int(op) - 1]
        except IndexError:
            raise IndexError(f'索引【{op}】越界')
        except ValueError:
            for i in lis:
                if op in i.text:
                    li = i
                    break
            else:
                raise Exception(f'选项【{op}】不存在')

        target_lis.append(li)
        return target_lis

    @staticmethod
    def match_many(ops, lis):
        """多个选项匹配"""
        target_lis = []

        if ops[0] == 'all':
            target_lis = lis
            return target_lis

        try:
            op_ids = [int(i) - 1 for i in ops]
            target_lis = [lis[i] for i in op_ids]
        except ValueError:
            op_names = [n.strip() for n in ops]
            for name in op_names:
                for li in lis:
                    if name in li.text:
                        target_lis.append(li)
                        break
                else:
                    logger.info(f'【{name}】选项不存在，跳过勾选')
        except:
            raise

        return target_lis


class SelectWithDisplayOps(BaseSelect):
    """ 筛选选项后，非目标li依旧存在，仅变更style的display值"""

    def get_lis(self):
        lis = super().get_lis()
        lis = [li for li in lis if not self.check_style_val(li, 'display: none')]
        return lis


class SelectWithApi(BaseSelect):
    """ 需要调用API查询筛选选项"""

    def search(self, search_for: str, sleep_sec: float = 2):
        super().search(search_for=search_for, sleep_sec=sleep_sec)


class SelectWithGroup(BaseSelect):
    """ 选项被分组的下拉框"""

    # li元素
    lis_loc = './/li[@class="bk-option-group"]'

    def handle_options(self, options, lis, instance=None):
        # 处理options
        options = str(options).strip().replace('，', ',').split(',')
        for ops in options:
            group_name, ops_name = ops.split('::')
            for group_li in lis:
                if self.find_group(group_li, group_name):
                    ops_li = self.find_ops_li(group_li, ops_name)
                    if ops_li != -1:
                        ops_li.click()

    @staticmethod
    def find_group(group_li: WebElement, g_name):
        group_name_loc = './/div[@class="bk-option-group-name"]'
        group_name_ele = group_li.find_element(By.XPATH, group_name_loc)
        return g_name in group_name_ele.text

    @staticmethod
    def find_ops_li(group_li: WebElement, ops_name):
        ops_li_loc = './/ul/li'
        ops_lis = group_li.find_elements(By.XPATH, ops_li_loc)
        for ops_li in ops_lis:
            if ops_name in ops_li.text:
                return ops_li
        return -1


class User(BaseSelect):

    def input_box(self, input_wrapper: WebElement, options=None, search_for=None, instance=None, auto_unfold=False):
        # 先尝试清空值
        try:
            self.hover(input_wrapper)
            clear_icon = input_wrapper.find_element(By.XPATH, self.clear_icon_loc)
            clear_icon.click()
        except NoSuchElementException:
            logger.info('条件值本来就是空的，无需清空')
            pass

        # 等待下拉框可点击
        field = input_wrapper.find_element(By.TAG_NAME, 'div')
        self.wait_element_no_attr_value(field, attr_type='class', value="is-loading")

        # super().input_box(input_wrapper=input_wrapper, options=options, search_for=search_for, instance=instance,
        #                   auto_unfold=auto_unfold)

        # 检查是否自动展开
        if not auto_unfold:
            input_wrapper.click()
            time.sleep(0.5)

        # 截屏并保存PNG
        save_png(instance)

        # 搜索
        if search_for is not None:
            self.search(search_for)
            self.wait_element_no_attr_value(field, attr_type='class', value="is-loading")

        # 获取所有lis
        lis = self.get_lis()
        try:
            # 查找并处理options
            self.handle_options(options, lis, instance=instance)
        except:
            raise
        finally:
            self._back_up(input_wrapper)

    def search(self, search_for: str, sleep_sec: float = 1):
        super().search(search_for=search_for, sleep_sec=sleep_sec)


# # =============================================== ITSM合并过来的 =====================================================
class Text(BasicComponent):
    """ 单行文本 """
    input_loc = './/div[1]/input'
    clear_icon_loc = ".//div[2]/i"

    def input_box(self, input_wrapper: WebElement, content=None):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param content: 输入内容
        :return:
        """
        input_ = input_wrapper.find_element(By.XPATH, self.input_loc)

        # 先尝试清空值
        self.clear(input_wrapper, self.clear_icon_loc)

        if content is not None:
            input_.send_keys(content)

    # 动作：输入并回车查询
    def input_and_enter(self, input_wrapper: WebElement, content=None):
        input_ = input_wrapper.find_element(By.XPATH, self.input_loc)

        # 先尝试清空值
        self.clear(input_wrapper, self.clear_icon_loc)

        if content is not None:
            input_.send_keys(content + Keys.ENTER)


class Textarea(Text):
    """ 多行文本 """
    input_loc = ".//div[1]/textarea"


class Number(BasicComponent):
    """ 数值 """
    input_loc = ".//div/input"

    def input_box(self, input_wrapper: WebElement, content=None):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param content: 输入内容
        :return:
        """
        input_ = input_wrapper.find_element(By.XPATH, self.input_loc)

        if content is not None:
            input_.send_keys(content)


class Radio(BasicComponent):
    """ 单选框 """

    # 组件最小原子
    input_loc = './/div[contains(@class, "bk-form-radio-group")]'

    def input_box(self, input_wrapper: WebElement, option=None):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param option: 选项，eg: 选项1; eg: 1;
        :return:
        """
        radio_group_ele = input_wrapper.find_element(By.XPATH, self.input_loc)
        lis = radio_group_ele.find_elements(By.TAG_NAME, 'label')

        try:
            lis[int(option) - 1].click()
        except IndexError:
            raise IndexError(f'选项位置索引{option}越界')
        except ValueError:
            for li in lis:
                if option in li.text:
                    li.click()
                    break
            else:
                raise Exception(f'选项【{option}】不存在')


class Checkbox(BasicComponent):
    """ 复选框 """

    # 组件最小原子
    input_loc = './/div[contains(@name, "bk-checkbox-group")]'

    def input_box(self, input_wrapper: WebElement, options=None):
        """
        :param self:
        :param input_wrapper: 包囊组件的父级WebElement
        :param options: 目标选项, e.g: 1,2,4   e.g:选项1，选项2
        :return:
        """
        checkbox_group_ele = input_wrapper.find_element(By.XPATH, self.input_loc)
        lis = checkbox_group_ele.find_elements(By.TAG_NAME, 'label')

        if options.strip() == 'all':
            target_lis = lis
        else:
            options = options.strip().replace('，', ',').split(',')
            try:
                idxs = [int(idx) - 1 for idx in options]
                target_lis = [lis[i] for i in idxs]
            except ValueError:
                option_names = [name.strip() for name in options]
                target_lis = []
                for name in option_names:
                    for li in lis:
                        if name in li.text:
                            target_lis.append(li)
                            break
                    else:
                        logger.info(f"选项【{name}】未找到，跳过勾选")

        for li in target_lis:
            if self.check_class_val(li, 'is-checked'):
                logger.info(f'{li.text}已被勾选，忽略')
                continue
            li.click()


class Select(BasicComponent):
    """ 单选下拉 """

    # 选项集面板
    options_ul_loc = '//div[@class="bk-options-wrapper"]/ul'
    # 搜索框
    search_input_loc = '//div[@class="bk-select-search-wrapper"]/input'
    # 清空icon
    clear_icon_loc = './/span[contains(@class, "bk-select-clear")]'
    # li元素
    lis_loc = './/li'

    def input_box(self, input_wrapper: WebElement, option=None, instance=None, auto_unfold=False):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param option: 选项，eg: 1;  eg: 选项1
        :param instance: 所在的Test类实例
        :param auto_unfold: 是否自动展开
        """
        # 检查是否自动展开
        if not auto_unfold:
            input_wrapper.click()
            time.sleep(0.5)

        # 截屏并保存PNG
        save_png(instance)

        ul_ele = self.find_element(self.options_ul_loc)
        lis = ul_ele.find_elements(By.XPATH, self.lis_loc)

        if not len(lis):
            null_error = "搜索结果为空，或暂无选项"
            raise Exception(null_error)

        try:
            lis[int(option) - 1].click()
        except IndexError:
            raise IndexError(f'选项索引【{option}】越界')
        except ValueError:
            for li in lis:
                if option in li.text:
                    li.click()
                    break
            else:
                raise Exception(f'选项【{option}】不存在')
        except:
            raise
        finally:
            self._back_up(input_wrapper)


class MultiSelect(Select):
    """ 多选下拉 """

    # 勾选框
    # check_loc = './/label[@class="bk-form-checkbox"]'

    def input_box(self, input_wrapper: WebElement, options: str = None, instance=None, auto_unfold=False):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param options: 多个选项，eg: 1,2;  eg: 选项1,选项2； eg: all
        :param instance: 所在的Test类实例
        :param auto_unfold: 是否自动展开输入框
        :return:
        """

        # 检查是否自动展开
        if not auto_unfold:
            input_wrapper.click()
            time.sleep(0.5)

        # 截屏并保存PNG
        save_png(instance)

        options_ul_ele = self.driver.find_element(By.XPATH, self.options_ul_loc)
        lis = options_ul_ele.find_elements(By.XPATH, self.lis_loc)

        try:
            if options.strip() == 'all':
                target_lis = lis
            else:
                options = options.strip().replace('，', ',').split(',')
                try:
                    idxs = [int(idx) - 1 for idx in options]
                    target_lis = [lis[i] for i in idxs]
                except ValueError:
                    option_names = [name.strip() for name in options]
                    target_lis = []
                    for name in option_names:
                        for li in lis:
                            if name in li.text:
                                target_lis.append(li)
                                break
                        else:
                            not_find_msg = f"【{name}】选项未找到，跳过勾选"
                            logger.info(not_find_msg)

            for li in target_lis:
                if self.check_class_val(li, 'is-selected'):
                    logger.info(f'{li.text}已被勾选，忽略')
                    continue
                # li.find_element(By.XPATH, self.check_loc).click()
                li.click()
                # 截屏并保存PNG
                save_png(instance)
        except:
            raise
        finally:
            self._back_up(input_wrapper)


class DynamicSelect(Select):
    """ 可搜索的单选/多选下拉  -- 仅支持搜索后动态更新ul的li """

    def input_box(self, input_wrapper: WebElement, options: str = None, search_for: str = None, instance=None,
                  auto_unfold=False):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param options: 多个选项，eg: 1,2;  eg: 选项1,选项2； eg: all
        :param search_for: 搜索关键字
        :param instance: 所在的Test类实例
        :param auto_unfold: 是否自动展开输入框
        :return:
        """

        # 检查是否自动展开
        if not auto_unfold:
            input_wrapper.click()
            self.key_sleep(0.5)

        # 搜索
        if search_for is not None:
            self.search(search_for)
            # 截屏并保存PNG
            save_png(instance)

        options_ul_ele = self.driver.find_element(By.XPATH, self.options_ul_loc)
        lis = options_ul_ele.find_elements(By.XPATH, self.lis_loc)

        try:
            options = str(options)
            if options.strip() == 'all':
                target_lis = lis
            else:
                options = options.strip().replace('，', ',').split(',')
                try:
                    idxs = [int(idx) - 1 for idx in options]
                    target_lis = [lis[i] for i in idxs]
                except ValueError:
                    option_names = [name.strip() for name in options]
                    target_lis = []
                    for name in option_names:
                        for li in lis:
                            if name in li.text:
                                target_lis.append(li)
                                break
                        else:
                            not_find_msg = f"【{name}】选项未找到，跳过勾选"
                            logger.info(not_find_msg)

            for li in target_lis:
                if self.check_class_val(li, 'is-selected'):
                    logger.info(f'{li.text}已被勾选，忽略')
                    continue
                li.click()
                # 截屏并保存PNG
                save_png(instance)
        except:
            raise
        finally:
            self._back_up(input_wrapper)

    def search(self, search_for: str, sleep_sec: float = 1):
        """ 组件内搜索 """
        # 内部搜索框对象
        search_input_ele = self.driver.find_element(By.XPATH, self.search_input_loc)
        search_input_ele.send_keys(search_for)
        self.key_sleep(sleep_sec)


class User1(Select):
    """ 单选人员 """

    def input_box(self, input_wrapper: WebElement, option=None, search_for: str = None, sleep_sec=1, instance=None,
                  auto_unfold=False):
        """
        :param self:
        :param input_wrapper: 包囊组件的父级WebElement
        :param option: 目标选项，e.g: 人员名称、索引
        :param search_for: 搜索关键字
        :param sleep_sec: 搜索后等待
        :param instance: 所在的Test类实例
        :param auto_unfold: 是否自动展开输入框
        :return:
        """
        # 检查是否自动展开
        if not auto_unfold:
            input_wrapper.click()

        if search_for is not None:
            self.search(search_for, sleep_sec)

        super().input_box(input_wrapper, option, instance=instance, auto_unfold=True)

    def search(self, search_for: str, sleep_sec: float):
        """ 组件内搜索 """
        self.key_sleep(sleep_sec)
        # 内部搜索框对象
        search_input_ele = self.driver.find_element(By.XPATH, self.search_input_loc)
        search_input_ele.send_keys(search_for)
        self.key_sleep(sleep_sec)


class MultiUser(MultiSelect):
    """ 多选人员"""

    def input_box(self, input_wrapper: WebElement, options=None, search_for: str = None, sleep_sec=1, instance=None,
                  auto_unfold=False):
        """
        :param self:
        :param input_wrapper: 包囊组件的父级WebElement
        :param options: 多个选项，e.g: 人员名称、索引
        :param search_for: 搜索关键字
        :param sleep_sec: 搜索后等待
        :param instance: 所在的Test类实例
        :param auto_unfold: 是否自动展开输入框
        :return:
        """
        # 检查是否自动展开
        if not auto_unfold:
            input_wrapper.click()

        if search_for is not None:
            self.search(search_for, sleep_sec)

        super().input_box(input_wrapper, options, instance=instance, auto_unfold=True)

    def search(self, search_for: str, sleep_sec: float):
        """ 组件内搜索 """
        self.key_sleep(sleep_sec)
        # 内部搜索框对象
        search_input_ele = self.driver.find_element(By.XPATH, self.search_input_loc)
        search_input_ele.send_keys(search_for)
        self.key_sleep(sleep_sec)


class Cascade(BasicComponent):
    """ 单选级联 """

    # 级联搜索框
    search_input_loc = './/div[@class="bk-cascade-name"]/input'
    # 级联ul选项集
    ul_loc = '//div[@class="bk-cascade-panel"]/ul[@class="bk-cascade-panel-ul"]'

    # 级联层级结构
    panels_wrap_loc = '//*[@class="bk-cascade-options"]'
    panel_structure = '/div[@class="bk-cascade-panel"]'

    def input_box(self, input_wrapper: WebElement, option: str, search_for: str = None, instance=None,
                  auto_unfold=False):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param option: 选项，eg:数字； eg:具体选项路径，如：陆路>汽车类>卡车
        :param search_for: 搜索关键字
        :param instance: Test类实例
        :param auto_unfold: 是否自动展开输入框
        :return:
        """
        # 检查是否自动展开
        if not auto_unfold:
            input_wrapper.click()
        # 截屏并保存PNG
        save_png(instance)

        try:
            if search_for is not None:
                search_input_ele = input_wrapper.find_element(By.XPATH, self.search_input_loc)
                search_input_ele.send_keys(search_for)
                ul_ele = self.driver.find_element(By.XPATH, self.ul_loc)
                lis = ul_ele.find_elements(By.TAG_NAME, 'li')
                lis[int(option) - 1].click()
            else:
                option_parser = [node.strip() for node in option.split('>')]
                for level, op_name in enumerate(option_parser, 1):
                    # 拼接出每级panel的ul
                    current_ul_loc = self.panels_wrap_loc + self.panel_structure * level + '/ul'
                    ul_ele = self.driver.find_element(By.XPATH, current_ul_loc)
                    current_li = [li for li in ul_ele.find_elements(By.TAG_NAME, 'li') if op_name in li.text][0]
                    current_li.click()
        except:
            raise
        finally:
            self._back_up(input_wrapper)


class MultiCascade(Cascade):
    """ 多选级联 """

    # 级联选框中，所有的子元素位置
    # 勾选框
    check_loc = './/div[@class="bk-cascade-check"]'

    def input_box(self, input_wrapper: WebElement, options: str, search_for: str = None, instance=None,
                  auto_unfold=False):
        """
        :param input_wrapper: 包囊组件的父级WebElement
        :param options: 多个级联选项，支持两种格式. eg: 数字1,数字2；eg: 具体选项路径，如：陆路>汽车类>卡车，水路>船类
        :param search_for: 搜索关键字
        :param instance: Test类实例
        :param auto_unfold: 是否自动展开输入框
        :return:
        """
        # 检查是否自动展开
        if not auto_unfold:
            input_wrapper.click()
        # 截屏并保存PNG
        save_png(instance)

        try:
            if search_for is not None:
                search_input_ele = input_wrapper.find_element(By.XPATH, self.search_input_loc)
                search_input_ele.send_keys(search_for)
                ul_ele = self.driver.find_element(By.XPATH, self.ul_loc)
                lis = ul_ele.find_elements(By.TAG_NAME, 'li')

                # 点击指定的li
                options = str(options).strip()

                if options == 'all':
                    target_lis = lis
                else:
                    options = options.replace('，', ',').split(',')
                    try:
                        idxs = [int(idx) - 1 for idx in options]
                        target_lis = [lis[i] for i in idxs]
                    except ValueError:
                        target_lis = []
                        for name in options:
                            for li in lis:
                                if name in li.text:
                                    target_lis.append(li)
                                    break
                            else:
                                not_find_msg = f"【{name}】选项未找到，跳过勾选"
                                logger.info(not_find_msg)

                for li in target_lis:
                    li.find_element(By.XPATH, self.check_loc).click()
            else:
                cleaned_options = options.strip().replace('，', ',').split(',')
                for option in cleaned_options:
                    option_parser = [node.strip() for node in option.split('>')]
                    for level, op_name in enumerate(option_parser, 1):
                        # 拼接出每级panel的ul
                        current_ul_loc = self.panels_wrap_loc + self.panel_structure * level + '/ul'
                        ul_ele = self.driver.find_element(By.XPATH, current_ul_loc)
                        current_li = [li for li in ul_ele.find_elements(By.TAG_NAME, 'li') if op_name in li.text][0]
                        if level == len(option_parser):
                            check_ele = current_li.find_element(By.XPATH, self.check_loc)
                            check_ele.click()
                        else:
                            current_li.click()
        except:
            raise
        finally:
            self._back_up(input_wrapper)


class File(BasicComponent):
    """ 附件 """

    # 上传文件的input
    file_input_loc = './/input[@type="file"]'

    def input_box(self, input_wrapper: WebElement, files: str, sleep_sec=1, instance=None):
        """
        :param self:
        :param input_wrapper: 包囊组件的父级WebElement， 必须是input[@type="file"]的父级
        :param files: 文件名称，用逗号分隔。 注意：需要把文件放到根目录的assets文件夹下
        :param sleep_sec: 上传间隔秒数
        :param instance: Test类实例
        :return:
        """
        input_ele = input_wrapper.find_element(By.XPATH, self.file_input_loc)
        files = [ROOT_PATH + f'/assets/{f_name.strip()}' for f_name in files.replace('，', ',').split(',')]
        for f_path in files:
            input_ele.send_keys(f_path)
            # 截屏并保存PNG
            save_png(instance)
            self.key_sleep(sleep_sec)
