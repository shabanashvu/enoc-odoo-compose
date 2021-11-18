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


import datetime

from odoo import models, fields


class ResUsers(models.Model):
    
    _inherit = 'res.users'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    oauth1_session_ids = fields.One2many(
        comodel_name='muk_rest.access_token',
        inverse_name='user_id',
        domain="[('user_id', '=', uid)]",
        string="OAuth1 Sessions"
    )
    
    oauth2_session_ids = fields.One2many(
        comodel_name='muk_rest.bearer_token',
        inverse_name='user_id',
        domain="""[
            '&', ('user_id', '=', uid), 
            '|', ('expiration_date', '=', False), 
            ('expiration_date', '>', datetime.datetime.utcnow())
        ]""",
        string="OAuth2 Sessions"
    )
    
    #----------------------------------------------------------
    # Framework
    #----------------------------------------------------------
    
    def __init__(self, pool, cr):
        init_result = super(ResUsers, self).__init__(pool, cr)
        access_oauth_fields = ['oauth1_session_ids', 'oauth2_session_ids']
        readable_fields = list(self.SELF_READABLE_FIELDS)
        writeable_fields = list(self.SELF_WRITEABLE_FIELDS)
        readable_fields.extend(access_oauth_fields)
        writeable_fields.extend(access_oauth_fields)
        type(self).SELF_READABLE_FIELDS = readable_fields
        type(self).SELF_WRITEABLE_FIELDS = writeable_fields
        return init_result
            