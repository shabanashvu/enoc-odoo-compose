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


from odoo import models, api, fields
from odoo.addons.muk_rest.tools import common


class Request(models.Model):
    
    _name = 'muk_rest.request_data'
    _description = "Request"

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------

    client_key = fields.Char(
        string="Client Key",
        readonly=True,
    )
    
    timestamp = fields.Char(
        string="Timestamp",
        readonly=True,
    )
    
    nonce = fields.Char(
        string="Nonce",
        readonly=True,
    )
    
    token_hash = fields.Char(
        string="Token",
        readonly=True,
    )
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    def _check_timestamp_and_nonce(self, client_key, timestamp, nonce, token=None):
        timestamp_and_nonce_domain = [
            ('client_key', '=', client_key), 
            ('timestamp', '=', timestamp), 
            ('nonce', '=', nonce)
        ]
        for record in self.search(timestamp_and_nonce_domain):
            if record.token_hash is None and token is None:
                return False
            elif token and common.KEY_CRYPT_CONTEXT.verify(token, record.token_hash):
                return False
        return self.create({
            'client_key': client_key,
            'timestamp': timestamp,
            'nonce': nonce,
            'token_hash': token and common.hash_token(token) or None
        })
         
    #----------------------------------------------------------
    # Autovacuum
    #----------------------------------------------------------
    
    @api.autovacuum
    def _autovacuum_requests(self):
        limit_date = fields.Datetime.subtract(fields.Datetime.now(), days=1)
        self.search([('create_date', '<', limit_date)]).unlink()
