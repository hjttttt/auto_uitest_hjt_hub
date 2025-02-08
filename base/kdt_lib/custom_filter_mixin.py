# Created by 黄景涛
# DATE: 2024/10/29
from .base_mixin import BaseMiXin

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement

import base.kdt_lib.components as components
from config.settings import ROOT_PATH
from utils.log_helper.logger import logger
from utils.screenshot.picture_tool import save_png

""" 定开功能： 适用于实例的高级搜索 """


class Filter(BaseMiXin):
    """ 实例高级筛选 """

    # 高级筛选抽屉中的筛选区域
    custom_filer_loc = '//div[@class="custom-filters"]'

    # 条件添加按钮
    add_button_loc = './/div[@class="condition-button"]'
    # 属性选择弹窗
    attr_dialog_loc = '//div[contains(@class, "bk-dialog-wrapper") and not(contains(@class, ' \
                      '"bk-dialog-hidden"))]//div[@class="bk-dialog"]'

    # 弹窗：模型分组
    obj_attr_group_loc = './/div[contains(@class, "obj-attr-group")]'
    # 弹窗：模型分组的模型名称
    obj_name_loc = './/h3'
    # 弹窗：具体属性、属性名称、属性勾选框
    attr_loc = './/div[@class="obj-attr-item"]'
    attr_label_loc = './/label'
    attr_checkbox_loc = './/label/span[@class="bk-checkbox"]'
    # 弹窗：确定按钮
    confirm_button_loc = './/div[@class="bk-dialog-footer"]//span[contains(text(),"确定")]'

    # 已添加的条件组
    condition_row_loc = './/div[@class="form-box"]'
    # 条件组名称
    condition_row_name_loc = './/div[@class="form-label"]/span'
    # 条件组的删除icon
    condition_row_del_icon_loc = './/div[@class="form-label"]/i'

    # 条件行的运算符选择框
    operator_loc = './/div[@class="form-item"]/div[contains(@class, "form-item-logic")]'
    # 条件行的输入框wrapper
    input_wrapper_loc = './/div[@class="form-item"]/div[contains(@class, "form-item-control")]'

    # 条件行中，没有运算符的组件
    exclude_components = ['DateTime', 'Date']

    def __init__(self, driver):
        super().__init__(driver)
        self.filer = self.find_element(self.custom_filer_loc)

    def key_add(self, fields: str, instance=None):
        # 点击添加按钮
        add_button = self.filer.find_element(By.XPATH, self.add_button_loc)
        add_button.click()

        # 参数处理
        fields_list = fields.strip().replace('，', ',').split(',')
        fields_list = list(map(lambda item: item.split('-'), fields_list))

        # 在属性弹窗中，依次勾选属性
        attr_dialog = self.find_element(self.attr_dialog_loc)
        obj_attr_groups = attr_dialog.find_elements(By.XPATH, self.obj_attr_group_loc)

        for field in fields_list:
            group_name = field[0].strip()
            field_name = field[1].strip()
            for obj_attr_group in obj_attr_groups:
                group_h3 = obj_attr_group.find_element(By.XPATH, self.obj_name_loc)
                # 查找匹配模型名称
                if group_name in group_h3.text:
                    current_group = obj_attr_group
                    attrs = current_group.find_elements(By.XPATH, self.attr_loc)
                    for attr in attrs:
                        # 查找匹配属性名称
                        if field_name in attr.text:
                            attr_label = attr.find_element(By.XPATH, self.attr_label_loc)
                            # 检查是否已勾选
                            if self.check_class_val(attr_label, 'is-checked'):
                                break

                            attr_checkbox = attr.find_element(By.XPATH, self.attr_checkbox_loc)
                            attr_checkbox.click()
                            # 截屏并保存PNG
                            save_png(instance)
                            break
                    else:
                        logger.error(f'{field_name}不存在，填写有误')

                    break
            else:
                logger.error(f'{group_name}不存在，填写有误')

        # 点击弹窗确定
        confirm_button = attr_dialog.find_element(By.XPATH, self.confirm_button_loc)
        confirm_button.click()

    def key_edite(self, field: str, operator: str, *args, instance=None, **kwargs):

        # 参数处理
        condition_name, component_cls_name = map(lambda item: ''.join(item.split()), field.replace('，', ',').split(','))
        # 从组件库获取对应的组件类
        component_cls = getattr(components, component_cls_name, None)
        if component_cls is None:
            msg = f'{component_cls_name}在kdt_lib/components.py中不存在'
            logger.error(msg)
            raise Exception(msg)

        # 查找条件行
        row = self.find_condition_row(condition_name)

        if component_cls_name not in self.exclude_components:
            # 选择运算符
            operator_ele = row.find_element(By.XPATH, self.operator_loc)
            components.Eum(self.driver).input_box(operator_ele, operator, instance=instance)

        # 输入条件值
        input_wrapper = row.find_element(By.XPATH, self.input_wrapper_loc)
        # 实例化组件
        component_inst = component_cls(self.driver)

        # 兼容需要传instance参数的组件
        try:
            component_inst.input_box(input_wrapper, *args, **kwargs, instance=instance)
        except TypeError:
            component_inst.input_box(input_wrapper, *args, **kwargs)

    def key_delete(self, field: str, instance=None):
        # 查找条件行
        row = self.find_condition_row(field)

        actions = ActionChains(self.driver)
        actions.move_to_element(row).perform()
        # 截屏并保存PNG
        save_png(instance)

        delete_icon = row.find_element(By.XPATH, self.condition_row_del_icon_loc)
        delete_icon.click()

    @classmethod
    def check_class_val(cls, element: WebElement, val) -> bool:
        """ class中是否有val值 """
        is_exist = element.get_attribute("class").find(val) != -1
        return is_exist

    def find_condition_row(self, row_name: str):
        condition_rows = self.filer.find_elements(By.XPATH, self.condition_row_loc)
        for row_ele in condition_rows:
            ele_name = row_ele.find_element(By.XPATH, self.condition_row_name_loc).text
            ele_name = ''.join(ele_name.split())
            row_name = ''.join(row_name.split())
            if row_name in ele_name:
                return row_ele
        else:
            raise Exception(f'条件{row_name}未找到')
