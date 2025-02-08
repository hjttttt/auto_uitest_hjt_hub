# Created by 黄景涛
# DATE: 2024/10/16

import logging
import logging.config
import os

from config.settings import ROOT_PATH, LOGGING_CONFIG

# 检查日志目录是否存在
log_directory = os.path.join(ROOT_PATH, 'logs')
if not os.path.exists(log_directory):
    os.makedirs(log_directory)


def _setup_logging(config=LOGGING_CONFIG):
    """
    logging记录器设置
    :param config: format格式、版本、控制台处理器、文件处理器等配置信息
    :return:
    """
    logging.config.dictConfig(config)


def get_logger(name=None):
    """
    获取日志记录器实例
    :param name: 记录器名称
    :return: 记录器
    """
    if not logging.getLogger().hasHandlers():
        _setup_logging()
    if name is None:
        name = __file__
    return logging.getLogger(name)


# logger记录器实例
logger = get_logger()

if __name__ == '__main__':
    # logger = get_logger()
    logger.info('info信息')
