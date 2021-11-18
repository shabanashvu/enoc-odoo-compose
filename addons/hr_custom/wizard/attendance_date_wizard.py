# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
import logging
from dateutil.rrule import rrule, MONTHLY
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError
import calendar

class AttendanceDate(models.TransientModel):
    _name = 'attendance.date'
    _description = "Attendance Date"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)

    def action_show(self):
        """  """
        list_overtime=[]
        strt_dt = self.start_date
        end_dt = self.end_date
        delta = end_dt - strt_dt       # as timedelta
        emp = self.env['hr.employee'].search([])
        for i in range(delta.days + 1):
            day1 = strt_dt + timedelta(days=i)
            day=day1.strftime("%Y-%m-%d")
            for e in emp:
                att = self.env['hr.attendance'].search([('employee_id','=',e.id),])
                
                if att:
                    for a in att:
                        kk=a.check_in + timedelta(hours=4, minutes=0, seconds=0)
                        if (a.check_in + timedelta(hours=4, minutes=0, seconds=0)).strftime("%Y-%m-%d") == str(day):
                            flag=0
                            if not self.env['overtime.data'].search([('emp_id','=',e.id),('date_work','=',day)]):
                                vals={
                                        'emp_id' : e.id,
                                        'date_work':day
                                       }
                                ot = self.env['overtime.data'].create(vals)
                                list_overtime.append(ot.id)
                            else:
                                res=self.env['overtime.data'].search([('emp_id','=',e.id),('date_work','=',day)])
                                list_overtime.append(res.id)
        return {
            'view_mode': 'tree',
            'res_model': 'overtime.data',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', list_overtime)],
            'name':'Attendance Requests'
        }
        
class AttendanceDateR2(models.TransientModel):
    _name = 'attendance.date.r2'
    _description = "Attendance Date"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)

    def action_show(self):
        """  """
        list_overtime=[]
        strt_dt = self.start_date
        end_dt = self.end_date
        delta = end_dt - strt_dt       # as timedelta
        emp = self.env['hr.employee'].search([])
        for i in range(delta.days + 1):
            day1 = strt_dt + timedelta(days=i)
            day=day1.strftime("%Y-%m-%d")
            for e in emp:
                att = self.env['hr.attendance'].search([('employee_id','=',e.id),])
                if att:
                    for a in att:
                        if (a.check_in + timedelta(hours=4, minutes=0, seconds=0)).strftime("%Y-%m-%d") == str(day):
                            if  self.env['overtime.data'].search([('emp_id','=',e.id),('date_work','=',day),('state','=','validate1')]):
                                res=self.env['overtime.data'].search([('emp_id','=',e.id),('date_work','=',day),('state','=','validate1')])
                                list_overtime.append(res.id)
        return {
            'view_mode': 'tree',
            'res_model': 'overtime.data',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', list_overtime)],
             'name':'Attendance Requests'
        }

class generate_schedule_wizard(models.TransientModel):
    _name = "generate.schedule.wizard"
    _description = 'generate.schedule.wizard'
    
    month_id = fields.Selection([('Jan','Jan'),('Feb','Feb'),('Mar','Mar'),('Apr','Apr'),('May','May'),('Jun','Jun'),('Jul','Jul'),('Aug','Aug'),('Sep','Sep'),('Oct','Oct'),('Nov','Nov'),('Dec','Dec')])
    year_id = fields.Selection([('2021','2021'),('2022','2022'),('2023','2023'),('2024','2024'),('2025','2025'),('2026','2026'),('2027','2027'),('2028','2028'),('2029','2029'),('2030','2030'),('2031','2031'),
                                ('2032','2032'),('2033','2033'),('2034','2034'),('2035','2035'),('2036','2036'),('2037','2037'),('2038','2038'),('2039','2039'),('2040','2040'),('2041','2041'),('2042','2042'),('2043','2043'),
                                ('2044','2044'),('2045','2045'),('2046','2046'),('2047','2047'),('2048','2048'),('2049','2049'),('2050','2050')])
    employee_ids = fields.Many2many('hr.employee', 'schedule_employee_rel', 'employee_id', 'sched_id')
    
    def generate_schedule(self):
        if self.employee_ids.ids:
            emps = self.env['hr.employee'].search([('id','in',self.employee_ids.ids)])
        else:
            emps = self.env['hr.employee'].search([])
            
        for emp in emps:
            schedule=''
            if emp.schedule_id:
                schedule= emp.schedule_id
            if not schedule:
                raise UserError('Employee not having schedule Id with name '+str(emp.name))
            if not self.env['employee.schedule'].search([('emp_id','=',emp.id),('month_id','=',self.month_id),('year_id','=',self.year_id)]):
                self.env['employee.schedule'].create({  
                                                    'month_id':self.month_id,
                                                    'year_id':self.year_id,
                                                    'emp_id':emp.id,
                                                    'working_hrs':schedule.hrs,
                                                    'overtime':schedule.hrs +schedule.overtime,
                                                    'special_ot':schedule.hrs +schedule.overtime+schedule.special_ot,
                                                    'weekly_off':schedule.weekly_off,
                                                    'week_days':schedule.week_days
                                                    })
                
        return True
    
