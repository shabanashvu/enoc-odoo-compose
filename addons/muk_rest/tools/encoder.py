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
import json

from odoo import fields, models
from odoo.http import Response
from odoo.tools import ustr, config

from odoo.addons.muk_rest.tools.common import parse_exception


class ResponseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            if isinstance(obj, datetime.datetime):
                return fields.Datetime.to_string(obj)
            return fields.Date.to_string(obj)
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode()
        return ustr(obj)


class RecordEncoder(ResponseEncoder):
    def default(self, obj):
        if isinstance(obj, models.BaseModel):
            return obj.name_get()
        return ResponseEncoder.default(self, obj)


class LogEncoder(json.JSONEncoder):
    def iterencode(self, o, _one_shot=False):
        markers = {} if self.check_circular else None

        def limit_str(o):
            text = json.encoder.encode_basestring(o)
            limit = int(config.get('rest_logging_attribute_limit', 150))
            return '{}...'.format(text[:limit]) if limit and len(text) > limit else text

        if (_one_shot and json.encoder.c_make_encoder is not None and self.indent is None):
            _iterencode = json.encoder.c_make_encoder(
                markers, self.default, limit_str, self.indent,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, self.allow_nan
            )
        else:
            _iterencode = json.encoder._make_iterencode(
                markers, self.default, limit_str, self.indent, json.dumps,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, _one_shot
            )
        return _iterencode(o, 0)


def ustr_sql(value):
    return ustr(value, errors='replace').replace("\x00", "\uFFFD")


def limit_text_size(text):
    limit = int(config.get('rest_logging_content_limit', 25000))
    if limit and len(text) > limit:
        return '{}\n\n...'.format(text[:limit])
    return text


def encode_request(request):
    return limit_text_size(json.dumps(
        request.params, indent=4, cls=LogEncoder, default=lambda o: str(o)
    ))
    
            
def encode_response(response):
    if isinstance(response, Response):
        if response.mimetype == 'application/json':
            return json.dumps(
                json.loads(response.data), indent=4, 
                cls=LogEncoder, default=lambda o: str(o)
            )
        return limit_text_size(ustr_sql(response.data))
    if isinstance(response, Exception):
        json.dumps(parse_exception(resposen), indent=4, default=lambda o: str(o))
    return limit_text_size(ustr_sql(response))
