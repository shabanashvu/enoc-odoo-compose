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


import os
import re
import tempfile
import datetime

from werkzeug import exceptions

from odoo import http, service
from odoo.http import request, Response
from odoo.tools import misc, config
from odoo.sql_db import db_connect

from odoo.addons.muk_rest import core
from odoo.addons.muk_rest.tools.docs import api_doc
from odoo.addons.muk_rest.tools.http import build_route
from odoo.addons.muk_rest.tools.common import DBNAME_PATTERN


class DatabaseController(http.Controller):
    
    _api_doc_components = {
        'DatabaseList': {
            'type': 'object',
            'properties': {
                'databases': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                    }
                },
                'incompatible_databases': {
                    'type': 'array',
                    'items': {
                        
                    }
                },
            },
            'description': 'Information about the available databases.'
        },
        'DatabaseSize': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                },
                'size': {
                    'type': 'integer',
                },
                'text': {
                    'type': 'string',
                },
            },
            'description': 'The database size.'
        }
    }
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------

    @api_doc(
        tags=['Database'], 
        summary='Database List', 
        description='Lists all databases.',
        responses={
            '200': {
                'description': 'List of Databases', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/DatabaseList'
                        },
                        'example': {
                            'databases': ['mydb'],
                            'incompatible_databases': []
                        }
                    }
                },
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/database/list'), 
        methods=['GET'],
    )
    def database_list(self, **kw):
        databases = http.db_list()
        return request.make_json_response({
            'databases': databases, 
            'incompatible_databases': service.db.list_db_incompatible(databases)
        })
    
    @api_doc(
        tags=['Database'], 
        summary='Database Size', 
        description='Returns the database size.',
        parameter={
            'database_name': {
                'name': 'database_name',
                'description': 'Database Name',
                'required': True,
                'schema': {
                    'type': 'string'
                }
            },
        },
        responses={
            '200': {
                'description': 'Size of Database', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/DatabaseSize'
                        },
                        'example': {
                          'name': 'mydb',
                          'size': 10000000,
                          'text': '10 MB'
                        }
                    }
                },
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/database/size',
            '/database/size/<string:database_name>',
        ]), 
        methods=['GET'],
    )
    def database_size(self, database_name, master_password='admin', **kw):
        service.db.check_super(master_password)
        databases = http.db_list()
        database_size = [False, False]
        if database_name in databases:
            with db_connect('postgres').cursor() as cursor:
                cursor.execute('''
                    SELECT pg_database_size('{dbname}'),
                        pg_size_pretty(pg_database_size('{dbname}'));
                '''.format(dbname=database_name))
                database_size = cursor.fetchone()
        return request.make_json_response({
            'name': database_name, 
            'size': database_size[0], 
            'text': database_size[1]
        })

    @api_doc(
        tags=['Database'], 
        summary='Create Database', 
        description='Creates a new database.',
        show=config.get('list_db', True),
        parameter={
            'database_name': {
                'name': 'database_name',
                'description': 'Database Name',
                'required': True,
                'schema': {
                    'type': 'string'
                }
            },
            'admin_login': {
                'name': 'admin_login',
                'description': 'Admin User Login',
                'required': True,
                'schema': {
                    'type': 'string'
                }
            },
            'admin_password': {
                'name': 'admin_password',
                'description': 'Admin User Password',
                'required': True,
                'schema': {
                    'type': 'string'
                }
            },
            'master_password': {
                'name': 'master_password',
                'description': 'Master Password',
                'schema': {
                    'type': 'string'
                }
            },
            'lang': {
                'name': 'lang',
                'description': 'Language',
                'schema': {
                    'type': 'string'
                }
            },
            'demo': {
                'name': 'demo',
                'description': 'Load Demo Data',
                'schema': {
                    'type': 'boolean'
                }
            },
            'country_code': {
                'name': 'country_code',
                'description': 'Country Code',
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
        routes=build_route('/database/create'), 
        methods=['POST'],
        disable_logging=True,
    )
    def database_create(self, database_name, admin_login, admin_password, master_password='admin', lang='en_US', **kw):
        if not re.match(DBNAME_PATTERN, database_name):
            raise exceptions.BadRequest('Invalid database name.')
        http.dispatch_rpc('db', 'create_database', [
            master_password, 
            database_name,
            bool(kw.get('demo')), 
            lang,
            admin_password, 
            admin_login,
            kw.get('country_code', False)
        ])
        return request.make_json_response(True)
    
    @api_doc(
        tags=['Database'], 
        summary='Duplicate Database', 
        description='Duplicates a database.',
        show=config.get('list_db', True),
        parameter={
            'database_old': {
                'name': 'database_old',
                'description': 'Old Database Name',
                'required': True,
                'schema': {
                    'type': 'string'
                }
            },
            'database_new': {
                'name': 'database_new',
                'description': 'New Database Name',
                'required': True,
                'schema': {
                    'type': 'string'
                }
            },
            'master_password': {
                'name': 'master_password',
                'description': 'Master Password',
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
        routes=build_route('/database/duplicate'), 
        methods=['POST'],
        disable_logging=True,
    )
    def database_duplicate(self, database_old, database_new, master_password='admin', **kw):
        if not re.match(DBNAME_PATTERN, database_new):
            raise exceptions.BadRequest('Invalid database name.')
        http.dispatch_rpc('db', 'duplicate_database', [
            master_password, database_old, database_new
        ])
        return request.make_json_response(True)
    
    
    @api_doc(
        tags=['Database'], 
        summary='Drop Database', 
        description='Drop a database.',
        show=config.get('list_db', True),
        parameter={
            'database_name': {
                'name': 'database_name',
                'description': 'Database Name',
                'required': True,
                'schema': {
                    'type': 'string'
                }
            },
            'master_password': {
                'name': 'master_password',
                'description': 'Master Password',
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
        routes=build_route('/database/drop'), 
        methods=['POST'],
        disable_logging=True,
    )
    def database_drop(self, database_name, master_password='admin', **kw):
        http.dispatch_rpc('db','drop', [master_password, database_name])
        request._cr = None
        return request.make_json_response(True)

    #----------------------------------------------------------
    # Backup & Restore
    #----------------------------------------------------------        
    
    @api_doc(
        tags=['Database'], 
        summary='Backup Database', 
        description='Backup a database.',
        show=config.get('list_db', True),
        parameter={
            'database_name': {
                'name': 'database_name',
                'description': 'Database Name',
                'required': True,
                'schema': {
                    'type': 'string'
                }
            },
            'master_password': {
                'name': 'master_password',
                'description': 'Master Password',
                'schema': {
                    'type': 'string'
                }
            },
            'backup_format': {
                'name': 'backup_format',
                'description': 'Format',
                'schema': {
                    'type': 'string'
                }
            },
        },
        responses={
            '200': {
                'description': 'Database Backup', 
                'content': {
                    'application/octet-stream': {
                        'schema': {
                            'type': 'string',
                            'format': 'binary'
                        }
                    },
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/database/backup'), 
        methods=['POST'],
        disable_logging=True,
    )
    @service.db.check_db_management_enabled
    def database_backup(self, database_name, master_password='admin', backup_format='zip', **kw):
        service.db.check_super(master_password)
        ts = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
        filename = '{}_{}.{}'.format(database_name, ts, backup_format)
        headers = [
            ('Content-Type', 'application/octet-stream; charset=binary'),
            ('Content-Disposition', http.content_disposition(filename)),
        ]
        dump_stream = service.db.dump_db(database_name, None, backup_format)
        return Response(dump_stream, headers=headers, direct_passthrough=True)
    
    @api_doc(
        tags=['Database'], 
        summary='Restore Database', 
        description='Restore a database.',
        show=config.get('list_db', True),
        parameter={
            'database_name': {
                'name': 'database_name',
                'description': 'Database Name',
                'required': True,
                'schema': {
                    'type': 'string'
                }
            },
            'master_password': {
                'name': 'master_password',
                'description': 'Master Password',
                'schema': {
                    'type': 'string'
                }
            },
            'copy': {
                'name': 'copy',
                'description': 'Database is a Copy',
                'schema': {
                    'type': 'boolean'
                }
            },
        },
        exclude_parameters=['backup_file'],
        requestBody={
            'description': 'Backup File',
            'required': True,
            'content': {
                'multipart/form-data': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'backup_file': {
                                'type': 'string',
                                'format': 'binary'
                            }
                        }
                    }
                }
            }
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
        routes=build_route('/database/restore'), 
        methods=['POST'],
        disable_logging=True,
    )
    @service.db.check_db_management_enabled
    def restore(self, backup_file, database_name, master_password='admin', copy=False, **kw):
        service.db.check_super(master_password)
        try:
            with tempfile.NamedTemporaryFile(delete=False) as file:
                backup_file.save(file)
            service.db.restore_db(database_name, file.name, misc.str2bool(copy))
            return request.make_json_response(True)
        except Exception:
            raise
        finally:
            os.unlink(file.name)