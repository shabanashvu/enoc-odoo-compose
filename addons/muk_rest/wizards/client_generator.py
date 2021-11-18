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

from urllib import parse

from odoo import api, models, fields
from odoo.addons.muk_rest.tools import common, docs


class ClientGenerator(models.TransientModel):
    
    _name = 'muk_rest.client_generator'
    _description = "Client Generator"
    
    #----------------------------------------------------------
    # Selections
    #----------------------------------------------------------
    
    @api.model
    def _selection_language(self):
        codegen_url = docs.get_api_docs_codegen_url(self.env)
        language_url = '{}/clients'.format(codegen_url)
        response = requests.get(language_url)
        if response.status_code == 200:
            languages = response.json()
            return [
                (lang, ' '.join(map(lambda l: l.capitalize(), lang.split('-'))))
                for lang in languages
            ]
        return []

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------

    language = fields.Selection(
        selection='_selection_language',
        string="Language",
        required=True,
    )

    options = fields.Text(
        compute='_compute_options',
        string="Option Values",
        readonly=False,
        store=True,
    )

    send_options = fields.Boolean(
        string="Options"
    )

    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------

    @api.depends('send_options', 'language')
    def _compute_options(self):
        codegen_url = '{}/options?version=V3'.format(
            docs.get_api_docs_codegen_url(self.env)
        )
        for record in self:
            if record.language and record.send_options:
                option_url = '{}&language={}'.format(
                    codegen_url, record.language
                )
                record.options = json.dumps(
                    requests.get(option_url).json(), 
                    sort_keys=True, indent=4
                )
            else:
                record.options = None

    #----------------------------------------------------------
    # Actions
    #----------------------------------------------------------

    def action_generate_client(self):
        self.ensure_one()
        generate_url = '{}/docs/client/{}'.format(
            common.BASE_URL, self.language
        )
        if self.send_options:
            generate_url += '?{}'.format(parse.urlencode({
                'options': self.options
            }))
        return {
            'type': 'ir.actions.act_url',
            'url': generate_url,
            'target': 'new',
        }
