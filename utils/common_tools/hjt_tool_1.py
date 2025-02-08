# Created by 黄景涛
# DATE: 2024/11/25
from datetime import datetime
import base64
import zipfile
import inspect
import os
import shutil
import textwrap
from pypinyin import pinyin, Style
from pathlib import Path

from config.settings import ROOT_PATH
from utils.log_helper.logger import logger


def format_time(format_="%Y-%m-%d_%H%M%S"):
    now_time = datetime.now()
    return now_time.strftime(format_)


def check_dir_exist(dir_path):
    """ 检查并创建目录 """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.info(f"目录 '{dir_path}' 已被创建.")
    else:
        logger.info(f"目录 '{dir_path}' 已经存在.")


def clear_dir(path, recursive=False):
    """
     递归删除目录下的所有子目录和文件
    :param path: 目标目录（本身会被保留）
    :param recursive: 是否删除子目录（递归）
    :return:
    """
    if not os.path.exists(path):
        logger.error(f'目录{path}不存在')

    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            file_path = os.path.join(root, name)
            os.remove(file_path)

        if not recursive:
            break

        for name in dirs:
            dir_path = os.path.join(root, name)
            shutil.rmtree(dir_path)


def get_files_in_dir(dir_path, f_suffix=None):
    """获取指定目录下，指定后缀的所有文件 """
    d_path = Path(dir_path)
    if f_suffix is None:
        return d_path.glob('*')
    else:
        return d_path.glob(f'*{f_suffix}')


def get_filename_without_extension(file_path: str) -> str:
    """ 获取不带后缀的文件名称 """
    path = Path(file_path)
    # 获取不带后缀的文件名
    return path.stem


def file_path_diff(full_path, prefix_path) -> str:
    """
    文件路径差
    :param full_path: 待差值的路径
    :param prefix_path: 路径前缀
    :return: 目标路径
    """
    return os.path.relpath(full_path, prefix_path)


def zip_reports(reports_dir, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:

        # 遍历 reports 目录
        for root, dirs, files in os.walk(reports_dir):
            # 只保留 gifs 子目录和 report.html 文件
            if root == reports_dir:
                if 'gifs' in dirs:
                    dir_path = os.path.join(root, 'gifs')
                    # 递归添加 gifs 子目录文件
                    for sub_root, sub_dirs, sub_files in os.walk(dir_path):
                        for sub_file in sub_files:
                            file_path = os.path.join(sub_root, sub_file)
                            zipf.write(file_path, os.path.relpath(file_path, reports_dir))
                # 添加 report.html 文件
                if 'report.html' in files:
                    file_path = os.path.join(root, 'report.html')
                    zipf.write(file_path, os.path.relpath(file_path, reports_dir))

    return zip_filename


def img_to_base64(img_path):
    """ 图片转换为Base64编码的字符串 """
    with open(img_path, 'rb') as f:
        image_data = f.read()
        # 编码为Base64格式
        base64_encoded_data = base64.b64encode(image_data)
        # 将Base64编码转换为字符串
        base64_encoded_string = base64_encoded_data.decode('utf-8')

        return base64_encoded_string


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


if __name__ == '__main__':
    # print(get_filename_without_extension('testcases\\tmp\\test_zj_xzslbgl.py'))
    #
    # d_path = 'D:\\项目资料\\auto\\acmdb_uitest_6.x\\reports\\pngs\\Test_zj_xzslbgl\\004_1732534874771328.png'
    # print(img_to_base64(d_path))
    # tmp_path = os.path.join(ROOT_PATH, 'reports/pngs')
    # clear_dir(tmp_path, recursive=True)
    # print(zip_reports(os.path.join(ROOT_PATH, 'reports'), os.path.join(ROOT_PATH, f'reports_{format_time()}.zip')))
    print(chinese_to_pinyin('主机_手动新增'))
