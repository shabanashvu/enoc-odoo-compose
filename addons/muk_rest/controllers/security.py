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


import collections

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError

from odoo.addons.muk_rest import tools, core
from odoo.addons.muk_rest.tools.docs import api_doc
from odoo.addons.muk_rest.tools.http import build_route


class SecurityController(http.Controller):

    _api_doc_components = {
        'AccessGroups': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'category_id': {
                        '$ref': '#/components/schemas/RecordTuple',
                    },
                    'comment': {
                        'type': 'string',
                    },
                    'full_name': {
                        'type': 'string',
                    },
                    'id': {
                        'type': 'integer',
                    },
                    'name': {
                        'type': 'string',
                    },
                    'xmlid': {
                        'type': 'string',
                    }
                },
            },
            'description': 'Information about access groups.'
        }
    }

    @api_doc(
        tags=['Security'], 
        summary='Access Rights', 
        description='Check the access rights for the current user.',
        parameter={
            'model': {
                'name': 'model',
                'description': 'Model',
                'required': True,
                'schema': {
                    'type': 'string'
                },
                'example': 'res.partner',
            },
            'operation': {
                'name': 'operation',
                'description': 'Operation',
                'schema': {
                    'type': 'string'
                }
            },
        },
        responses={
            '200': {
                'description': 'Returns True or False', 
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'boolean'
                        },
                    }
                },
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/access/rights',
            '/access/rights/<string:model>',
            '/access/rights/<string:model>/<string:operation>',
        ]), 
        methods=['GET'],
        protected=True,
    )
    def access_rights(self, model, operation='read', **kw):
        try:
            return request.make_json_response(request.env[model].check_access_rights(operation))
        except (AccessError, UserError):
            pass
        return request.make_json_response(False)

    @api_doc(
        tags=['Security'], 
        summary='Access Rules', 
        description='Check the access rules for the current user.',
        parameter={
            'model': {
                'name': 'model',
                'description': 'Model',
                'required': True,
                'schema': {
                    'type': 'string'
                },
                'example': 'res.partner',
            },
            'ids': {
                'name': 'ids',
                'description': 'Record IDs',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordIDs',
                        }
                    }
                },
                'example': [],
            },
            'operation': {
                'name': 'operation',
                'description': 'Operation',
                'schema': {
                    'type': 'string'
                }
            },
        },
        responses={
            '200': {
                'description': 'Returns True or False', 
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'boolean'
                        },
                    }
                },
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/access/rules',
            '/access/rules/<string:model>',
            '/access/rules/<string:model>/<string:operation>',
        ]), 
        methods=['GET'],
        protected=True,
    )
    def access_rules(self, model, ids, operation='read', **kw):
        ids = tools.common.parse_ids(ids)
        try:
            return request.make_json_response(
                request.env[model].browse(ids).check_access_rule(operation) is None
            )
        except (AccessError, UserError):
            pass
        return request.make_json_response(False)
     
    @api_doc(
        tags=['Security'], 
        summary='Access Fields', 
        description='Check the access to fields for the current user.',
        parameter={
            'model': {
                'name': 'model',
                'description': 'Model',
                'required': True,
                'schema': {
                    'type': 'string'
                },
                'example': 'res.partner',
            },
            'operation': {
                'name': 'operation',
                'description': 'Operation',
                'schema': {
                    'type': 'string'
                }
            },
            'fields': {
                'name': 'fields',
                'description': 'Fields',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordFields',
                        }
                    }
                },
                'example': ['name'],
            },
        },
        responses={
            '200': {
                'description': 'Returns True or False', 
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'boolean'
                        },
                    }
                },
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/access/fields',
            '/access/fields/<string:model>',
            '/access/fields/<string:model>/<string:operation>',
        ]), 
        methods=['GET'],
        protected=True,
    )
    def access_fields(self, model, operation='read', fields=None, **kw):
        try:
            return request.make_json_response(request.env[model].check_field_access_rights(
                operation, fields=tools.common.parse_value(fields)
            ))
        except (AccessError, UserError):
            pass
        return request.make_json_response(False)
    
    @api_doc(
        tags=['Security'], 
        summary='Access', 
        description='Check the access for the current user.',
        parameter={
            'model': {
                'name': 'model',
                'description': 'Model',
                'required': True,
                'schema': {
                    'type': 'string'
                },
                'example': 'res.partner',
            },
            'ids': {
                'name': 'ids',
                'description': 'Record IDs',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordIDs',
                        }
                    }
                },
                'example': [],
            },
            'operation': {
                'name': 'operation',
                'description': 'Operation',
                'schema': {
                    'type': 'string'
                }
            },
            'fields': {
                'name': 'fields',
                'description': 'Fields',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordFields',
                        }
                    }
                },
                'example': ['name'],
            },
        },
        responses={
            '200': {
                'description': 'Returns True or False', 
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'boolean'
                        },
                    }
                },
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/access',
            '/access/<string:model>',
            '/access/<string:model>/<string:operation>',
        ]), 
        methods=['GET'],
        protected=True,
    )
    def access(self, model, ids, operation='read', fields=None, **kw):
        ids = tools.common.parse_ids(ids)
        fields = tools.common.parse_value(fields)
        try:
            rights = request.env[model].check_access_rights(operation)
            rules = request.env[model].browse(ids).check_access_rule(operation) is None
            fields = request.env[model].check_field_access_rights(operation, fields=fields)
            return request.make_json_response(rights and rules and bool(fields))
        except (AccessError, UserError):
            pass
        return request.make_json_response(False)
    
    @api_doc(
        tags=['Security'], 
        summary='Access Groups', 
        description='Returns the access groups of the current user.',
        responses={
            '200': {
                'description': 'Access Groups', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/AccessGroups'
                        },
                        'example': [{
                            'category_id': [62, 'Administration'],
                            'comment': False,
                            'full_name': 'Administration / Access Rights',
                            'id': 2,
                            'name': 'Access Rights',
                            'xmlid': 'base.group_erp_manager'
                        }]
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/groups'), 
        methods=['GET'],
        protected=True,
    )
    def access_groups(self, **kw):
        groups = request.env['res.groups'].sudo().search([
            ('users', '=', request.env.uid)
        ])
        groups_data = groups.read([
            'name', 'category_id', 'full_name', 'comment'
        ])
        xmlids = collections.defaultdict(list)
        model_data = request.env['ir.model.data'].sudo().search_read(
            [('model', '=', 'res.groups'), ('res_id', 'in', groups.ids)], 
            ['module', 'name', 'res_id']
        )
        for rec in model_data:
            xmlids[rec['res_id']].append(
               '{}.{}'.format(rec['module'], rec['name'])
            )
        for rec in groups_data:
            rec['xmlid'] = xmlids.get(rec['id'], [''])[0]
        return request.make_json_response(groups_data)
 
    @api_doc(
        tags=['Security'], 
        summary='Access Group', 
        description='Check if the current user is a member of the group.',
        parameter={
            'group': {
                'name': 'group',
                'description': 'XMLID of the Group',
                'required': True,
                'schema': {
                    'type': 'string'
                },
                'example': 'base.group_user',
            },
        },
        responses={
            '200': {
                'description': 'Returns True or False', 
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'boolean'
                        },
                    }
                },
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/has_group'), 
        methods=['GET'],
        protected=True,
    )
    def access_has_group(self, group, **kw):
        return request.make_json_response(request.env.user.has_group(group))
    