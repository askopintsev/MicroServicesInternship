import os

import aiohttp

from user_service import create_app


HOST = os.environ.get("HOST", default="localhost")


app = create_app()


if __name__ == "__main__":
    aiohttp.web.run_app(app, host=HOST, port=5000)
