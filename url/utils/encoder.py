import random

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(num):
    if num == 0:
        return BASE62[0]

    chars = []
    while num > 0:
        num, rem = divmod(num, 62)
        chars.append(BASE62[rem])

    return ''.join(reversed(chars))


def random_prefix(length=2):
    return ''.join(random.choices(BASE62, k=length))