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
import urllib
import logging
import requests
import unittest
import requests

from odoo import _, SUPERUSER_ID
from odoo.tests import common

from odoo.addons.muk_rest.tools.common import generate_token
from odoo.addons.muk_rest.tests.common import oauthlib, requests_oauthlib
from odoo.addons.muk_rest.tests.common import skip_check_authentication
from odoo.addons.muk_rest.tests.common import RestfulCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class RulesTestCase(RestfulCase):
    
    def setUp(self):
        super(RulesTestCase, self).setUp()
        self.oauth_settings_client_key = generate_token()
        self.oauth_settings_client_secret = generate_token()
        self.oatuh_settings_client = self.env['muk_rest.oauth2'].create({
            'name': "Security Rules Test",
            'client_id': self.oauth_settings_client_key,
            'client_secret': self.oauth_settings_client_secret,
            'state': 'password',
            'security': 'advanced',
            'rule_ids': [(0, 0, {
                'route': '/api/v1/search',
                'sequence': 5,
                'expression_ids': [(0, 0, {
                    'param': 'model',
                    'operation': '*',
                }), (0, 0, {
                    'param': 'model',
                    'operation': '#',
                    'expression': 'res.partner|res.users',
                })]
            }), (0, 0, {
                'route': '/api/v1/.+',
                'sequence': 10,
                'expression_ids': [(0, 0, {
                    'param': 'model',
                    'operation': '=',
                    'expression': 'res.partner',
                })]
            })]
        })
        self.env['muk_rest.oauth2'].flush()
        
    @skip_check_authentication()
    def test_oauth_valid(self):
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=self.oauth_settings_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        oauth.headers.update({self.db_header: self.env.cr.dbname})
        token = oauth.fetch_token(
            token_url=self.oauth2_access_token_url,
            client_id=self.oauth_settings_client_key, 
            client_secret=self.oauth_settings_client_secret,
            username=self.login,
            password=self.password
        )
        self.assertTrue(oauth.get(self.search_url, data={'model': 'res.partner'}))
        
    @skip_check_authentication()
    def test_oauth_invalid(self):
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=self.oauth_settings_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        oauth.headers.update({self.db_header: self.env.cr.dbname})
        token = oauth.fetch_token(
            token_url=self.oauth2_access_token_url,
            client_id=self.oauth_settings_client_key, 
            client_secret=self.oauth_settings_client_secret,
            username=self.login,
            password=self.password
        )
        self.assertFalse(oauth.get(self.search_url, data={'model': 'res.lang'}))
        
    @skip_check_authentication()
    def test_oauth_generic_rule(self):
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=self.oauth_settings_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        oauth.headers.update({self.db_header: self.env.cr.dbname})
        token = oauth.fetch_token(
            token_url=self.oauth2_access_token_url,
            client_id=self.oauth_settings_client_key, 
            client_secret=self.oauth_settings_client_secret,
            username=self.login,
            password=self.password
        )
        self.assertTrue(oauth.get(self.xmlid_url, data={'xmlid': 'base.main_company'}))
        self.assertFalse(oauth.get(self.field_names_url, data={'model': 'res.users'}))
        self.assertTrue(oauth.get(self.field_names_url, data={'model': 'res.partner'}))
        self.assertTrue(oauth.get(self.search_url, data={'model': 'res.users'}))
        