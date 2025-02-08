# Created by 黄景涛
# DATE: 2024/10/17

import re
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from base.kdt_lib.base_mixin import BaseMiXin


class LocalMiXin(BaseMiXin):
    """ 提供字段的多样化定位方式，eg:
        1、按普通Loc定位;                                         -- 通用，本质就是按selenium提供的xpath、id、class等定位
        2、按父标签定位（一般地，对于form表单中的字段很管用）;           --需要定开，按自己公司的组件来修改_location_by_parent方法
        3、若字段组件是规范的，可以按字段中的label值，定位整个字段div     --需要定开，按自己公司的组件来修改_location_by_name方法
    """

    # 内置，收起下拉框
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

    # 内置，按字段的父表单定位
    def _location_by_parent(self, form_loc: str, field_name: str):
        """
        :param self:
        :param form_loc: 字段所在的父表单
        :param field_name: 字段名称
        :return:
        """
        form = self.driver.find_element(By.XPATH, form_loc)
        # 适配1：itsm-3.x版本的工单字段
        ticket_v3_fields = form.find_elements(By.XPATH, './/div[contains(@class, "bk-form-item")]')
        # 适配2：itsm-4.x版本的工单字段、ACMDB-6.x
        ticket_v4_fields = form.find_elements(By.XPATH, './/div[contains(@class, "field-form-item")]')
        # 适配3：itsm-4.x版本的dialog表单字段
        dialog_fields = form.find_elements(By.XPATH, './/div[contains(@class, "bk-form-item")]')
        # 还可以添加其他适配...
        fields = ticket_v4_fields or dialog_fields or ticket_v3_fields
        for field in fields:
            if field_name in field.text:
                return field
        raise Exception(f'不存在字段【{field_name}】')

    # 内置，按字段label名称定位
    def _location_by_name(self, field_label_name: str):
        """
        :param self:
        :param field_label_name: 字段的label名称
        :return:
        """
        span_name_loc = '//label[@class="bk-label"]/span'  # 配置管理中心V6.x
        spans = self.driver.find_elements(By.XPATH, span_name_loc)
        target_span = None
        for s in spans:
            if field_label_name in s.text:
                target_span = s
                break

        if target_span is None:
            raise Exception(f'未找到名称为【{field_label_name}】的字段！')

        # 向上找 “div>label>span” span的父标签
        label = target_span.find_element(By.XPATH, './ancestor::label[1]')
        field = label.find_element(By.XPATH, './parent::div')
        return field

    # 内置，按实例属性名定位
    def _location_by_att_name(self, field_att_name: str):
        """
        实例新增页面的属性定位
        :param self:
        :param field_att_name: 实例属性的名称
        :return:
        """
        # 配置管理中心V6.x  --实例属性详情页\实例新增页\批量更新页
        span_name_loc = "//div[@class='property-label-wrapper']/span[contains(@class, 'property-label')]"
        spans = self.driver.find_elements(By.XPATH, span_name_loc)
        target_span = None
        for s in spans:
            if field_att_name in s.text:
                target_span = s
                break

        if target_span is None:
            raise Exception(f'未找到名称为【{field_att_name}】的字段！')

        # 向上找 “div>div>span” span的父标签
        label = target_span.find_element(By.XPATH, './ancestor::div[1]')
        field = label.find_element(By.XPATH, './parent::div')

        # 不包含label的文本域
        field_area = field.find_element(By.XPATH, './/div[@class="property-value"]')
        return field_area

    # 内置，按普通方式定位字段
    def _location_by_loc(self, loc):
        """
        :param self:
        :param loc: 定位参数
        :return:
        """
        return self.find_element(loc)

    def located_field(self, type_args):
        """
        定位字段的统一入口函数
        :param type_args: 定位参数, 包含定位方式、参数
        :return: WebElement对象
        """
        # 正则匹配逗号，但忽略在方括号内的逗号
        pattern = re.compile(r',\s*(?![^\[]*])')
        # 正则分割
        loc_type, *args = pattern.split(type_args.replace('，', ','))
        loc_function_name = '_location_' + loc_type.strip()

        try:
            location_function = getattr(self, loc_function_name)
        except AttributeError as e:
            raise Exception(f'loc_type参数错误, {self.__class__.__name__}中找不到【{loc_function_name}】,e: {e}')

        field = location_function(*args)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)  # 元素滚动到视图的正中间
        return field


class AttrLocalMiXin(LocalMiXin):
    """ 定开：模型实例的属性定位 """

    def _location_by_att_name(self, field_att_name: str):
        """
        实例属性详情页中的属性定位
        :param field_att_name: 实例属性的名称
        :return: 属性字段的名称元素
        """
        att_name_loc = "//div[@class='property-name']"  # 配置管理中心V6.x  --实例属性详情页
        property_names = self.driver.find_elements(By.XPATH, att_name_loc)
        target_name_ele = None
        for n in property_names:
            if field_att_name in n.text:
                target_name_ele = n
                break

        if target_name_ele is None:
            raise Exception(f'未找到名称为【{field_att_name}】的属性！')

        try:
            # 向上找父标签  -- 实例列表中，实例属性详情页
            field = target_name_ele.find_element(By.XPATH, './parent::form')
        except NoSuchElementException:
            # 向上找父标签  -- 拓扑节点的实例属性详情页
            field = target_name_ele.find_element(By.XPATH, './parent::div')
        except Exception:
            raise
        return field
