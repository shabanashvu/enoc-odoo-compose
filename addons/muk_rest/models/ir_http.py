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
import threading
import werkzeug

from odoo import api, models, tools, http, registry, SUPERUSER_ID
from odoo.tools import ustr, ignore, mute_logger
from odoo.http import request, Response

from odoo.addons.muk_rest.tools import common, security
from odoo.addons.muk_rest.tools.common import parse_exception
from odoo.addons.muk_rest.tools import encoder

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    
    _inherit = 'ir.http'
    
    @classmethod
    def _rest_update_request(cls, endpoint, args):
        cls._handle_debug()
        request.is_rest = True
        request.is_frontend = False
        request.website_routing = False
        auth_method = endpoint.routing.get('auth', 'none')
        request.set_handler(endpoint, args, auth_method)

    @classmethod 
    def _rest_authenticate_request(cls, routing, params):
        env = api.Environment(request.cr, SUPERUSER_ID, {})
        user = None

        def update_request(user):
            request.uid = user.id
            request.disable_db = False
            request.session.login = user.login
            request.session.uid = user.id
            request.session.get_context()
            threading.current_thread().uid = user.id
            return user
        
        with env['res.users']._assert_can_auth():
            if common.ACTIVE_BASIC_AUTHENTICATION:
                user = security.verify_basic_request()
            if not user and common.ACTIVE_OAUTH1_AUTHENTICATION:
                user = security.verify_oauth1_request(routing, params)
            if not user and common.ACTIVE_OAUTH2_AUTHENTICATION:
                user = security.verify_oauth2_request(routing, params)

        if not user:
            raise werkzeug.exceptions.Unauthorized()
        return update_request(user)

    @classmethod
    def _auth_method_rest(cls):
        cls._rest_authenticate_request(
            request.endpoint.routing,
            request.params
        )

    @classmethod
    def _rest_dispatch(cls, rule, args):
        try:
            cls._rest_update_request(rule.endpoint, args)
            if rule.endpoint.routing.get('protected', False):
                cls._rest_authenticate_request(
                    rule.endpoint.routing,
                    {**args, **request.params}
                )
            response = request.dispatch()
            if isinstance(response, Exception):
                raise response
            return response
        except Exception as exc:
            return cls._handle_exception(exc)

    @classmethod
    def _rest_logging(cls, rule, args, response):
        if tools.config.get('rest_logging', True) and \
                not rule.endpoint.routing.get('disable_logging', False):
                
            def create_log(env, response):
                env['muk_rest.logging'].create({
                    'user_id': http.request.session.uid,
                    'url': http.request.httprequest.base_url,
                    'ip_address': request.httprequest.remote_addr,
                    'method': http.request.httprequest.method,
                    'request': '{}\r\n\r\n\r\n{}'.format(
                        '\r\n'.join([
                            '{}: {}'.format(key, 'authorization' in key.lower() and '***' or value)
                            for key, value in http.request.httprequest.headers.to_wsgi_list()
                        ]),
                        encoder.encode_request(http.request)
                    ),
                    'status': getattr(response, 'status_code', None),
                    'response': '{}\r\n{}'.format(
                        ustr(getattr(response, 'headers', '')),
                        encoder.encode_response(response)
                    ),
                })
                
            with ignore(Exception), mute_logger('odoo.sql_db'), \
                    registry(http.request.session.db).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                if rule.endpoint.routing.get('rest_custom', False):
                    endpoint = env['muk_rest.endpoint'].search([
                        ('endpoint', '=', args.get('endpoint'))
                    ], limit=1)
                    if not endpoint or endpoint.logging:
                        create_log(env, response)
                else:
                    create_log(env, response)

    @classmethod
    def _dispatch(cls):
        try:
            rule, args = cls._match(request.httprequest.path)
        except Exception:
            return super(IrHttp, cls)._dispatch()
        
        if rule.endpoint.routing.get('rest', False) and \
                not request._is_cors_preflight(rule.endpoint):
            response = cls._rest_dispatch(rule, args)
            cls._rest_logging(rule, args, response)
            return response
        return super(IrHttp, cls)._dispatch()

    @classmethod
    def _handle_exception(cls, exception):
        if bool(getattr(request, 'is_rest', False)):
            error_message = parse_exception(exception)
            try:
                super(IrHttp, cls)._handle_exception(exception)
            except Exception as exc:
                _logger.exception('Restful API Error')
            return Response(json.dumps(error_message, indent=4, cls=encoder.RecordEncoder),
                content_type='application/json', status=error_message.get('code', 500)
            )
        return super(IrHttp, cls)._handle_exception(exception)
