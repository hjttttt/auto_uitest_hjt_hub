# Created by 黄景涛
# DATE: 2024/10/16

import os
from pathlib import Path

import yaml

# 项目根目录
ROOT_PATH = Path(__file__).parent.parent.as_posix()

# 读取config.yaml配置
with open(ROOT_PATH + '/config/config.yaml', mode='r', encoding='utf8') as f:
    # cfg = json.load(f)
    cfg = yaml.safe_load(f)


def get_environment_url(url_template: str):
    """ 拼接当前环境的完整url """
    env = cfg.get('env')
    saas_name = cfg.get('saas_name')
    url = url_template.format(env=env, saas_name=saas_name)
    return url


# 配置日志系统， 固定格式
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s [%(pathname)s::%(funcName)s:%(lineno)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(ROOT_PATH, 'logs', 'test.log'),
            'formatter': 'standard',
            'encoding': 'utf8',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

