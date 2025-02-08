# Created by 黄景涛
# DATE: 2024/12/30
import builtins
import json
import os
import re
import yaml
from config.settings import cfg, ROOT_PATH
from utils.common_tools import hjt_tool_3


class VarProcess:
    get_mode = ['pool', 'function']
    custom_functions = hjt_tool_3
    env = cfg.get('env', None)
    pool_file = os.path.join(ROOT_PATH, f'config/{env}_var_pool.yaml')

    def __init__(self, test_instance):
        self.test_cls_name = f"{test_instance[0].__class__.__name__}"
        self.seq_number = test_instance[1]

    @classmethod
    def is_var(cls, s: str):
        """
        检查是否是变量
        :param s:
        :return:
        """
        if not isinstance(s, str):
            return False

        s = s.strip()
        if re.search(r'\$\{.*?}', s):
            return True
        else:
            return False

    def get_var_value(self, var_name: str):
        """
        获取变量值
        :param var_name: 变量名
        :return:
        """
        get_mode = self.get_mode[0]

        with open(self.pool_file, mode='r', encoding='utf8') as f:
            var_pool = yaml.safe_load(f)
        var_value = var_pool.get(var_name)

        if var_value is None:
            f = getattr(self.custom_functions, var_name)
            if f is not None:
                var_value = f()
            else:
                f = getattr(builtins, var_name)
                if f is not None:
                    var_value = f()
            get_mode = self.get_mode[1]

        return var_value, get_mode

    def write_back_var(self, var_value: str):
        """
        回写变量，把前面步骤生成的变量保存到pool中
        :param var_value: 解析后的变量值
        :return:
        """
        with open(self.pool_file, mode='r', encoding='utf8') as f:
            pool: dict = yaml.safe_load(f)

        var_k = f'{self.test_cls_name}.{self.seq_number}'
        pool.update([(var_k, var_value)])

        with open(self.pool_file, mode='w', encoding='utf8') as f:
            yaml.dump(pool, f, allow_unicode=True)

    def sub(self, var: str) -> str:
        """
        变量替换
        :param var: 变量占位符
        :return:
        """
        if not self.is_var(var):
            return var

        pattern = r"\$\{(.*)}"
        var_name = re.search(pattern, var).group(1)
        value, get_mode = self.get_var_value(var_name)
        new_value = re.sub(pattern, value, var)

        if get_mode == self.get_mode[1]:
            self.write_back_var(new_value)

        return new_value


if __name__ == '__main__':
    var = VarProcess(('abc', 1))
    print(var.sub('//span[contains(text(), "${host_asst_model1}")]'))
