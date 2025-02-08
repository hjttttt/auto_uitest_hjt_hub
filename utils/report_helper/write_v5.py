# -*-encoding: Utf-8 -*-
# author: 黄景涛
# Time：2024/11/23
import os
import time
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from utils.log_helper.logger import logger
from config.settings import cfg, ROOT_PATH


class MakeHtmlReport:
    """ 制作html版的报告 """

    html_template_path = 'templates/temp_v5.html'
    output_file = os.path.join(ROOT_PATH, cfg.get('report_info').get('report_path'),
                               cfg.get('report_info').get('html_report_name'))

    # 获取报告头信息
    summary = {
        "title": cfg.get('report_info').get('title'),
        "reporter": cfg.get('report_info').get('reporter'),
        "env": cfg.get('env'),
        "saas_name": cfg.get('saas_name'),
        "create_time": None,

    }

    @classmethod
    def parser_data(cls, report_data: list) -> list[dict]:
        """
        解析标准化的报告数据, 提供给html模板使用
        :param report_data: 必须特定格式，eg:
        [
            {
                "file_name": "test_host",
                "flow_name": "新增主机",
                "success_rate": "50.0%",
                "full_gif": "xx.gif",
                "step_name": "2.点击展开",
                "fail_pngs": ["xx1.png", "xx2.png",...]
        :return: list[flow]
        """
        # 数据合并规则
        data = []
        current_file = None
        current_case = None
        case_steps = []

        for flow in report_data:
            file_name = flow.get('file_name')
            flow_name = flow.get('flow_name')
            rate = flow.get('success_rate')
            step_name = flow.get('step_name')
            if step_name:
                step_id = step_name.split('.')[0]
            else:
                step_id = None
            fail_gifs = flow.get('fail_pngs')
            # 绝对路径转换为相对路径
            # fail_gifs = [os.path.relpath(gif_path, ROOT_PATH) for gif_path in fail_gifs]
            full_gf = flow.get('full_gif')
            # 绝对路径转换为相对路径
            workspace = cfg.get('report_info').get('workspace')
            full_gf = os.path.join(workspace, os.path.relpath(full_gf, ROOT_PATH))
            if current_file != file_name or current_case != flow_name:
                if case_steps:
                    data[-1]['steps'] = case_steps
                    case_steps = []
                data.append({
                    'file_name': file_name,
                    'testcase_name': flow_name,
                    'success_rate': rate,
                    'full_gif': full_gf,
                    'steps_button': True})
                current_file = file_name
                current_case = flow_name
            case_steps.append({
                'step_name': step_name,
                'step_id': step_id,
                'fail_gif': fail_gifs})

        # 处理最后一个用例的步骤
        if case_steps:
            data[-1]['steps'] = case_steps

        return data

    def render_report(self, report_data, terminalreporter):
        """ 生成 html报告 """
        data = self.parser_data(report_data)

        # 设置Jinja2环境
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env = Environment(loader=FileSystemLoader(current_dir))
        template = env.get_template(self.html_template_path)

        text_report_data = MakeTextReport().parser_data(report_data)
        self.summary.update(
            create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            duration_time=f'{(time.time() - terminalreporter._sessionstarttime) // 60 or 1} 分钟',
            test_path=cfg.get('saas_base_url').format(env=cfg.get('env'), saas_name=cfg.get('saas_name')),
            all_flow_counts=text_report_data.get('all_flow_counts'),
            success_flow_counts=text_report_data.get('success_flow_counts'),
            fail_flow_counts=text_report_data.get('fail_flow_counts'),
        )

        # 向Html中添加其他配置信息
        config_info = dict(
            service_href=cfg.get('report_info').get('service_href'))

        # 渲染模板
        html_content = template.render(data=data, summary=self.summary, cfg=config_info, enumerate=enumerate)

        # 保存文件
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info('html报告创建完成')
        return html_content


class MakeTextReport:
    """ 制作text版的报告 """
    text_template_path = 'templates/temp_v1.j2'
    output_file = os.path.join(ROOT_PATH, cfg.get('report_info').get('report_path'),
                               cfg.get('report_info').get('text_report_name'))

    @classmethod
    def parser_data(cls, report_data: list) -> dict:
        """
        解析标准化的报告数据, 提供给html模板使用
        :param report_data: 必须特定格式，同parser_report_data_to_html
        :return: list
        """
        data = {}
        all_flow = set()
        fail_flow = set()
        for step in report_data:
            flow_name = step.get('flow_name')
            all_flow.add(flow_name)
            failed_step_counts = step.get('failed_step_counts')
            if failed_step_counts != 0:
                fail_flow.add(flow_name)

        data.update(
            all_flow_counts=len(all_flow),
            success_flow_counts=len(all_flow) - len(fail_flow),
            fail_flow_counts=len(fail_flow)
        )
        return data

    def render_report(self, report_data, terminalreporter):
        """生成 文本报告 """
        """ 生成 html报告 """
        data = self.parser_data(report_data)
        duration = time.time() - terminalreporter._sessionstarttime
        data.update(
            duration=f'{duration // 60 or 1} 分钟',
            test_path=cfg.get('saas_base_url').format(env=cfg.get('env'), saas_name=cfg.get('saas_name')),
            browser_name=cfg.get('report_info').get('browser_name'),
            report_link=cfg.get('report_info').get('report_link').format(
                service_href=cfg.get('report_info').get('service_href'),
                workspace=cfg.get('report_info').get('workspace')))

        # 设置Jinja2环境
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env = Environment(loader=FileSystemLoader(current_dir))
        template = env.get_template(self.text_template_path)

        # 渲染模板
        text_content = template.render(**data)
        # 保存文件
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        logger.info('文本报告创建完成')
        return text_content


if __name__ == '__main__':
    ...
