# Created by 黄景涛
# DATE 2024/7/5

import os
from jinja2 import Environment, FileSystemLoader

import config.settings as settings
from utils.log_helper.logger import logger
from utils.common_tools import hjt_tool_1

tmp_dir = settings.ROOT_PATH + "/testcases/tmp"

# 设定模板目录和环境
template_dir = './base/_code/template/'  # 模板文件所在目录
env = Environment(loader=FileSystemLoader(template_dir))

# 加载模板
template = env.get_template('class_template.j2')


def create_class_py(class_data: dict):
    # 生成代码并写入文件
    class_code = template.render(mark_order=class_data['mark_order'],
                                 sheet_name=class_data['sheet_name'],
                                 flow_name=class_data['flow_name'],
                                 class_name=class_data['class_name'],
                                 methods=class_data['methods'],
                                 steps=class_data['steps'])
    filename = f"{class_data['class_name'].lower()}.py"
    fullpath = f"{tmp_dir}/{class_data['test_file']}"
    hjt_tool_1.check_dir_exist(fullpath)
    with open(fullpath + f'/{filename}', 'w', encoding='utf-8') as f:
        f.write(class_code)
    logger.info(f"【{class_data['class_name']}】类，已写入文件【{filename}】")


if __name__ == '__main__':
    # 定义类信息

    classes = [
        {
            'class_name': 'MyClass1',
            'methods': [
                {'name': 'method1', 'body': f'print("This is MyClass1 method1")\nname=1'},
                {'name': 'method2', 'body': 'print("This is MyClass1 method2")\nage=1'}
            ]
        },
        {
            'class_name': 'MyClass2',
            'methods': [
                {'name': 'method1', 'body': """print("This is MyClass2 method1")\nname=1"""},
                {'name': 'method2', 'body': 'print("This is MyClass2 method2")'}
            ]
        },
    ]
    create_class_py(classes)
