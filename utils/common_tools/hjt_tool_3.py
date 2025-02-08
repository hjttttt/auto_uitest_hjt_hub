# Created by 黄景涛
# DATE: 2024/12/30

from datetime import datetime
from utils.common_tools.hjt_tool_4 import IP


def format_time(format_="%Y-%m-%d_%H%M%S"):
    now_time = datetime.now()
    return now_time.strftime(format_)


def get_ip():
    return IP().generate_ip()


if __name__ == '__main__':
    print(get_ip())
