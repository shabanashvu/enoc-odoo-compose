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


import werkzeug

from odoo import http
from odoo.http import request
from odoo.tools.image import image_data_uri

from odoo.addons.muk_rest import core
from odoo.addons.muk_rest.tools.docs import api_doc
from odoo.addons.muk_rest.tools.http import build_route


class CommonController(http.Controller):

    _api_doc_components = {
        'ModuleData': {
            'type': 'object',
            'properties': {
                'model': {
                    'type': 'string',
                },
                'id': {
                    'type': 'integer',
                },
            },
            'description': 'A map of the model name and the corresponding ID.'
        },
        'RecordXMLID': {
            'type': 'object',
            'properties': {
                'model': {
                    'type': 'string',
                },
                'id': {
                    'type': 'integer',
                },
            },
            'description': 'The model name and the ID of the record.'
        },
        'CurrentUser': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                },
                'uid': {
                    'type': 'integer',
                },
            },
            'description': 'The name and ID of the current user.'
        },
        'UserInfo': {
            'type': 'object',
            'properties': {
                'address': {
                    'type': 'object',
                    'properties': {
                        'country': {
                            'type': 'string',
                        },
                        'formatted': {
                            'type': 'string',
                        },
                        'locality': {
                            'type': 'string',
                        },
                        'postal_code': {
                            'type': 'string',
                        },
                        'region': {
                            'type': 'string',
                        },
                        'street_address': {
                            'type': 'string',
                        },
                    },
                },
                'email': {
                    'type': 'string',
                },
                'locale': {
                    'type': 'string',
                },
                'name': {
                    'type': 'string',
                },
                'phone_number': {
                    'type': 'string',
                },
                'picture': {
                    'type': 'string',
                },
                'sub': {
                    'type': 'integer',
                },
                'updated_at': {
                    'type': 'string',
                    'format': 'date-time',
                },
                'username': {
                    'type': 'string',
                },
                'website': {
                    'type': 'string',
                },
                'zoneinfo': {
                    'type': 'string',
                },
            },
            'description': 'Information about the current user.'
        },
        'UserCompany': {
            'type': 'object',
            'properties': {
                'allowed_companies': {
                    '$ref': '#/components/schemas/RecordTuples',
                },
                'current_company': {
                    '$ref': '#/components/schemas/RecordTuple',
                },
                'current_company_id': {
                    'type': 'integer',
                },
            },
            'description': 'Information about the current company and allowed companies of the current user.'
        },
        'UserSession': {
            'type': 'object',
            'properties': {
                'db': {
                    'type': 'string',
                },
                'uid': {
                    'type': 'integer',
                },
                'username': {
                    'type': 'string',
                },
                'name': {
                    'type': 'string',
                },
                'partner_id': {
                    'type': 'integer',
                },
                'company_id': {
                    'type': 'integer',
                },
                'user_context': {
                    '$ref': '#/components/schemas/UserContext',
                },
            },
            'additionalProperties': True,
            'description': 'Information about the current session.'
        }
    }

    #----------------------------------------------------------
    # Utility
    #----------------------------------------------------------

    @core.http.rest_route(
        routes=build_route('/<path:path>'),
        rest_access_hidden=True,
        disable_logging=True,
    )
    def catch(self, **kw):
        return werkzeug.exceptions.NotFound()

    #----------------------------------------------------------
    # Common
    #----------------------------------------------------------

    @api_doc(
        tags=['Common'], 
        summary='Modules', 
        description='Returns a list of installed modules.',
        parameter_context=False,
        parameter_company=False,
        responses={
            '200': {
                'description': 'List of Modules', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/ModuleData'
                        },
                        'example': {
                            'base': 1,
                            'web': 2,
                        }
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/modules'), 
        methods=['GET'],
        protected=True,
    )
    def modules(self):
        return request.make_json_response(
            request.env['ir.module.module']._installed()
        )
        
    @api_doc(
        tags=['Common'], 
        summary='XML ID', 
        description='Returns the XML ID record.',
        parameter={
            'xmlid': {
                'name': 'xmlid',
                'description': 'XML ID',
                'schema': {
                    'type': 'string'
                },
                'example': 'base.main_company',
            },
        },
        parameter_context=False,
        parameter_company=False,
        responses={
            '200': {
                'description': 'XML ID Record', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/RecordXMLID'
                        },
                        'example': {
                            'model': 'res.company',
                            'id': 1,
                        }
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/xmlid',
            '/xmlid/<string:xmlid>',
        ]), 
        methods=['GET'],
        protected=True,
    )
    def xmlid(self, xmlid, **kw):
        record = request.env.ref(xmlid)
        return request.make_json_response({
            'model': record._name, 'id': record.id
        })
    
    #----------------------------------------------------------
    # Session
    #----------------------------------------------------------
    
    @api_doc(
        tags=['Common'], 
        summary='User', 
        description='Returns the current user.',
        responses={
            '200': {
                'description': 'Current User', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/CurrentUser'
                        },
                        'example': {
                            'name': 'Admin',
                            'uid': 2,
                        }
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/user'), 
        methods=['GET'],
        protected=True,
    )
    def user(self, **kw):
        return request.make_json_response({
            'uid': request.session and request.session.uid, 
            'name': request.env.user and request.env.user.name
        })

    @api_doc(
        tags=['Common'], 
        summary='User Information', 
        description='Returns the user information.',
        responses={
            '200': {
                'description': 'User Information', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/UserInfo'
                        },
                        'example': {
                            'address': {
                                'country': 'United States',
                                'formatted': 'YourCompany\n215 Vine St\n\nScranton PA 18503\nUnited States',
                                'locality': 'Scranton',
                                'postal_code': '18503',
                                'region': 'Pennsylvania (US)',
                                'street_address': '215 Vine St'
                            },
                            'email': 'admin@yourcompany.example.com',
                            'locale': 'en_US',
                            'name': 'Mitchell Admin',
                            'phone_number': '+1 555-555-5555',
                            'picture': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
                            'sub': 2,
                            'updated_at': '2020-11-11 13:57:48',
                            'username': 'admin',
                            'website': False,
                            'zoneinfo': 'Europe/Vienna'
                        }
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/userinfo'), 
        methods=['GET'],
        protected=True,
    )
    def userinfo(self, **kw):
        user = request.env.user
        uid = request.session.uid
        return request.make_json_response({
            'sub': uid,
            'name': user.name,
            'locale': user.lang,
            'zoneinfo': user.tz,
            'username': user.login,
            'email': user.partner_id.email,
            'website': user.partner_id.website,
            'phone_number': user.partner_id.phone,
            'address': {
                'formatted': user.partner_id.contact_address,
                'street_address': user.partner_id.street,
                'locality': user.partner_id.city,
                'postal_code': user.partner_id.zip,
                'region': user.partner_id.state_id.display_name,
                'country': user.partner_id.country_id.display_name,
            },
            'updated_at': user.partner_id.write_date,
            'picture': image_data_uri(user.partner_id.image_1024),
        })

    @api_doc(
        tags=['Common'], 
        summary='Company Information', 
        description='Returns the current company.',
        responses={
            '200': {
                'description': 'Current Company', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/UserCompany'
                        },
                        'example': {
                            'allowed_companies': [[1, 'YourCompany']],
                            'current_company': [1, 'YourCompany'],
                            'current_company_id': 1
                        }
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/company'), 
        methods=['GET'],
        protected=True,
    )
    def company(self, **kw):
        user = request.env.user
        suid = request.session.uid
        user_company_information = {
            'current_company_id': user.company_id.id if suid else None,
            'current_company': (user.company_id.id, user.company_id.name) if suid else None, 
            'allowed_companies': []
        }
        if request.env.user and request.env.user.has_group('base.group_user'):
            user_company_information['allowed_companies'] = [
                (comp.id, comp.name) for comp in user.company_ids
            ]
        return request.make_json_response(user_company_information)

    @api_doc(
        tags=['Common'], 
        summary='Session Information', 
        description='Returns the current session.',
        responses={
            '200': {
                'description': 'Current Session', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/UserSession'
                        },
                        'example': {
                            'db': 'mydb',
                            'user_id': 2,
                            'company_id': 1,
                            'user_context': {
                                'lang': 'en_US',
                                'tz': 'Europe/Vienna',
                                'uid': 2
                            },
                        }
                    }
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route('/session'), 
        methods=['GET'],
        protected=True,
    )
    def session(self, **kw):
        return request.make_json_response(request.env['ir.http'].session_info())
