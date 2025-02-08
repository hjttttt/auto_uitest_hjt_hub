# Created by 黄景涛
# DATE: 2024/11/25
import copy
import os
from utils.common_tools import hjt_tool_1


def get_cls_attr(cls: object):
    return dict((k, v) for k, v in cls.__dict__.items() if not k.startswith(("__", "_")))


class StepInfo:
    name = None
    status = None
    screenshot = []
    exception = None


class ReportData:
    """ 定制的报告数据类 """

    def __init__(self, report_data: list):
        """
        :param report_data: 必须是特定格式
        """
        self.report_data = report_data

    def extra_process_data(self):
        for flow in self.report_data:
            steps_detail = []
            steps = {}
            for step in flow.get('steps', None):
                step_seq, step_name, *_ = step
                steps[f'test_{step_seq}'] = dict(**get_cls_attr(StepInfo))
                steps[f'test_{step_seq}'].update(name=step_name)

                steps_detail.append(f'{step_seq}. {step_name}')
            # flow中，steps值换成字典
            flow.update(steps=steps)
            # flow中，额外增加steps_detail属性
            steps_detail.sort(key=lambda item: int(item.split('.')[0]), reverse=False)
            flow.update(steps_detail=steps_detail)
            # flow中，额外增加所有步骤数量
            flow.update(all_step_counts=len(steps_detail))
            # flow中，额外增加失败步骤数量
            flow.update(failed_step_counts=0)
        return self

    def process_data_in_setup(self):
        """
         在pytest的setup阶段，处理报告数据
        :return:
        """
        return self.extra_process_data()

    def update_step_info(self, terminalreporter, pngs_path):
        """
         在pytest的teardown阶段，更新流程用例中的步骤信息： status、screenshot、exception
        :return:
        """
        for case in terminalreporter.stats.get('failed', []):
            cls_name, step_name = case.location[2].split('.')
            # 获取当前用例的执行状态、执行异常信息
            current_case_status = case.outcome
            current_case_exception = str(case.longrepr)

            # 获取当前用例的png截图
            step_id = int(step_name.split('_')[-1])
            flow_png_path = os.path.join(pngs_path, cls_name)
            current_case_pngs = self.get_case_png_from_pngs_dir(step_id, flow_png_path, f_suffix='.png')

            # 遍历excel中每条流程用例
            for flow in self.report_data:
                class_name = flow.get('class_name')
                if class_name == cls_name:
                    s_info = flow.get('steps').get(step_name, None)
                    if not s_info:
                        break
                    # 更新失败步骤信息
                    s_info.update(
                        status=current_case_status,
                        screenshot=current_case_pngs,
                        exception=current_case_exception
                    )
                    # 更新失败步骤数量
                    flow.update(failed_step_counts=flow['failed_step_counts'] + 1)
                    break

        return self

    def update_flow_gif(self, gifs_dir_path):
        """ 更新流程用例中的full_gif值 """
        # 遍历excel中每条流程用例
        for flow in self.report_data:
            flow_name = flow.get('class_name')
            current_flow_gifs = self.get_flow_gif_from_gif_dir(flow_name, gifs_dir_path, f_suffix='.gif')
            flow.update(full_gif=current_flow_gifs[0])
        return self

    def filter_to_get_failed_steps(self):
        """ 过滤最终的报告，得到仅失败的步骤信息 """
        # report_data_copy = copy.deepcopy(self.report_data)
        # 遍历excel中每条流程用例
        for flow in self.report_data:
            steps: dict = flow.get('steps')
            removed_steps = [s_name for s_name, s_info in steps.items() if s_info.get('status') != 'failed']
            for s_name in removed_steps:
                steps.pop(s_name)
        return self

    def pngs_to_base64(self):
        """ 把报告里的所有图片转换为base64 """
        for flow in self.report_data:
            full_gif_path: str = flow.get('full_gif')
            flow.update(full_gif=full_gif_path)
            # gif图转化为base64格式
            # flow.update(full_gif=hjt_tool_1.img_to_base64(full_gif_path))
            for s_name, s_info in flow.get('steps').items():
                screenshot_base64 = [hjt_tool_1.img_to_base64(img_path) for img_path in s_info.get('screenshot')]
                flow.get('steps').get(s_name).update(screenshot=screenshot_base64)
        return self

    def sorted_flows(self, flows: list):
        """对所有的流程用例，按mark_order排序 """
        ...

    def sorted_steps(self, steps: dict):
        """ 对当前流程用例，所有的step排序 """
        ...

    def get_flow_gif_from_gif_dir(self, flow_name, gifs_dir_path: str, f_suffix):
        """
        从/reports/pngs/Test_n目录下，查找目标步骤的所有png文件
        :param flow_name: 流程用例名称，eg: Test_zj_xzslbgl
        :param gifs_dir_path: 存放gif的直接目录
        :param f_suffix: 文件后缀，带.
        :return: gifs_list
        """
        target_gifs = []
        all_gifs = hjt_tool_1.get_files_in_dir(dir_path=gifs_dir_path, f_suffix=f_suffix)
        all_sorted_gifs = sorted(all_gifs, key=lambda file: str(file).split('\\')[-1].split('.')[0], reverse=True)
        for gif in all_sorted_gifs:
            gif_file_name = hjt_tool_1.get_filename_without_extension(str(gif))
            # 取gif文件名（去除后两位），转换为流程用例名称
            f_name = '_'.join(gif_file_name.split('_')[:-2])
            if f_name == flow_name:
                gif_full_path = os.path.join(gifs_dir_path, gif)
                target_gifs.append(gif_full_path)
        return target_gifs

    def get_case_png_from_pngs_dir(self, case_id, png_dir_path: str, f_suffix):
        """
        从/reports/pngs/Test_n目录下，查找目标步骤的所有png文件
        :param case_id: 步骤id
        :param png_dir_path: 存放png的直接目录
        :param f_suffix: 文件后缀，带.
        :return: pngs_list
        """
        target_pngs = []
        all_pngs = hjt_tool_1.get_files_in_dir(dir_path=png_dir_path, f_suffix=f_suffix)
        all_sorted_pngs = sorted(all_pngs, key=lambda file: str(file).split('\\')[-1].split('.')[0], reverse=False)
        for png in all_sorted_pngs:
            # 取png文件前三位，转换为步骤id
            png_file_name = hjt_tool_1.get_filename_without_extension(str(png))
            step_id = int(png_file_name.split('_')[0])
            if int(case_id) == step_id:
                png_full_path = os.path.join(png_dir_path, png)
                target_pngs.append(png_full_path)
        return target_pngs

    def standardized_output(self):
        """ 标准化输出为html模板渲染的数据格式 """

        standard_data = []
        for flow in self.report_data:
            step_dict = dict(
                file_name=flow.get('test_file'),
                flow_name=flow.get('flow_name'),
                success_rate=f"{(1 - flow.get('failed_step_counts') / flow.get('all_step_counts')):.0%}",
                steps_detail=flow.get('steps_detail'),
                all_step_counts=flow.get('all_step_counts'),
                failed_step_counts=flow.get('failed_step_counts'),
                full_gif=flow.get('full_gif'),
                step_name=None,
                fail_pngs=None
            )
            if len(flow.get('steps')):
                for s_name, s_info in flow.get('steps').items():
                    current_step = copy.deepcopy(step_dict)
                    s_id = s_name.split('_')[-1]
                    current_step.update(
                        step_name=f"{s_id}.{s_info.get('name')}",
                        fail_pngs=s_info.get('screenshot')
                    )
                    standard_data.append(current_step)
            else:
                standard_data.append(step_dict)
        return standard_data


