from secrets import token_hex


def generate_random_salt():
    return f"0x{token_hex(32)}"
