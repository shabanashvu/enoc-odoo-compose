# -*- coding: utf-8 -*-

from . import models

def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    attendances = env['hr.attendance'].search([])
    for rec in attendances:
        contracts = rec.employee_id.contract_ids.filtered(lambda x: x.state in ['open'])
        if contracts:
            rec.resource_calendar_id = contracts[0].resource_calendar_id
        else:
            rec.resource_calendar_id = rec.employee_id.resource_calendar_id
