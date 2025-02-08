# Created by 黄景涛
# DATE: 2024/7/16
import os
from time import sleep
from base._code.excel_writer import excel_transfer_python, global_report_data
from config.settings import ROOT_PATH
from utils.screenshot.picture_tool import cfg, generate_gifs
from utils.log_helper.logger import logger
from utils.common_tools import hjt_tool_1, hjt_tool_2, excel_tool
from utils.report_helper import collection
from utils.report_helper.write_v5 import MakeHtmlReport, MakeTextReport
from utils.report_helper.send_report import wechat_email_send, wechat_send

r_data = collection.ReportData(global_report_data)


# 收集测试用例之前执行
def pytest_sessionstart(session):
    # 创建python测试文件
    excel_transfer_python()

    # 获取定制化报告内容
    report_data = r_data.process_data_in_setup()
    logger.info(f"开始收集报告数据: {report_data}")

    # ==================================初始化实例导入的excel模板==============================================
    file_ = os.path.join(ROOT_PATH, cfg.get('init_excel').get('host_template_excel'))
    host_excel = excel_tool.HostExcel(file_)
    host_excel.run()

    file_ = os.path.join(ROOT_PATH, cfg.get('init_excel').get('biz_template_excel'))
    biz_excel = excel_tool.BizExcel(file_)
    biz_excel.run()

    file_ = os.path.join(ROOT_PATH, cfg.get('init_excel').get('cmodel_template_excel'))
    other_excel = excel_tool.UniversalModelExcel(file_)
    other_excel.run()


def pytest_sessionfinish(session):
    sleep(2)
    # 清理tmp下的所有目录/文件
    tmp_path = os.path.join(ROOT_PATH, 'testcases/tmp')
    hjt_tool_1.clear_dir(tmp_path, recursive=True)
    # 生成gif文件
    generate_gifs()
    sleep(2)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """ pytest_terminal_summary比 pytest_sessionfinish更晚执行 """

    pngs_path = os.path.join(ROOT_PATH, cfg.get("pngs_info"))
    gifs_path = os.path.join(ROOT_PATH, cfg.get("gifs_info"))

    builder_report_path = cfg.get('report_info').get('builder_report_path').format(
        workspace=cfg.get('report_info').get('workspace'))

    output_report = os.path.join(cfg.get('report_info').get('report_path'),
                                 cfg.get('report_info').get('html_report_name'))

    try:
        # 依次更新r_data：更新flow中的full_gif > 更新失败步骤信息 > 更新只保留失败步骤 > img转base64 > 输出标准报告数据
        standard_data = r_data.update_flow_gif(gifs_path).update_step_info(terminalreporter, pngs_path). \
            filter_to_get_failed_steps().pngs_to_base64().standardized_output()

        # 生成html报告
        html_report_content = MakeHtmlReport().render_report(standard_data, terminalreporter)
        # 生成字符串报告
        text_report_content = MakeTextReport().render_report(standard_data, terminalreporter)

        # copy文件到构建机的flask/static目录下
        hjt_tool_2.copy_file(os.path.join(ROOT_PATH, 'reports/report.html'),
                             os.path.join(builder_report_path, 'report.html'))

        hjt_tool_2.copy_dir(os.path.join(ROOT_PATH, 'reports/gifs/'),
                            os.path.join(builder_report_path, 'gifs/'))

        # 发送企微邮件
        if cfg.get('email').get('is_send'):
            wechat_email_send(text_report_content, [output_report, ])

        # 发送企微消息
        if cfg.get('wechat').get('is_send'):
            wechat_send(cfg.get('wechat').get('little_team_key'), text_report_content, [output_report, ])
            wechat_send(cfg.get('wechat').get('cmdb_robot_key'), text_report_content)

    finally:
        # 清理/reports/pngs下的子目录及文件
        hjt_tool_1.clear_dir(pngs_path, recursive=True)
        hjt_tool_1.clear_dir(gifs_path, recursive=True)
        pass


if __name__ == '__main__':
    ...
