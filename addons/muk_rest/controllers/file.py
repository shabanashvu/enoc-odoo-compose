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

from odoo import http
from odoo.http import request
from odoo.tools import misc, image_guess_size_from_field_name, image_process

from odoo.addons.web.controllers import main
from odoo.addons.muk_rest.tools.docs import api_doc
from odoo.addons.muk_rest.tools.http import build_route
from odoo.addons.muk_rest import core


class FileController(http.Controller):
    
    _api_doc_components = {
        'FileContent': {
            'type': 'object',
            'properties': {
                'content': {
                    'type': 'string',
                },
                'content_disposition': {
                    'type': 'string',
                },
                'content_length': {
                    'type': 'integer',
                },
                'content_type': {
                    'type': 'string',
                },
                'filename': {
                    'type': 'string',
                },
            },
            'description': 'The file content information.'
        },
        'UploadContent': {
            'type': 'object',
            'properties': {
                'ufile': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'format': 'binary',
                    }
                }
            },
            'description': 'File content to upload.'
        },
        'UploadResult': {
            'oneOf': [
                {'type': 'boolean'},
                {'$ref': '#/components/schemas/RecordTuples'}
            ],
            'description': 'Result of the file upload.'
        },
    }

    def get_binary_content_values(
        self, xmlid=None, model='ir.attachment', id=None, field='datas', 
        unique=None, filename=None, filename_field='name', mimetype=None
    ):
        http_model = request.env['ir.http']
        content, headers, status = None, [], None
        default_mimetype = 'application/octet-stream'
        record, status = http_model._get_record_and_check(
            xmlid=xmlid, model=model, id=id, field=field, access_token=None
        )
        if not record:
            return status or 404, [], None, filename
        
        if record._name == 'ir.attachment':
            status, content, filename, mimetype, filehash = http_model._binary_ir_attachment_redirect_content(
                record, default_mimetype=default_mimetype
            )
        if not content:
            status, content, filename, mimetype, filehash = http_model._binary_record_content(
                record, field=field, filename=filename, filename_field=filename_field, default_mimetype=default_mimetype
            )
        status, headers, content = http_model._binary_set_headers(
            status, content, filename, mimetype, unique, filehash=filehash, download=True
        )
        return status, headers, content, filename
    
    @api_doc(
        tags=['File'], 
        summary='File Download', 
        description='Returns the file content.',
        parameter={
            'xmlid': {
                'name': 'xmlid',
                'description': 'XML ID',
                'schema': {
                    'type': 'string'
                },
            },
            'model': {
                'name': 'model',
                'description': 'Model',
                'schema': {
                    'type': 'string'
                },
            },
            'id': {
                'name': 'id',
                'description': 'ID',
                'schema': {
                    'type': 'integer'
                },
            },
            'field': {
                'name': 'field',
                'description': 'Field',
                'schema': {
                    'type': 'string'
                },
            },
            'unique': {
                'name': 'unique',
                'description': 'Cache Control',
                'schema': {
                    'type': 'boolean'
                },
            },
            'filename': {
                'name': 'filename',
                'description': 'Filename',
                'schema': {
                    'type': 'string'
                },
            },
            'filename_field': {
                'name': 'filename_field',
                'description': 'Filename Field',
                'schema': {
                    'type': 'string'
                },
            },
            'mimetype': {
                'name': 'mimetype',
                'description': 'Mimetype',
                'schema': {
                    'type': 'string'
                },
            },
            'file_response': {
                'name': 'file_response',
                'description': 'Return the Response as a File',
                'schema': {
                    'type': 'boolean'
                }
            },
        },
        responses={
            '200': {
                'description': 'File Content', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/FileContent'
                        },
                        'example': {
                            'content': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
                            'content_disposition': 'attachment; filename*=UTF-8''image.png',
                            'content_length': 128,
                            'content_type': 'image/png',
                            'filename': 'image.png'
                        }
                    },
                    'application/octet-stream': {
                        'schema': {
                            'type': 'string',
                            'format': 'binary'
                        }
                    }
                    
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/download',        
            '/download/<string:xmlid>',
            '/download/<string:xmlid>/<string:filename>',
            '/download/<int:id>',
            '/download/<int:id>/<string:filename>',
            '/download/<int:id>-<string:unique>',
            '/download/<int:id>-<string:unique>/<string:filename>',
            '/download/<string:model>/<int:id>/<string:field>',
            '/download/<string:model>/<int:id>/<string:field>/<string:filename>'
        ]), 
        methods=['GET'],
        protected=True,
    )
    def download(
        self, xmlid=None, model='ir.attachment', id=None, field='datas', unique=None, filename=None, 
        filename_field='name', mimetype=None, file_response=False, **kw
    ):  
        status, headers, content, filename = self.get_binary_content_values(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, 
            filename=filename, filename_field=filename_field, mimetype=mimetype
        )
        if status != 200:
            return request.env['ir.http']._response_by_status(
                status, headers, content
            )
        if file_response and misc.str2bool(file_response):
            decoded_content = base64.b64decode(content)
            headers.append(('Content-Length', len(decoded_content)))
            return request.make_response(decoded_content, headers)
        header_values = dict(headers)
        return request.make_json_response({
            'content': content,
            'filename': filename,
            'content_disposition': header_values.get('Content-Disposition'),
            'content_type': header_values.get('Content-Type'),
            'content_length': len(base64.b64decode(content))
        })
    
    
    @api_doc(
        tags=['File'], 
        summary='Image Download', 
        description='Returns the image content.',
        parameter={
            'xmlid': {
                'name': 'xmlid',
                'description': 'XML ID',
                'schema': {
                    'type': 'string'
                },
            },
            'model': {
                'name': 'model',
                'description': 'Model',
                'schema': {
                    'type': 'string'
                },
            },
            'id': {
                'name': 'id',
                'description': 'ID',
                'schema': {
                    'type': 'integer'
                },
            },
            'field': {
                'name': 'field',
                'description': 'Field',
                'schema': {
                    'type': 'string'
                },
            },
            'unique': {
                'name': 'unique',
                'description': 'Cache Control',
                'schema': {
                    'type': 'boolean'
                },
            },
            'filename': {
                'name': 'filename',
                'description': 'Filename',
                'schema': {
                    'type': 'string'
                },
            },
            'filename_field': {
                'name': 'filename_field',
                'description': 'Filename Field',
                'schema': {
                    'type': 'string'
                },
            },
            'mimetype': {
                'name': 'mimetype',
                'description': 'Mimetype',
                'schema': {
                    'type': 'string'
                },
            },
            'width': {
                'name': 'width',
                'description': 'Width',
                'schema': {
                    'type': 'integer'
                },
            },
            'height': {
                'name': 'height',
                'description': 'Height',
                'schema': {
                    'type': 'integer'
                },
            },
            'crop': {
                'name': 'crop',
                'description': 'Crop',
                'schema': {
                    'type': 'boolean'
                },
            },
            'quality': {
                'name': 'quality',
                'description': 'Quality',
                'schema': {
                    'type': 'integer'
                },
            },
            'file_response': {
                'name': 'file_response',
                'description': 'Return the Response as a File',
                'schema': {
                    'type': 'boolean'
                }
            },
        },
        responses={
            '200': {
                'description': 'Image Content', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/FileContent'
                        },
                        'example': {
                            'content': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
                            'content_disposition': 'attachment; filename*=UTF-8''image.png',
                            'content_length': 128,
                            'content_type': 'image/png',
                            'filename': 'image.png'
                        }
                    },
                    'application/octet-stream': {
                        'schema': {
                            'type': 'string',
                            'format': 'binary'
                        }
                    }
                    
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/image',
            '/image/<string:xmlid>',
            '/image/<string:xmlid>/<string:filename>',
            '/image/<string:xmlid>/<int:width>x<int:height>',
            '/image/<string:xmlid>/<int:width>x<int:height>/<string:filename>',
            '/image/<string:model>/<int:id>/<string:field>',
            '/image/<string:model>/<int:id>/<string:field>/<string:filename>',
            '/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>',
            '/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>/<string:filename>',
            '/image/<int:id>',
            '/image/<int:id>/<string:filename>',
            '/image/<int:id>/<int:width>x<int:height>',
            '/image/<int:id>/<int:width>x<int:height>/<string:filename>',
            '/image/<int:id>-<string:unique>',
            '/image/<int:id>-<string:unique>/<string:filename>',
            '/image/<int:id>-<string:unique>/<int:width>x<int:height>',
            '/image/<int:id>-<string:unique>/<int:width>x<int:height>/<string:filename>'
        ]), 
        methods=['GET'],
        protected=True,
    )
    def image(
        self, xmlid=None, model='ir.attachment', id=None, field='datas', unique=None, filename=None, 
        filename_field='name', mimetype=None, width=0, height=0, crop=False, 
        quality=0, file_response=False, **kw
    ):  
        status, headers, content, filename = self.get_binary_content_values(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, 
            filename=filename, filename_field=filename_field, mimetype=mimetype, 
        )
        if status in [301, 304]:
            return request.env['ir.http']._response_by_status(
                status, headers, content
            )
        if not content:
            placeholder = 'placeholder.png'
            if  model and model in request.env:
                record = id and request.env[model].browse(int(id)) or request.env[model]
                placeholder = record._get_placeholder_filename(field=field)
            content = base64.b64encode(main.Binary.placeholder(image=placeholder))
            if not (width or height):
                width, height = image_guess_size_from_field_name(field)

        content = image_process(content, size=(int(width), int(height)), crop=crop, quality=int(quality))
        decoded_content = base64.b64decode(content)
        headers = http.set_safe_image_headers(headers, decoded_content)
        
        if file_response and misc.str2bool(file_response):
            response = request.make_response(decoded_content, headers)
            response.status_code = status
            return response
        header_values = dict(headers)
        return request.make_json_response({
            'content': content,
            'filename': filename,
            'content_disposition': header_values.get('Content-Disposition'),
            'content_type': header_values.get('Content-Type'),
            'content_length': len(decoded_content)
        })

    @api_doc(
        tags=['File'], 
        summary='File Upload', 
        description='Uploads file content.',
        parameter={
            'model': {
                'name': 'model',
                'description': 'Model',
                'required': True,
                'schema': {
                    'type': 'string'
                },
            },
            'id': {
                'name': 'id',
                'description': 'ID',
                'required': True,
                'schema': {
                    'type': 'integer'
                },
            },
            'field': {
                'name': 'field',
                'description': 'Field',
                'schema': {
                    'type': 'string'
                },
            },
        },
        requestBody={
            'description': 'Files',
            'required': True,
            'content': {
                'multipart/form-data': {
                    'schema': {
                        '$ref': '#/components/schemas/UploadContent'
                    }
                }
            }
        },
        responses={
            '200': {
                'description': 'Upload Result', 
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/UploadResult'
                        },
                        'example': [[1, 'image.png']]
                    },
                }
            }
        },
        default_responses=['400', '401', '500'],
    )
    @core.http.rest_route(
        routes=build_route([
            '/upload',        
            '/upload/<string:model>/<int:id>',
            '/upload/<string:model>/<int:id>/<string:field>',
        ]), 
        methods=['POST'],
        protected=True,
    )
    def upload(self, model, id, field=None, **kw):
        files = request.httprequest.files.getlist('ufile')
        if field is not None and len(files) == 1:
            return request.make_json_response(request.env[model].browse(int(id)).write({
                field: base64.encodebytes(files[0].read())
            }))
        attachment_ids = []
        attachment_model = request.env['ir.attachment']
        for ufile in files:
            attachment_ids.append(attachment_model.create({
                'datas': base64.encodebytes(ufile.read()),
                'name': ufile.filename,
                'res_model': model,
                'res_id': int(id),
            }).id)
        return request.make_json_response(attachment_model.browse(attachment_ids).name_get())
