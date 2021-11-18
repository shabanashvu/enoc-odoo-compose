from odoo import api, fields, models
import pytz


class HrAttendanceExt(models.Model):
    _inherit = 'hr.attendance'

    checkin_day = fields.Date('Check In Day', compute='_get_checkin_day', store=True)

    @api.depends('check_in', 'check_out')
    def _get_checkin_day(self):
        utc = pytz.timezone('UTC')
        tz = pytz.timezone('Asia/Dubai')
        for item in self:
            checkin_utc = utc.localize(item.check_in)
            checkin_tz = checkin_utc.astimezone(tz)
            item.checkin_day = checkin_tz.date()

