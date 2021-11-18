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
import requests
import werkzeug

from odoo import _
from odoo.tools import config
from odoo.modules import get_resource_path
from odoo.http import Controller, Response, request, route, send_file

from odoo.addons.muk_rest.tools.http import make_json_response
from odoo.addons.muk_rest.tools.common import parse_value
from odoo.addons.muk_rest.tools import docs


class DocsController(Controller):
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    def _get_base_url(self):
        return request.env['ir.config_parameter'].sudo().get_param('web.base.url')

    def _get_api_docs(self):
        rest_docs = docs.generate_docs(self._get_base_url())
        paths, components = request.env['muk_rest.endpoint'].get_docs()
        if paths:
            rest_docs['tags'].append('Custom')
            rest_docs['paths'].update(paths)
            rest_docs['components']['schemas'].update(components)
        return rest_docs
    
    #----------------------------------------------------------
    # Routes
    #----------------------------------------------------------
    
    @route(
        route=['/rest/docs', '/rest/docs/index.html'],
        methods=['GET'],
        type='http',
        auth='public',
    )
    @docs.ensure_docs_access
    def docs_index(self, template='docs', **kw):
        if not template or not template.startswith('docs'):
            raise werkzeug.exceptions.BadRequest(_('Invalid template name.'))
        return request.render('muk_rest.{}'.format(template), {
            'db_header': config.get('rest_db_header', 'DATABASE'),
            'db_param': config.get('rest_db_param', 'db'),
            'base_url': self._get_base_url().strip('/'),
            'db_name': request.env.cr.dbname,
        })

    @route(
        route='/rest/docs/api.json',
        methods=['GET'],
        type='http',
        auth='public',
    )
    @docs.ensure_docs_access
    def docs_json(self, **kw):
        return make_json_response(self._get_api_docs())

    @route(
        route='/rest/docs/oauth2/redirect',
        methods=['GET'],
        type='http',
        auth='none', 
        csrf=False,
    )
    def oauth_redirect(self, **kw):
        return send_file(get_resource_path(
            'muk_rest', 'static', 'lib', 'swagger-ui', 'oauth2-redirect.html'
        ))
    
    @route(
        route=[
            '/rest/docs/client',
            '/rest/docs/client/<string:language>',
        ],
        methods=['GET'],
        type='http',
        auth='public',
    )
    @docs.ensure_docs_access
    def docs_client(self, language='python', options=None, **kw):
        server_url = self._get_base_url()
        rest_docs = json.dumps(self._get_api_docs())
        attachment = request.env['ir.attachment'].sudo().create({
            'name': 'rest_api_docs.json', 'raw': rest_docs.encode(),
        })
        try:
            attachment.generate_access_token()
            docs_url = '{}/web/content/{}?access_token={}'.format(
                server_url, attachment.id, attachment.access_token
            )
            codegen_url = '{}/generate'.format(docs.get_api_docs_codegen_url(request.env))
            response = requests.post(codegen_url, allow_redirects=True, stream=True, json={
                'specURL' : docs_url, 
                'lang' : language, 
                'type' : 'CLIENT', 
                'codegenVersion' : 'V3' ,
                'options': parse_value(options, {}),
            })
            headers = [
                ('Content-Type', response.headers.get('content-type')),
                ('Content-Disposition', response.headers.get('content-disposition')),
                ('Content-Length', response.headers.get('content-length')),
            ]
            return Response(response.raw, headers=headers, direct_passthrough=True)
        finally:
            attachment.unlink()

    @route(route='/rest/docs/check', type='json', auth='user')
    def docs_check(self, **kw):
        return docs.has_access_to_docs()
        