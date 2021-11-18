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


import datetime

from oauthlib.oauth2 import RequestValidator
from oauthlib.oauth2 import InvalidRequestFatalError

from odoo import api, fields, http, SUPERUSER_ID
from odoo.tools.misc import consteq

from odoo.addons.muk_rest.tools import security
from odoo.addons.muk_rest.tools.http import build_route


class OAuth2RequestValidator(RequestValidator):
    
    #----------------------------------------------------------
    # Configuration
    #----------------------------------------------------------
    
    def client_authentication_required(self, request, *args, **kwargs):
        if request.grant_type in ('password', 'authorization_code', 'refresh_token'):
            request = self._ensure_client_parameters(request)
            if request.client_id and self.get_client(request.client_id):
                return True
        return False
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    def _ensure_request_client(self, request, client_id):
        if not request.client:
            request.client = self.get_client(client_id)
        return request.client
            
    def _ensure_client_parameters(self, request):
        if not request.client_id:
            authorization_header = request.headers.get('Authorization')
            username, password = security.decode_http_basic_authentication(authorization_header)
            request.client_id = username
            request.client_secret = password
        if not request.client_id:
            raise InvalidRequestFatalError(description='Missing client_id parameter.', request=request)
        return request
    
    def _check_client_id(self, obj, client_key):
        return obj and consteq(obj.oauth_id.client_id, client_key)
    
    def _retrieve_rule_routes(self, rules):
        return rules.filtered('applied').mapped('route')
        
    #----------------------------------------------------------
    # Validate
    #----------------------------------------------------------
    
    def validate_client_id(self, client_id, request, *args, **kwargs):
        self._ensure_request_client(request, client_id)
        return bool(request.client)

    def validate_redirect_uri(self, client_id, redirect_uri, request):
        self._ensure_request_client(request, client_id)
        if not request.client:
            return False
        request.redirect_uri = redirect_uri
        if redirect_uri  == self.get_docs_redirect_uri():
            return True
        return request.client.oauth_id._check_callback(redirect_uri)

    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        self._ensure_request_client(request, client_id)
        if not request.client:
            return False
        request.response_type = response_type
        return response_type in security.get_response_type(request.client.state)

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        if client and client.security == 'advanced':
            return set(self._retrieve_rule_routes(client.rule_ids)).issuperset(set(scopes))
        return True
    
    def validate_user(self, username, password, client, request, *args, **kwargs):
        request.user = security.check_login_credentials(
            http.request.session.db, username, password
        )
        return bool(request.user)

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        self._ensure_request_client(request, client_id)
        if not request.client:
            return False
        return grant_type == 'refresh_token' or grant_type == request.client.state

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        self._ensure_request_client(request, client_id)
        if not request.client:
            return False
        authorization_code = self.get_authorization_code(code, getattr(request, 'state', ''))
        if self._check_client_id(authorization_code, request.client.client_id):
            request.user = authorization_code.user_id.id
            return True
        return False

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        authorization_code = self.get_authorization_code(code, getattr(request, 'state', ''))
        if self._check_client_id(authorization_code, client_id):
            authorization_code.unlink()

    def validate_bearer_token(self, token, scopes, request):
        if not request.access_token:
            request.access_token = self.get_bearer_token(token)
        if not request.access_token:
            return False
        if request.access_token and request.access_token.oauth_id.security == 'advanced':
            rules = self._retrieve_rule_routes(request.access_token.oauth_id.rule_ids)
            return set(rules).issuperset(set(scopes))    
        if request.access_token.expiration_date is not None and \
                datetime.datetime.utcnow() > request.access_token.expiration_date:
            return False
        return True
    
    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        request.refresh_token = self.get_refresh_token(refresh_token)   
        if self._check_client_id(request.refresh_token, client.client_id):
            request.user = request.refresh_token.user_id.id
            return True
        return False   
        
    #----------------------------------------------------------
    # Authenticate
    #----------------------------------------------------------

    def authenticate_client(self, request, *args, **kwargs):
        request = self._ensure_client_parameters(request)
        self._ensure_request_client(request, request.client_id)
        if not request.client:
            return False
        if not request.client.client_secret:
            return True
        return request.client_secret and consteq(request.client.client_secret, request.client_secret)

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        request = self._ensure_client_parameters(request)
        self._ensure_request_client(request, client_id or request.client_id)
        if not request.client:
            return False
        return request.client and consteq(request.client.client_id, client_id)
    
    #----------------------------------------------------------
    # Confirm
    #----------------------------------------------------------
    
    def confirm_redirect_uri(self, client_id, code, redirect_uri, client, request, *args, **kwargs):
        self._ensure_request_client(request, client_id)
        if not request.client:
            return False
        authorization_code = self.get_authorization_code(code, getattr(request, 'state', ''))
        return authorization_code and authorization_code.callback == redirect_uri or False
    
    #----------------------------------------------------------
    # Getter
    #----------------------------------------------------------

    def get_client(self, client_id):
        domain = [('client_id', '=', client_id)]
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        return env['muk_rest.oauth2'].search(domain, limit=1)
      
    def get_docs_redirect_uri(self):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        base_url = env['ir.config_parameter'].get_param('web.base.url')
        return '{}{}'.format(base_url, build_route('/docs/oauth2/redirect')[0])
    
    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        self._ensure_request_client(request, client_id)
        return request.client.default_callback_id.url
      
    def get_default_scopes(self, client_id, request, *args, **kwargs):
        self._ensure_request_client(request, client_id)
        if request.client and request.client.security == 'advanced': 
            return self._retrieve_rule_routes(request.client.rule_ids)
        return []
    
    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        if not request.refresh_token:
            request.refresh_token = self.get_refresh_token(refresh_token)
        if request.refresh_token and request.refresh_token.oauth_id.security == 'advanced':
            return self._retrieve_rule_routes(request.refresh_token.oauth_id.rule_ids)
        return []
             
    def get_authorization_code(self, code, state):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        return env['muk_rest.authorization_code']._check_code(code, state)
    
    def get_bearer_token(self, token):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        return env['muk_rest.bearer_token']._check_token(token)
    
    def get_refresh_token(self, token):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        return env['muk_rest.bearer_token']._check_refresh(token)
    
    #----------------------------------------------------------
    # Setter
    #----------------------------------------------------------
    
    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        env['muk_rest.authorization_code']._save_authorization_code({
            'user_id': request.user,
            'oauth_id': request.client.id,
            'code': code['code'],
            'state': code.get('state', None),
            'callback': request.redirect_uri
        }) 

    def save_bearer_token(self, token, request, *args, **kwargs):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        expiration_date = None
        if token.get('expires_in', False):
            expires_in = env['ir.config_parameter'].get_param(
                'muk_rest.oauth2_bearer_expires_in_seconds', False
            )
            expires_in = int(expires_in or token['expires_in']) 
            timedelta = datetime.timedelta(seconds=expires_in)
            expiration_date = fields.Datetime.to_string(
                fields.Datetime.now() + timedelta
            )
            token['expires_in'] = expires_in
        env['muk_rest.bearer_token']._save_bearer_token({
            'user_id': request.user,
            'oauth_id': request.client.id,
            'access_token': token['access_token'],
            'refresh_token': token.get('refresh_token', None),
            'expiration_date': expiration_date,
        }) 
    
    #----------------------------------------------------------
    # Revoke
    #----------------------------------------------------------
    
    def revoke_token(self, token, token_type_hint, request, *args, **kwargs):
        access_token = self.get_bearer_token(token)
        return access_token and access_token.unlink()
