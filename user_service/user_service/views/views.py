import datetime
import json
import os

import aiohttp
import argon2
import asyncpg
import jwt
import sqlalchemy as sa
from aiohttp_session import get_session, new_session
from functools import wraps
from user_service import model

SECRET = str(os.environ.get("SECRET"))


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


def jwt_decode(jwt_token):
    """Function to check fact of jwt expiration.
    Returns decoded payload of jwt if it's OK or string 'Expired jwt'"""

    try:
        decoded_jwt = jwt.decode(jwt_token, SECRET, algorithms="HS256")
    except jwt.ExpiredSignatureError as err:
        return str(err)

    return decoded_jwt


def login_required(func):
    """Decorator-function allows to pass to views for authorised users only"""

    @wraps(func)
    async def wrapped(self, *args, **kwargs):

        # get access token string from header
        access_check = self.headers.get("Authorization", None)
        if access_check is None:
            return aiohttp.web.json_response(data={"success": False,
                                                   "reason": "User unauthorised"},
                                             status=403
                                             )

        # remove 'Bearer ' string from access token string
        access_check = access_check[7:]

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
        decoded_access = jwt_decode(access_check)

        if decoded_access == "Expired jwt":
            # that 'if' for tokens refresh feature
            if self.path == "/refresh":
                return await func(self, access_check, *args, **kwargs)
            else:
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
        username = request.query["username"]
        password = request.query["password"]
    except KeyError:
        return aiohttp.web.json_response(data={"success": False,
                                               "message": "Username and password required"},
                                         status=403
                                         )

    # saving user to DB with check of username duplication
    async with request.app["db"].acquire() as conn:
        try:
            await conn.execute(
                sa.insert(model.User).values(
                    username=username,
                    password=argon2.PasswordHasher().hash(password)
                )
            )

        except asyncpg.exceptions.UniqueViolationError:
            return aiohttp.web.json_response(data={"success": False,
                                                   "message": "Username already exists"},
                                             status=403
                                             )

    return aiohttp.web.json_response(data={"success": True,
                                           "message": "User " + username + " was created"},
                                     status=201
                                     )


async def login(request):
    """View for user logging into the system. Obligatory params: username, password.
    Supports generation of access and refresh tokens.
    """

    # getting user info from request
    try:
        username = request.query["username"]
        password = request.query["password"]
    except KeyError:
        return aiohttp.web.json_response(data={"success": False,
                                               "message": "Username and password required"},
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
                                                       "message": "Wrong password"},
                                                 status=403
                                                 )

            # creating session
            session = await new_session(request)

            # creating tokens
            access_jwt, refresh_jwt = generate_tokens(user_id)
            print("rt:", refresh_jwt)
            print("at: ", access_jwt)

            # save tokens to session
            session[str(access_jwt)] = str(refresh_jwt)

            return aiohttp.web.json_response(data={"success": True,
                                                   "message": "You are logged"},
                                             status=200
                                             )
        else:
            return aiohttp.web.json_response(data={"success": False,
                                                   "message": "User not found"},
                                             status=403
                                             )


@login_required
async def profile(request, access_check):
    """View for user information.
    Accepts input param 'access_check' as decoded access token payload from wrapper function login_required.
    Shows user info based on user_id from token."""

    # getting user_if from current access token
    decoded_access = jwt_decode(access_check)
    user_id = decoded_access["user_id"]

    # query for user profile info select
    query_select = sa.select("*").where(model.User.id == user_id)

    # retrieve user profile data block
    async with request.app["db"].acquire() as conn:
        result = await conn.fetchrow(query_select)
    user_id = str(result["id"])
    username = result["username"]
    password = result["password"]

    return aiohttp.web.json_response(data={"success": True,
                                           "message": {"user_id": user_id,
                                                       "username": username,
                                                       "password": password}
                                           },
                                     status=200
                                     )


@login_required
async def profile_update(request, access_check):
    """View for updating user information.
    Accepts input param 'access_check' as decoded access token payload from wrapper function login_required.
    Accepts non-obligatory 'new_username' and 'new_password' params from request
    and updates user profile if they are not empty"""

    # getting user_if from current access token
    decoded_access = jwt_decode(access_check)
    user_id = decoded_access["user_id"]

    # getting params for profile update
    new_username = request.query.get("new_username", None)
    new_password = request.query.get("new_password", None)
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
                                                   "message": "Username already exists"},
                                             status=403
                                             )
        return aiohttp.web.json_response(data={"success": True,
                                               "message": "Profile data updated"},
                                         status=201
                                         )


@login_required
async def refresh(request, access_check):
    """View for tokens refresh feature. It generates new tokens and updates session tokens.
    Accepts input param 'access_check' as decoded access token payload from wrapper function login_required.
    """

    # getting session
    session = await get_session(request)

    # get and check refresh token
    refresh_token = session[access_check]
    decoded_refresh = jwt_decode(refresh_token)
    if decoded_refresh == "Expired jwt":
        return aiohttp.web.json_response(data={"success": False,
                                               "message": "You need to re-login"},
                                         status=403
                                         )

    # generating new tokens for user from token
    user_id = decoded_refresh["user_id"]
    new_access, new_refresh = generate_tokens(user_id)

    # updating session with new tokens
    session[str(new_access)] = str(new_refresh)
    session.changed()

    return aiohttp.web.json_response(data={"success": True,
                                           "message": "User tokens refreshed"},
                                     status=200
                                     )


@login_required
async def logout(request, access_check):
    """View for user logout.
    Accepts input param 'access_check' as decoded access token payload from wrapper function login_required.
    Invalidates user session and tokens
    """

    session = await get_session(request)
    session.invalidate()
    return aiohttp.web.json_response(data={"success": True,
                                           "message": "User logout"},
                                     status=200
                                     )