class weekly_off_calculator_wizard(models.TransientModel):
    _name = "weekly_off.wizard"
    _description = 'weekly_off calculator wizard'
    
    month_id = fields.Selection([('Jan','Jan'),('Feb','Feb'),('Mar','Mar'),('Apr','Apr'),('May','May'),('Jun','Jun'),('Jul','Jul'),('Aug','Aug'),('Sep','Sep'),('Oct','Oct'),('Nov','Nov'),('Dec','Dec')])
    year_id = fields.Selection([('2021','2021'),('2022','2022'),('2023','2023'),('2024','2024'),('2025','2025'),('2026','2026'),('2027','2027'),('2028','2028'),('2029','2029'),('2030','2030'),('2031','2031'),
                                ('2032','2032'),('2033','2033'),('2034','2034'),('2035','2035'),('2036','2036'),('2037','2037'),('2038','2038'),('2039','2039'),('2040','2040'),('2041','2041'),('2042','2042'),('2043','2043'),
                                ('2044','2044'),('2045','2045'),('2046','2046'),('2047','2047'),('2048','2048'),('2049','2049'),('2050','2050')])
    
        
    def recalculate(self):
        overtime_rec=[]
        over_data = self.env['overtime.data'].search([])
        datetime_object = datetime.strptime(self.month_id, "%b")
        month_number = datetime_object.month
        calendar.monthrange(int(self.year_id), month_number)
        for od in over_data:
            if od.date_work.strftime("%b") == self.month_id and od.date_work.strftime("%Y") == self.year_id:
                overtime_rec.append(od.id)
        strt_dt = datetime.strptime('01-'+self.month_id+'-'+self.year_id,"%d-%b-%Y").date()
        end_dt = datetime.strptime(str(calendar.monthrange(int(self.year_id), month_number)[1])+'-'+self.month_id+'-'+self.year_id,"%d-%b-%Y").date()
        delta = end_dt - strt_dt       # as timedelta
        emps = self.env['hr.employee'].search([])
        for emp in emps:
            att = self.env['hr.attendance'].search([('employee_id','=',emp.id)])
            over_data =  self.env['overtime.data'].search([('id','in',overtime_rec),('emp_id','=',emp.id)])
            emp_sch =self.env['employee.schedule'].search([('emp_id','=',emp.id),('month_id','=',self.month_id),('year_id','=',self.year_id)])
            if emp_sch:
                working_days = emp_sch.week_days
                weekly_off = emp_sch.weekly_off
            else:
                raise UserError('Employee not having Employee schedule  with name '+str(emp.name))   
            cnt = 0
            weekly_off_flag = 0
            for i in range(delta.days + 1):
                day = strt_dt + timedelta(days=i)
                day_of_ot =self.env['overtime.data'].search([('date_work','=',day),('id','in',over_data.ids)])
                if day_of_ot:
                    if cnt < working_days and weekly_off_flag ==0:
                        cnt=cnt+1
                    else:
                        if weekly_off_flag < weekly_off:
                            day_of_ot.write({'to_be_added':True,'holiday_hrs':day_of_ot.total_hrs})
                            if att:
                                for a in att:
                                    if (a.check_in + timedelta(hours=4, minutes=0, seconds=0)).strftime("%Y-%m-%d") == str(day_of_ot.date_work):
                                        if not a.gloal_hrs:
                                            a.write({'holiday_hrs':day_of_ot.total_hrs,'total_overtime':0,'special_overtime':0})
                            weekly_off_flag = weekly_off_flag +1
                        else:
                            weekly_off_flag =0
                            cnt =0
                else:
                    cnt=0
        
        return True
        
        
        
        
        