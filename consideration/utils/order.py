from secrets import token_hex


def generate_random_salt():
    return int(token_hex(32), 16)
