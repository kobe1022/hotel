"""MainApp."""

from contextlib import asynccontextmanager
from time import time
from typing import Final
lazy from collections.abc import AsyncGenerator, Awaitable, Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.gzip import (
    GZipMiddleware,  # https://fastapi.tiangolo.com/advanced/middleware/#gzipmiddleware
)
from loguru import logger
from pyinstrument import Profiler
lazy from fastapi.responses import HTMLResponse

from gast.banner import banner
from gast.config import dev_db_populate, profiling
from gast.config.dev.db_populate import db_populate
from gast.problem_details import ProblemDetails
from gast.repository.session_factory import engine
from gast.router import (
    gast_router,
    gast_write_router,
    health_router,
    hello_router,
    shutdown_router,
)
from gast.security import router as auth_router, set_response_headers

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


@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    response = await call_next(request)
    return set_response_headers(response)


@app.exception_handler(RequestValidationError)
def handle_validation_error(
    _request: Request,
    exc: RequestValidationError,
) -> Response:
    """Pydantic-Validierungsfehler als ProblemDetails gemäß RFC 7807 ausliefern."""
    return ProblemDetails.create(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=jsonable_encoder(exc.errors()),
    ).to_response()


# --------------------------------------------------------------------------------------
# R E S T
# --------------------------------------------------------------------------------------
app.include_router(health_router, prefix="/health")
app.include_router(hello_router, prefix="/hello")
app.include_router(auth_router, prefix="/auth")
app.include_router(gast_router, prefix="/rest")
app.include_router(gast_write_router, prefix="/rest")
app.include_router(shutdown_router, prefix="/shutdown")
