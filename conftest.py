# Created by 黄景涛
# DATE 2024/7/19


from time import sleep
import os
import pytest
from base.code.excel_writer import excel_transfer_python
from utils.screenshot.picture_util import cfg, generate_gifs, delete_all_subdirs


def clear_tmp_dir():
    """ 清空tmp目录 """
    tmp_path = os.path.join(os.getcwd(), r'testcases\tmp')  # 获取tmp目录的绝对路径
    # 检查目录是否存在
    if os.path.exists(tmp_path) and os.path.isdir(tmp_path):
        for filename in os.listdir(tmp_path):
            file_path = os.path.join(tmp_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # 删除文件或符号链接
            except Exception as e:
                print(f'{file_path}删除失败. 原因: {e}')
    else:
        print(f'{tmp_path}不存在，或不是目录')


# 收集测试用例之前执行
def pytest_sessionstart(session):
    excel_transfer_python()  # 创建python测试文件


# 收集测试用例之前执行
def pytest_sessionfinish(session):
    sleep(2)
    # 清理tmp下的test文件
    clear_tmp_dir()
    # 生成gif文件
    try:
        generate_gifs()
        sleep(2)
    except:
        pass
    finally:
        # 清理/reports/pngs下的子目录
        delete_all_subdirs(f'/{cfg.get("pngs_info")}')
        ...


# 测试日志部分
def pytest_collection_modifyitems(items):
    # 解决pytest执行用例，标题有中文时显示编码不正确的问题
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        print(item.nodeid)
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")


# 解决测试报告乱码

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()
    if item.function.__doc__ is None:
        report.description = str(item.function.__name__)  # 如果没有三引号注释（'''注释'''），就提取函数名到case的输出文案中，就是上面的test_id
    else:
        report.description = str(item.function.__doc__)  # 提取三引号注释（'''注释'''）到case的输出文案中
    report.nodeid = report.nodeid.encode("unicode_escape").decode("utf-8")  # 再把编码改回来


if __name__ == '__main__':
    clear_tmp_dir()
