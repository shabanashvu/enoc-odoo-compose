# -*- coding: utf-8 -*-

import math
from pytz import timezone, all_timezones
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class generate_missing_attendance(models.TransientModel):
    _name = "generate.missing.draft.attendance"
    _description = 'Generate Missing Attendance Wizard'
    
    time_zone = fields.Selection('_tz_get', string='Timezone', required=True, default=lambda self: self.env.user.tz or 'UTC')
    
    def _tz_get(self):
        return [(x, x) for x in all_timezones]
    
    def generate_attendance(self):
        self.ensure_one()
        try:
            hr_attendance = self.env['hr.draft.attendance']
            atten = {}
            employees = self.env['hr.employee'].search([])
            for employee in employees:
                attendance_ids = hr_attendance.search([('employee_id','=',employee.id),('moved','=',False)], order='name asc')
                if attendance_ids:
                    atten[employee.id] = {}
                    for att in attendance_ids:
                        if att.date in atten[employee.id]:
                            atten[employee.id][att.date].append(att)
                        else:
                            atten[employee.id][att.date] = []
                            atten[employee.id][att.date].append(att)
            if atten:
                for emp in atten:
                    if emp:
                        employee_dic = atten[emp]
                        for attendance_day in atten[emp]:
                            day_dict = employee_dic[attendance_day]
                            if len(day_dict) == 1:
                                date = datetime.strptime(str(day_dict[0].name), DEFAULT_SERVER_DATETIME_FORMAT)
                                if day_dict[0].attendance_status == 'sign_in':
                                    action = 'sign_out'
                                    hour = self.get_day_hours(day_dict[0].employee_id, 
                                                              date.strftime('%A'), day_dict[0].name, 'out')
                                else:
                                    action = 'sign_in'
                                    hour = self.get_day_hours(day_dict[0].employee_id, 
                                                              date.strftime('%A'), day_dict[0].name, 'in')
                                if hour:
                                    result = '{0:02.0f}:{1:02.0f}:00'.format(*divmod(hour * 60, 60))
                                    new_date_time = str(day_dict[0].date)+' '+result
                                    new_date = datetime.strptime(new_date_time, '%Y-%m-%d %H:%M:%S')
                                    local_timezone = timezone(self.time_zone)
                                    local_date = local_timezone.localize(new_date).astimezone(timezone('UTC'))
                                    tz_date = datetime.strptime(datetime.strftime(local_date, DEFAULT_SERVER_DATETIME_FORMAT),DEFAULT_SERVER_DATETIME_FORMAT)
                                    # add inverse action of this one
                                    self.create_inverse_attendance(day_dict[0].employee_id, action, tz_date)
                            elif len(day_dict) >= 2:
                                f_action = day_dict[0].attendance_status
                                # check what missing in or out and create inverse
                                l_action = day_dict[len(day_dict)-1].attendance_status
                                if f_action == l_action:
                                    if f_action == 'sign_in':
                                        last_date = day_dict[0]
                                    else:
                                        last_date = day_dict[len(day_dict)-1]
                                    
                                    fl_date = datetime.strptime(str(last_date.name), DEFAULT_SERVER_DATETIME_FORMAT)
                                    if f_action == 'sign_in':
                                        action = 'sign_out'
                                        hour = self.get_day_hours(last_date.employee_id,fl_date.strftime('%A'),last_date.name, 'out')
                                    else:
                                        action = 'sign_in'
                                        hour = self.get_day_hours(last_date.employee_id,fl_date.strftime('%A'),last_date.name, 'in')
                                    if hour:
                                        result = '{0:02.0f}:{1:02.0f}:00'.format(*divmod(hour * 60, 60))
                                        new_date_time = str(last_date.date)+' '+result
                                        new_date = datetime.strptime(new_date_time, DEFAULT_SERVER_DATETIME_FORMAT)
                                        local_timezone = timezone(self.time_zone)
                                        local_date = local_timezone.localize(new_date).astimezone(timezone('UTC'))
                                        tz_date = datetime.strptime(datetime.strftime(local_date, DEFAULT_SERVER_DATETIME_FORMAT),DEFAULT_SERVER_DATETIME_FORMAT)
                                        self.create_inverse_attendance(last_date.employee_id, action, tz_date)
        except Exception as e:
            raise UserError(_("The following error occured while generating missing attendances.\n\n" + str(e)))
        
    def create_inverse_attendance(self ,employee ,action ,date):
        self.ensure_one()   
        hr_attendance = self.env['hr.draft.attendance']
        vals = {
              'employee_id': employee.id,
              'attendance_status': action,
              'name': date,
              'date': date.date(),
              'is_missing': True,
              'day_name': str(date.strftime('%A')),
                }
        hr_attendance.create(vals)
    
    def get_day_hours(self, employee, day_id ,date, action):
        self.ensure_one()
        local_timezone = timezone(self.time_zone)
        tz = timezone('UTC')
        date = tz.localize(date).astimezone(timezone(str(local_timezone)))
        day_of_week = {'Monday':0 ,'Tuesday':1 ,'Wednesday':2 ,'Thursday':3 ,'Friday':4 ,'Saturday':5 ,'Sunday':6 }
        contract = employee.contract_id
        time_hour = False
        
        days = contract.resource_calendar_id.attendance_ids.filtered(lambda d:d.dayofweek == str(day_of_week[day_id]))
        for day in contract.resource_calendar_id.attendance_ids.filtered(lambda d:d.dayofweek == str(day_of_week[day_id])):
            if action == 'in' and day.hour_from < date.hour:
                time_hour = day.hour_from
            elif action == 'out' and day.hour_to > date.hour:
                time_hour = day.hour_to
        return time_hour
            
        return False
    
    
