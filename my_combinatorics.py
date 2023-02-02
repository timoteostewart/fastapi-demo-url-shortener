import random

import config
import my_db


def generate_code(length=config.short_url_length):
    """
    Create an alphanumeric code of length `length`
    """
    return "".join([random.choice(config.alphabet) for _ in range(length)])


def get_short_url():
    """
    Generate a short code that isn't already in use
    """
    while True:
        short_url = generate_code()
        if not my_db.short_url_already_exists(short_url):
            break
    return short_url


def get_admin_key():
    """
    Generate a longer alphanumeric code for use as an admin key
    """
    return generate_code(length=16)
