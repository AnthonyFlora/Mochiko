import string


def decrypt(text):
    return string.translate(text, lookup_rot13)


def encrypt(text):
    return string.translate(text, lookup_rot13)


lookup_rot13 = string.maketrans(
    "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
    "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")

