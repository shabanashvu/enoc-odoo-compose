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

from odoo import conf, models, api, fields, _
from odoo.exceptions import ValidationError


class AccessRule(models.Model):
    
    _name = 'muk_rest.access_rules'
    _description = "Access Control"
    _order = 'sequence, route'
    _rec_name = 'route'
    
    #----------------------------------------------------------
    # Selections
    #----------------------------------------------------------
    
    @api.model
    def _selection_routes(self):
        rest_route_urls_set = set()
        ir_http = self.env['ir.http']
        if hasattr(ir_http, '_routing_map'):
            for url, endpoint, routing in ir_http._generate_routing_rules(
                sorted(self.env.registry._init_modules | set(conf.server_wide_modules)),
                converters=ir_http._get_converters()
            ):  
                if routing and routing.get('rest', False) and routing.get('routes', False) and \
                        not routing.get('rest_access_hidden', False):
                    rest_route_urls_set.add(routing['routes'][0])    
            rest_route_urls_set.update(
                self.env['muk_rest.endpoint'].sudo().search([]).mapped('route')
            )      
        return [(url, url) for url in sorted(rest_route_urls_set)]
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------

    oauth_id = fields.Many2one(
        comodel_name='muk_rest.oauth',
        ondelete='cascade',
        string="OAuth Configuration",
        required=True, 
    )
    
    sequence = fields.Integer(
        string="Sequence",
        default=15,
    )

    applied = fields.Boolean(
        string="Applied",
        default=True
    )
    
    route = fields.Char(
        compute='_compute_route',
        string='Route',
        readonly=False,
        required=True, 
        store=True,
        help="The route value can be a regular expression."
    )
    
    route_selection = fields.Selection(
        selection='_selection_routes',
        string='Route Selection',
        store=False,
    )

    rule = fields.Text(
        compute='_compute_rule',
        string='Rule',
        readonly=True,
        store=True,
    )

    expression_ids = fields.One2many(
        comodel_name='muk_rest.access_rules.expression',
        inverse_name='rule_id',
        string="Expressions",
    )

    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('route_selection')
    def _compute_route(self):
        for record in self:
            record.route = record.route_selection

    @api.depends(
        'expression_ids', 
        'expression_ids.param', 
        'expression_ids.operation', 
        'expression_ids.expression'
    )
    def _compute_rule(self):
        for record in self:
            if not record.expression_ids:
                record.rule = None
            else:
                rule = list()
                for expr in record.expression_ids:
                    rule.append([
                        expr.operation, 
                        expr.param, 
                        expr.expression
                    ])
                record.rule = json.dumps(
                    rule, sort_keys=True, indent=4
                )


class AccessRuleExpression(models.Model):
    
    _name = 'muk_rest.access_rules.expression'
    _description = "Access Control Expression"
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------

    rule_id = fields.Many2one(
        comodel_name='muk_rest.access_rules',
        ondelete='cascade',
        string="Rule",
        required=True, 
    )

    name = fields.Char(
        compute='_compute_name',
        string="Name",
    )

    param = fields.Char(
        string="Parameter",
        required=True,
    )

    operation = fields.Selection(
        selection=[
            ('!', 'is forbidden'),
            ('*', 'is required'),
            ('=', 'is equal to'),
            ('!=', 'is not equal to'),
            ('%', 'contains'),
            ('!%', 'doesn\'t contains'),
            ('#', 'match against'),
        ],
        string="Operation",
        required=True,
    )

    expression = fields.Char(
        compute='_compute_expression',
        string="Expression",
        readonly=False,
        store=True,
    )

    #----------------------------------------------------------
    # Constrains
    #----------------------------------------------------------

    @api.constrains('operation', 'expression')
    def _check_operation(self):
        for record in self:
            if record.operation not in ['!', '*'] and not record.expression:
                raise ValidationError(_("Invalid Expression!"))

    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('param', 'operation', 'expression')
    def _compute_name(self):
        for record in self:
            if record.operation not in ['!', '*']:
                record.name = '{} {} {}'.format(
                    record.param, record.operation, record.expression
                )
            else:
                record.name = '({}) {}'.format(
                    record.operation, record.param
                )

    @api.depends('operation')
    def _compute_expression(self):
        for record in self:
            if record.operation in ['!', '*']:
                record.expression = None
            else:
                record.expression = record.expression
