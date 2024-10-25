# Created by 黄景涛
# DATE: 2024/10/16

from pathlib import Path
import os

# 项目根目录
ROOT_PATH = Path(__file__).parent.parent.as_posix()


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
            'filename': os.path.join(os.path.join(ROOT_PATH, 'logs'), 'test.log'),
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