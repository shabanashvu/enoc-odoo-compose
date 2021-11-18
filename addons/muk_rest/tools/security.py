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


import base64
import urllib
import logging
import functools
import werkzeug

from odoo import http, api, registry, SUPERUSER_ID
from odoo.exceptions import AccessDenied
from odoo.addons.muk_rest import validators, tools

_logger = logging.getLogger(__name__)


def decode_http_basic_authentication(encoded_header):
    header_values = encoded_header.strip().split(' ')

    def decode_http_basic_authentication_value(value):
        try:
            username, password = base64.b64decode(value).decode().split(':', 1)
            return urllib.parse.unquote(username), urllib.parse.unquote(password)
        except:
            return None, None
    if len(header_values) == 1:
        return decode_http_basic_authentication_value(header_values[0])
    if len(header_values) == 2 and header_values[0].strip().lower() == 'basic':
        return decode_http_basic_authentication_value(header_values[1])
    return None, None


def get_response_type(grant_type):
    return tools.common.GRANT_RESPONSE_MAP.get(grant_type, [])


def check_login_credentials(dbname, login, password):
    model = registry(dbname)['res.users']
    return model.authenticate(dbname, login, password, {
        'interactive': True
    })


def verify_basic_request(raise_exception=False):
    try:
        authorization_header = http.request.httprequest.headers.get('Authorization', '')
        username, password = decode_http_basic_authentication(authorization_header)
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        user = None
        try:
            user = env['res.users'].browse(int(username))
            user.with_user(user)._check_credentials(password, {'interactive': False})
        except:
            user = env['res.users'].search([('login', '=', username)], limit=1)
            user.with_user(user)._check_credentials(password, {'interactive': False})
        return user
    except Exception: 
        if raise_exception:
            raise
    return None
    

def verify_oauth1_request(routing, params, realms=None, raise_exception=False):
    try:
        valid, request = validators.oauth1_provider.validate_protected_resource_request(
            uri=tools.http.clean_query_params(http.request.httprequest.url, clean_db=True),
            http_method=http.request.httprequest.method,
            body=http.request.httprequest.form,
            headers=dict(http.request.httprequest.headers.to_wsgi_list()),
            realms=realms or []
        )
        access_token = request and request.access_token or None
        if not valid or not (access_token and access_token.user_id):
            raise AccessDenied()
        if access_token.oauth_id.security == 'advanced' and \
                not access_token.oauth_id.oauth_id._check_security(routing, params):
            raise AccessDenied()
        return request.access_token.user_id
    except Exception:
        if raise_exception:
            raise
    return None


def verify_oauth2_request(routing, params, scopes=None, raise_exception=False):
    try:
        valid, request = validators.oauth2_provider.verify_request(
            uri=tools.http.clean_query_params(http.request.httprequest.url, clean_db=True),
            http_method=http.request.httprequest.method,
            body=http.request.httprequest.form,
            headers=dict(http.request.httprequest.headers.to_wsgi_list()),
            scopes=scopes or []
        )
        if not valid or not (request and request.access_token):
            raise AccessDenied()
        access_token = request.access_token
        oauth = access_token.oauth_id
        user = access_token.user_id
        if not user and oauth._name == 'muk_rest.oauth2' and \
                oauth.state == 'client_credentials' and oauth.user_id:
            user = request.access_token.oauth_id.user_id
        if not user:
            raise AccessDenied()
        
        if oauth.oauth_id.security == 'advanced' and \
                not oauth.oauth_id._check_security(routing, params):
            raise AccessDenied()
        return user
    except Exception:
        if raise_exception:
            raise
    return None


def handle_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            _logger.exception("Handle Error")   
            if http.request._cr:
                http.request._cr.rollback()
            http.request._failed = exc
            with registry(http.request.session.db).cursor() as cr:
                message = getattr(exc, 'description', getattr(exc, 'message', repr(exc)))
                env = api.Environment(cr, SUPERUSER_ID, http.request.session.context or {})
                html = env['ir.ui.view']._render_template('muk_rest.authorize_error', {
                    'error': message and message.replace('"', "'") or ''
                })
            return werkzeug.wrappers.Response(
                html, status=getattr(exc, 'code', 400), content_type='text/html'
            )
    return wrapper
