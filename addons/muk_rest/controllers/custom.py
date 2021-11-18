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

from odoo import api, http, SUPERUSER_ID
from odoo.exceptions import AccessDenied
from odoo.http import request

from odoo.addons.muk_rest import core
from odoo.addons.muk_rest.tools.http import build_route


class CustomController(http.Controller):
    
    @core.http.rest_route(
        routes=build_route('/custom/<path:endpoint>'),
        rest_access_hidden=True,
        rest_custom=True,
        ensure_db=True
    )
    def custom(self, endpoint, **kw):
        env = api.Environment(request.cr, SUPERUSER_ID, {})
        endpoint = env['muk_rest.endpoint'].search([
            ('endpoint', '=', endpoint)
        ], limit=1)
        if endpoint and request.httprequest.method == endpoint.method:
            user = env.ref('base.public_user')
            try:
                user = env['ir.http']._rest_authenticate_request(
                    {'custom_route': endpoint.route, **self.custom.routing},
                    dict(request.params),
                )
            except (AccessDenied, werkzeug.exceptions.Unauthorized):
                if endpoint.protected:
                    raise
            return endpoint.evaluate(
                request.httprequest.headers, request.params, user
            )
        return werkzeug.exceptions.NotFound()
