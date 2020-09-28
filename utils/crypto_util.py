# author:hao.lu
# create_date: 9/28/2020 2:24 PM
# file : crypto_util.py
# IDE: PyCharm

# ! -*- coding: utf-8 -*-
import base64

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


def rsa_encode(message):
    """
    rsa 加密
    Args:
        message:  example: message = b"123456"

    Returns: example: KlJbQmYqrl/cpBIeeElPuBH/ul3Y0/o1qf/IobpaGgh2L3sCrm6KAtPHOuOtM2ooNcgHsnxVDFq3n7pbrvAexZgJk3SYruT
                      108r5x0Z3pF2XDdSszRzOWweFoUnTGMXiMkfW/wJ9XE+C1q2+SUhOvLXmjosmDz5D2gYKdUm/ZAs=

    """

    # message_bytes = message.encode("utf-8")
    with open("./utils/public_key.pem") as f:
        public_key = f.read()
    rsa_key = RSA.importKey(public_key)
    cipher = PKCS1_v1_5.new(rsa_key)
    encrypt_text = cipher.encrypt(message)
    cipher_text = base64.b64encode(encrypt_text).decode()
    return cipher_text


def rsa_decode(message):
    """
    rsa 解密
    Args:
        message: example: message = b"EUBDSS52evOMGZjiD/v68v2bKCBRpWPVyxHEXrSuiMXIQ2cjYMyRpn/Md57BErq
        Bk3X32e3TufT0QgJkC/Dm5zXpRNJVg4eFskzK0JXxhcBjT04G1Zc6N/Cp07qUzUNPB2Vk//XqCjIF1Zi1wc7FXZ6gTcj6mJjs1BbCuFvrRXE="

    Returns:字符串, example: 4asasasasas

    """
    with open("./utils/private_key.pem") as f:
        private_key = f.read()
    text = base64.b64decode(message)
    rsa_key = RSA.importKey(private_key)
    cipher_rsa = PKCS1_v1_5.new(rsa_key)
    decode_text = cipher_rsa.decrypt(text, None).decode()
    return decode_text