if __name__ == '__main__':
    d = [
        {
            'test_file': 'test_host_for_common_user',
            'mark_order': 1,
            'sheet_name': 'debug',
            'flow_name': '主机_新增实例并关联',
            'class_name': 'Test_zj_xzslbgl',
            'steps': {'test_2': {'name': '等待', 'status': None, 'screenshot': [], 'exception': None},
                      'test_3': {'name': '进入维护模块', 'status': None, 'screenshot': [], 'exception': None},
                      'test_4': {'name': '展开侧边', 'status': None, 'screenshot': [], 'exception': None},
                      'test_5': {'name': '点击侧边-资源目录', 'status': None, 'screenshot': [], 'exception': None}},
            'methods': [{'step_func_name': 'test_2', 'step_name': '等待', 'body': 'exec_step(self, step)',
                         'step_info': [2, '等待', 'sleep', 2]},
                        {'step_func_name': 'test_3', 'step_name': '进入维护模块', 'body': 'exec_step(self, step)',
                         'step_info': [3, '进入维护模块', 'click', "//span[text()='维护']"]},
                        {'step_func_name': 'test_4', 'step_name': '展开侧边', 'body': 'exec_step(self, step)',
                         'step_info': [4, '展开侧边', 'click', "//span[@class='footer-icon-svg1']"]},
                        {'step_func_name': 'test_5', 'step_name': '点击侧边-资源目录', 'body': 'exec_step(self, step)',
                         'step_info': [5, '点击侧边-资源目录', 'click', "//span[contains(text(), '资源目录')]"]}]},
        {
            'test_file': 'test_host_for_common_user',
            'mark_order': 2,
            'sheet_name': 'debug',
            'flow_name': '主机_1111',
            'class_name': 'Test_zj_1111',
            'steps': {'test_2': {'name': '等待', 'status': None, 'screenshot': [], 'exception': None},
                      'test_3': {'name': '进入维护模块', 'status': None, 'screenshot': [], 'exception': None},
                      'test_4': {'name': '展开侧边', 'status': None, 'screenshot': [], 'exception': None}}, 'methods': [
            {'step_func_name': 'test_2', 'step_name': '等待', 'body': 'exec_step(self, step)',
             'step_info': [2, '等待', 'sleep', 2]},
            {'step_func_name': 'test_3', 'step_name': '进入维护模块', 'body': 'exec_step(self, step)',
             'step_info': [3, '进入维护模块', 'click', "//span[text()='维护']"]},
            {'step_func_name': 'test_4', 'step_name': '展开侧边', 'body': 'exec_step(self, step)',
             'step_info': [4, '展开侧边', 'click', "//span[@class='footer-icon-svg1']"]}]}]
    r_data = ReportData(d)
    r_data.extra_process_data()
    print(d)

    print(get_cls_attr(StepInfo))
