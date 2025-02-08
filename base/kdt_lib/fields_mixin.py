# Created by 黄景涛
# DATE 2024/8/19

from base.kdt_lib.local_mixin import LocalMiXin
import base.kdt_lib.components as components


class FieldsMiXin(LocalMiXin):

    # 字段：单行文本
    def key_text_field(self, type_args, content=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param content: 输入内容
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.Text(self.driver)
        component.input_box(field, content)

    # 字段：多行文本
    def key_textarea_field(self, type_args, content=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param content: 输入内容
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.Textarea(self.driver)
        component.input_box(field, content)

    def key_number_field(self, type_args, content=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param content: 输入内容
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.Number(self.driver)
        component.input_box(field, content)

    # 字段：单选框
    def key_radio_field(self, type_args, option=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param option: 选项，e.g: 选项1   e.g: 选项索引1
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.Radio(self.driver)
        component.input_box(field, option)

    # 字段：复选框
    def key_checkbox_field(self, type_args, options=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param options: 目标选项, e.g: 1,2,4   e.g:选项1，选项2
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.Checkbox(self.driver)
        component.input_box(field, options)

    # 字段：通用下拉（支持单选、多选、搜索）
    def key_base_select_field(self, type_args, options=None, search_for=None, instance=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param options: 指定选项，两种写法：1、第n个选项，传入数字n；2、传入选项名称；
        :param search_for: 搜索选项名称
        :param instance: 所在的Test类实例
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.SelectWithDisplayOps(self.driver)
        component.input_box(field, search_for=search_for, options=options, auto_unfold=False, instance=instance)

    # 字段：api请求的下拉（支持单选、多选、搜索）
    def key_api_select_field(self, type_args, options=None, search_for=None, instance=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param options: 指定选项，两种写法：1、第n个选项，传入数字n；2、传入选项名称；
        :param search_for: 搜索选项名称
        :param instance: 所在的Test类实例
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.SelectWithApi(self.driver)
        component.input_box(field, search_for=search_for, options=options, auto_unfold=False, instance=instance)

    # 字段：人员的下拉（支持单选、多选、搜索）
    def key_user_select_field(self, type_args, options=None, search_for=None, instance=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param options: 指定选项，两种写法：1、第n个选项，传入数字n；2、传入选项名称；
        :param search_for: 搜索选项名称
        :param instance: 所在的Test类实例
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.User(self.driver)
        component.input_box(field, search_for=search_for, options=options, auto_unfold=False, instance=instance)

    # 字段：选项分组的下拉（支持单选、多选、搜索）
    def key_group_select_field(self, type_args, options=None, search_for=None, instance=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param options: 指定选项，两种写法：1、第n个选项，传入数字n；2、传入选项名称；
        :param search_for: 搜索选项名称
        :param instance: 所在的Test类实例
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.SelectWithGroup(self.driver)
        component.input_box(field, search_for=search_for, options=options, auto_unfold=False, instance=instance)

    # 字段：单选下拉
    def key_select_field(self, type_args, option=None, instance=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param option: 指定选项，两种写法：1、第n个选项，传入数字n；2、传入选项名称；
        :param instance: 所在的Test类实例
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.Select(self.driver)
        component.input_box(field, option=option, instance=instance, auto_unfold=False)

    # 字段：特殊的单选下拉（lis位置不一样）
    def key_special_select_field(self, type_args, options=None, search_for: str = None, instance=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param options: 指定选项，两种写法：1、第n个选项，传入数字n；2、传入选项名称；
        :param search_for: 搜索关键字
        :param instance: 所在的Test类实例
        :return:
        """
        # 字段
        field = self.located_field(type_args)
        # 组件实例化
        component = components.DynamicSelect(self.driver)
        component.lis_loc = './/section/main/ul/li'
        component.input_box(field, options=options, search_for=search_for, instance=instance, auto_unfold=False)

    # 字段：多选下拉
    def key_multiselect_field(self, type_args, options: str = None, instance=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param options: 多个下拉选项， e.g: 1,2   e.g: 选项1,选项3   e.g: all，表示所有
        :param instance: 所在的Test类实例
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.MultiSelect(self.driver)
        component.input_box(field, options=options, instance=instance, auto_unfold=False)

    # 字段：单选人员
    def key_user_field(self, type_args, option=None, search_for: str = None, sleep_sec=1, instance=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param search_for: 搜索关键字
        :param option: 目标选项，e.g: 人员名称、索引
        :param sleep_sec: 搜索后等待
        :param instance: 所在的Test类实例
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.User1(self.driver)
        component.input_box(field, option=option, search_for=search_for, sleep_sec=sleep_sec, instance=instance,
                            auto_unfold=False)

    # 字段：多选人员
    def key_multiuser_field(self, type_args, options=None, search_for: str = None, sleep_sec=2, instance=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param search_for: 搜索关键字
        :param options: 选项名称或选项下标，用逗号隔开，  e.g: 选项1,选项3  e.g: all
        :param sleep_sec: 搜索后等待
        :param instance: 所在的Test类实例
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.MultiUser(self.driver)
        component.input_box(field, options=options, search_for=search_for, sleep_sec=sleep_sec, instance=instance,
                            auto_unfold=False)

    # 字段：单选级联
    def key_cascade_field(self, type_args, option: str, search_for: str = None, instance=None):
        """
        :param type_args: 定位复合参数
        :param option: 选项，支持两种格式：a.数字；b.具体选项路径，如：陆路>汽车类>卡车
        :param search_for: 搜索关键字
        :param instance: Test类实例
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.Cascade(self.driver)
        component.input_box(field, option=option, search_for=search_for, instance=instance,
                            auto_unfold=False)

    # 字段：多选级联
    def key_multicascade_field(self, type_args, options: str, search_for: str = None, instance=None):
        """
        :param type_args: 定位复合参数
        :param options: 选项，支持两种格式：a.数字列表，或all；b.具体选项路径（多条），如：陆路>汽车类>卡车,水路>轮船
        :param search_for: 搜索关键字
        :param instance: Test类实例
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.MultiCascade(self.driver)
        component.input_box(field, options=options, search_for=search_for, instance=instance,
                            auto_unfold=False)

    # 字段：日期
    def key_date_field(self, type_args, content=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param content: 输入内容, 格式yyyy-mm-dd
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.Date(self.driver)
        component.input_box(field, content)

    # 字段：日期时间
    def key_datetime_field(self, type_args, content: str = None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param content: 输入内容, 格式yyyy-mm-dd hh:mm:ss
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.DateTime(self.driver)
        component.input_box(field, content)

    # 字段：附件上传
    def key_file_field(self, type_args, files: str, sleep_sec=1):
        """
        :param self:
        :param type_args: 定位复合参数
        :param files: 文件名称，用逗号分隔。 注意：需要把文件放到根目录的assets文件夹下
        :param sleep_sec: 上传间隔秒数
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 组件实例化
        component = components.File(self.driver)
        component.input_box(field, files, sleep_sec=sleep_sec)


if __name__ == '__main__':
    ...
