# Created by 黄景涛
# DATE 2024/7/5

import os
from pathlib import Path

from config.settings import ROOT_PATH
from base.data import data_by_excel
from base._code.cls_writer import create_class_py
from base._code.template.func_template import add_step
from utils.common_tools.hjt_tool_1 import chinese_to_pinyin, get_function_body
from config.settings import cfg
from utils.log_helper.logger import logger
from utils.common_tools import hjt_tool_1

# 定制化报告内容
global_report_data = []


def mk_pngs_dir(dir_name):
    """ 创建pngs目录 """
    report_pngs_dir = ROOT_PATH + f'/{cfg.get("pngs_info")}/' + f'{dir_name}'
    hjt_tool_1.check_dir_exist(report_pngs_dir)


def flow_transfer_python(mark_order: int, excel_file_path):
    """ 流程用例转test_class的py文件 """
    cases_dict = data_by_excel(excel_file_path)
    # 构造class列表数据结构
    testcases: list = []
    # test_class的执行优先级标记
    for sheet_name, flows in cases_dict.items():
        for flow_name, flow_steps in flows.items():
            # 创建png子目录
            mk_pngs_dir(f'Test_{chinese_to_pinyin(flow_name)}')

            # 处理每条流程用例
            mark_order += 1
            flow_info = dict(
                test_file=hjt_tool_1.get_filename_without_extension(excel_file_path),
                mark_order=mark_order,
                sheet_name=sheet_name,
                flow_name=flow_name,
                class_name=f'Test_{chinese_to_pinyin(flow_name)}',
                full_gif=None,
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
            testcases.append(flow_info)
            create_class_py(flow_info)

    return mark_order, testcases


def excel_transfer_python():
    """ excel转多个test文件 """
    global global_report_data

    # 项目根目录
    test_path = Path(os.path.join(ROOT_PATH, 'testcases'))
    # 自动收集Excel文件
    file_list = test_path.glob('test_*.xlsx')
    sorted_file_list = sorted(file_list, reverse=False)
    excel_files_info = f'一共搜集到{len(sorted_file_list)}个excel用例文件, 如下：{",".join(file.stem for file in sorted_file_list)}'
    logger.info(excel_files_info)
    logger.info(f'开始创建python测试文件...')

    mark_order = 0
    for file in sorted_file_list:
        mark_order, testcases = flow_transfer_python(mark_order, file)
        global_report_data.extend(testcases)
    logger.info(f'python测试文件创建完成！')


if __name__ == '__main__':
    # f_name = r'C:\Users\canway\Desktop\jingmai_uitest\testcases\aatest_login.xlsx'
    # excel_to_python(f_name)
    excel_transfer_python()
