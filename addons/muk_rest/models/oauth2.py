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
from odoo.exceptions import ValidationError

from odoo.addons.muk_rest.tools import common


class OAuth2(models.Model):
    
    _name = 'muk_rest.oauth2'
    _description = "OAuth2 Configuration"

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------

    oauth_id = fields.Many2one(
        comodel_name='muk_rest.oauth',
        ondelete='cascade',
        string='OAuth',
        delegate=True,  
        required=True,
    )
    
    active = fields.Boolean(
        related='oauth_id.active',
        readonly=False,
        store=True,
    )
    
    state = fields.Selection(
        selection=[
            ('authorization_code', 'Authorization Code'),
            ('implicit', 'Implicit'),
            ('password', 'Password Credentials'),
            ('client_credentials', 'Client Credentials')
        ],
        string="OAuth Type",
        required=True,
        default='authorization_code'
    )
    
    client_id = fields.Char(
        string="Client Key",
        required=True,
        default=lambda x: common.generate_token()
    )
    
    client_secret = fields.Char(
        string="Client Secret",
        states={
            'authorization_code': [('required', True)], 
            'client_credentials': [('required', True)]
        },
        default=lambda x: common.generate_token()
    )
    
    default_callback_id = fields.Many2one(
        compute='_compute_default_callback_id',
        comodel_name='muk_rest.callback',
        string="Default Callback",
        readonly=True,
        store=True,
    )
    
    user_id = fields.Many2one(
        comodel_name='res.users',
        ondelete='cascade',
        string="User",
        states={
            'authorization_code': [('invisible', True)], 
            'implicit': [('invisible', True)], 
            'password': [('invisible', True)], 
            'client_credentials': [('required', True)]
        },
    )
    
    #----------------------------------------------------------
    # Constraints
    #----------------------------------------------------------
    
    _sql_constraints = [
        ('client_id_unique', 'UNIQUE (client_id)', 'Client ID must be unique.'),
        ('client_secret_unique', 'UNIQUE (client_secret)', 'Client Secret must be unique.'),
    ]
    
    @api.constrains('state', 'callback_ids')
    def _check_default_callback_id(self):
        for record in self.filtered(lambda rec: rec.state == 'authorization_code'):
            if not record.default_callback_id:
                raise ValidationError(_("Authorization Code needs a default callback."))
    
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('callback_ids', 'callback_ids.sequence')
    def _compute_default_callback_id(self):
        for record in self:
            if len(record.callback_ids) >= 1:
                record.default_callback_id = record.callback_ids[0]
            else:
                record.default_callback_id = False
        
    #----------------------------------------------------------
    # Create / Update / Delete
    #----------------------------------------------------------

    def unlink(self):
        self.mapped('oauth_id').unlink()
        return super(OAuth2, self).unlink()
        