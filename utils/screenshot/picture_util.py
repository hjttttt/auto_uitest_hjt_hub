# Created by 黄景涛
# DATE 2024/8/20

import json
import os
import shutil
import time
from datetime import datetime
from PIL import Image
from pathlib import Path

from config.settings import ROOT_PATH

with open(os.path.join(ROOT_PATH, 'config/config.json'), mode='r', encoding='utf8') as f:
    cfg = json.load(f)


def save_png(instance):
    """
    浏览器实例截图功能
    :param instance: 调用该方法的类实例
    :return: None
    """
    if instance is None:
        return
    time.sleep(0.0001)
    timestamp = str(datetime.now().timestamp()).replace('.', '').ljust(16, '0')
    screenshot_path = ROOT_PATH + f"/{cfg.get('pngs_info')}" + f"/{instance.__class__.__name__}" + f"/{timestamp}.png"
    instance.driver.save_screenshot(screenshot_path)


def create_gif_from_screenshots(screenshot_paths, gif_path):
    """ 将一系列截图合并为一个 GIF 动图 """
    if len(screenshot_paths):
        images = [Image.open(path) for path in screenshot_paths]
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=500, loop=1)


def generate_gifs():
    # 创建gifs子目录
    report_gifs_dir = ROOT_PATH + f'/{cfg.get("gifs_info")}'
    report_pngs_dir = ROOT_PATH + f'/{cfg.get("pngs_info")}'
    if not os.path.exists(report_gifs_dir):
        os.makedirs(report_gifs_dir)
        print(f"目录 '{report_gifs_dir}' 已被创建.")
    else:
        print(f"目录 '{report_gifs_dir}' 已经存在.")

    # 遍历主目录下的每个子目录
    for subdir in os.listdir(report_pngs_dir):
        subdir_path = Path(report_pngs_dir) / subdir
        screenshot_paths = []
        sorted_png_files = sorted(subdir_path.glob('*.png'),
                                  key=lambda file: int(str(file).split('\\')[-1].split('.')[0]), reverse=False)
        for png_file in sorted_png_files:
            png_path = os.path.join(subdir, png_file)
            screenshot_paths.append(png_path)
        formatted_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        gif_file_path = os.path.join(report_gifs_dir, f'{subdir}_{formatted_time}.gif')
        create_gif_from_screenshots(screenshot_paths, gif_file_path)


def delete_all_subdirs(dir):
    # 遍历 base_dir 目录中的所有内容
    base_dir = ROOT_PATH + dir
    for item in os.listdir(base_dir):
        # 构造每个子项的完整路径
        item_path = os.path.join(base_dir, item)

        # 检查该路径是否为目录
        if os.path.isdir(item_path):
            # 删除目录及其内容
            shutil.rmtree(item_path)
