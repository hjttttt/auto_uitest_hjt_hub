# Created by 黄景涛
# DATE: 2024/11/4

from base.kdt_lib.local_mixin import LocalMiXin
import base.kdt_lib.components as components

""" 定开功能： 适用于实例新增页、批量更新页 """


class InstAttrMiXin(LocalMiXin):

    def basic_field(self, type_args, component, *args, instance=None, **kwargs):
        """
        :param type_args: 复合定位参数， eg: by_att_name,实例名
        :param component: 组件类的实例对象
        :param args:
        :param instance:
        :param kwargs:
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 兼容需要传instance参数的组件
        try:
            component.input_box(field, *args, **kwargs, instance=instance)
        except TypeError:
            component.input_box(field, *args, **kwargs)

    def key_singlechar(self, type_args, content=None):
        component = components.SingleChar(self.driver)
        self.basic_field(type_args, component, content)

    def key_longchar(self, type_args, content=None):
        component = components.LongChar(self.driver)
        component.input_loc = components.SingleChar.input_loc
        self.basic_field(type_args, component, content)

    def key_int(self, type_args, content=None):
        component = components.Int(self.driver)
        self.basic_field(type_args, component, content)

    def key_float(self, type_args, content=None):
        component = components.Float(self.driver)
        self.basic_field(type_args, component, content)

    def key_eum(self, type_args, option=None, instance=None, auto_unfold=False):
        component = components.Eum(self.driver)
        self.basic_field(type_args, component, option, instance=instance, auto_unfold=auto_unfold)

    def key_list(self, type_args, option=None, instance=None, auto_unfold=False):
        component = components.List(self.driver)
        self.basic_field(type_args, component, option, instance=instance, auto_unfold=auto_unfold)

    def key_date(self, type_args, content=None):
        component = components.Date(self.driver)
        self.basic_field(type_args, component, content)

    def key_datetime(self, type_args, content=None):
        component = components.DateTime(self.driver)
        self.basic_field(type_args, component, content)

    def key_user(self, type_args, options=None, search_for: str = None, instance=None, auto_unfold=False):
        component = components.User(self.driver)
        self.basic_field(type_args, component, options, search_for, instance=instance, auto_unfold=auto_unfold)

    def key_organization(self, type_args, option_loc=None, search_for: str = None, is_expand='True', instance=None, auto_unfold=False):
        component = components.Organization(self.driver)
        self.basic_field(type_args, component, option_loc, search_for, is_expand, instance=instance, auto_unfold=auto_unfold)

    def key_bool(self, type_args, set_status: str, instance=None):
        component = components.Bool(self.driver)
        self.basic_field(type_args, component, set_status, instance=instance)

    def key_timezone(self, type_args, options=None, search_for: str = None, instance=None, auto_unfold=False):
        component = components.TimeZone(self.driver)
        self.basic_field(type_args, component, options, search_for, instance=instance, auto_unfold=auto_unfold)
