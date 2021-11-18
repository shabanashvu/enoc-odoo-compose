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


import base64
import logging
import dateutil
import textwrap

from pytz import timezone
from werkzeug import exceptions

from odoo import tools, models, api, fields, _
from odoo.http import request, Response
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.tools.safe_eval import datetime, time, dateutil

from odoo.addons.muk_rest.tools import common, docs
from odoo.addons.muk_rest.tools.http import make_json_response
from odoo.addons.muk_rest.tools.safe_eval import responses, exceptions


class Endpoint(models.Model):
    
    _name = 'muk_rest.endpoint'
    _description = "Custom Restful Endpoint"

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    name = fields.Char(
        string="Name",
        required=True
    )
    
    active = fields.Boolean(
        string="Active",
        default=True, 
        help="When unchecked, the endpoint is inactive and will not be available through the API."
    )
    
    method = fields.Selection(
        selection=[
            ("GET", "GET"),
            ("POST", "POST"),
            ("PUT", "PUT"),
            ("DELETE", "DELETE")
        ],
        string="HTTP Method",
        required=True,
        default='GET'
    )
    
    endpoint = fields.Char(
        string="Custom Endpoint",
        required=True
    )
    
    route = fields.Char(
        compute='_compute_route',
        string="Custom Route",
        readonly=True,
        store=True
    )
    
    url = fields.Char(
        compute='_compute_url',
        string="Custom Route URL",
    )
    
    protected = fields.Boolean(
        string='Protected', 
        default=True,
        help="When unchecked, the endpoint is protected and only users with valid credentials can use it."
    )
    
    model_id = fields.Many2one(
        comodel_name='ir.model', 
        string='Model', 
        required=True, 
        ondelete='cascade'
    )
    
    model_name = fields.Char(
        related='model_id.model',
        string="Model Name",
        readonly=True,
    )

    state = fields.Selection(
        selection=[
            ('domain', 'Evaluate Domain'),
            ('action', 'Execute a Server Action'),
            ('code', 'Execute Python Code')
        ],
        string='Evaluation Type',
        required=True,
        default='domain', 
        help=textwrap.dedent("""\
            Type of the endpoint. The following values are available:
            - Evaluate Domain: A domain that is evaluated on the model.
            - Execute a Server Action: A server action that is run.
            - Execute Python Code: A block of Python code that will be executed.
        """)
    )
    
    eval_sudo = fields.Boolean(
        string="Sudo Evaluation",
        default=False,
        help="If checked the result is evaluated without access checks.",
    )
    
    wrap_response = fields.Boolean(
        string="Wrap Response",
        default=True,
        states={
            'domain': [('invisible', False)], 
            'action': [('invisible', False)], 
            'code': [('invisible', True)]
        },
        help="If checked the result is wrapped with meta information.",
    )
    
    action_id = fields.Many2one(
        comodel_name='ir.actions.server', 
        string="Server Actions",
        domain="[('model_id', '=', model_id)]",
        ondelete='cascade',
        states={
            'domain': [('invisible', True)], 
            'action': [('required', True)], 
            'code': [('invisible', True)]
        },
        help="Action that is called by the endpoint."
    )
    
    domain = fields.Char(
        string='Domain',
        states={
            'domain': [('required', True)], 
            'action': [('invisible', True)], 
            'code': [('invisible', True)]
        },
        help="Domain that is called by the endpoint."
    )
    
    domain_field_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        domain="[('model_id', '=', model_id)]", 
        string='Fields',
        states={
            'action': [('invisible', True)], 
            'code': [('invisible', True)]
        },
        help="Domain Field that will be automatically read after the search."
    )
    
    code = fields.Text(
        string='Code',
        states={
            'domain': [('invisible', True)], 
            'action': [('invisible', True)], 
            'code': [('required', True)]
        },
        help="Python code that is called by the endpoint.",
        default=textwrap.dedent("""\
            # Information about Python expression is available in the help tab of this document.
            # Enter Python code here...
        """)
    )
    
    logging = fields.Boolean(
        string="Logging",
        default=True,
    )
    
    show_logging = fields.Boolean(
        compute='_compute_show_logging',
        string="Show Logging",
    )

    docs_summary = fields.Char(
        string="Summary"
    )
    
    docs_description = fields.Text(
        string="Description"
    )
    
    docs_parameters = fields.Text(
        string="Parameters",
        help="Describe the parameters to display them in the documentation."
    )
    
    docs_responses = fields.Text(
        string="Responses",
        help="Describe the responses to display them in the documentation."
    )
    
    docs_default_response_200 = fields.Boolean(
        string="200",
        default=True,
    )
    
    docs_default_response_400 = fields.Boolean(
        string="400",
        default=True,
    )
    
    docs_default_response_401 = fields.Boolean(
        string="401",
        default=True,
    )
    
    docs_default_response_500 = fields.Boolean(
        string="500",
        default=True,
    )
    
    docs_components = fields.Text(
        string="Components",
        help=textwrap.dedent("""\
            Describe the components to display them in the documentation.
            Components are global objects. It is therefore possible to use 
            components of other endpoints, as well as those defined by 
            REST API itself. Since all components share the same scope it
            is important to define a unique name.
        """)
    )
    
    #----------------------------------------------------------
    # Constrains
    #----------------------------------------------------------
    
    @api.constrains('docs_parameters')
    def _check_docs_parameters(self):
        for record in self.sudo().filtered('docs_parameters'):
            try:
                params = common.parse_value(
                    record.docs_parameters or '[]', 
                    raise_exception=True
                )
                if not isinstance(params, list):
                    raise ValidationError(_("Parameters need to be a list of objects."))
            except Exception as exc:
                raise ValidationError(_("Parameters are not valid JSON\n\n{}".format(repr(exc))))
            
    @api.constrains('docs_responses')
    def _check_docs_responses(self):
        for record in self.sudo().filtered('docs_responses'):
            try:
                responses = common.parse_value(
                    record.docs_responses or '{}', 
                    raise_exception=True
                )
                if not isinstance(responses, dict):
                    raise ValidationError(_("Responses need to be a map of status codes."))
            except Exception as exc:
                raise ValidationError(_("Responses are not valid JSON\n\n{}".format(repr(exc))))
            
    @api.constrains('docs_components')
    def _check_docs_components(self):
        for record in self.sudo().filtered('docs_components'):
            try:
                components = common.parse_value(
                    record.docs_components or '{}', 
                    raise_exception=True
                )
                if not isinstance(components, dict):
                    raise ValidationError(_("Components need to be a map of component names."))
            except Exception as exc:
                raise ValidationError(_("Components are not valid JSON\n\n{}".format(repr(exc))))

    @api.constrains('code')
    def _check_code(self):
        for record in self.sudo().filtered('code'):
            message = test_python_expr(expr=record.code.strip(), mode="exec")
            if message:
                raise ValidationError(message)
    
    @api.constrains('state', 'action_id', 'code')
    def _validate(self):
        validators = {
            'domain': lambda rec: True,
            'action': lambda rec: rec.action_id,
            'code': lambda rec: rec.code,
        }
        for record in self:
            if not validators[record.state](record):
                raise ValidationError(_("Endpoint validation has failed!"))

    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('endpoint')
    def _compute_route(self):
        for record in self:
            record.route = '{}/custom/{}'.format(
                common.BASE_URL, (record.endpoint or '').lstrip('/')
            )
            
    @api.depends('route')
    def _compute_url(self):
        params = request.env['ir.config_parameter'].sudo()
        server_url = params.get_param('web.base.url')
        for record in self:
            record.url = '{}{}'.format(server_url, record.route)
    
    def _compute_show_logging(self):
        self.update({'show_logging': tools.config.get('rest_logging', True)})
        
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    @api.model
    def _get_eval_context(self, headers, params, model):
        return {
            'time': time,
            'datetime': datetime,
            'dateutil': dateutil,
            'timezone': timezone,
            'json': tools.safe_eval.json,
            'b64encode': base64.b64encode,
            'b64decode': base64.b64decode,
            'date_format': DEFAULT_SERVER_DATE_FORMAT,
            'datetime_format': DEFAULT_SERVER_DATETIME_FORMAT,
            'string_to_date': fields.Date.to_date,
            'date_to_string': fields.Date.to_string,
            'string_to_datetime': fields.Datetime.to_datetime,
            'datetime_to_string': fields.Datetime.to_string,
            'make_response': make_json_response,
            'responses': responses,
            'exceptions': exceptions,
            'Response': Response,
            'uid': model.env.uid,
            'user': model.env.user,
            'env': model.env,
            'model': model,
            'headers': headers,
            'params': params,
            'logger': logging.getLogger(
                '%s (%s)'.format(__name__, self.name)
            ),
        }
        
    def _evaluate_domain(self, headers, params, user):
        model_with_user = self.env[self.model_id.model].with_user(user)
        model = model_with_user.sudo() if self.eval_sudo else model_with_user   
        fields = self.domain_field_ids.mapped('name') or None
        domain = safe_eval(self.domain or '[]', {
            'datetime': datetime, 'uid': user.id,
        })
        limit = params.get('limit', None)
        offset = params.get('offset', None)
        result = model.search_read(
            domain,
            fields=fields,
            limit=limit and int(limit) or None,
            offset=offset and int(offset) or None,

        )
        if self.wrap_response:
            return make_json_response({
                'endpoint': self.route,
                'model': model._name,
                'domain': domain,
                'fields': fields,
                'limit': limit and int(limit) or None,
                'offset': offset and int(offset) or None,
                'result': result,
                'count': model.search_count(domain),
            })
        return make_json_response(result)
        
    def _evaluate_action(self, headers, params, user):
        active_id = common.parse_value(params.get('id'))
        active_ids = common.parse_value(params.get('ids'), [])
        model_with_user = self.env[self.model_id.model].with_user(user)
        model = model_with_user.sudo() if self.eval_sudo else model_with_user
        result = self.action_id.with_user(user).sudo(self.eval_sudo).with_context(
            active_id=active_id,
            active_ids=active_ids,
            active_model=model._name,
        ).run()
        if self.wrap_response:
            return make_json_response({
                'endpoint': self.route,
                'action': self.action_id.display_name,
                'result': result,
            })
        return make_json_response(result)
        
    def _evaluate_code(self, headers, params, user):
        model_with_user = self.env[self.model_id.model].with_user(user)
        model = model_with_user.sudo() if self.eval_sudo else model_with_user
        eval_context = self._get_eval_context(headers, params, model)
        safe_eval(self.code.strip(), eval_context, mode="exec", nocopy=True)   
        if eval_context.get('result', False):
            return make_json_response({
                'endpoint': self.route, 
                'result': eval_context['result']
            })
        elif eval_context.get('content', False):
            return make_json_response(eval_context['content'])
        elif eval_context.get('response', False):
            return eval_context['response']
        return make_json_response(True)
    
    #----------------------------------------------------------
    # Actions
    #----------------------------------------------------------
    
    def action_open_docs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '{}/docs#/Custom/{}{}_custom_{}'.format(
                common.BASE_URL, 
                self.method.lower(), 
                common.BASE_URL.lower().replace('/', '_'),
                self.endpoint.replace('/', '_')
            ),
            'target': 'new',
        }
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Custom Endpoints'),
            'template': '/muk_rest/static/xls/muk_rest_endpoints.xls'
        }]
        
    @api.model
    def get_docs(self):
        endpoints = self.sudo().search([])
        if not endpoints:
            return {}, {}
        custom_paths = {}
        custom_component = {}
        for endpoint in endpoints:
            endpoint_path_values = {
                'tags': ['Custom'],
                'summary': endpoint.docs_summary or '',
                'description': endpoint.docs_description or '',
                'parameters': common.parse_value(endpoint.docs_parameters, []),
            }  
            responses = common.parse_value(endpoint.docs_responses, {})
            for response in ['200', '400', '401', '500']:
                field = 'docs_default_response_{}'.format(response)
                if getattr(endpoint, field, False) and response not in responses:
                    responses[response] = docs.DEFAULT_RESPONSES[response]
            endpoint_path_values['responses'] = responses
            if endpoint.protected:
                endpoint_path_values['security'] = []
                if common.ACTIVE_BASIC_AUTHENTICATION:
                    endpoint_path_values['security'].append({
                        'BasicAuth': []
                    })
                if common.ACTIVE_OAUTH2_AUTHENTICATION:
                    endpoint_path_values['security'].append({
                        'OAuth2': []
                    })
            custom_paths[endpoint.route] = {
                endpoint.method.lower(): endpoint_path_values
            }
            custom_component.update(common.parse_value(endpoint.docs_components, {}))
        return custom_paths, custom_component

    def evaluate(self, headers, params, user):
        self.ensure_one()
        if hasattr(self, '_evaluate_{}'.format(self.state)):
            return getattr(self, '_evaluate_{}'.format(self.state))(headers, params, user)
        return exceptions.BadRequest('Invalid endpoint!')
        