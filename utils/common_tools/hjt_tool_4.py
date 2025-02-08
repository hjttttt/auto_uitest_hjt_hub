# Created by 黄景涛
# DATE: 2024/12/30

""" ip相关函数 """
import os
import random

import yaml

from config.settings import cfg, ROOT_PATH


class IP:
    """ IP处理类 """

    env = cfg.get('env', None)
    pool_file = os.path.join(ROOT_PATH, f'config/{env}_var_pool.yaml')

    def __init__(self):
        with open(self.pool_file, mode='r', encoding='utf8') as f:
            var_pool: dict = yaml.safe_load(f)
        self.inner_ip_range: str = var_pool.get('inner_ip_config').get('range')
        self.ip_counter: str = var_pool.get('inner_ip_config').get('counter')

        if self.ip_counter and self.inner_ip_range and self.ip_counter.split('.')[0] != self.inner_ip_range.split('.')[
            0]:
            self.ip_counter = ''

    def verify_ip(self, ip: str) -> bool:
        """
        校验ip是否合法
        :param ip:
        :return:
        """

    def is_exists(self, ip: str):
        """
        检查ip是否存在
        :param ip:
        :return:
        """

    def iter_ip(self, ip: str):
        """
        基于当前ip值，迭代下一个ip
        :param ip: 当前ip
        :return:
        """
        nets = list(map(int, ip.split('.')[::-1]))

        ip = []
        mod = 0
        for idx, net in enumerate(nets):
            if idx == 0:
                if net < 255:
                    net += 1
                    mod = 0
                else:
                    net = 0
                    mod = 1
            else:
                if net < 255:
                    net += mod
                    mod = 0
                else:
                    net = 0
                    mod = 1

            ip.append(net)

        return '.'.join(map(str, ip[::-1]))

    def write_back_ip_counter(self):
        with open(self.pool_file, mode='r', encoding='utf8') as f:
            pool: dict = yaml.safe_load(f)

        pool.get('inner_ip_config').update(counter=self.ip_counter)

        with open(self.pool_file, mode='w', encoding='utf8') as f:
            yaml.dump(pool, f, allow_unicode=True)

    def generate_ip(self):
        """
        生成ip
        :return:
        """
        if not self.inner_ip_range:
            net_1 = str(random.randint(0, 255))
        else:
            net_1 = self.inner_ip_range.split('.')[0]

        if not self.ip_counter:
            self.ip_counter = f'{net_1}.0.0.1'
        else:
            self.ip_counter = self.iter_ip(self.ip_counter)

        self.write_back_ip_counter()
        return self.ip_counter

    def batch_generate_ip(self, counts=1):
        """
        批量生成ip
        :param counts:
        :return:
        """
        return [self.generate_ip() for _ in range(counts)]


if __name__ == '__main__':
    IP_ = IP()
    print(IP_.batch_generate_ip(10))
