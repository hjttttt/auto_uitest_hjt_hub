# Created by 黄景涛
# DATE 2024/8/20

import os
import shutil
import time
from datetime import datetime
from PIL import Image
from pathlib import Path

from config.settings import ROOT_PATH, cfg
from utils.log_helper.logger import logger


def save_png(instance):
    """
    浏览器实例截图功能
    :param instance: 调用该方法的类实例
    :return: None
    """
    if instance is None:
        return
    test_inst, step_seq = instance

    time.sleep(0.001)
    step_seq = str(step_seq).rjust(3, '0')
    timestamp = str(datetime.now().timestamp()).replace('.', '').ljust(16, '0')
    png_name = f'{step_seq}_{timestamp}'
    screenshot_path = ROOT_PATH + f"/{cfg.get('pngs_info')}" + f"/{test_inst.__class__.__name__}" + f"/{png_name}.png"
    test_inst.driver.save_screenshot(screenshot_path)


def create_gif_from_screenshots(screenshot_paths, gif_path):
    """ 将一系列截图合并为一个 GIF 动图 """
    if len(screenshot_paths):
        images = [Image.open(path) for path in screenshot_paths]
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=800, loop=0)


def generate_gifs():
    # 创建gifs子目录
    report_gifs_dir = ROOT_PATH + f'/{cfg.get("gifs_info")}'
    report_pngs_dir = ROOT_PATH + f'/{cfg.get("pngs_info")}'
    if not os.path.exists(report_gifs_dir):
        os.makedirs(report_gifs_dir)
        logger.info(f"目录 '{report_gifs_dir}' 已被创建.")
    else:
        logger.info(f"目录 '{report_gifs_dir}' 已经存在.")

    # 遍历主目录下的每个子目录
    for subdir in os.listdir(report_pngs_dir):
        subdir_path = Path(report_pngs_dir) / subdir
        screenshot_paths = []
        sorted_png_files = sorted(subdir_path.glob('*.png'),
                                  key=lambda file: str(file).split('\\')[-1].split('.')[0], reverse=False)
        for png_file in sorted_png_files:
            png_path = os.path.join(subdir, png_file)
            screenshot_paths.append(png_path)
        formatted_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        gif_file_path = os.path.join(report_gifs_dir, f'{subdir}_{formatted_time}.gif')
        create_gif_from_screenshots(screenshot_paths, gif_file_path)

