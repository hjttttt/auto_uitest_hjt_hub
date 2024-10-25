# Created by 黄景涛
# DATE 2024/7/5

import os
from jinja2 import Environment, FileSystemLoader

import config.settings as settings
from utils.logger.custom_logger import logger

tmp_dir = settings.ROOT_PATH + "/testcases/tmp"
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)
    logger.info(f"目录 '{tmp_dir}' 已被创建.")
else:
    logger.info(f"目录 '{tmp_dir}' 已经存在.")

# 设定模板目录和环境
template_dir = './base/code/template/'  # 模板文件所在目录
env = Environment(loader=FileSystemLoader(template_dir))

# 加载模板
template = env.get_template('class_template.j2')


def create_class_py(classes: list[dict]):
    # 生成代码并写入文件
    for cls in classes:
        class_code = template.render(mark_order=cls['mark_order'],
                                     sheet_name=cls['sheet_name'],
                                     flow_name=cls['flow_name'],
                                     class_name=cls['class_name'],
                                     methods=cls['methods'],
                                     steps=cls['steps'])
        filename = f"{cls['class_name'].lower()}.py"
        fullpath = f"{tmp_dir}/" + filename
        with open(fullpath, 'w', encoding='utf-8') as f:
            f.write(class_code)
        logger.info(f"【{cls['class_name']}】类，已写入文件【{filename}】")


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
