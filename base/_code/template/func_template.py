# Created by 黄景涛
# DATE 2024/7/5

import allure

from base.kdt import KeyWordLib
from base.kdt_lib import inst_detail_mixin, custom_filter_mixin
from utils.screenshot.picture_tool import save_png
from utils.log_helper.logger import logger
from utils.variable_helper.var_tool import VarProcess


def add_step(self, step: list):
    exec_step(self, step)


def exec_step(self, step: list):
    """
     test函数主体代码
    :param self: Test类实例
    :param step: 步骤信息
    :return:
    """
    seq_number, step_name, *kw_and_args = step
    logger.info(f'步骤{seq_number}：{step_name} ==> 开始执行...')
    try:
        keyword = kw_and_args[0]
        # 为了对子类隐藏self，单独定一个变量名
        instance = (self, seq_number)

        # args = tuple(kw_and_args[1:])
        args = step_args_handle(kw_and_args[1:], instance)
        logger.info(f'关键字：{keyword}, 参数：{args}')
        kw_func = keyword_parser(self, keyword)

        try:
            # 执行关键字函数
            with allure.step(step_name):
                kw_func(*args, instance=instance)
        except TypeError:
            with allure.step(step_name):
                kw_func(*args)
        except Exception as e:
            logger.error('执行出错', exc_info=True)
            raise e
        finally:
            # 截屏保存PNG
            save_png(instance)
            allure.attach(self.driver.get_screenshot_as_png(), step_name, allure.attachment_type.PNG)

        logger.info(f'步骤{seq_number}.{step_name}  ==> 执行完毕!')

    except Exception as e:
        logger.error(f'步骤{seq_number}.{step_name}  ==> 执行完毕!', exc_info=True)
        raise e


def keyword_parser(self, keyword: str):
    """
    解析关键字写法，提供两种写法：1、直接函数名； 2、类名.函数名
    :param self:
    :param keyword:  关键字的字符串形式
    :return:  关键字函数引用
    """
    kw_list = keyword.split('.')
    if len(kw_list) == 1:
        keyword_cls = KeyWordLib(self.driver)
        kw_func = keyword_cls.get_kw_method(keyword)
    else:
        keyword_cls_name = kw_list.pop(0)

        keyword_cls = getattr(inst_detail_mixin, keyword_cls_name, None) or getattr(custom_filter_mixin,
                                                                                    keyword_cls_name, None)
        if not keyword_cls:
            raise Exception(f'kdt_lib/mixin文件中不存在【{keyword_cls_name}】')

        instance = keyword_cls(self.driver)
        func_name = kw_list[-1]
        kw_func = instance.get_kw_method(func_name)
    return kw_func


def step_args_handle(args, test_instance) -> tuple:
    """
    步骤中的参数加工
    :param args: 参数集
    :param test_instance: 测试类信息
    :return:
    """
    new_args = tuple(map(VarProcess(test_instance).sub, args))
    return new_args


# # ==========================废弃 ==================================================
def exec_step_bak(self, step: list):
    """
     test函数主体代码
    :param self: Test类实例
    :param step: 步骤信息
    :return:
    """
    seq_number, step_name, *kw_and_args = step
    logger.info(f'步骤{seq_number}：{step_name} ==> 开始执行...')
    kw = KeyWordLib(self.driver)
    try:
        keyword = kw_and_args[0]
        args = tuple(kw_and_args[1:])
        logger.info(f'关键字：【{keyword}】, 参数：{args}')
        kw_func = kw.get_kw_method(keyword)

        # 为了对子类隐藏self，单独定一个变量名
        instance = self
        try:
            # 执行关键字函数
            with allure.step(step_name):
                kw_func(*args, instance=instance)
        except TypeError:
            with allure.step(step_name):
                kw_func(*args)
        except Exception as e:
            logger.error('执行出错', exc_info=True)
            raise e
        finally:
            # 截屏保存PNG
            save_png(instance)
            allure.attach(kw.driver.get_screenshot_as_png(), step_name, allure.attachment_type.PNG)

        logger.info(f'步骤{seq_number}.{step_name}  ==> 执行完毕!')

    except Exception as e:
        logger.error(f'步骤{seq_number}.{step_name}  ==> 执行完毕!', exc_info=True)
        raise e


if __name__ == '__main__':
    ...
