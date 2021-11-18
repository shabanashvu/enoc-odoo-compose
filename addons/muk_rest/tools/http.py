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


import json

from urllib.parse import urlencode
from urllib.parse import urlparse, urlunparse, parse_qs

from odoo.http import request, Response

from odoo.addons.muk_rest.tools import common
from odoo.addons.muk_rest.tools.encoder import RecordEncoder


def build_route(route):
    param_routes = route
    if not isinstance(route, list):
        param_routes = [route]
    api_routes = []
    for item in param_routes:
        api_routes.append('{}{}'.format(common.BASE_URL, item))
    return api_routes


def clean_query_params(query, clean_db=True, clean_debug=True):
    cleaned_params = {}
    parsed_url = urlparse(query)
    params = parse_qs(parsed_url.query)
    for key, value in params.items():
        invalid_param_check = any(
            param and not set(param) <= common.SAFE_URL_CHARS or \
                common.INVALID_HEX_PATTERN.search(param) or \
                (clean_debug and key == 'debug') or \
                (clean_db and key == 'db')
            for param in value
        )
        if not invalid_param_check and not ():
            cleaned_params[key] = value
    parsed_url = parsed_url._replace(
        query=urlencode(cleaned_params, True)
    )
    return urlunparse(parsed_url)


def make_json_response(data, headers=None, cookies=None, encoder=RecordEncoder):
    json_headers = {} if headers is None else headers
    json_headers[common.CONTENT_TYPE_HEADER] = common.JSON_CONTENT_TYPE
    json_data = json.dumps(data, sort_keys=True, indent=4, cls=encoder)
    response = Response(json_data, headers=headers)
    if cookies:
        for k, v in cookies.items():
            response.set_cookie(k, v)
    return response


