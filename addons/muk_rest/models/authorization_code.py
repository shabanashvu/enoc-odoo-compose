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


from odoo import _, models, api, fields
from odoo.addons.muk_rest.tools import common

class AuthorizationCode(models.Model):
    
    _name = 'muk_rest.authorization_code'
    _description = "OAuth2 Authorization Code"
    _auto = False
    
    #----------------------------------------------------------
    # Setup Database
    #----------------------------------------------------------
    
    def init(self):
        self.env.cr.execute("""
            CREATE TABLE IF NOT EXISTS {table} (
                id SERIAL PRIMARY KEY,
                state VARCHAR,
                callback VARCHAR,
                code VARCHAR NOT NULL,
                index VARCHAR({index_size}) NOT NULL CHECK (char_length(index) = {index_size}),
                oauth_id INTEGER NOT NULL REFERENCES muk_rest_oauth2(id),
                user_id INTEGER NOT NULL REFERENCES res_users(id),
                create_date TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'UTC')
            );
            CREATE INDEX IF NOT EXISTS {table}_index_idx ON {table} (index);
        """.format(table=self._table, index_size=common.TOKEN_INDEX))

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    create_date = fields.Datetime(
        string="Creation Date", 
        readonly=True
    )

    callback = fields.Char(
        string="Callback",
        readonly=True
    )
    
    user_id = fields.Many2one(
        comodel_name='res.users',
        ondelete='cascade',
        string="User",
        readonly=True,
    )
    
    oauth_id = fields.Many2one(
        comodel_name='muk_rest.oauth2',
        ondelete='cascade',
        string="Configuration",
        required=True, 
        readonly=True,
    )
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    @api.model
    def _check_code(self, code, state=None):
        if not code:
            return False
        self.env.cr.execute(
            "SELECT id, code FROM {table} WHERE index = %s {where_state}".format(
                table=self._table, where_state=(state and 'AND (state IS NULL OR state = %s)' or '')
            ), 
            [code[:common.TOKEN_INDEX]], state
        )
        for code_id, code_hash in self.env.cr.fetchall():
            if common.KEY_CRYPT_CONTEXT.verify(code, code_hash):
                return self.browse([code_id])
        return False

    @api.model
    def _save_authorization_code(self, values):
        fields = ['oauth_id', 'user_id', 'callback', 'index', 'code']
        insert = [
            values['oauth_id'], 
            values['user_id'], 
            values['callback'],
            values['code'][:common.TOKEN_INDEX], 
            common.hash_token(values['code'])
        ]
        if values.get('state', False):
            fields.append('state')
            insert.append(values['state'])
        self.env.cr.execute("""
            INSERT INTO {table} ({fields})
            VALUES ({values})
            RETURNING id
        """.format(
            table=self._table, 
            fields=', '.join(fields), 
            values=', '.join(['%s' for _ in range(len(fields))])
        ), insert)
    
    #----------------------------------------------------------
    # Autovacuum
    #----------------------------------------------------------
    
    @api.autovacuum
    def _autovacuum_code(self):
        limit_date = fields.Datetime.subtract(fields.Datetime.now(), days=7)
        self.search([('create_date', '<', limit_date)]).unlink()
