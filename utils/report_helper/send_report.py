# Created by 黄景涛
# DATE: 2024/11/26
import requests
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from config.settings import cfg, ROOT_PATH
from utils.log_helper.logger import logger

""" 发送各种渠道的报告 """


class WeChatEmail:
    def __init__(self, smtp_server, sender_email, sender_password, smtp_port=465):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(self, recipient_email, subject, text_content, attachment_paths: list = None):
        # 创建邮件对象, 支持包含不同多媒体类型的主体
        message = MIMEMultipart('mixed')
        message['Subject'] = subject
        message['From'] = self.sender_email
        message['To'] = recipient_email

        # 将内容添加到邮件中
        part1 = MIMEText(text_content, 'plain')
        message.attach(part1)

        # 如果提供了附件路径，则附加该附件
        if attachment_paths is not None and len(attachment_paths):
            for path in attachment_paths:
                with open(os.path.join(ROOT_PATH, path), 'rb') as f:
                    file_name = os.path.basename(path)
                    attachment = MIMEApplication(f.read(), Name=file_name)
                    # 添加附件的必要头信息
                    attachment['Content-Disposition'] = f'attachment; filename="{file_name}"'
                    message.attach(attachment)

        # 使用smtplib发送邮件
        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient_email, message.as_string())
            logger.info('html测试报告，通过企微邮件发送成功！')


def wechat_email_send(text_content, attachment_paths):
    """
    发送企业微信邮件
    :param text_content: 正文中的文本内容
    :param attachment_paths: 邮件附件
    :return:
    """
    mail_info = cfg.get('email')
    smtp_server = mail_info.get('smtp_server')
    sender_email = mail_info.get('sender_email')
    sender_password = mail_info.get('sender_password')
    recipient_email = mail_info.get('recipient_email')
    subject = mail_info.get('subject')
    email = WeChatEmail(smtp_server, sender_email, sender_password)
    email.send_email(recipient_email, subject, text_content, attachment_paths)


def wechat_send(WEBHOOK_KEY: str, text_content: str, file_paths: list = None):
    """
     发送企业微信消息
    :param WEBHOOK_KEY: 企微群中机器人的WEBHOOK_KEY
    :param text_content: 正文中的文本内容
    :param file_paths: 额外的文件
    :return:
    """
    headers = {'Content-Type': 'application/json'}
    webhook_base_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook'
    webhook_send_url = webhook_base_url + f'/send?key={WEBHOOK_KEY}'

    def send_text(content: str):
        text_data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        response = requests.post(webhook_send_url, headers=headers, data=json.dumps(text_data))
        if response.status_code == 200:
            logger.info('text测试报告，通过企业微信群发送成功！')
        else:
            error_msg = f'text测试报告发送企业微信群失败，状态码：{response.status_code}\t,响应结果：{response.text}'
            logger.error(error_msg[:200])

    def send_file(file: str):
        # 1. 文件上传到企微文件服务器
        webhook_upload_url = webhook_base_url + f'/upload_media?key={WEBHOOK_KEY}&type=file'
        with open(os.path.join(ROOT_PATH, file), 'rb') as f:
            response = requests.post(webhook_upload_url, files={'file': f})
        if response.status_code == 200:
            file_data = response.json()
            media_id = file_data['media_id']
            logger.info(f'文件成功上传到企微文件服务器，media_id: {media_id}')
        else:
            logger.error(f'文件上传企微文件服务器失败：{response.text[:200]}')
            return

        # 2. 详情企微群中发送文件消息
        file_data = {
            "msgtype": "file",
            "file": {
                "media_id": media_id
            }
        }
        response = requests.post(webhook_send_url, headers=headers, data=json.dumps(file_data))
        if response.status_code == 200:
            logger.info('文件成功发送至企业微信群！')
        else:
            error_msg = f'文件发送企业微信群失败，状态码：{response.status_code}\t,响应结果：{response.text}'
            logger.error(error_msg[:200])

    # 先发送文本内容
    send_text(text_content)
    # 再发送文件
    if file_paths is not None and len(file_paths):
        for file in file_paths:
            send_file(file)


# 示例使用
if __name__ == "__main__":
    wechat_email_send('123', ['output.html'])
    text = """
    各位好：

    本次配置管理中心-UI自动化测试报告汇总，如下：
        用 例 总 数  ：1
        执 行 成 功  ：0
        执 行 失 败  ：1
        执 行 环 境  ： test
        浏  览   器  ：google
        执 行 耗 时  ：62.01 s

    具体的报告详情，请查看邮件附件。（需要修改附件后缀为.html）
    """
    robot_key = cfg.get('email').get('cmdb_robot_key')
    wechat_send(robot_key, text, ['output.html'])
