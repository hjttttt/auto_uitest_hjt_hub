# Created by 黄景涛
# DATE: 2025/1/6

import openpyxl

from utils.common_tools.hjt_tool_1 import format_time
from utils.common_tools.hjt_tool_4 import IP
from utils.log_helper.logger import logger


class Excel:

    def __init__(self, file: str):
        """
        :param file: excel文件
        """
        self.excel_path = file
        self.workbook = openpyxl.load_workbook(file)

    def update_cell_by_header_name(self, sheet_name: str, header_name: str, new_val: str, row_num: int):
        """
        按表头的列名，更新单元格值
        :param sheet_name: sheet名
        :param header_name: 表头的列名
        :param new_val: 单元格新值
        :param row_num: 更新的行号
        :return: None
        """
        # =====================================================2.0.5版本以下才适用的代码 =================================
        sheet_ = self.workbook.get_sheet_by_name(sheet_name)

        header_ = {cell_.value: col_idx + 1 for col_idx, cell_ in enumerate(sheet_.rows[0])}

        for col_name, idx in header_.items():
            if header_name in col_name:
                col_num = idx
                sheet_.cell(row=row_num, column=col_num).value = new_val

        # =====================================================2.0.5版本以下才适用的代码 =================================
    def save(self):
        self.workbook.save(self.excel_path)


class HostExcel(Excel):
    """ 主机的excel导入模板 """
    s_name = 'host'

    def update_inst_sheet(self, sheet_name: str, data: list[dict]):
        """
        更新实例的sheet页
        :param sheet_name: sheet页
        :param data: 更新的信息
        :return:
        """
        for d in data:
            header_name = d.get('header_name')
            new_vals = d.get('new_vals')
            row_nums = d.get('row_nums')
            for row_num in range(*row_nums):
                self.update_cell_by_header_name(sheet_name=sheet_name, header_name=header_name,
                                                new_val=new_vals[row_num - row_nums[0]],
                                                row_num=row_num)

        self.save()

    def update_asst_sheet(self, sheet_name: str):
        """
        更新关联关系的sheet页
        :param sheet_name:
        :return:
        """

    def run(self):
        start, end = 4, 7
        data = [
            {
                "header_name": "内网IP(必填)",
                "new_vals": IP().batch_generate_ip(counts=end - start),
                "row_nums": (start, end)
            }]

        self.update_inst_sheet(sheet_name=self.s_name, data=data)
        logger.info(f'主机的导入模板初始化成功！')


class UniversalModelExcel(HostExcel):
    """ 通用模型的excel导入模板 """

    s_name = 'automodule_893'
    inst_name_prefix = f'893_UI导入实例'

    def run(self):
        start, end = 4, 7
        data = [{
            "header_name": "实例名(必填)",
            "new_vals": [f'{self.inst_name_prefix}_{i}_{format_time()}' for i in range(end - start)],
            "row_nums": (start, end)
        },
            {
                "header_name": "整数字段",
                "new_vals": (10, 100, 301),
                "row_nums": (start, end)
            }
        ]

        self.update_inst_sheet(sheet_name=self.s_name, data=data)
        logger.info(f'通用模型的导入模板初始化成功！')


class BizExcel(HostExcel):
    """ 业务的excel导入模板 """

    s_name = 'biz'
    inst_name_prefix = f'UI导入业务'

    def run(self):
        start, end = 4, 6
        data = [{
            "header_name": "业务名(必填)",
            "new_vals": [f'{self.inst_name_prefix}_{i}_{format_time()}' for i in range(end - start)],
            "row_nums": (start, end)
        }
        ]

        self.update_inst_sheet(sheet_name=self.s_name, data=data)
        logger.info(f'业务的导入模板初始化成功！')


if __name__ == '__main__':
    # file_ = r'D:\项目资料\auto\acmdb_uitest_6.x\assets\host_template_2025-1-6.xlsx'
    # exc = HostExcel(file_)
    # exc.run()

    file_ = r'D:\项目资料\auto\acmdb_uitest_6.x\assets\automodule_893_template_2025-1-6.xlsx'
    exc = UniversalModelExcel(file_)
    exc.run()
