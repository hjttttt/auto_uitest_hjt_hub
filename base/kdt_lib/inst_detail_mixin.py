# Created by 黄景涛
# DATE: 2024/10/18

from abc import abstractmethod

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from base.kdt_lib.local_mixin import AttrLocalMiXin
import base.kdt_lib.components as components


""" 定开功能 - 适用于实例属性详情页 """


class BaseAttribute(AttrLocalMiXin):
    """ 实例属性详情中，属性字段 """

    # 属性字段类型
    field_type = None

    # 属性的铅笔按钮
    pen_loc = './/div[@class="property-tools"]/i[contains(@class, "cmdb-edit")]'
    # 属性的copy按钮
    copy_loc = './/div[@class="property-tools"]/i[contains(@class, "cmdb-copy")]'
    # 属性值
    property_value_loc = './/span[@class="property-value"]/span'
    # 属性写状态下，属性输入框
    input_loc_under_writable_property = './/span[@class="property-value"]/div/div[1]/div'
    # 属性写状态下，工具按钮
    tools_loc_under_writable_property = './/span[@class="property-value"]/div/div[2]'

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = None

    @abstractmethod
    def _input_box(self, *args, **kwargs):
        """ 不同类型属性的输入框处理。 eg: 下拉框处理 """
        ...

    def located_field(self, *args, **kwargs):
        """ 定位实例的属性 """
        self.field = super().located_field(*args, **kwargs)
        return self.field

    def located_pen_icon(self, type_args):
        """ 定位属性的铅笔按钮 """
        # 属性字段定位
        self.located_field(type_args)

        # 定位属性的编辑按钮（铅笔图标）
        ele: WebElement = self.field.find_element(By.XPATH, self.pen_loc)
        return ele

    def located_copy_icon(self, type_args):
        """ 定位属性的copy按钮 """
        # 属性字段定位
        self.located_field(type_args)

        # 定位属性的copy按钮
        ele: WebElement = self.field.find_element(By.XPATH, self.copy_loc)
        return ele

    # 获取属性值
    def key_get_value(self, type_args):
        """ 获取实例的属性值 """
        self.located_field(type_args)
        property_value_ele: WebElement = self.field.find_element(By.XPATH, self.property_value_loc)
        value = property_value_ele.get_attribute("title")
        return value

    # 点击copy，copy属性值
    def key_copy(self, type_args):
        """ 点击copy按钮 """
        copy_ele = self.located_copy_icon(type_args)
        copy_ele.click()

    def key_hover_on_pen(self, type_args):
        """ 定位并hover到铅笔 """
        pen_ele = self.located_pen_icon(type_args)
        self._hover_pen(pen_ele)

    # hover到铅笔按钮
    def _hover_pen(self, pen_ele):
        """ hover到铅笔 """
        actions = ActionChains(self.driver)
        actions.move_to_element(pen_ele).perform()

    # 点击铅笔，编辑属性值
    def key_edite_by_pen(self, type_args, *args, **kwargs):
        """ 点击编辑铅笔 """
        pen_ele = self.located_pen_icon(type_args)
        self._hover_pen(pen_ele)
        pen_ele.click()

        try:
            # 输入框处理
            self._input_box(*args, **kwargs)
        except:
            raise
        finally:
            # 点击✔保存
            confirm_icon_loc = self.tools_loc_under_writable_property + "/i[1]"
            confirm_ele = self.find_element(confirm_icon_loc)
            confirm_ele.click()


class SingleChar(BaseAttribute, components.SingleChar):
    def _input_box(self, content=None):
        field_input = self.find_element(self.input_loc_under_writable_property)
        super().input_box(field_input, content)


class LongChar(BaseAttribute, components.LongChar):
    """ 长字符 """
    def _input_box(self, content=None):
        field_input = self.find_element(self.input_loc_under_writable_property)
        super().input_box(field_input, content)


class Int(BaseAttribute, components.Int):
    """ 数字 """

    def _input_box(self, content=None):
        field_input = self.find_element(self.input_loc_under_writable_property)
        super().input_box(field_input, content)


class Float(Int):
    """ 浮点数 """
    ...


class Eum(BaseAttribute, components.Eum):
    """ 枚举 """

    def _input_box(self, option=None, instance=None, auto_unfold=True):
        field_input = self.find_element(self.input_loc_under_writable_property)
        super().input_box(field_input, option=option, instance=instance, auto_unfold=auto_unfold)


class List(Eum):
    """ 列表 """
    ...


class Date(BaseAttribute, components.Date):
    """ 日期 """

    def _input_box(self, content=None):
        field_input = self.find_element(self.input_loc_under_writable_property)
        super().input_box(field_input, content)


class DateTime(Date):
    """ 日期时间 """
    ...


class User(BaseAttribute, components.User):
    """ 用户 """
    loading_img_loc = '//img[@class ="bk-select-loading"]'

    def _input_box(self, options=None, search_for: str = None, instance=None, auto_unfold=False):
        field_input = self.find_element(self.input_loc_under_writable_property)

        # 等待field_input加载完成
        self.wait_element_appear_and_disappear(self.loading_img_loc)

        super().input_box(field_input, options=options, search_for=search_for, instance=instance)


class Organization(BaseAttribute, components.Organization):
    """ 组织 """

    # loading蒙层
    loading_loc = '//div[@class="select-dropdown-content"]/div[@class="bk-loading"]'
    # 组织树
    tree_loc = '//div[@class="select-dropdown-content"]/div[contains(@class, "org-tree")]'
    # 搜索框
    search_input_loc = '//div[@class="select-dropdown-content"]/div[@class="search-bar"]/div/div/input'

    def _input_box(self, option_loc=None, search_for: str = None, is_expand='True', instance=None, auto_unfold=True):
        field_input = self.find_element(self.input_loc_under_writable_property)
        super().input_box(field_input, option_loc=option_loc, search_for=search_for, is_expand=is_expand,
                          instance=instance, auto_unfold=auto_unfold)


class Bool(BaseAttribute, components.Bool):
    """ 布尔 """

    def _input_box(self, set_status: str, instance=None):
        field_input = self.find_element(self.input_loc_under_writable_property)
        super().input_box(field_input, set_status=set_status, instance=instance)


class TimeZone(BaseAttribute, components.TimeZone):
    """ 时区 """

    # li元素
    lis_loc = './/section/main/ul/li'

    def _input_box(self, option=None, search_for: str = None, instance=None, auto_unfold=True):
        field_input = self.find_element(self.input_loc_under_writable_property)
        super().input_box(field_input, options=option, search_for=search_for, instance=instance, auto_unfold=auto_unfold)


if __name__ == '__main__':
    ...
