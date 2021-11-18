# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    duplicate_punches_seconds = fields.Integer('Duplicate Punches Seconds', config_parameter='hr_attendance_zktecho.duplicate_punches_seconds', default=0.0)
