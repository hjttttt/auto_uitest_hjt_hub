# @Author:黄景涛
# @Date: 2023/8/27

import re
import datetime
import requests
import warnings
from base.encrypt import encrypt_password

from utils.log_helper.logger import logger


def login(url, username, password):
    """
    登录函数，通过请求登录页面，然后重定向获取新的URL以请求用户身份信息。
    param url: 登录页面的URL
    param username: 登录用户名
    param password: 密码
    return: 登录成功后的cookie字符串
    """
    warnings.filterwarnings("ignore")
    logger.info(f"开始切换{username}登录...")
    # 发送GET请求，获取登录页面
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36",
        "Upgrade-Insecure-Requests": "1"
    }
    session = requests.session()  # 创建一个会话对象，用于保持登录状态
    login_page = session.get(url, headers=headers, verify=False)  # 发送GET请求获取登录页面的内容

    # 从登录页面提取：①提取登录页面html中，name="csrfmiddlewaretoken"; ②提取加密公钥PASSWORD_RSA_PUBLIC_KEY
    set_cookie = login_page.headers['Set-Cookie']
    pattern = r"bklogin_csrftoken=(.*?);"
    csrfmiddlewaretoken = re.search(pattern, set_cookie).group(1)
    pattern = r'PASSWORD_RSA_PUBLIC_KEY = "(.*?)"'
    PASSWORD_RSA_PUBLIC_KEY = re.search(pattern, login_page.text).group(1)

    # 发送POST请求进行登录
    # 密码加密处理
    password = encrypt_password(password, PASSWORD_RSA_PUBLIC_KEY)
    # 登录参数
    login_data = {
        "csrfmiddlewaretoken": csrfmiddlewaretoken,  # data中的重要参数，服务器会校验
        "username": username,
        "password": password,
        "next": "",
        "app_id": ""
    }

    # post请求的核心校验信息
    headers['Referer'] = url  # headers中的重要参数，服务器会校验
    login_resp = session.post(url, data=login_data, headers=headers, verify=False)  # 发送带有登录数据的POST请求进行登录
    assert login_resp.history, '登录失败，请检查用户名和密码'
    # print(f'登录login_post的结果：{login_page.text}')

    # 重定向到itsm页面
    redirect_resp = session.get(login_resp.url, headers=headers, verify=False)  # 重定向访问登录响应中的URL
    assert redirect_resp.status_code in (200, 201), f'重定向失败。URL: {login_resp.url}'  # 检查重定向响应的状态码，确保重定向成功

    # 提取并返回cookie信息
    cookies = session.cookies.get_dict()  # 从会话对象中获取cookie信息
    logger.info(f"{username}登录成功！")
    return cookies

