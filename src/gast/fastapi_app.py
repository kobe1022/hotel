# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""MainApp."""

from contextlib import asynccontextmanager
from time import time
from typing import Final
lazy from collections.abc import AsyncGenerator, Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.gzip import (
    GZipMiddleware,  # https://fastapi.tiangolo.com/advanced/middleware/#gzipmiddleware
)
from loguru import logger
from pyinstrument import Profiler
lazy from fastapi.responses import HTMLResponse

from gast.banner import banner
from gast.config import dev_db_populate, profiling
from gast.config.dev.db_populate import db_populate
from gast.repository.session_factory import engine
from gast.router import health_router, hello_router

__all__: list[str] = []


# --------------------------------------------------------------------------------------
# S t a r t u p   u n d   S h u t d o w n
# --------------------------------------------------------------------------------------
# https://fastapi.tiangolo.com/advanced/events
# pylint: disable=redefined-outer-name
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """DB neu laden, falls im dev-Modus, sowie Banner in der Konsole."""
    if dev_db_populate:
        db_populate()
    banner(app.routes)
    try:
        yield
    finally:
        logger.info("Der Server wird heruntergefahren")
        logger.info("Connection-Pool fuer die DB wird getrennt.")
        engine.dispose()


app: Final = FastAPI(lifespan=lifespan)

app.add_middleware(GZipMiddleware, minimum_size=500)


if profiling:

    @app.middleware("http")
    async def profile_request(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> HTMLResponse | Response:
        profiling = request.query_params.get("profile", False)
        if profiling:
            logger.warning("Profiling aktiviert")
            profiler = Profiler()
            profiler.start()
            response = await call_next(request)
            profiler.stop()
            print(profiler.output_text(unicode=True, color=True))
            # return HTMLResponse(profiler.output_html())
            return response
        return await call_next(request)


@app.middleware("http")
async def log_request_header(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    logger.debug(f"{request.method} '{request.url}'")
    return await call_next(request)


@app.middleware("http")
async def log_response_time(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    start = time()
    response = await call_next(request)
    duration_ms = (time() - start) * 1000
    logger.debug(
        f"Response time: {duration_ms:.2f} ms, statuscode: {response.status_code}",
    )
    return response


# --------------------------------------------------------------------------------------
# R E S T
# --------------------------------------------------------------------------------------
app.include_router(health_router, prefix="/health")
app.include_router(hello_router, prefix="/hello")
