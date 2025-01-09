import os
import re
from urllib.parse import unquote


# 个人奇妙小工具

# 将文本信息存储到指定路径
def save_text_to_file(text, file_path):
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # 写入文本到文件
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"Text successfully saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while trying to save the file: {e}")


# 读取路径下文件内容
def read_text_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except Exception as e:
        print(f"An error occurred while trying to read the file: {e}")


# 解密邮箱加密
def Decryption_email(cfemail: str):
    email_list = re.findall(r'.{2}', cfemail)
    key = email_list[0]
    ll = []
    for e in email_list[1:]:
        # 对十六进制进行异或运算
        r = hex(int(key, 16) ^ int(e, 16))
        ll.append(r)
    # 拼接运算后的字符串
    a = ''.join(ll)
    # URL解码字符串
    email = unquote(a.replace('0x', '%'))
    return email
