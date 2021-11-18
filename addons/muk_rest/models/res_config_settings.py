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


from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------

    rest_docs_security_group_id = fields.Many2one(
        comodel_name='res.groups',
        compute='_compute_rest_docs_security_group_id',
        inverse='_inverse_rest_docs_security_group_id',
        string="API Docs Group",
    )

    rest_docs_security_group_xmlid = fields.Char(
        string="API Docs Group XMLID",
        config_parameter='muk_rest.docs_security_group'
    )
    
    rest_oauth2_bearer_expires_in_seconds = fields.Integer(
        string="OAuth 2 Expires In (in Seconds)",
        config_parameter='muk_rest.oauth2_bearer_expires_in_seconds',
        default=3600
    )
    
    rest_oauth2_bearer_autovacuum_days = fields.Integer(
        string="OAuth 2 Autovacuum (in Days)",
        config_parameter='muk_rest.oauth2_bearer_autovacuum_days',
        default=7
    )

    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------

    @api.depends('rest_docs_security_group_xmlid')
    def _compute_rest_docs_security_group_id(self):
        for record in self:
            xmlid = record.rest_docs_security_group_xmlid
            group = xmlid and self.env.ref(xmlid, False) or None
            record.rest_docs_security_group_id = group

    #----------------------------------------------------------
    # Inverse
    #----------------------------------------------------------

    def _inverse_rest_docs_security_group_id(self):
        print("HIER")
        