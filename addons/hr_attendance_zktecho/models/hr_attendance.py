# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
    
class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    
    is_missing = fields.Boolean('Missing', default=False)

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        for attendance in self:
            if not attendance.check_out:
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], limit=1, order="check_in ASC")
                if no_check_out_attendances:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                        'empl_name': attendance.employee_id.name,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(no_check_out_attendances.check_in))),
                    })
        return super(HrAttendance, self)._check_validity()
    