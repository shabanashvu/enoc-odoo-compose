# -*- coding: utf-8 -*-

import operator
import logging
from odoo import api, fields, models, _
from odoo.exceptions import except_orm, UserError
from datetime import datetime, timedelta

_logger = logging.getLogger('move_attendance')

class move_attendance_wizard(models.TransientModel):
    _name = "move.draft.attendance.wizard"
    _description = 'Move Draft Attendance Wizard'
    
    date1 = fields.Datetime('From', required=True)
    date2 = fields.Datetime('To', required=True)
    employee_ids = fields.Many2many('hr.employee', 'move_att_employee_rel', 'employee_id', 'wiz_id')
    
    def move_confirm(self):
        try:
            hr_attendance_draft = self.env['hr.draft.attendance']
            hr_attendance = self.env['hr.attendance']
            hr_employee = self.env['hr.employee']
            employees = []
            if self.employee_ids:
                employees = self.employee_ids
            else:
                employees = hr_employee.search([])
                
            atten = {}
            all_attendances = []
            for employee in employees:
                attendance_ids = hr_attendance_draft.search([('employee_id','=',employee.id),
                                                             ('attendance_status','!=','sign_none'),
                                                             ('name1','>=',self.date1),
                                                             ('name1','<=',self.date2),
                                                             ('moved','=',False)], order='name1 asc')
                if attendance_ids:
                    all_attendances += attendance_ids
                    atten[employee.id] = {}
                    for att in attendance_ids:
                        if att.date in atten[employee.id]:
                            atten[employee.id][att.date].append(att)
                        else:
                            atten[employee.id][att.date] = []
                            atten[employee.id][att.date].append(att)
                else:
                    _logger.warn('Valid Draft Attendance records not found for employee ' + str(employee.name))
            if atten:
                for emp in atten:
                    created_rec = False
                    if emp:
                        employee_dic = atten[emp]
                        sorted_employee_dic = sorted(employee_dic.items(), key=operator.itemgetter(0))
                        last_action = False
                        for attendance_day in sorted_employee_dic:
                            day_dict = attendance_day[1]
                            for line in day_dict:
                                if line.attendance_status != 'sign_none':
                                    if line.attendance_status == 'sign_in':
                                        _logger.info('.....Processing CHECK IN draft record ' + str(line) + ' -- ' + str(line.attendance_status))
                                        check_in = line.name1
                                        vals = {
                                                'employee_id': line.employee_id.id,
                                                'check_in': check_in,
                                                }
                                        hr_attendance = hr_attendance.search([('check_in','=', str(line.name1)), ('employee_id','=',line.employee_id.id)])
                                        if not hr_attendance:
                                            # if last_action != line.attendance_status:
                                                no_check_out_attendances = self.env['hr.attendance'].search([
                                                        ('employee_id', '=', line.employee_id.id),
                                                        ('check_out', '=', False),
                                                ]       , limit=1, order="check_in ASC")
                                                same_checkin_attendances = self.env['hr.attendance'].search([
                                                        ('employee_id', '=', line.employee_id.id),
                                                        ('check_in','<=',check_in),
                                                         ('check_out','>=',check_in),
                                                ]       , limit=1, order="check_in ASC")
                                                if not no_check_out_attendances and not same_checkin_attendances:
                                                    created_rec = hr_attendance.create(vals)
                                                    line.moved = True
                                                    line.moved_to = created_rec.id
                                                _logger.info('Create Attendance '+ str(created_rec) +' for '+ str(line.employee_id.name)+' on ' + str(line.name1))
                                        else:
                                            line.moved = True
                                            line.moved_to = hr_attendance.ids[0]
                                            _logger.info('Skipping Create Attendance because it already exists for '+ str(line.employee_id.name)+' on ' + str(line.name1))
                                    elif line.attendance_status == 'sign_out':
                                        check_out = line.name1
                                        if created_rec and created_rec.employee_id.id == line.employee_id.id:
                                            if not created_rec.check_out:
                                                duration= line.name1-created_rec.check_in
                                                hrs_timer = self.env["ir.config_parameter"].sudo().get_param("hr_custom.schedular_time")
                                                if (duration < timedelta(hours=int(hrs_timer), minutes=0, seconds=0)):
                                                    created_rec.write({'check_out':check_out})
                                                    line.moved = True
                                                    line.moved_to = created_rec.id
                                                    _logger.info('Updated '+str(created_rec.check_in.strftime("%A"))+ "'s Attendance, "+str(line.employee_id.name)+ ' Checked Out at: '+ str(check_out))
                                        else:
                                            _logger.warn('Unable to find relevant attendance record on '+str(line.date)+ " for Attendance, "+str(line.employee_id.name)+ ' Checked Out at: '+ str(check_out))
                                    else:
                                        raise except_orm(_('Warning !'), _('Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in) at '+str(line.name1)+' for '+str(line.employee_id.name)))
                                    last_action = line.attendance_status
                                else:
                                    _logger.warn('....invalid draft state ' + str(line.attendance_status) + ' -- ' + str(line))
            for employee in employees:
                att_ids = hr_attendance_draft.search([('employee_id','=',employee.id),
                                                             ('attendance_status','=','sign_out'),
                                                             ('name1','>=',self.date1),
                                                             ('name1','<=',self.date2),
                                                             ('moved','=',False)], order='name1 asc')
                
                if att_ids:
                    for at in att_ids:
                        attendances = hr_attendance.search([('employee_id','=',employee.id),
                                             ('check_in','>=',self.date1),
                                             ('check_in','<=',self.date2),
                                             ('check_out','=',False),
                                             ('check_in','<=',at.name1),])
                        for att in attendances:
                            duration= at.name1-att.check_in
                            hrs_timer = self.env["ir.config_parameter"].sudo().get_param("hr_custom.schedular_time")
                            if (duration < timedelta(hours=int(hrs_timer), minutes=0, seconds=0)):
                                att.write({'check_out':at.name1})
                                at.write({'moved':True})
                            break   
                            # return True
            strt_dt = self.date1
            end_dt = self.date2
            for employee in employees:
                attendance_ids = hr_attendance_draft.search([('employee_id','=',employee.id),
                                                        ('attendance_status','=','sign_in'),
                                                        ('name1','>=',strt_dt),
                                                        ('name1','<=',end_dt),
                                                        ('moved','=',False)], order='name1 asc')
                for att_in in attendance_ids:
                    attendance_out = hr_attendance_draft.search([('employee_id','=',employee.id),
                                                            ('attendance_status','=','sign_out'),
                                                            ('name1','>=',strt_dt),
                                                            ('name1','<=',end_dt),
                                                            ('name1','>=',att_in.name1),
                                                            ('moved','=',False)], order='name1 asc')
                    if attendance_out:
                        same_checkin_attendances = self.env['hr.attendance'].search([
                                                ('employee_id', '=', employee.id),
                                                ('check_in','<=',att_in.name1),
                                                 ('check_out','>=',att_in.name1),
                                        ]       , limit=1, order="check_in ASC")
                        if not same_checkin_attendances:
                            duration= attendance_out[0].name1-att_in.name1
                            duration_in_s = duration.total_seconds()
                            hrs_timer = self.env["ir.config_parameter"].sudo().get_param("hr_custom.schedular_time")
                            if (duration < timedelta(hours=int(hrs_timer), minutes=0, seconds=0)):
                                vals = {
                                    'employee_id': employee.id,
                                    'check_in': att_in.name1,
                                    'check_out':attendance_out[0].name1
                                    }
                                created_rec = hr_attendance.create(vals)
                                attendance_out[0].moved = True
                                attendance_out[0].moved_to = created_rec.id
                                att_in.moved = True
                                att_in.moved_to = created_rec.id   
                            else:
                                vals = {
                                    'employee_id': employee.id,
                                    'check_in': att_in.name1,
                                    'check_out':att_in.name1 + timedelta(hours=float(employee.schedule_id.hrs), minutes=0, seconds=0)
                                    }
                                created_rec = hr_attendance.create(vals)
                                att_in.moved = True
                                att_in.moved_to = created_rec.id   
                    
        except Exception as e:
            raise UserError("The following error occured while moving attendances.\n\n" + str(e))    

