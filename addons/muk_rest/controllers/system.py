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


import inspect

from odoo import http
from odoo.http import request
from odoo.models import regex_private

from odoo.addons.muk_rest import tools, core
from odoo.addons.muk_rest.tools.docs import api_doc
from odoo.addons.muk_rest.tools.http import build_route


class SystemController(http.Controller):
    
    _api_doc_components = {
        'ModelNames': {
            'type': 'array',
            'items': {
                'type': 'string',
            },
            'description': 'A list of all available models.'
        },
        'ModelAttributes': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'model': {
                        'type': 'string',
                    },
                    'name': {
                        'type': 'string',
                    },
                    'order': {
                        'type': 'string',
                    },
                    'transient': {
                        'type': 'boolean',
                    },
                },
            },
            'description': 'A list of all available models.'
        },
        'FieldNames': {
            'type': 'array',
            'items': {
                'type': 'string',
            },
            'description': 'A list of all available field names.'
        },
        'FieldAttributes': {
            'type': 'object',
            'description': 'A list of all available fields attributes.'
        },
        'FunctionNames': {
            'type': 'array',
            'items': {
                'type': 'string',
            },
            'description': 'A list of all available function names.'
        },
        'FunctionAttributes': {
            'type': 'object',
            'description': 'A list of all available function attributes.'
        },
        'Metadata': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'create_date': {
                        'type': 'string',
                        'type': 'date-time',
                    },
                    'create_uid': {
                        '$ref': '#/components/schemas/RecordTuple'
                    },
                    'id': {
                        'type': 'integer',
                    },
                    'noupdate': {
                        'type': 'boolean',
                    },
                    'write_date': {
                        'type': 'string',
                        'type': 'date-time',
                    },
                    'write_uid': {
                        '$ref': '#/components/schemas/RecordTuple'
                    },
                    'xmlid': {
                        'type': 'string',
                    },
                },
            },
            'description': 'Meta information on the given records.'
        }
    }

    @api_doc(
        tags=['System'], 
        summary='Model Names', 
        description='List of model names.',
        parameter_context=False,
        parameter_company=False,
        responses={
            '200': {
                'description': 'Model Names', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/ModelNames',
                        },
                        'example': ['res.partner', 'res.users']
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/model_names'), 
        methods=['GET'],
        protected=True,
    )
    def model_names(self, **kw):
        return request.make_json_response(list(request.registry.models.keys()))
    
    @api_doc(
        tags=['System'], 
        summary='Models', 
        description='List of model attributes.',
        parameter_context=False,
        parameter_company=False,
        responses={
            '200': {
                'description': 'Model Attributes', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/ModelAttributes',
                        },
                        'example': [{
                            'model': 'base',
                            'name': 'Base',
                            'order': 'id',
                            'transient': False
                        }]
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/models'), 
        methods=['GET'],
        protected=True,
    )
    def models(self, **kw):
        names = list(request.registry.models.keys())
        
        def get_info(model):
            return {
                'model': model._name,
                'name': model._description,
                'order': model._order,
                'transient': model._transient,
            }
        
        return request.make_json_response(
            [get_info(request.env[name]) for name in names]
        )
    
    @api_doc(
        tags=['System'], 
        summary='Field Names', 
        description='List of field names.',
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
        },
        parameter_context=False,
        parameter_company=False,
        responses={
            '200': {
                'description': 'Field Names', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/FieldNames',
                        },
                        'example': ['name', 'active']
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/field_names',
            '/field_names/<string:model>',
        ]), 
        methods=['GET'],
        protected=True,
    )
    def field_names(self, model, **kw):
        return request.make_json_response(request.env[model].fields_get_keys())
    
    
    @api_doc(
        tags=['System'], 
        summary='Field Attributes', 
        description='List of field attributes.',
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
            'attributes': {
                'name': 'attributes',
                'description': 'Attributes',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'array',
                            'items': {
                                'type': 'string'
                            },
                        }
                    }
                },
                'example': ['type'],
            },
        },
        parameter_context=False,
        parameter_company=False,
        responses={
            '200': {
                'description': 'Field Attributes', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/FieldAttributes',
                        },
                        'example': {
                            '__last_update': {
                                'change_default': False,
                                'company_dependent': False,
                                'depends': [
                                  'create_date',
                                  'write_date'
                                ],
                                'manual': False,
                                'readonly': True,
                                'required': False,
                                'searchable': False,
                                'sortable': False,
                                'store': False,
                                'string': 'Last Modified on',
                                'type': 'datetime'
                            },
                        }
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/fields',
            '/fields/<string:model>',
        ]), 
        methods=['GET'],
        protected=True,
    )
    def fields(self, model, fields=None, attributes=None, **kw):
        
        print(fields, attributes, kw)
        
        fields = tools.common.parse_value(fields)
        attributes = tools.common.parse_value(attributes)
        return request.make_json_response(request.env[model].fields_get(
            allfields=fields, attributes=attributes
        ))
    
    @api_doc(
        tags=['System'], 
        summary='Function Names', 
        description='List of function names.',
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
        },
        parameter_context=False,
        parameter_company=False,
        responses={
            '200': {
                'description': 'Function Names', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/FunctionNames',
                        },
                        'example': ['action_archive', 'action_unarchive']
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/function_names',
            '/function_names/<string:model>',
        ]), 
        methods=['GET'],
        protected=True,
    )
    def function_names(self, model, **kw):
        functions = inspect.getmembers(
            request.registry[model], inspect.isfunction
        )
        return request.make_json_response([
            name for name, _ in functions
            if not regex_private.match(name)
        ])
    
    @api_doc(
        tags=['System'], 
        summary='Function Attributes', 
        description='List of function attributes.',
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
        },
        parameter_context=False,
        parameter_company=False,
        responses={
            '200': {
                'description': 'Function Attributes', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/FunctionAttributes',
                        },
                        'example': {
                            'activity_feedback': {
                                'info': [
                                    'Set activities as done, limiting to some activity types and',
                                    'optionally to a given user.'
                                ],
                                'parameters': [
                                    {
                                        'default': None,
                                        'name': 'act_type_xmlids'
                                    },
                                    {
                                        'default': None,
                                        'name': 'user_id'
                                    },
                                    {
                                        'default': None,
                                        'name': 'feedback'
                                    }
                                ]
                            },
                        }
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/functions',
            '/functions/<string:model>',
        ]), 
        methods=['GET'],
        protected=True,
    )
    def functions(self, model, **kw):
        functions = inspect.getmembers(
            request.registry[model], inspect.isfunction
        )
        function_data = {}
        for name, func in functions:
            if not regex_private.match(name):
                function_data[name] = {
                    'info': func.__doc__ and func.__doc__.splitlines() or False,
                    'parameters': [
                        {
                            'name': name, 
                            'default': param.default != param.empty and param.default or None
                        }
                        for name, param in inspect.signature(func).parameters.items()
                        if name not in ['cls', 'self']
                    ]
                }
        return request.make_json_response(function_data)

    @api_doc(
        tags=['System'], 
        summary='Metadata', 
        description='Meta information of a model.',
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
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordIDs',
                        }
                    }
                },
                'example': [1, 2, 3],
            },
        },
        parameter_context=False,
        parameter_company=False,
        responses={
            '200': {
                'description': 'Metadata', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/Metadata',
                        },
                        'example': [{
                            'create_date': '2020-08-30 19:40:25',
                            'create_uid': False,
                            'id': 1,
                            'noupdate': True,
                            'write_date': '2020-08-30 19:47:14',
                            'write_uid': [1, 'OdooBot'],
                            'xmlid': 'base.main_partner'
                        }]
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/metadata',
            '/metadata/<string:model>',
        ]), 
        methods=['GET'],
        protected=True,
    )
    def metadata(self, model, ids, **kw):
        return request.make_json_response(request.env[model].browse(
            tools.common.parse_ids(ids)
        ).get_metadata())
        