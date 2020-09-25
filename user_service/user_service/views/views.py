import datetime
import os

import aiohttp
import argon2
import asyncpg
import jwt
import sqlalchemy as sa
from aiohttp_session import get_session, new_session

from user_service import model

from dotenv import load_dotenv
load_dotenv()

SECRET = os.getenv('SECRET')
ALGORITHM = os.getenv('ALGORITHM')


def generate_tokens(user_id):
    """Function to generate JWT tokens - access and refresh.
    Returns two values - access token and refresh token"""

    access_jwt = jwt.encode(
        {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
            "user_id": str(user_id),
            "created_at": str(datetime.datetime.utcnow()),
        },
        SECRET,
    ).decode("utf-8")

    refresh_jwt = jwt.encode(
        {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=3),
            "user_id": str(user_id),
            "created_at": str(datetime.datetime.utcnow()),
        },
        SECRET,
    ).decode("utf-8")

    return access_jwt, refresh_jwt


class MyJWTError(Exception):
    """Class of user-defined exception to handle JWT expiration cases"""

    def __init__(self):
        self.txt = "Expired jwt"


def jwt_decode(jwt_token):
    """Function to check fact of jwt expiration.
    Returns decoded payload of jwt if it's OK or string 'Expired jwt'"""

    try:
        decoded_jwt = jwt.decode(jwt_token, SECRET, algorithms=ALGORITHM)
    except jwt.ExpiredSignatureError:
        raise MyJWTError

    return decoded_jwt


def login_required(func):
    """Decorator-function allows to pass to views for authorised users only"""

    async def wrapped(self, *args, **kwargs):

        # get access token string from header
        access_check = self.headers.get("Authorization", None)[7:]
        if access_check is None:
            return aiohttp.web.json_response(data={"success": False,
                                                   "reason": "User unauthorised"},
                                             status=403
                                             )

        # check access token in session
        session = await get_session(self)
        try:
            session[access_check]
        except KeyError:
            return aiohttp.web.json_response(data={"success": False,
                                                   "reason": "User unauthorised (wrong token)"},
                                             status=403
                                             )

        # check expiration of access token and decode access token payload
        if self.path != "/refresh":
            try:
                jwt_decode(access_check)
            except MyJWTError:
                return aiohttp.web.json_response(data={"success": False,
                                                       "reason": "You need to re-login"},
                                                 status=403
                                                 )

        return await func(self, access_check, *args, **kwargs)

    return wrapped


async def register(request):
    """View for user registration. Obligatory params: username, password.
    User Id is creating on model initialisation.
    Password hashes with argon2 also on initialisation"""

    # getting user info from request
    try:
        data = await request.post()
        username = data["username"]
        password = data["password"]
    except KeyError:
        return aiohttp.web.json_response(data={"success": False,
                                               "reason": "Username and password required"},
                                         status=403
                                         )

    # saving user to DB with check of username duplication
    async with request.app["db"].acquire() as conn:
        try:
            await conn.execute(
                sa.insert(model.User).values(username=username,
                                             password=argon2.PasswordHasher().hash(password))
            )

        except asyncpg.exceptions.UniqueViolationError:
            return aiohttp.web.json_response(data={"success": False,
                                                   "reason": "Username already exists"},
                                             status=403
                                             )
    return aiohttp.web.json_response(data={"success": True,
                                           "reason": "User " + username + " was created"},
                                     status=201
                                     )


async def login(request):
    """View for user logging into the system. Obligatory params: username, password.
    Supports generation of access and refresh tokens.
    """

    # getting user info from request
    try:
        data = await request.post()
        username = data["username"]
        password = data["password"]
    except KeyError:
        return aiohttp.web.json_response(data={"success": False,
                                               "reason": "Username and password required"},
                                         status=403
                                         )

    # query to select user profile info
    query = sa.select("*").where(model.User.username == username)

    async with request.app["db"].acquire() as conn:
        user = await conn.fetchrow(query)
        if user is not None:
            pass_db = user["password"]
            user_id = user["id"]

            # password check
            try:
                argon2.PasswordHasher().verify(pass_db, password)
            except argon2.exceptions.VerifyMismatchError:
                return aiohttp.web.json_response(data={"success": False,
                                                       "reason": "Wrong username or password"},
                                                 status=403
                                                 )

            # creating tokens
            access_jwt, refresh_jwt = generate_tokens(user_id)

            # creating session
            session = await new_session(request)

            # save tokens to session
            session[str(access_jwt)] = str(refresh_jwt)

            # work with response
            response = aiohttp.web.json_response(data={"success": True,
                                                       "reason": "You are logged"},
                                                 headers={"Authorization": access_jwt},
                                                 status=200
                                                 )
            response.set_cookie("rt", str(refresh_jwt), max_age=10800, httponly=True)
            return response

        else:
            return aiohttp.web.json_response(data={"success": False,
                                                   "reason": "Wrong username or password"},
                                             status=403
                                             )


