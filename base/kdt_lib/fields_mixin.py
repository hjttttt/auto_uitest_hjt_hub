# Created by 黄景涛
# DATE 2024/8/19
import re
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from base.kdt_lib.base_mixin import BaseMiXin
from base.kdt_lib.local_mixin import LocalMiXin
from config.settings import ROOT_PATH
from utils.logger.custom_logger import logger
from utils.screenshot.picture_util import save_png


class FieldsMiXin(LocalMiXin, BaseMiXin):
    """
    继承WebElement基础类、字段定位方式类
    """

    # 字段：单行文本
    def key_text_field(self, type_args, content=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param content: 输入内容
        :return:
        """
        # 单行文本字段中的文本框
        input_loc = './/div[contains(@class,"bk-input")]/input'

        # 字段
        field = self.located_field(type_args)
        # 字段的内部文本框
        field_input = field.find_element(By.XPATH, input_loc)
        field_input.clear()
        if content is not None:
            field_input.send_keys(content)

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

        # 多行文本字段中的文本框
        input_loc = './/div[@class="bk-textarea-wrapper"]/textarea'

        field_input = field.find_element(By.XPATH, input_loc)
        field_input.clear()
        if content is not None:
            field_input.send_keys(content)

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

        # 单选框中的选项集
        options_group_loc = './/div[contains(@class, "bk-form-radio-group")]'  # 配置管理中心V6.x

        try:
            group_ele = field.find_element(By.XPATH, options_group_loc)
            lis = group_ele.find_elements(By.TAG_NAME, 'label')
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

        # 选项集
        options_group_loc = './/div[contains(@name, "bk-checkbox-group")]'

        try:
            group_ele = field.find_element(By.XPATH, options_group_loc)
            lis = group_ele.find_elements(By.TAG_NAME, 'label')

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
        except:
            raise

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
        # 点击展开下拉框
        field.click()

        # 截屏并保存PNG
        save_png(instance)

        # 选项集面板
        options_ul_loc = '//div[@class="bk-options-wrapper"]/ul'

        try:
            ul_ele = self.find_element(options_ul_loc)
            lis = ul_ele.find_elements(By.TAG_NAME, 'li')
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
        finally:
            # 截屏并保存PNG
            save_png(instance)
            self._back_up(field)

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
        # 点击展开下拉框
        field.click()

        # 截屏并保存PNG
        save_png(instance)

        # 选项集面板
        options_ul_loc = '//div[@class="bk-options-wrapper"]/ul'
        # 勾选框
        check_loc = './/label[@class="bk-form-checkbox"]'

        try:
            ul_ele = self.find_element(options_ul_loc)
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
                li.find_element(By.XPATH, check_loc).click()
                # 截屏并保存PNG
                save_png(instance)
        except:
            raise
        finally:
            # 截屏并保存PNG
            save_png(instance)
            self._back_up(field)

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
        select = self.located_field(type_args)
        # 点击展开下拉框
        select.click()

        # 截屏并保存PNG
        save_png(instance)

        # 下拉人员中的选项集
        options_ul_loc = '//div[@class="bk-options-wrapper"]/ul'
        # 搜索框
        search_input_loc = '//div[@class="bk-select-search-wrapper"]/input'

        try:
            if search_for is not None:
                self.key_sleep(sleep_sec)
                # 内部搜索框对象
                input_ele = self.driver.find_element(By.XPATH, search_input_loc)
                input_ele.send_keys(search_for)
                self.key_sleep(sleep_sec)
                # 截屏并保存PNG
                save_png(instance)

            # 选项集ul对象
            options_ul = self.find_element(options_ul_loc)
            visible_lis = options_ul.find_elements(By.TAG_NAME, 'li')

            if not len(visible_lis):
                null_error = "暂无选项"
                raise Exception(null_error)

            try:
                option_idx = int(option)
                li_ = visible_lis[option_idx - 1]
                li_.click()
            except ValueError:
                for li in visible_lis:
                    if search_for in li.text:
                        li.click()
                        break
                else:
                    no_such_option_error = f"暂无选项【{search_for}】,【{option}】"
                    raise Exception(no_such_option_error)
        except:
            raise
        finally:
            # 截屏并保存PNG
            save_png(instance)
            self._back_up(select)

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
        select = self.located_field(type_args)
        # 点击展开下拉框
        select.click()

        # 截屏并保存PNG
        save_png(instance)

        # 下拉人员中的选项集
        options_ul_loc = '//div[@class="bk-options-wrapper"]/ul'
        # 搜索框
        search_input_loc = '//div[@class="bk-select-search-wrapper"]/input'

        try:
            if search_for is not None:
                self.key_sleep(sleep_sec)
                # 内部搜索框对象
                input_ele = self.driver.find_element(By.XPATH, search_input_loc)
                input_ele.send_keys(search_for)
                self.key_sleep(sleep_sec)
                # 截屏并保存PNG
                save_png(instance)

            if options.strip() == 'all':
                option_idxs = [-1, ]
            elif isinstance(options, int):
                option_idxs = [options, ]
            else:
                option_idxs = options.strip().replace('，', ',').split(',')
                try:
                    option_idxs = [int(i) for i in option_idxs]
                except ValueError:
                    option_idxs = [i.strip() for i in option_idxs]

            # 选项集ul对象
            options_ul = self.find_element(options_ul_loc)
            visible_lis = options_ul.find_elements(By.TAG_NAME, 'li')

            if not len(visible_lis):
                null_error = "暂无选项"
                raise Exception(null_error)

            if option_idxs[0] == -1:
                for li in visible_lis:
                    li.click()
            else:
                for i in option_idxs:
                    if isinstance(i, int):
                        visible_lis[i - 1].click()
                    else:
                        for li in visible_lis:
                            if i in li.text:
                                li.click()
        except:
            raise
        finally:
            # 截屏并保存PNG
            save_png(instance)
            self._back_up(select)

    # 字段：单选级联
    def key_cascade_field(self, type_args, option: str, search_for: str = None, instance=None):
        """
        :param type_args: 定位复合参数
        :param option: 选项，支持两种格式：a.数字；b.具体选项路径，如：陆路>汽车类>卡车
        :param search_for: 搜索关键字
        :param instance: 所在的Test类实例
        :return:
        """
        # 字段
        field = self.located_field(type_args)
        # 点击展开下拉框
        field.click()

        # 截屏并保存PNG
        save_png(instance)

        # 级联选框中，所有的子元素位置
        # 搜索框
        search_input_loc = './/div[@class="bk-cascade-name"]/input'
        # 搜索后的ul
        ul_loc = '//*[@class="bk-cascade-options"]/div[1]/ul[@class="bk-cascade-panel-ul"]'

        try:
            if search_for is not None:
                input_ele = field.find_element(By.XPATH, search_input_loc)
                input_ele.send_keys(search_for)
                # 截屏并保存PNG
                save_png(instance)

                ul_ele = field.find_element(By.XPATH, ul_loc)
                lis = ul_ele.find_elements(By.TAG_NAME, 'li')
                lis[int(option) - 1].click()
            else:
                option_parser = [node.strip() for node in option.split('>')]
                # 级联下拉框的整体
                panels_wrap_loc = '//*[@class="bk-cascade-options"]'
                panel_structure = '/div[@class="bk-cascade-panel"]'
                for level, op_name in enumerate(option_parser, 1):
                    # 拼接出每级panel的ul
                    current_ul_loc = panels_wrap_loc + panel_structure * level + '/ul'
                    ul_ele = field.find_element(By.XPATH, current_ul_loc)
                    current_li = [li for li in ul_ele.find_elements(By.TAG_NAME, 'li') if op_name in li.text][0]
                    current_li.click()
        except:
            raise
        finally:
            # 截屏并保存PNG
            save_png(instance)
            self._back_up(field)

    # 字段：多选级联
    def key_multicascade_field(self, type_args, options: str, search_for: str = None, instance=None):
        """
        :param type_args: 定位复合参数
        :param options: 选项，支持两种格式：a.数字列表，或all；b.具体选项路径（多条），如：陆路>汽车类>卡车,水路>轮船
        :param search_for: 搜索关键字
        :param instance: 所在的Test类实例
        :return:
        """
        # 字段
        field = self.located_field(type_args)
        # 点击展开下拉框
        field.click()

        # 截屏并保存PNG
        save_png(instance)

        # 级联选框中，所有的子元素位置
        # 搜索框
        search_input_loc = './/div[@class="bk-cascade-name"]/input'
        # 勾选框
        check_loc = './/div[@class="bk-cascade-check"]'
        # 搜索后的ul
        ul_loc = '//*[@class="bk-cascade-options"]/div[1]/ul[@class="bk-cascade-panel-ul"]'

        try:
            if search_for is not None:
                input_ele = field.find_element(By.XPATH, search_input_loc)
                input_ele.send_keys(search_for)
                # 截屏并保存PNG
                save_png(instance)

                ul_ele = field.find_element(By.XPATH, ul_loc)
                lis = ul_ele.find_elements(By.TAG_NAME, 'li')

                # 点击指定的li
                if options.strip() == 'all':
                    target_lis = lis
                else:
                    idxs = [int(idx) - 1 for idx in options.strip().replace('，', ',').split(',')]
                    target_lis = [lis[i] for i in idxs]

                for li in target_lis:
                    li.find_element(By.XPATH, check_loc).click()
            else:
                cleaned_options = options.strip().replace('，', ',').split(',')
                for option in cleaned_options:
                    option_parser = [node.strip() for node in option.split('>')]
                    # 级联下拉框的整体
                    panels_wrap_loc = '//*[@class="bk-cascade-options"]'
                    panel_structure = '/div[@class="bk-cascade-panel"]'
                    for level, op_name in enumerate(option_parser, 1):
                        # 拼接出每级panel的ul
                        current_ul_loc = panels_wrap_loc + panel_structure * level + '/ul'
                        ul_ele = field.find_element(By.XPATH, current_ul_loc)
                        current_li = [li for li in ul_ele.find_elements(By.TAG_NAME, 'li') if op_name in li.text][0]
                        if level == len(option_parser):
                            check_ele = current_li.find_element(By.XPATH, check_loc)
                            check_ele.click()
                        else:
                            current_li.click()
        except:
            raise
        finally:
            # 截屏并保存PNG
            save_png(instance)
            self._back_up(field)

    # 字段：日期
    def key_date_field(self, type_args, content=None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param content: 输入内容, 格式yyyy-mm-dd
        :return:
        """
        # 输入框
        input_loc = './/input'

        # 字段
        field = self.located_field(type_args)
        field_input = field.find_element(By.XPATH, input_loc)
        field_input.clear()
        if content is not None:
            cleaned_content = content.replace('"', '').replace('“', '')
            field_input.send_keys(cleaned_content)

    # 字段：时间
    def key_time_field(self, type_args, content: str = None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param content: 输入内容, 格式hh:mm:ss
        :return:
        """
        # 输入框
        input_loc = './/input'

        # 字段
        field = self.located_field(type_args)
        field_input = field.find_element(By.XPATH, input_loc)
        field_input.clear()
        if content is not None:
            cleaned_content = content.replace('"', '').replace('“', '')
            field_input.send_keys(cleaned_content)

    # 字段：日期时间
    def key_datetime_field(self, type_args, content: str = None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param content: 输入内容, 格式yyyy-mm-dd hh:mm:ss
        :return:
        """
        # 输入框
        input_loc = './/input'

        # 字段
        field = self.located_field(type_args)
        field_input = field.find_element(By.XPATH, input_loc)
        field_input.clear()
        if content is not None:
            cleaned_content = content.replace('"', '').replace('“', '')
            field_input.send_keys(cleaned_content)

    # 字段：日期范围
    def key_daterange_field(self, type_args, content: str = None):
        """
        :param self:
        :param type_args: 定位复合参数
        :param content: 输入内容, 格式yyyy-mm-dd - yyyy-mm-dd, 示例2024-09-18 - 2024-09-20
        :return:
        """
        # 输入框
        input_loc = './/input'

        # 字段
        field = self.located_field(type_args)
        field_input = field.find_element(By.XPATH, input_loc)
        field_input.clear()
        if content is not None:
            cleaned_content = content.replace('"', '').replace('“', '')
            field_input.send_keys(cleaned_content)

    # 字段：附件上传
    def key_file_field(self, type_args, files: str, sec=1):
        """
        :param self:
        :param type_args: 定位复合参数
        :param files: 文件名称，用逗号分隔。 注意：需要把文件放到根目录的assets文件夹下
        :param sec: 上传间隔秒数
        :return:
        """
        # 字段
        field = self.located_field(type_args)

        # 上传文件的input
        file_input_loc = './/input[@type="file"]'
        input_ele = field.find_element(By.XPATH, file_input_loc)
        cleaned_files = [ROOT_PATH + f'/assets/{f_name.strip()}' for f_name in files.replace('，', ',').split(',')]
        for f_path in cleaned_files:
            input_ele.send_keys(f_path)
            self.key_sleep(sec)

    # 字段：富文本
    def key_richtext_field(self, type_args, content: str, instance=None):
        """
        :param type_args: 定位复合参数
        :param content: 支持三种，1.传null，表示为空；2.传default，填各种媒体； 3.传字符串
        :param instance: 所在的Test类实例
        :return:
        """

        def insert_contents(field, content="default"):
            # 构建复杂内容的 HTML 字符串
            if content != "default":
                body_content = f'<p>{content}</p>'
            else:
                demo_txt_path = ROOT_PATH + '/assets/富文本模板.txt'
                with open(demo_txt_path, mode='r', encoding='utf8') as f:
                    default_content = f.read()
                body_content = default_content

            final_content = f"""<!DOCTYPE html>\n<html>\n<head>\n</head>\n<body>\n{body_content}\n</body>\n</html>"""

            # 点击源代码按钮
            source_button_loc = './/button[@title="源代码"]'
            source_button = field.find_element(By.XPATH, source_button_loc)
            source_button.click()

            # 弹窗中填写html源码
            tox_textarea_loc = '//*[contains(@id, "dialog-describe")]/div/div/div/div/textarea'
            tox_textarea = self.driver.find_element(By.XPATH, tox_textarea_loc)
            tox_textarea.clear()
            tox_textarea.send_keys(final_content)

            # 关闭弹窗
            save_button_loc = '//div[@class="tox-dialog__footer"]/div[2]/button[@title="保存"]'
            save_button = tox_textarea.find_element(By.XPATH, save_button_loc)
            save_button.click()

        # 字段
        field = self.located_field(type_args)

        content = content.strip()
        if content == 'null':
            return
        try:
            if isinstance(content, str) and content != 'default':
                # 插入文字
                insert_contents(field, content)
            elif content == 'default':
                # 插入内置内容，包含：文字、图片、表格、代码段
                insert_contents(field)
            else:
                raise Exception(f'【{content}】不支持')
        except Exception:
            raise
        finally:
            # 截屏并保存PNG
            save_png(instance)
            self.driver.switch_to.default_content()


if __name__ == '__main__':
    ...
