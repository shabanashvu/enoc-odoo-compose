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
import logging
import werkzeug
import functools

from odoo import http
from odoo.tools import config
from odoo.http import request, Response

from odoo.addons.muk_rest.tools import common
from odoo.addons.muk_rest.tools.encoder import RecordEncoder

_logger = logging.getLogger(__name__)


class RestRequest(http.HttpRequest):
    def __init__(self, *args):
        super(RestRequest, self).__init__(*args)

        if self.httprequest.mimetype == 'application/json' and \
                self.httprequest.method in ('POST', 'PUT'):
            data = self.httprequest.get_data().decode(
                self.httprequest.charset
            )
            self.params.update(common.parse_value(data, {}))

        context = dict(getattr(self.session, 'context', {}))

        if self.params.get('with_context', False):
            context.update(common.parse_value(self.params['with_context'], {}))

        if self.params.get('with_company', False):
            with_company_id = int(self.params['with_company'])
            allowed_company_ids = context.get('allowed_company_ids', [])
            if with_company_id in allowed_company_ids:
                allowed_company_ids.remove(with_company_id)
            allowed_company_ids.insert(0, with_company_id)
            context.update({'allowed_company_ids': allowed_company_ids})

        self.session.context = context
        self.context = context

    def _handle_exception(self, exception):
        error_message = common.parse_exception(exception)
        try:
            super(RestRequest, self)._handle_exception(exception)
        except Exception:
            _logger.exception('Restful API Error')
        return Response(json.dumps(error_message, indent=4, cls=RecordEncoder),
            content_type='application/json', status=error_message.get('code', 500)
        )

    def make_json_response(self, data, headers=None, cookies=None, encoder=RecordEncoder):
        json_headers = {} if headers is None else headers
        json_headers[common.CONTENT_TYPE_HEADER] = common.JSON_CONTENT_TYPE
        json_data = json.dumps(data, sort_keys=True, indent=4, cls=encoder)
        return self.make_response(json_data, headers=json_headers, cookies=cookies)


@common.monkey_patch(http.Root)
def get_request(self, httprequest):
    if common.BASE_URL in httprequest.base_url:
        return RestRequest(httprequest)
    return get_request.super(self, httprequest)


@common.monkey_patch(http.Root)
def setup_session(self, httprequest):
    if common.BASE_URL in httprequest.base_url:
        httprequest.session = self.session_store.new()
        return True
    return setup_session.super(self, httprequest)


@common.monkey_patch(http.Root)
def setup_db(self, httprequest):
    res = setup_db.super(self, httprequest)
    if common.BASE_URL in httprequest.base_url:
        db_param = config.get('rest_db_param', 'db')
        database = httprequest.args.get(
            db_param, httprequest.form.get(db_param, '')
        ).strip()
        if not database:
            db_header = config.get('rest_db_header', 'DATABASE')
            db_header = 'HTTP_{}'.format(db_header.upper().replace('-', '_'))
            database = httprequest.environ.get(db_header, '').strip()
        if database and database in http.db_filter([database], httprequest=httprequest):
            httprequest.session.db = database
    return res


def rest_route(routes=None, **kw):
    cors_config = config.get('rest_default_cors', False)
    cors_params = dict(cors=cors_config) if cors_config else dict()
    fixed_params = dict(rest=True, type='http', csrf=False, save_session=False)
    params = {'auth': 'none', **cors_params, **kw, **fixed_params}

    if kw.get('protected', False):
        params['ensure_db'] = True
        params['auth'] = 'rest'

    def dec(func):
        @functools.wraps(func)
        @http.route(route=routes, **params)
        def wrapper(*args, **kwargs):
            if not request.db and kw.get('ensure_db', False):
                message = {
                    'message': "No database could be matched to the request.",
                    'code': 400,
                }
                return Response(json.dumps(message, indent=4, cls=RecordEncoder),
                    content_type='application/json', status=400
                )
            response = func(*args, **kwargs)
            if isinstance(response, werkzeug.exceptions.HTTPException):
                message = {
                    'message': response.description,
                    'code': response.code,
                }
                return Response(json.dumps(message, indent=4, cls=RecordEncoder),
                    content_type='application/json', status=response.code
                )
            return response
        return wrapper
    return dec
