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

from oauthlib.common import to_unicode
from oauthlib.oauth1 import SIGNATURE_HMAC, RequestValidator

from odoo import api, http, SUPERUSER_ID
from odoo.tools.misc import consteq


class OAuth1RequestValidator(RequestValidator):
    
    #----------------------------------------------------------
    # Configuration
    #----------------------------------------------------------

    @property
    def client_key_length(self):
        return (20, 50)

    @property
    def request_token_length(self):
        return (20, 50)

    @property
    def access_token_length(self):
        return (20, 50)

    @property
    def nonce_length(self):
        return (20, 50)

    @property
    def verifier_length(self):
        return (20, 50)
    
    @property
    def enforce_ssl(self):
        if os.environ.get('OAUTHLIB_INSECURE_TRANSPORT'):
            return False
        return True
    
    #----------------------------------------------------------
    # Properties
    #----------------------------------------------------------

    @property
    def allowed_signature_methods(self):
        return (SIGNATURE_HMAC)

    @property
    def realms(self):
        return http.request.env['ir.model'].sudo().search([]).mapped('model')

    @property
    def dummy_client(self):
        return to_unicode('dummy_client', 'utf-8')

    @property
    def dummy_request_token(self):
        return to_unicode('dummy_request_token', 'utf-8')

    @property
    def dummy_access_token(self):
        return to_unicode('dummy_access_token', 'utf-8')

    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    def _ensure_request_client(self, request, client_key):
        if not request.client:
            request.client = self.get_client(client_key)
        return request.client
    
    def _ensure_request_token(self, request, token):
        if not request.request_token:
            request.request_token = self.get_request_token(token)
        return request.request_token
    
    def _ensure_access_token(self, request, token):
        if not request.access_token:
            request.access_token = self.get_access_token(token)
        return request.access_token

    def _check_client_key(self, token, client_key):
        return token and consteq(token.oauth_id.consumer_key, client_key)

    def _retrieve_rule_routes(self, rules):
        return rules.filtered('applied').mapped('route')
        
    #----------------------------------------------------------
    # Validate
    #----------------------------------------------------------
    
    def validate_client_key(self, client_key, request):
        self._ensure_request_client(request, client_key)
        return bool(request.client)

    def validate_request_token(self, client_key, token, request):
        self._ensure_request_token(request, token)
        return self._check_client_key(request.request_token, client_key)

    def validate_access_token(self, client_key, token, request):
        self._ensure_access_token(request, token)
        return self._check_client_key(request.access_token, client_key)
        
    def validate_timestamp_and_nonce(
        self, client_key, timestamp, nonce, request, request_token=None, access_token=None
    ):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        return env['muk_rest.request_data']._check_timestamp_and_nonce(
            client_key, timestamp, nonce, request_token or access_token
        )

    def validate_redirect_uri(self, client_key, redirect_uri, request):
        self._ensure_request_client(request, client_key)
        if not request.client:
            return False
        if not request.client.callback_ids and redirect_uri == 'oob':
            return True
        request.redirect_uri = redirect_uri
        return request.client.oauth_id._check_callback(redirect_uri)

    def validate_requested_realms(self, client_key, realms, request):
        self._ensure_request_client(request, client_key)
        if request.client and request.client.security == 'advanced': 
            rules = self._retrieve_rule_routes(request.client.rule_ids)
            return set(rules).issuperset(set(realms))
        return True
        
    def validate_realms(self, client_key, token, request, uri=None, realms=None):
        self._ensure_request_token(request, token)
        if request.request_token and request.request_token.oauth.security == 'advanced': 
            rules = self._retrieve_rule_routes(request.request_token.oauth_id.rule_ids)
            return set(rules).issuperset(set(realms))
        return True
        
    def validate_verifier(self, client_key, token, verifier, request):
        self._ensure_request_token(request, token)
        if not request.request_token:
            return None
        verifier_token = request.request_token._check_verifier(verifier)
        if self._check_client_key(request.request_token, client_key) and verifier_token and \
                verifier_token == request.request_token:
            request.user = request.request_token.user_id.id
            return True
        return None

    def invalidate_request_token(self, client_key, request_token, request):
        self._ensure_request_token(request, request_token)
        if self._check_client_key(request.request_token, client_key):
            request.request_token.unlink()

    #----------------------------------------------------------
    # Getter
    #----------------------------------------------------------

    def get_client(self, client_key):
        domain = [('consumer_key', '=', client_key)]
        client = http.request.env['muk_rest.oauth1'].sudo().search(domain, limit=1)
        return client.exists() and client

    def get_client_secret(self, client_key, request):
        if not (request.client or request.client_secret):
            request.client = self.get_client(client_key)
        if request.client:
            request.client_secret = request.client.consumer_secret
        if request.client_secret:
            return request.client_secret
        return None

    def get_request_token(self, token):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        return env['muk_rest.request_token']._check_resource(token)
    
    def get_request_token_secret(self, client_key, token, request):
        self._ensure_request_token(request, token)
        if self._check_client_key(request.request_token, client_key):
            return request.request_token._get_secret(request.request_token.id)
        return None
    
    def get_access_token(self, token):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        return env['muk_rest.access_token']._check_resource(token)
        
    def get_access_token_secret(self, client_key, token, request):
        self._ensure_access_token(request, token)
        if self._check_client_key(request.access_token, client_key):
            return request.access_token._get_secret(request.access_token.id)
        return None
    
    def get_redirect_uri(self, token, request):
        self._ensure_request_token(request, token)
        if request.request_token and request.request_token.callback:
            return request.request_token.callback
        return 'oob'
    
    def get_default_realms(self, client_key, request):
        if not request.client:
            request.client = self.get_client(client_key)
        if request.client and request.client.security == 'advanced': 
            return self._retrieve_rule_routes(request.client.rule_ids)
        return []

    def get_realms(self, token, request):
        self._ensure_request_token(request, token)
        if request.request_token and request.request_token.oauth_id.security == 'advanced':
            return self._retrieve_rule_routes(request.request_token.oauth_id.rule_ids)
        return []

    #----------------------------------------------------------
    # Setter
    #----------------------------------------------------------

    def save_request_token(self, token, request):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        env['muk_rest.request_token']._save_resource_owner({
            'callback': request.redirect_uri,
            'oauth_id': request.client.id,
            'resource_owner_key': token['oauth_token'],
            'resource_owner_secret': token['oauth_token_secret']
        })

    def save_verifier(self, token, verifier, request):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        token = env['muk_rest.request_token']._check_resource(token)
        token._update_resource_verifier(token, {
            'verifier': verifier['oauth_verifier'],
            'user': verifier['user']
        })

    def save_access_token(self, token, request):
        env = api.Environment(http.request.cr, SUPERUSER_ID, {})
        env['muk_rest.access_token']._save_resource_owner({
            'user_id': request.user,
            'oauth_id': request.client.id,
            'resource_owner_key': token['oauth_token'],
            'resource_owner_secret': token['oauth_token_secret']
        })
    
    #----------------------------------------------------------
    # Verify
    #----------------------------------------------------------

    def verify_request_token(self, token, request):
        self._ensure_request_token(request, token)
        if request.request_token:
            return True
        return False

    def verify_realms(self, token, realms, request):
        self._ensure_request_token(request, token)
        if request.request_token and request.request_token.oauth_id.security == 'advanced':
            rules = self._retrieve_rule_routes(request.request_token.oauth_id.rule_ids)
            return set(rules).issuperset(set(realms))
        return True
    