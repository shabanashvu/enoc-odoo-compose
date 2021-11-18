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


import os
import logging

from odoo import http, tools
from odoo.addons.muk_rest.tools.http import build_route

_logger = logging.getLogger(__name__)

try:
    import oauthlib
    import requests_oauthlib
except ImportError:
    _logger.warning("The Python library requests_oauthlib is not installed, OAuth authentication wont work.")
    requests_oauthlib = False
    oauthlib = False
finally:
    ACTIVE_AUTHENTICATION = bool(requests_oauthlib)
    
if os.environ.get('MUK_REST_ENABLE_DATABASE_TESTS'):
    DISABLE_DATABASE_TESTS = False
else:
    DISABLE_DATABASE_TESTS = True

ACTIVE_AUTHENTICATION_TEXT = "Skipped because no authentication is available!"
DISABLE_DATABASE_TEXT = "Skipped to avoid side effects on the server."

# Authentication

HOST = '127.0.0.1'
PORT = tools.config['http_port']
MASTER_PASSWORD = tools.config['admin_passwd'] or "admin"

LOGIN = "admin"
PASSWORD = "admin"

CLIENT_KEY = "1234567890123456789012345"
CLIENT_SECRET = "1234567890123456789012345"
CALLBACK_URL = 'https://127.0.0.1/callback'

OAUTH1_REQUEST_TOKEN_URL = build_route('/authentication/oauth1/initiate')[0]
OAUTH1_AUTHORIZATION_URL = build_route('/authentication/oauth1/authorize')[0]
OAUTH1_ACCESS_TOKEN_URL = build_route('/authentication/oauth1/token')[0]

OAUTH2_AUTHORIZATION_URL = build_route('/authentication/oauth2/authorize')[0]
OAUTH2_ACCESS_TOKEN_URL = build_route('/authentication/oauth2/token')[0]
OAUTH2_REVOKE_URL = build_route('/authentication/oauth2/revoke')[0]

TEST_AUTHENTICATION_URL = build_route('/search/res.partner')[0]

# Server

VERSION_URL = build_route('/')[0]
LANGUAGES_URL = build_route('/languages')[0]
COUNTRIES_URL = build_route('/countries')[0]
DATABASE_URL = build_route('/database')[0]
CHANGE_MASTER_PASSWORD_URL = build_route('/change_master_password')[0]

# Common

MODULES_URL = build_route('/modules')[0]
XMLID_URL = build_route('/xmlid')[0]
USER_URL = build_route('/user')[0]
USERINFO_URL = build_route('/userinfo')[0]
SESSION_URL = build_route('/session')[0]

# Binary

BINARY_URL = build_route('/download')[0]
UPLOAD_URL = build_route('/upload')[0]

# Report

REPORT_URL = build_route('/report')[0]
REPORTS_URL = build_route('/reports')[0]

# Model

CALL_URL = build_route('/call')[0]
FIELD_NAMES_URL = build_route('/field_names')[0]
FIELDS_URL = build_route('/fields')[0]
METADATA_URL = build_route('/metadata')[0]
SEARCH_URL = build_route('/search')[0]
NAME_URL = build_route('/name')[0]
READ_URL = build_route('/read')[0]
SEARCH_READ_URL = build_route('/search_read')[0]
READ_GROUP_URL = build_route('/read_group')[0]
CREATE_URL = build_route('/create')[0]
WRITE_URL = build_route('/write')[0]
UNLINK_URL = build_route('/unlink')[0]

# Access

ACCESS_URL = build_route('/access')[0]
ACCESS_RIGHTS_URL = build_route('/access/rights')[0]
ACCESS_RULES_URL = build_route('/access/rules')[0]
ACCESS_FIELDS_URL = build_route('/access/fields')[0]

# Database

DATABASE_LIST = build_route('/database/list')[0]
DATABASE_SIZE = build_route('/database/size')[0]
DATABASE_CREATE = build_route('/database/create')[0]
DATABASE_DUPLICATE = build_route('/database/duplicate')[0]
DATABASE_DROP = build_route('/database/drop')[0]
DATABASE_BACKUP = build_route('/database/backup')[0]
DATABASE_RESTORE = build_route('/database/restore')[0]
