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


import urllib

from werkzeug import exceptions

from odoo import http, api, SUPERUSER_ID, _
from odoo.http import request, Response
from odoo.exceptions import AccessDenied

from odoo.addons.muk_rest import validators, tools, core
from odoo.addons.muk_rest.tools.http import build_route


class AuthenticationController(http.Controller):
    
    def __init__(self):
        super(AuthenticationController, self).__init__()
        self.oauth1 = validators.oauth1_provider
        self.oauth2 = validators.oauth2_provider

    #----------------------------------------------------------
    # OAuth Helper
    #----------------------------------------------------------
    
    def _check_active_oauth1(self):
        if not (tools.common.ACTIVE_OAUTH1_AUTHENTICATION and validators.oauth1_provider):
            raise exceptions.NotImplemented()
    
    def _check_active_oauth2(self):
        if not (tools.common.ACTIVE_OAUTH2_AUTHENTICATION and validators.oauth2_provider):
            raise exceptions.NotImplemented()    
    
    def _client_information(self, client, values={}):
        values.update({
            'name': client.homepage,
            'company': client.company,
            'homepage': client.homepage,
            'logo_url': client.logo_url,
            'privacy_policy': client.privacy_policy,
            'service_terms': client.service_terms,
            'description': client.description,
        })
        return values
     
    def _oauth1_information(self, token, realms=[], values={}):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        request_token = env['muk_rest.request_token']._check_resource(token)
        if token:
            values = self._client_information(
                request_token.oauth_id, values
            )
            values.update({
                'api_url': build_route('/authentication/oauth1/authorize')[0],
                'oauth_token': token,
                'callback': request_token.callback,
                'realms': realms or [],
            })
            return values
        raise exceptions.BadRequest()
         
    def _oauth2_information(self, client_id, redirect_uri, response_type, state=None, scopes=[], values={}):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        oauth = env['muk_rest.oauth2'].search([('client_id', '=', client_id)], limit=1)
        if client_id and redirect_uri and response_type and oauth:
            values = self._client_information(
                oauth, values
            )
            values.update({
                'api_url': build_route('/authentication/oauth2/authorize')[0],
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'response_type': response_type,
                'state': state,
                'scopes': scopes or []
            })
            return values
        raise exceptions.BadRequest()

    #----------------------------------------------------------
    # OAuth 1.0
    #----------------------------------------------------------
 
    @core.http.rest_route(
        routes=build_route('/authentication/oauth1/initiate'),
        methods=['GET', 'POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True
    )
    def oauth1_initiate(self, **kw):
        self._check_active_oauth1()
        headers, body, status = self.oauth1.create_request_token_response(
            uri=tools.http.clean_query_params(request.httprequest.url, clean_db=True),
            http_method=request.httprequest.method,
            body=request.httprequest.form,
            headers=dict(request.httprequest.headers.to_wsgi_list())
        )
        return Response(response=body, headers=headers, status=status) 

    @core.http.rest_route(
        routes=build_route('/authentication/oauth1/authorize'),
        methods=['GET', 'POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True
    )
    def oauth1_authorize(self, **kw):
        self._check_active_oauth1()
        if request.httprequest.method.upper() == 'POST':
            token = request.params.get('oauth_token')
            realms = request.httprequest.form.getlist('realms')
            try:
                uid = tools.security.check_login_credentials(
                    request.session.db, 
                    request.params.get('login', None), 
                    request.params.get('password', None)
                )
                headers, body, status = self.oauth1.create_authorization_response(
                    uri=tools.http.clean_query_params(request.httprequest.url, clean_db=True),
                    http_method=request.httprequest.method,
                    body=request.httprequest.form,
                    headers=dict(request.httprequest.headers.to_wsgi_list()),
                    realms=realms or [],
                    credentials={'user': uid}
                )
                if status == 200:
                    verifier = str(urllib.parse.parse_qs(body)['oauth_verifier'][0])
                    return request.make_json_response({
                        'oauth_token': token, 'oauth_verifier': verifier
                    })
                return Response(body, status=status, headers=headers)
            except AccessDenied:
                values = self._oauth1_information(token, realms)
                values.update({'error': _("Invalid login or password!")})
                return request.render('muk_rest.authorize_oauth1', values)
            
        realms, credentials = self.oauth1.get_realms_and_credentials(
            uri=request.httprequest.url,
            http_method=request.httprequest.method,
            body=request.httprequest.form,
            headers=dict(request.httprequest.headers.to_wsgi_list())
        )
        resource_owner_key = credentials.get('resource_owner_key', False)
        values = self._oauth1_information(resource_owner_key, realms)
        return request.render('muk_rest.authorize_oauth1', values)

    @core.http.rest_route(
        routes=build_route('/authentication/oauth1/token'),
        methods=['GET', 'POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True
    )
    def oauth1_token(self, **kw):
        self._check_active_oauth1()
        headers, body, status = self.oauth1.create_access_token_response(
            uri=tools.http.clean_query_params(request.httprequest.url, clean_db=True),
            http_method=request.httprequest.method,
            body=request.httprequest.form,
            headers=dict(request.httprequest.headers.to_wsgi_list())
        )
        return Response(response=body, headers=headers, status=status) 
    
    #----------------------------------------------------------
    # OAuth 2.0
    #----------------------------------------------------------

    @core.http.rest_route(
        routes=build_route('/authentication/oauth2/authorize'),
        methods=['GET', 'POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True
    )
    def oauth2_authorize(self, **kw):
        self._check_active_oauth2()
        if request.httprequest.method.upper() == 'POST':
            client_id = request.params.get('client_id')
            scopes = request.httprequest.form.getlist('scopes')
            try:
                uid = tools.security.check_login_credentials(
                    request.session.db, 
                    request.params.get('login', None), 
                    request.params.get('password', None)
                )
                headers, body, status = self.oauth2.create_authorization_response(
                    uri=tools.http.clean_query_params(request.httprequest.url, clean_db=True),
                    http_method=request.httprequest.method,
                    body=request.httprequest.form,
                    headers=dict(request.httprequest.headers.to_wsgi_list()),
                    scopes=scopes or [],
                    credentials={'user': uid}
                )
                return Response(body, status=status, headers=headers)
            except AccessDenied:
                if http.request._cr:
                    http.request._cr.rollback()
                values = self._oauth2_information(
                    client_id, 
                    request.params.get('redirect_uri', False), 
                    request.params.get('response_type', False), 
                    request.params.get('state', False), 
                    scopes
                )
                values.update({'error': _("Invalid login or password!")})
                return request.render('muk_rest.authorize_oauth2', values)
            
        scopes, credentials = self.oauth2.validate_authorization_request(
            uri=request.httprequest.url,
            http_method=request.httprequest.method,
            body=request.httprequest.form,
            headers=dict(request.httprequest.headers.to_wsgi_list())
        )
        values = self._oauth2_information(
            credentials.get('client_id', False), 
            credentials.get('redirect_uri', False), 
            credentials.get('response_type', False),
            credentials.get('state', False), 
            scopes
        )
        return request.render('muk_rest.authorize_oauth2', values)  

    @core.http.rest_route(
        routes=build_route('/authentication/oauth2/token'),
        methods=['GET', 'POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True
    )
    def oauth2_token(self, **kw):
        self._check_active_oauth2()
        headers, body, status = self.oauth2.create_token_response(
            uri=tools.http.clean_query_params(request.httprequest.url, clean_db=True),
            http_method=request.httprequest.method,
            body=request.httprequest.form,
            headers=dict(request.httprequest.headers.to_wsgi_list())
        )
        return Response(response=body, headers=headers, status=status) 
     
    @core.http.rest_route(
        routes=build_route('/authentication/oauth2/revoke'),
        methods=['GET', 'POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True
    )
    def oauth2_revoke(self, **kw):
        self._check_active_oauth2()
        headers, body, status = self.oauth2.create_revocation_response(
            uri=tools.http.clean_query_params(request.httprequest.url, clean_db=True),
            http_method=request.httprequest.method,
            body=request.httprequest.form,
            headers=dict(request.httprequest.headers.to_wsgi_list())
        )
        return Response(response=body, headers=headers, status=status) 
