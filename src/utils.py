import base64
import random


def _encode_char(ch: str) -> str:
    f = lambda x: chr((ord(ch) - x + 13) % 26 + x)
    return f(97) if ch.islower() else (f(65) if ch.isupper() else ch)


def _rot(s: str) -> str:
    return "".join(_encode_char(c) for c in s)


def _generate_code() -> str:
    ret_code = ""
    rand = str(random.randint(1000, 9999))
    ret_code += "0054s397" + rand[0]
    ret_code += "p6234378" + rand[1]
    ret_code += "o09pn7q3" + rand[2]
    ret_code += "r5qropr7" + rand[3]
    return ret_code


def _extend_byte_array(origin: str, extend_type: int = 0) -> bytearray:
    if extend_type == 0:
        return bytearray(_rot(origin), encoding="utf-8")
    gene_str = ""
    for i in range(0, 4):
        gene_str += origin[i * 9 : (i * 9 + 8)]
    return bytearray(_rot(gene_str), encoding="utf-8")


def _xor_code(byte_array: bytearray) -> bytearray:
    pwd_array = _extend_byte_array(_generate_code(), extend_type=1)
    out_array = bytearray()
    for i in range(0, len(byte_array)):
        out_array.insert(i, byte_array[i] ^ pwd_array[i])
    return out_array


def sdk_base64_decode(data_str: str) -> bytes:
    """Base64 decode string to bytes."""
    return base64.b64decode(data_str)


def sdk_base64_encode(data_bytes: bytes) -> str:
    """Base64 encode bytes to string."""
    return base64.b64encode(data_bytes).decode("utf-8")


import string

def decode_app_secret(app_secret: str) -> str:
    """Decode the app secret if it's encrypted."""
    # If the secret is 32 characters and contains only hex digits, 
    # it is likely a plain AppSecret (which is usually a 32-char hex string).
    # In this case, we return it as is to avoid corrupting it by attempting to decode.
    if len(app_secret) == 32 and all(c in string.hexdigits for c in app_secret):
        return app_secret

    if len(app_secret) != 32:
        return app_secret
    try:
        base64_decode = sdk_base64_decode(app_secret)
        base64_xor = _xor_code(bytearray(base64_decode))
        return sdk_base64_encode(base64_xor)
    except Exception:
        return app_secret
