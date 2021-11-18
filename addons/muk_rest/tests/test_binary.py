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
import json
import urllib
import shutil
import logging
import requests
import unittest
import tempfile

import requests

from odoo import _, SUPERUSER_ID
from odoo.tests import common

from odoo.addons.muk_rest.tests.common import RestfulCase, skip_check_authentication

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)


class BinaryTestCase(RestfulCase):
    
    @skip_check_authentication()
    def test_binary(self):
        client = self.authenticate()
        att = self.env["ir.attachment"].search([], limit=1)
        response = client.get(self.binary_url, data={"id": att.id})
        self.assertTrue(response)
        self.assertTrue(response.json().get("content"))

    @skip_check_authentication()
    def test_binary_file(self):
        client = self.authenticate()
        att = self.env["ir.attachment"].search([], limit=1)
        response = client.get(
            self.binary_url, data={"id": att.id, "file_response": True}
        )
        self.assertTrue(response)
        self.assertTrue(response.content)

    @skip_check_authentication()
    def test_upload_file(self):
        client = self.authenticate()
        tmp_dir = tempfile.mkdtemp()
        filename = os.path.join(tmp_dir, "test.txt")
        try:
            with open(filename, "w") as file:
                file.write("Lorem ipsum!")
            with open(filename, "rb") as file:
                files_01 = {"ufile": file}
                files_02 = {"ufile": file}
                data_01 = {"model": "res.partner", "id": 1}
                data_02 = {"model": "ir.attachment", "id": 1, "field": "datas"}
                response_01 = client.post(self.upload_url, files=files_01, data=data_01)
                response_02 = client.post(self.upload_url, files=files_02, data=data_02)
                self.assertTrue(response_01)
                self.assertTrue(response_02)
        finally:
            shutil.rmtree(tmp_dir)

    @skip_check_authentication()
    def test_upload_files(self):
        client = self.authenticate()
        tmp_dir = tempfile.mkdtemp()
        filename = os.path.join(tmp_dir, "test.txt")
        try:
            with open(filename, "w") as file:
                file.write("Lorem ipsum!")
            with open(filename, "rb") as file:
                files = [("ufile", file), ("ufile", file)]
                data = {"model": "res.partner", "id": 1}
                response = client.post(self.upload_url, files=files, data=data)
                self.assertTrue(response)
        finally:
            shutil.rmtree(tmp_dir)
