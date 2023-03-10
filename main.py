from enum import Enum

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

import my_db

# pip install wheel black isort
# pip install fastapi[all]

# start test server:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000

my_db.establish_db_connection()

app = FastAPI(root_path="/fastapi-demo-url-shortener")  # Dear User: delete or modify this `root_path` argument as your needs dictate


def get_status():
    """
    Currently hardcoded as `OK` but could easily be made dynamic and informative.
    """
    return "OK"


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Respond with instructions.
    """

    html_content = """
    <html>
    <head>
    <title>short URL API</title>
    </head>
    <body>
    <p>This is a URL shortener written in Python using FastAPI with SQLite3 for persistent storage.<br/>
    Take it for a test drive using <a href="/fastapi-demo-url-shortener/docs">its OpenAPI interface</a>.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/status/")
async def status():
    """
    Respond with current status (currently hardcoded as `OK`).
    """

    return {"status": get_status()}


@app.get("/{short_url}")
async def redirect_from_short_url_to_long_url(short_url):
    """
    Redirect visitor to full_url, if short_url is valid.
    """
    if not my_db.short_url_already_exists(short_url):
        return {"error": "invalid short url"}

    full_url = my_db.retrieve_full_url_from_short_url(short_url)
    return RedirectResponse(url=full_url)


@app.get("/{short_url}/{admin_key}")
async def get_stats_for_short_url(short_url=None, admin_key=None):
    """
    Respond with the shortlink's statistics, if the `short_url` and `admin_key` are valid.
    """
    try:
        shortlink = my_db.retrieve_shortlink(short_url, admin_key)
        return shortlink
    except Exception as exc:
        return {"error": exc}


@app.post("/")
async def create_short_url(full_url: str, short_url: str | None = Query(default=None)):
    """
    Given a `full_url`, create a shortlink and return its details
    """
    try:
        shortlink = my_db.create_short_url(full_url=full_url, short_url=short_url)
        return shortlink
    except Exception as exc:
        return {"error": exc}


@app.delete("/{short_url}/{admin_key}")
async def delete_short_url(short_url=None, admin_key=None):
    """
    Delete a shortlink from the database. This will free up its `short_url` for re-use.
    """
    # check for valid `short_url` and `admin_key`
    try:
        shortlink = my_db.retrieve_shortlink(short_url, admin_key)
    except Exception as exc:
        return {"error": exc}

    try:
        my_db.delete_short_url(short_url)
    except Exception as exc:
        return {"error": exc}

    return {"result": f"short_url `{short_url}` deleted"}
