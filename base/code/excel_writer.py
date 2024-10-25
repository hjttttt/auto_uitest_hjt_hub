# Created by 黄景涛
# DATE 2024/7/5
import inspect
import json
import os
import textwrap
from pathlib import Path
from pypinyin import pinyin, Style


from config.settings import ROOT_PATH
from base.data import data_by_excel
from base.code.cls_writer import create_class_py
from base.code.template.func_template import add_step
from utils.logger.custom_logger import logger


with open(os.path.join(ROOT_PATH, 'config/config.json'), mode='r', encoding='utf8') as f:
    cfg = json.load(f)


def mk_pngs_dir(dir_name):
    """ 创建pngs目录 """
    report_pngs_dir = ROOT_PATH + f'/{cfg.get("pngs_info")}' + f'/{dir_name}'
    if not os.path.exists(report_pngs_dir):
        os.makedirs(report_pngs_dir)
        logger.info(f"目录 '{report_pngs_dir}' 已被创建.")
    else:
        logger.info(f"目录 '{report_pngs_dir}' 已经存在.")


def chinese_to_pinyin(text):
    """ 中文转拼音 """
    pinyin_words = []
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 判断是否为中文字符
            pinyin_list = pinyin(char, style=Style.NORMAL)
            pinyin_words.append(pinyin_list[0][0][0])
        else:
            pinyin_words.append(char)

    pinyin_text = ''.join(pinyin_words)

    return pinyin_text


def get_function_body(func):
    """ 获取test函数模板 """
    # 获取函数体的完整源码
    source_code = inspect.getsource(func)
    # 分割成行
    source_lines = source_code.splitlines()
    # 去掉函数定义行def ...
    function_body_lines = source_lines[1:]
    # 去除代码的前导空格
    dedented_function_body = textwrap.dedent("\n".join(function_body_lines))
    return dedented_function_body


def flow_transfer_python(excel_file_path):
    """ 流程用例转test_class的py文件 """
    cases_dict = data_by_excel(excel_file_path)
    # 构造class列表数据结构
    classes = []
    # test_class的执行优先级标记
    mark_order = 0
    for sheet_name, flows in cases_dict.items():
        for flow_name, flow_steps in flows.items():
            # 创建png子目录
            mk_pngs_dir(f'Test_{chinese_to_pinyin(flow_name)}')

            # 处理每条流程用例
            mark_order += 1
            flow_info = {}
            flow_info.update(mark_order=mark_order,
                             sheet_name=sheet_name,
                             flow_name=flow_name,
                             class_name=f'Test_{chinese_to_pinyin(flow_name)}',
                             steps=flow_steps)
            methods = []
            for step in flow_steps:
                # 处理每个步骤
                step_id, step_name, kw, *args = step
                # 构造test步骤信息
                step_info = {
                    'step_func_name': f'test_{step_id}',
                    'step_name': step_name,
                    'body': get_function_body(add_step),
                    'step_info': step
                }
                methods.append(step_info)
            flow_info.update(methods=methods)
            classes.append(flow_info)
    create_class_py(classes)


def excel_transfer_python():
    """ excel转多个test文件 """
    # 项目根目录
    test_path = Path(os.path.join(ROOT_PATH, 'testcases'))
    # 自动收集Excel文件
    file_list = test_path.glob('test_*.xlsx')
    file_list_l = list(file_list)
    excel_files_info = f'一共搜集到{len(file_list_l)}个excel用例文件, 如下：{",".join(f.stem for f in file_list_l)}'
    logger.info(excel_files_info)
    logger.info(f'开始创建python测试文件...')
    for file in file_list_l:
        flow_transfer_python(file)
        logger.info(f"文件列表: {file_list_l}")
    logger.info(f'python测试文件创建完成！')


if __name__ == '__main__':
    # f_name = r'C:\Users\canway\Desktop\jingmai_uitest\testcases\aatest_login.xlsx'
    # excel_to_python(f_name)
    excel_transfer_python()
