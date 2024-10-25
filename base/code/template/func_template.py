# Created by 黄景涛
# DATE 2024/7/5

import allure

from base.kdt import KeyWordLib
from utils.screenshot.picture_util import save_png
from utils.logger.custom_logger import logger


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
