# Created by 黄景涛
# DATE: 2024/12/27
import os
import shutil


""" 通用的工具函数 """


def copy_file(file_path: str, target_path: str):
    """
    复制文件
    :param file_path:
    :param target_path:
    :return:
    """
    if os.path.exists(target_path):
        os.remove(target_path)
    shutil.copy2(file_path, target_path)


def copy_dir(dir_path: str, target_path: str):
    """
    复制目录及其文件
    :param dir_path:
    :param target_path:
    :return:
    """
    if os.path.exists(target_path):
        shutil.rmtree(target_path)
    shutil.copytree(dir_path, target_path)


if __name__ == '__main__':
    copy_file(r'D:\项目资料\auto\acmdb_uitest_6.x\reports\report.txt', r'C:\Users\hangjt\Desktop\demo\report.txt')
    copy_dir(r'D:\项目资料\auto\acmdb_uitest_6.x\reports\gifs', r'C:\Users\hangjt\Desktop\demo\gifs')
