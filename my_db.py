import sqlite3
from pathlib import Path

import config
import my_combinatorics
import my_time

conn = None
cur = None


class Shortlink:
    """
    Convenience class for initializing and storing shortlink details
    """

    short_url: str = None
    full_url: str = None
    admin_key: str
    when_created_unix: int
    access_count: int

    def __init__(
        self,
        full_url=None,
        short_url=None,
        admin_key=None,
        when_created_unix=None,
        access_count=None,
    ):
        self.full_url = full_url

        if short_url:
            self.short_url = short_url
        else:
            self.short_url = my_combinatorics.get_short_url()

        if admin_key:
            self.admin_key = admin_key
        else:
            self.admin_key = my_combinatorics.get_admin_key()

        if when_created_unix:
            self.when_created_unix = when_created_unix
        else:
            self.when_created_unix = my_time.cur_time_unix()

        if access_count:
            self.access_count = access_count
        else:
            self.access_count = 0


def establish_db_connection():
    """
    Connect to database, and create it and/or initialize if necessary.
    """
    global conn, cur

    # if db file doesn't exist, create it
    if not Path.is_file(Path(config.db_filename)):
        Path(config.db_filename).touch()

    conn = sqlite3.connect(config.db_filename)

    # if "urls" table doesn't exist, create it
    create_table_stmt = """
    CREATE TABLE IF NOT EXISTS urls (
        full_url TEXT NOT NULL,
        short_url TEXT NOT NULL,
        admin_key TEXT NOT NULL,
        when_created_unix INTEGER NOT NULL,
        access_count INTEGER NOT NULL
    );
    """
    cur = conn.cursor()
    cur.execute(create_table_stmt)
    conn.commit()


def close_db_connection():
    """
    Close the database
    """
    conn.close()


def create_short_url(full_url=None, short_url=None, only_this_short_url=False):
    """
    Request a shortlink for the provided `full_url`.
    Option to request a specific `short_url`.
    Option to fail if requested `short_url` isn't available.
    """

    if not full_url:
        raise Exception("no full url provided")

    # check whether preferred short url is already in use
    if short_url and short_url_already_exists(short_url):
        raise Exception("that short url already exists")
    else:
        if only_this_short_url:
            raise Exception(
                "can't use only this short url, because no short url was provided"
            )

    # invariant now: we can proceed to create shortlink

    shortlink = Shortlink(full_url=full_url, short_url=short_url)

    stmt = "INSERT INTO urls VALUES(?, ?, ?, ?, ?);"
    cur.execute(
        stmt,
        (
            shortlink.full_url,
            shortlink.short_url,
            shortlink.admin_key,
            shortlink.when_created_unix,
            shortlink.access_count,
        ),
    )
    conn.commit()

    return shortlink


def delete_short_url(short_url=None):
    """
    Delete `short_url` from database
    """
    try:
        cur.execute(f"DELETE FROM urls WHERE short_url = ?;", (short_url,))
        conn.commit()
    except Exception as exc:
        raise exc


def retrieve_full_url_from_short_url(short_url):
    """
    Get the `full_url` associated with a `short_url`, and increment the `access_count`
    """
    res = cur.execute(f"SELECT full_url FROM urls WHERE short_url = ?;", (short_url,))
    full_url = res.fetchone()[0]

    stmt = "UPDATE urls SET access_count = access_count + 1 WHERE short_url = ?;"
    res = cur.execute(stmt, (short_url,))
    conn.commit()

    return full_url


def retrieve_shortlink(short_url, admin_key):
    """
    Show stats for the shortlink, if the provided `short_url` and `admin_key` are valid.
    """
    raw_res = cur.execute(
        f"SELECT * FROM urls WHERE short_url = ? and admin_key = ?;",
        (
            short_url,
            admin_key,
        ),
    )
    res = raw_res.fetchone()
    if not res:
        raise Exception("invalid short_url or admin_key")

    return Shortlink(
        full_url=res[0],
        short_url=res[1],
        admin_key=res[2],
        when_created_unix=res[3],
        access_count=res[4],
    )


def short_url_already_exists(short_url):
    """
    Utility function to test if a `short_url` is already in use in the database.
    """
    res = cur.execute(f"SELECT count(*) FROM urls WHERE short_url = ?;", (short_url,))
    if int(res.fetchone()[0]) == 0:
        return False
    else:
        return True


def update_short_url(
    short_url=None, full_url=None, admin_key=None, preserve_existing_stats=False
):
    """
    Assign new `full_url` to an existing `short_url`.
    Requires use of `admin_key`.
    Option to preserve existing stats or not.
    """
    pass
    # TODO
