"""Funktion `run` für die FastAPI-Applikation mit dem ASGI-Server _uvicorn_."""

from ssl import PROTOCOL_TLS_SERVER

import uvicorn

from gast.config import (
    host_binding,
    port,
    tls_certfile,
    tls_keyfile,
)
from gast.fastapi_app import app  # ruff: ignore[unused-import]

__all__ = ["run"]


def run() -> None:
    """Start der Anwendung mit uvicorn."""
    # https://www.uvicorn.org/settings mit folgenden (Default-) Werten
    # host="127.0.0.1"
    # port=8000
    # loop="auto" (default), "asyncio", "uvloop" (nur Linux und MacOS)
    # http="auto" (default: "httptools" falls installiert, sonst "h11"), "h11",
    #      "httptools", "zttp", "zttp1", "zttp2"
    #      "zttp" fuer HTTP/1.1 und HTTP/2, "zttp1" fuer HTTP/1.1, "zttp2" fuer HTTP/2
    # interface="auto" (default), "asgi2", "asgi3", "wsgi"
    uvicorn.run(
        "gast:app",
        loop="asyncio",
        http="zttp",
        http2=True,  # NOSONAR
        interface="asgi3",
        host=host_binding,
        port=port,
        ssl_keyfile=tls_keyfile,
        ssl_certfile=tls_certfile,
        # "OpenSSL has deprecated all version specific protocols"
        # https://docs.python.org/3/library/ssl.html#protocol-versions
        ssl_version=PROTOCOL_TLS_SERVER,  # DevSkim: ignore DS440070
    )
