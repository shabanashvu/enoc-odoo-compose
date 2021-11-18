###################################################################################
#
#    Copyright (c) 2017-today MuK IT GmbH.
#
#    This file is part of MuK REST API for Odoo
#    (see https://mukit.at).
#
#    MuK Proprietary License v1.0
#
#    This software and associated files (the "Software") may only be used
#    (executed, modified, executed after modifications) if you have
#    purchased a valid license from MuK IT GmbH.
#
#    The above permissions are granted for a single database per purchased
#    license. Furthermore, with a valid license it is permitted to use the
#    software on other databases as long as the usage is limited to a testing
#    or development environment.
#
#    You may develop modules based on the Software or that use the Software
#    as a library (typically by depending on it, importing it and using its
#    resources), but without copying any source code or material from the
#    Software. You may distribute those modules under the license of your
#    choice, provided that this license is compatible with the terms of the
#    MuK Proprietary License (For example: LGPL, MIT, or proprietary licenses
#    similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of
#    the Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included
#    in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###################################################################################


import re
import ast
import json
import random
import passlib
import traceback

from string import ascii_letters, digits

from odoo import tools

VERSION = '1'
BASE_URL = '/api/v{}'.format(VERSION)

CONTENT_TYPE_HEADER = 'Content-Type'
JSON_CONTENT_TYPE = 'application/json'

TOKEN_INDEX = 10
KEY_CRYPT_CONTEXT = passlib.context.CryptContext(
    ['pbkdf2_sha512'], pbkdf2_sha512__rounds=6000,
)

GRANT_RESPONSE_MAP = {
    'authorization_code': ['code'],
    'implicit': ['token'],
}

UNICODE_ASCII_CHARACTERS = ascii_letters + digits

SAFE_URL_CHARS = set(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 
    'abcdefghijklmnopqrstuvwxyz'
    '0123456789' '_.-' 
    '=&;:%+~,*@!()/?'
)

INVALID_HEX_PATTERN = re.compile(
    r'%[^0-9A-Fa-f]|%[0-9A-Fa-f][^0-9A-Fa-f]'
)

DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'

DOCS_SECURITY_GROUP = tools.config.get(
    'rest_docs_security_group', False
)
DOCS_CODEGEN_URL = tools.config.get(
    'rest_docs_codegen_url', 
    'https://generator3.swagger.io/api'
)

ACTIVE_BASIC_AUTHENTICATION = tools.config.get(
    'rest_authentication_basic', True
)
ACTIVE_OAUTH1_AUTHENTICATION = tools.config.get(
    'rest_authentication_oauth1', True
)
ACTIVE_OAUTH2_AUTHENTICATION = tools.config.get(
    'rest_authentication_oauth2', True
)

try:
    import oauthlib
except ImportError:
    ACTIVE_OAUTH1_AUTHENTICATION = False
    ACTIVE_OAUTH2_AUTHENTICATION = False
    

def monkey_patch(cls):
    def decorate(func):
        name = func.__name__
        func.super = getattr(cls, name, None)
        setattr(cls, name, func)
        return func
    return decorate


def parse_value(value, default=None, raise_exception=False):
    if not value:
        return default
    if isinstance(value, (list, dict)):
        return value
    exception = None
    try:
        try:
            return json.loads(value)
        except json.decoder.JSONDecodeError as exc:
            if isinstance(value, str):
                value = value.replace('true', 'True')
                value = value.replace('false', 'False')
                value = value.replace('null', 'None')
            exception = exc
            return ast.literal_eval(value)
    except Exception as exc:
        if raise_exception:
            raise (exception or exc)
        return default


def parse_ids(ids):
    if isinstance(ids, int):
        return [ids]
    values = parse_value(ids, [])
    if isinstance(values, int):
        return [values]
    return list(map(lambda i: int(i), values))


def parse_domain(domain):
    domain = parse_value(domain, [])
    parsed_domain = []
    for item in domain:
        if isinstance(item, str) and item not in ['&', '|', '!']:
            item = parse_value(re.sub(r'^.*?List\s?', '', item), [])
        parsed_domain.append(item)
    return parsed_domain


def parse_exception(exc):
    modul = type(exc).__module__
    name = type(exc).__name__
    error = {
        'name': '%s.%s' % (modul, name) if modul else name,
        'message': getattr(exc, 'description', tools.ustr(exc)),
        'arguments': getattr(exc, 'args', None),
        'context': getattr(exc, 'context', {}),
        'code': getattr(exc, 'code', 500),
    }
    if tools.config.get('rest_debug', True):
        trace_text = ''.join(traceback.format_exception(
            exc.__class__, exc, exc.__traceback__)
        )
        error['traceback'] = trace_text.splitlines()
    return error


def generate_token(length=40, chars=UNICODE_ASCII_CHARACTERS):
    return ''.join(random.SystemRandom().choice(chars) for index in range(length))


hash_token = getattr(KEY_CRYPT_CONTEXT, 'hash', None) or KEY_CRYPT_CONTEXT.encrypt
