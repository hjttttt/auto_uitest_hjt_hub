# @Author:黄景涛
# @Date: 2023/9/27

import base64
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5


def encrypt_password(password: str, PASSWORD_RSA_PUBLIC_KEY: str) -> str:
    """
    明文密码加密
    param password: 明文密码，如123456A
    param PASSWORD_RSA_PUBLIC_KEY: 公钥，从登录页面中获取
    return: 密码的密文，字符串
    """
    if not password:
        msg = f"密码不能为空"
        raise Exception(msg)

    # 处理public_key: 将b64编码后的public_key字节流，用b64解码成普通字节流
    public_key = base64.b64decode(PASSWORD_RSA_PUBLIC_KEY.replace('\n', ''))

    rsa_key = RSA.import_key(public_key)

    # 2.创建 RSA加密器实例
    cipher_rsa = PKCS1_v1_5.new(rsa_key)

    # 3.明文密码，转换为字节流，并加密
    ciphertext = cipher_rsa.encrypt(password.encode())

    # 4. 密文，转换为 Base64编码的字节流，再解码为字符串
    encoded_password = base64.b64encode(ciphertext).decode()
    # print(f'数据类型：{type(encoded_password)}  密文：{encoded_password}')
    return encoded_password


if __name__ == '__main__':
    password = 'Canway@test32'
    pswd = encrypt_password(password,  "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlHZk1BMEdDU3FHU0liM0RRRUJBUVVBQTRHTkFEQ0JpUUtCZ1FETTlhUC9MRFl4MzgxZkc3N0tzS1lSWjkrMQp3L2JqRmRJYTdCMDN1Vm1xc05WSWNXTXhscWsrUFhHTzNJNVNJY3BEbi9LcWFGbzlJVTAwNi9LdVRobkJHS3QrCkFKTXE3Z1g4ampoaWhKUW1ZZ0J5Y2Q0NzBaNWxZdm5nT3FSb1l1cFlZYndiYWVrUHVRWG5yZkF2Nmd5OFI4eWMKUkdkOWdYTGhrZ2w3bXJRZFR3SURBUUFCCi0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQo=")
