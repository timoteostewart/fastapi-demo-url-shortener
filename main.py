import os
from enum import Enum
from typing import Union

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import RedirectResponse

import config
import my_db

# pip install fastapi[all] gunicorn slowapi

# start test server:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000

# start prod server:
# /srv/foo/bar/app/gunicorn -c gunicorn_conf.py main:app


root = os.path.dirname(os.path.abspath(__file__))

my_db.establish_db_connection()

base_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
root_path = os.getenv("FASTAPI_ROOT_PATH", "/")

print(base_url, root_path)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(root_path=root_path)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def get_status(request: Request):
    """
    Currently hardcoded as `OK` but could easily report errors, number of active shortlinks, etc.
    """
    return "OK"


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Respond with instructions.
    """

    html_content = f"""
<html>
<head>
<title>URL shortener API using FastAPI</title>
</head>
<body>
<p>This is a URL shortener written in Python using FastAPI with SQLite3 for persistent storage. <a href="https://github.com/timoteostewart/fastapi-demo-url-shortener">Source code on GitHub.</a></p>
<p>Take it for a test drive using <a href="{root_path}docs">its OpenAPI interface</a>.</p>

<p>Alternatively, interact with it via `curl` from your terminal:</p>

<p>PowerShell:<br/>
curl -X 'POST' `<br/>
'{base_url}{root_path}?full_url=https://dev.thnr.net' `<br/>
-H 'accept: application/json'</p>

<p>*sh:<br/>
curl -X 'POST' \ <br/>
'{base_url}{root_path}?full_url=https://dev.thnr.net' \ <br/>
-H 'accept: application/json'</p>

</body>
</html>

    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/status/")
async def status(request: Request):
    """
    Respond with current status (currently hardcoded as `OK`).
    """

    return {"status": get_status()}


@app.get("/{short_url}")
async def redirect_from_short_url_to_long_url(request: Request, short_url):
    """
    Redirect visitor to full_url, if short_url is valid.
    """
    if not my_db.short_url_already_exists(short_url):
        return {"error": "invalid short url"}

    full_url = my_db.retrieve_full_url_from_short_url(short_url)
    return RedirectResponse(url=full_url)


@app.get("/{short_url}/{admin_key}")
async def get_stats_for_short_url(request: Request, short_url=None, admin_key=None):
    """
    Respond with the shortlink's statistics, if the `short_url` and `admin_key` are valid.
    """
    try:
        shortlink = my_db.retrieve_shortlink(short_url, admin_key)
        return shortlink
    except Exception as exc:
        return {"error": str(exc)}


@app.post("/")
@limiter.limit("1/second")
async def create_short_url(
    request: Request, full_url: str, short_url: Union[str, None] = None
):
    """
    Given a `full_url`, create a shortlink and return its details
    """
    try:
        shortlink = my_db.create_short_url(full_url=full_url, short_url=short_url)
        return shortlink
    except Exception as exc:
        return {"error": str(exc)}


@app.delete("/{short_url}/{admin_key}")
async def delete_short_url(request: Request, short_url=None, admin_key=None):
    """
    Delete a shortlink from the database. This will free up its `short_url` for re-use.
    """
    # check for valid `short_url` and `admin_key`
    try:
        shortlink = my_db.retrieve_shortlink(short_url, admin_key)
    except Exception as exc:
        return {"error": str(exc)}

    try:
        my_db.delete_short_url(short_url)
    except Exception as exc:
        return {"error": str(exc)}

    return {"result": f"short_url `{short_url}` deleted"}
