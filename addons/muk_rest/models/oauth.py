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


import re
import datetime
import textwrap

from odoo import models, fields
from odoo.addons.muk_rest.tools.common import parse_value
from odoo.addons.muk_rest.tools.http import build_route


class OAuth(models.Model):
    
    _name = 'muk_rest.oauth'
    _description = "OAuth Configuration"
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------

    name = fields.Char(
        string="Name",
        required=True
    )
    
    active = fields.Boolean(
        string="Active",
        default=True
    )
    
    color = fields.Integer(
        string="Color"
    )
    
    company = fields.Char(
        string="Company"
    )
    
    homepage = fields.Char(
        string="Homepage URL"
    )
    
    logo_url = fields.Char(
        string="Product logo URL"
    )
    
    privacy_policy = fields.Char(
        string="Privacy policy URL"
    )
    
    service_terms = fields.Char(
        string="Terms of service URL"
    )
    
    description = fields.Text(
        string="Description"
    )
    
    security = fields.Selection(
        selection=[
            ('basic', "Basic Access Control"),
            ('advanced', "Advanced Access Control")
        ],
        string="Security",
        required=True,
        default='basic',
        help=textwrap.dedent("""\
            Defines the security settings to be used by the Restful API
            - Basic uses the user's security clearance to check requests from the API.
            - Advanced uses other rules in addition to the user security clearance, to further restrict the access.
        """)
    )
    
    callback_ids = fields.One2many(
        comodel_name='muk_rest.callback',
        inverse_name='oauth_id', 
        string="Callback URLs"
    )
    
    rule_ids = fields.One2many(
        comodel_name='muk_rest.access_rules',
        inverse_name='oauth_id', 
        string="Access Rules"
    )

    oauth1_ids = fields.One2many(
        comodel_name='muk_rest.oauth1',
        inverse_name='oauth_id',
    )
    
    oauth2_ids = fields.One2many(
        comodel_name='muk_rest.oauth2',
        inverse_name='oauth_id',
    )

    sessions = fields.Integer(
        compute='_compute_sessions',
        string="Sessions"
    )
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    def _check_callback(self, redirect_uri):
        callbacks = self.mapped('callback_ids.url')
        if redirect_uri in callbacks:
            return True
        for callback in callbacks:
            if re.match(callback, redirect_uri):
                return True
        return False

    def _check_security(self, routing, params):
        main_route = routing['routes'][0] if routing.get('routes') else None
        if main_route == build_route('/custom/<path:endpoint>')[0]:
            main_route = routing.get('custom_route', False)
        
        def get_applying_rules(route, rules):
            applying_rules = set()
            for rule in rules.filtered('applied'):
                if re.match(rule.route, route):
                    applying_rules.add(rule.id)
            return rules.browse(applying_rules)
        
        def check_rule(rule, params, cop, eop):
            if not rule.rule:
                return True
            for expr in parse_value(rule.rule, []):
                if expr[0] in cop and cop[expr[0]](str(expr[1]), params):
                    return False
                elif expr[0] in eop and expr[1] in params and \
                        eop[expr[0]](str(params[expr[1]]), str(expr[2])):
                    return False
            return True
            
        rules = get_applying_rules(main_route, self.rule_ids) 
        if rules:
            check_operators = {
                '*': lambda expr, params: expr not in params,
                '!': lambda expr, params: expr in params,
            }
            eval_operators = {
                '=': lambda val, expr: expr != val,
                '!=': lambda val, expr: expr == val,
                '%': lambda val, expr: expr not in val,
                '!%': lambda val, expr: expr in val,
                '#': lambda val, expr: not bool(re.match(expr, val)),
            }
            for rule in rules:
                if check_rule(rule, params, check_operators, eval_operators):
                    return True
        return False
    
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    def _compute_sessions(self):
        oauth1 = self.env['muk_rest.access_token'].sudo()
        oauth2 = self.env['muk_rest.bearer_token'].sudo()
        for record in self:
            sessions_count = 0
            sessions_count += oauth1.search_count([
                ('oauth_id.oauth_id', '=', record.id)
            ])
            sessions_count += oauth2.search_count([
                '&', ('oauth_id.oauth_id', '=', record.id), 
                '|', ('expiration_date', '>', datetime.datetime.utcnow()),
                ('expiration_date', '=', False),
            ])
            record.sessions = sessions_count
            
    #----------------------------------------------------------
    # Actions
    #----------------------------------------------------------
    
    def action_set_active(self):
        self.write({'active': True})

    def action_set_unactive(self):
        self.write({'active': False})
    
    def action_settings(self):
        self.ensure_one()
        action = {
            'name': _("Settings"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'current',
        }
        if self.oauth1_ids:
            action.update({
                'res_model': 'muk_rest.oauth1',
                'res_id': self.oauth1_ids.ids[0]
            })
        elif self.oauth2_ids:
            action.update({
                'res_model': 'muk_rest.oauth2',
                'res_id': self.oauth2_ids.ids[0]
            })
        return action
    
    def action_sessions(self):
        self.ensure_one()
        action = {
            'name': _("Sessions"),
            'type': 'ir.actions.act_window',
            'views': [(False, 'tree'), (False, 'form')],
            'target': 'current',
        }
        if self.oauth1_ids:
            action.update({
                'res_model': 'muk_rest.access_token',
                'domain': [('oauth_id', 'in', self.oauth1_ids.ids)],
            })
        elif self.oauth2_ids:
            action.update({
                'res_model': 'muk_rest.bearer_token',
                'domain': [('oauth_id', 'in', self.oauth2_ids.ids)],
                'context': {'search_default_active': 1},
            })
        return action