@login_required
async def profile(request, access_check):
    """View for user information. By default shows user info based on user_id from token.
    Accepts input param 'access_check' as decoded access token payload from wrapper function login_required.
    Accepts non-obligatory 'new_username' and 'new_password' params from request
    and updates user profile if they are not empty"""

    # getting user_if from current access token
    decoded_access = jwt_decode(access_check)
    user_id = decoded_access["user_id"]

    # query for user profile info select
    query_select = sa.select("*").where(model.User.id == user_id)

    # retrieve user profile data block
    async with request.app["db"].acquire() as conn:
        result = await conn.fetchrow(query_select)

    try:
        username = result["username"]
        user_id = str(result["id"])
    except TypeError:
        return aiohttp.web.json_response(data={"success": False,
                                               "reason": "User not found"},
                                         status=403
                                         )

    return aiohttp.web.json_response(data={"success": True,
                                           "profile data": {"user_id": user_id,
                                                            "username": username}
                                           },
                                     status=200
                                     )


@login_required
async def profile_update(request, access_check):
    """View for user information. By default shows user info based on user_id from token.
    Accepts input param 'access_check' as decoded access token payload from wrapper function login_required.
    Accepts non-obligatory 'new_username' and 'new_password' params from request
    and updates user profile if they are not empty"""

    # getting user_if from current access token
    decoded_access = jwt_decode(access_check)
    user_id = decoded_access["user_id"]

    data = await request.post()
    new_username = data.get("new_username", None)
    new_password = data.get("new_password", None)
    update_dict = {}

    if new_username:
        update_dict["username"] = new_username
    if new_password:
        update_dict["password"] = argon2.PasswordHasher().hash(new_password)

    # query to update user profile with data from update_dict dictionary
    query_update = (
        sa.update(model.User).values(update_dict).where(model.User.id == user_id)
    )

    # update user profile data block
    async with request.app["db"].acquire() as conn:
        try:
            await conn.fetchrow(query_update)
        except asyncpg.exceptions.UniqueViolationError:
            return aiohttp.web.json_response(data={"success": False,
                                                   "reason": "Username already exists"},
                                             status=403
                                             )
        return aiohttp.web.json_response(data={"success": True,
                                               "reason": "Profile data updated"},
                                         status=200
                                         )


@login_required
async def refresh(request, access_check):
    """View for tokens refresh feature. It generates new tokens and updates session tokens.
    Accepts input param 'access_check' as decoded access token payload from wrapper function login_required.
    """

    # getting session
    session = await get_session(request)

    # get and check refresh token
    refresh_token_db = session[access_check]
    refresh_token_rq = request.cookies.get('rt')

    if refresh_token_db != refresh_token_rq:
        return aiohttp.web.json_response(data={"success": False,
                                               "reason": "You need to re-login"},
                                         status=403
                                         )
    try:
        decoded_refresh = jwt_decode(refresh_token_rq)
    except MyJWTError:
        return aiohttp.web.json_response(data={"success": False,
                                               "reason": "You need to re-login"},
                                         status=403
                                         )

    # generating new tokens for user from token
    user_id = decoded_refresh["user_id"]
    new_access, new_refresh = generate_tokens(user_id)

    # updating session with new tokens
    session[str(new_access)] = str(new_refresh)
    session.changed()

    # work with response
    response = aiohttp.web.json_response(data={"success": True,
                                               "reason": "User tokens refreshed"},
                                         headers={"Authorization": new_access},
                                         status=201
                                         )
    response.del_cookie("rt")
    response.set_cookie("rt", str(new_refresh), max_age=10800, httponly=True)
    return response


@login_required
async def logout(request, access_check):
    """View for user logout.
    Accepts input param 'access_check' as decoded access token payload from wrapper function login_required.
    Invalidates user session and tokens
    """

    session = await get_session(request)
    session.invalidate()
    # del session[str(access_check)]
    # session.pop(access_check)
    return aiohttp.web.json_response(data={"success": True,
                                           "reason": "User logout"},
                                     status=200
                                     )
