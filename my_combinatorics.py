from random import choices

import config
import my_db


def generate_code(length=config.SHORT_URL_LENGTH):
    """
    Create an alphanumeric code of length `length`
    """
    return "".join(choices(config.alphabet, k=length))


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
