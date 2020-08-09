import asyncio
import os

import aiohttp_session
import aiohttp_swagger
import aioredis as aioredis
import asyncpgsa
from aiohttp import web
from aiohttp_session.redis_storage import RedisStorage

from .routes import setup_routes


async def create_app():
    app = web.Application()

    setup_routes(app)
    aiohttp_swagger.setup_swagger(app, swagger_url="/api/v1/doc", ui_version=2)

    redis = await aioredis.create_pool(
        (os.environ.get("REDIS_HOST", default="localhost"), 6379)
    )

    aiohttp_session.setup(app, RedisStorage(redis))

    app.on_startup.append(on_start)
    app.on_cleanup.append(on_shutdown)

    return app


async def on_start(app):
    app["db"] = await asyncpgsa.create_pool(
        dsn="postgresql://postgres:postgres@localhost:5432/users"
    )


async def on_shutdown(app):
    await app["db"].close()
