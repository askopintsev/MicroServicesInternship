import aiohttp

from user_service import create_app

app = create_app()


if __name__ == "__main__":
    aiohttp.web.run_app(app, host="localhost", port=5000)
