# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class BaseModuleUninstall(models.TransientModel):
    _inherit = "base.module.uninstall"

    def action_uninstall(self):
        modules = self.module_id
        self.env['user.recent.log'].search([('model','in', self.model_ids.mapped('model'))]).sudo().unlink()
        return modules.button_immediate_uninstall()