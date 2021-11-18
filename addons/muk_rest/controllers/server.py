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


from odoo import http, release, service
from odoo.http import request
from odoo.tools import config

from odoo.addons.muk_rest import core
from odoo.addons.muk_rest.tools.docs import api_doc
from odoo.addons.muk_rest.tools.common import VERSION
from odoo.addons.muk_rest.tools.http import build_route


class ServerController(http.Controller):
    
    _api_doc_components = {
        'VersionInformation': {
            'type': 'object',
            'properties': {
                'api_version': {
                    'type': 'string',
                },
                'server_serie': {
                    'type': 'string',
                },
                'server_version': {
                    'type': 'string',
                },
                'server_version_info': {
                    'type': 'array',
                    'items': {}
                },
            },
            'description': 'Server version information.'
        }
    }
    
    #----------------------------------------------------------
    # Common
    #----------------------------------------------------------

    @api_doc(
        tags=['Server'], 
        summary='Version Information', 
        description='Request version information.',
        responses={
            '200': {
                'description': 'Version Information', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/VersionInformation',
                        },
                        'example': {
                            'api_version': '1',
                            'server_serie': '14.0',
                            'server_version': '14.0',
                            'server_version_info': [14, 0, 0, 'final', 0, '']
                        }
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/'), 
        methods=['GET']
    )
    def version(self, **kw): 
        return request.make_json_response({
            'server_version': release.version,
            'server_version_info': release.version_info,
            'server_serie': release.serie,
            'api_version': VERSION,
        })
    
    @api_doc(
        tags=['Server'], 
        summary='Languages', 
        description='List of available languages',
        responses={
            '200': {
                'description': 'Languages', 
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'array',
                            'items': {
                                'type': 'array',
                                'items': {
                                    'type': 'string'
                                },
                                'minItems': 2,
                                'maxItems': 2,
                            }
                        },
                        'example': [['sq_AL', 'Albanian'], ['am_ET', 'Amharic']]
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/languages'), 
        methods=['GET']
    )
    def languages(self):
        return request.make_json_response([
            (lang[0], lang[1].split('/')[0].strip()) 
            for lang in service.db.exp_list_lang()
        ])
    
    @api_doc(
        tags=['Server'], 
        summary='Countries', 
        description='List of available countries',
        responses={
            '200': {
                'description': 'Countries', 
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'array',
                            'items': {
                                'type': 'array',
                                'items': {
                                    'type': 'string'
                                },
                                'minItems': 2,
                                'maxItems': 2,
                            }
                        },
                        'example': [['af', 'Afghanistan'], ['al', 'Albania']]
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/countries'), 
        methods=['GET']
    )
    def countries(self):
        return request.make_json_response(service.db.exp_list_countries())
    
    @api_doc(
        tags=['Server'], 
        summary='Database', 
        description='Returns the current database.',
        responses={
            '200': {
                'description': 'Current Database', 
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'database': {
                                    'type': 'string',
                                }
                            }
                        },
                        'example': {'database': 'mydb'}
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/database'), 
        methods=['GET'],
        ensure_db=True,
    )
    def database(self, **kw): 
        return request.make_json_response({'database': request.db})
    
    #----------------------------------------------------------
    # Security
    #----------------------------------------------------------
    
    @api_doc(
        tags=['Server'], 
        summary='Change Master Password', 
        description='Change the master password.',
        show=config.get('list_db', True),
        parameter={
            'password_new': {
                'name': 'password_new',
                'description': 'New Password',
                'required': True,
                'schema': {
                    'type': 'string'
                }
            },
            'password_old': {
                'name': 'password_old',
                'description': 'Old Password',
                'schema': {
                    'type': 'string'
                }
            },
        },
        responses={
            '200': {
                'description': 'Result', 
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
        routes=build_route('/change_master_password'), 
        methods=['POST'],
        disable_logging=True,
    )
    @service.db.check_db_management_enabled
    def change_password(self, password_new, password_old='admin' , **kw):
        http.dispatch_rpc('db', 'change_admin_password', [password_old, password_new])
        return request.make_json_response(True)
    