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


from odoo import http
from odoo.http import request
from odoo.models import check_method_name
from odoo.tools import misc

from odoo.addons.muk_rest import tools, core
from odoo.addons.muk_rest.tools.docs import api_doc
from odoo.addons.muk_rest.tools.http import build_route


class ModelController(http.Controller):
  
    _api_doc_components = {
        'ReadGroupResult': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    '__domain': {
                        '$ref': '#/components/schemas/Domain',
                    }
                },
                'additionalProperties': True,
            },
            'description': 'A list of grouped record information.'
        },
        'RecordValues': {
            'type': 'object',
            'description': 'A map of field names and their corresponding values.'
        },
    }
  
    #----------------------------------------------------------
    # Generic Method
    #----------------------------------------------------------
     
    @api_doc(
        tags=['Model'], 
        summary='Call', 
        description='Generic method call.',
        parameter={
            'model': {
                'name': 'model',
                'description': 'Model',
                'required': True,
                'schema': {
                    'type': 'string'
                },
            },
            'method': {
                'name': 'method',
                'description': 'Method',
                'required': True,
                'schema': {
                    'type': 'string'
                },
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
            'args': {
                'name': 'args',
                'description': 'Positional Arguments',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'array',
                            'items': {}
                        }
                    }
                },
                'example': [],
            },
            'kwargs': {
                'name': 'kwargs',
                'description': 'Keyword Arguments',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object'
                        }
                    }
                },
                'example': {},
            },
        },
        default_responses=['200', '400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/call',
            '/call/<string:model>',
            '/call/<string:model>/<string:method>',
        ]), 
        methods=['POST'],
        protected=True
    )
    def call(self, model, method, ids=None, args=None, kwargs=None, **kw):
        check_method_name(method)
        args = tools.common.parse_value(args, []) 
        kwargs = tools.common.parse_value(kwargs, {})
        records = request.env[model].browse(tools.common.parse_ids(ids))
        return request.make_json_response(getattr(records, method)(*args, **kwargs))

    #----------------------------------------------------------
    # Search / Read
    #----------------------------------------------------------

    @api_doc(
        tags=['Model'], 
        summary='Search', 
        description='Search for matching records',
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
            'domain': {
                'name': 'domain',
                'description': 'Search Domain',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/Domain',
                        }
                    }
                },
                'example': ['|', ('is_company', '=', True), ('parent_id', '=', False)],
            },
            'count': {
                'name': 'count',
                'description': 'Count',
                'schema': {
                    'type': 'boolean'
                },
            },
            'limit': {
                'name': 'limit',
                'description': 'Limit',
                'schema': {
                    'type': 'integer'
                },
            },
            'offset': {
                'name': 'offset',
                'description': 'Offset',
                'schema': {
                    'type': 'integer'
                },
            },
            'order': {
                'name': 'order',
                'description': 'Order',
                'schema': {
                    'type': 'string'
                },
            },
        },
        responses={
            '200': {
                'description': 'Records IDs', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordIDs'
                        },
                        'example': [1, 2, 3]
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/search',
            '/search/<string:model>',
            '/search/<string:model>/<string:order>',
            '/search/<string:model>/<int:limit>/<string:order>',
            '/search/<string:model>/<int:limit>/<int:offset>/<string:order>'
        ]), 
        methods=['GET'],
        protected=True,
    )
    def search(self, model, domain=None, count=False, limit=None, offset=0, order=None, **kw):
        domain = tools.common.parse_domain(domain)
        count = count and misc.str2bool(count) or None
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        model = request.env[model].with_context(prefetch_fields=False)
        result = model.search(domain, offset=offset, limit=limit, order=order, count=count)
        if not count:
            return request.make_json_response(result.ids)
        return request.make_json_response(result)
            
    @api_doc(
        tags=['Model'], 
        summary='Names', 
        description='Get the record names.',
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
                            '$ref': '#/components/schemas/RecordIDs'
                        }
                    }
                },
                'example': [1, 2, 3],
            },
        },
        responses={
            '200': {
                'description': 'List of ID and Name Tupels', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordTupels'
                        },
                        'example': [[1, 'YourCompany']]
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/name',
            '/name/<string:model>',
        ]), 
        methods=['GET'],
        protected=True,
    )
    def name(self, model, ids, **kw):
        return request.make_json_response(request.env[model].browse(
            tools.common.parse_ids(ids)
        ).name_get())

    @api_doc(
        tags=['Model'], 
        summary='Read', 
        description='Read the given records.',
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
                            '$ref': '#/components/schemas/RecordIDs'
                        }
                    }
                },
                'example': [1, 2, 3],
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
                'description': 'List of ID and name tupels', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordData'
                        },
                        'example': [{
                            'active': True,
                            'id': 14,
                            'name': 'Azure Interior'
                        }]
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/read',
            '/read/<string:model>',
        ]), 
        methods=['GET'],
        protected=True,
    )
    def read(self, model, ids, fields=None, **kw):
        return request.make_json_response(request.env[model].browse(
            tools.common.parse_ids(ids)
        ).read(tools.common.parse_value(fields)))

    @api_doc(
        tags=['Model'], 
        summary='Search Read', 
        description='Search for matching records',
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
            'domain': {
                'name': 'domain',
                'description': 'Search Domain',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/Domain',
                        }
                    }
                },
                'example': ['|', ('is_company', '=', True), ('parent_id', '=', False)],
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
            'limit': {
                'name': 'limit',
                'description': 'Limit',
                'schema': {
                    'type': 'integer'
                },
            },
            'offset': {
                'name': 'offset',
                'description': 'Offset',
                'schema': {
                    'type': 'integer'
                },
            },
            'order': {
                'name': 'order',
                'description': 'Order',
                'schema': {
                    'type': 'string'
                },
            },
        },
        responses={
            '200': {
                'description': 'Records', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordData'
                        },
                        'example': [{
                            'active': True,
                            'id': 14,
                            'name': 'Azure Interior'
                        }]
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/search_read',
            '/search_read/<string:model>',
            '/search_read/<string:model>/<string:order>',
            '/search_read/<string:model>/<int:limit>/<string:order>',
            '/search_read/<string:model>/<int:limit>/<int:offset>/<string:order>'
        ]), 
        methods=['GET'],
        protected=True,
    )
    def search_read(self, model, domain=None, fields=None, limit=None, offset=0, order=None, **kw):
        domain = tools.common.parse_domain(domain)
        fields = tools.common.parse_value(fields)
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        return request.make_json_response(request.env[model].search_read(
            domain, fields=fields, offset=offset, limit=limit, order=order
        ))

    @api_doc(
        tags=['Model'], 
        summary='Read Group', 
        description='Search for matching records',
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
            'domain': {
                'name': 'domain',
                'required': True,
                'description': 'Search Domain',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/Domain',
                        }
                    }
                },
                'example': ['|', ('is_company', '=', True), ('parent_id', '=', False)],
            },
            'fields': {
                'name': 'fields',
                'description': 'Fields',
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordFields',
                        }
                    }
                },
                'example': ['name', 'parent_id'],
            },
            'groupby': {
                'name': 'groupby',
                'description': 'GroupBy',
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'array',
                            'items': {
                                'type': 'string',
                            }
                        }
                    }
                },
                'example': ['parent_id'],
            },
            'limit': {
                'name': 'limit',
                'description': 'Limit',
                'schema': {
                    'type': 'integer'
                },
            },
            'offset': {
                'name': 'offset',
                'description': 'Offset',
                'schema': {
                    'type': 'integer'
                },
            },
            'orderby': {
                'name': 'orderby',
                'description': 'Order',
                'schema': {
                    'type': 'string'
                },
            },
            'lazy': {
                'name': 'lazy',
                'description': 'Lazy Loading',
                'schema': {
                    'type': 'boolean'
                },
            },
        },
        responses={
            '200': {
                'description': 'Records', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/ReadGroupResult',
                        },
                        'example': [{
                            '__domain': [
                                '&', ['parent_id', '=', False],
                                '|', ['is_company', '=', True],
                                ['parent_id', '=', False]
                            ],
                            'parent_id': False,
                            'parent_id_count': 12
                        }]
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/read_group',
            '/read_group/<string:model>',
            '/read_group/<string:model>/<string:orderby>',
            '/read_group/<string:model>/<int:limit>/<string:orderby>',
            '/read_group/<string:model>/<int:limit>/<int:offset>/<string:orderby>'
        ]), 
        methods=['GET'],
        protected=True,
    )
    def read_group(self, model, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True, **kw):
        domain = tools.common.parse_domain(domain)
        fields = tools.common.parse_value(fields)
        groupby = tools.common.parse_value(groupby, [])
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        lazy = misc.str2bool(lazy)
        return request.make_json_response(request.env[model].read_group(
            domain, fields, groupby=groupby, offset=offset, 
            limit=limit, orderby=orderby, lazy=lazy
        ))
     
    #----------------------------------------------------------
    # Create / Update / Delete
    #----------------------------------------------------------
    
    @api_doc(
        tags=['Model'], 
        summary='Create', 
        description='Creates new records.',
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
            'values': {
                'name': 'values',
                'description': 'Values',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordValues'
                        }
                    }
                },
                'example': {'name': 'New Name'},
            },
        },
        responses={
            '200': {
                'description': 'Records IDs', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordIDs'
                        },
                        'example': [1, 2, 3]
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/create',
            '/create/<string:model>',
        ]), 
        methods=['POST'],
        protected=True,
    )
    def create(self, model, values=None, **kw):
        return request.make_json_response(request.env[model].create(
            tools.common.parse_value(values, {})
        ).ids)

    @api_doc(
        tags=['Model'], 
        summary='Write', 
        description='Update records.',
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
                            '$ref': '#/components/schemas/RecordIDs'
                        }
                    }
                },
                'example': [1, 2, 3],
            },
            'values': {
                'name': 'values',
                'description': 'Values',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordValues'
                        }
                    }
                },
                'example': {'name': 'New Name'},
            },
        },
        responses={
            '200': {
                'description': 'Records IDs', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordIDs'
                        },
                        'example': [1, 2, 3]
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/write',
            '/write/<string:model>',
        ]), 
        methods=['PUT'],
        protected=True,
    )
    def write(self, model, ids=None, values=None, **kw):
        records = request.env[model].browse(tools.common.parse_ids(ids))
        records.write(tools.common.parse_value(values, {}))
        return request.make_json_response(records.ids)

    @api_doc(
        tags=['Model'], 
        summary='Delete', 
        description='Delete records.',
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
                            '$ref': '#/components/schemas/RecordIDs'
                        }
                    }
                },
                'example': [1, 2, 3],
            },
        },
        responses={
            '200': {
                'description': 'Records IDs', 
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'boolean'
                        },
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/unlink',
            '/unlink/<string:model>',
        ]), 
        methods=['DELETE'],
        protected=True,
    )
    def unlink(self, model, ids=None, **kw):
        return request.make_json_response(request.env[model].browse(
            tools.common.parse_ids(ids)
        ).unlink())
