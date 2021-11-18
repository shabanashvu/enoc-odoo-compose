# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import ValidationError, UserError
from odoo.modules.module import get_module_resource
import base64
import logging
import operator
from datetime import datetime,date, timedelta
_logger = logging.getLogger('move_attendance')
import pytz


class hrDraftAttendance(models.Model):
    _name = 'hr.draft.attendance'
    _description = 'Draft Attendance'
    _inherit = ['mail.thread','image.mixin']
    # _order = 'name desc'
    
    @api.model
    def _default_image(self):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())
    
    name1 = fields.Datetime('Datetime', required=False,tracking=True)
    date = fields.Date('Date', required=False,tracking=True)
    day_name = fields.Char('Day',tracking=True)
    attendance_status = fields.Selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('sign_none', 'None')], 'Attendance State', required=True,tracking=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',tracking=True)
    lock_attendance = fields.Boolean('Lock Attendance',tracking=True)
    biometric_attendance_id = fields.Integer(string='Biometric Attendance ID',tracking=True)
    is_missing = fields.Boolean('Missing', default=False,tracking=True)
    moved = fields.Boolean(default=False,copy= False)
    moved_to = fields.Many2one(comodel_name='hr.attendance', string='Moved to HR Attendance')
    image_1920 = fields.Image("Image")
    source = fields.Char('Source',tracking=True)
    latitude = fields.Char('Latitude',tracking=True)
    longitude = fields.Char('Longitude',tracking=True)
    
    def update_move_confirm(self):
        today = datetime.now()
        naive_start = today - timedelta(hours=24)
        naive_end = today + timedelta(hours=24)
        utc = pytz.timezone('UTC')
        user_tz = self.env['res.users'].browse(self.env.user.id)
        local = pytz.timezone('Asia/Dubai')
        end_dt = local.localize(naive_end, is_dst=None)
        start_dt = local.localize(naive_start, is_dst=None)
        utc_dt_start = start_dt.astimezone(pytz.utc)
        utc_dt_end = end_dt.astimezone(pytz.utc)
        try:
            hr_attendance_draft = self.env['hr.draft.attendance']
            hr_attendance = self.env['hr.attendance']
            hr_employee = self.env['hr.employee']
            employees = []
            employees = hr_employee.search([])
                
            atten = {}
            all_attendances = []
            for employee in employees:
                attendance_ids = hr_attendance_draft.search([('employee_id','=',employee.id),
                                                             ('attendance_status','!=','sign_none'),
                                                             ('name1','>=',utc_dt_start),
                                                             ('name1','<=',utc_dt_end),
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
                                    _logger.warn('....invalid draft state ' + str(attendance_status) + ' -- ' + str(line))
            for employee in employees:
                att_ids = hr_attendance_draft.search([('employee_id','=',employee.id),
                                                             ('attendance_status','=','sign_out'),
                                                             ('name1','>=',utc_dt_start),
                                                             ('name1','<=',utc_dt_end),
                                                             ('moved','=',False)], order='name1 asc')
                
                if att_ids:
                    for at in att_ids:
                        attendances = hr_attendance.search([('employee_id','=',employee.id),
                                             ('check_in','>=',utc_dt_start),
                                             ('check_in','<=',utc_dt_end),
                                             ('check_out','=',False),
                                             ('check_in','<=',at.name1),])
                        for att in attendances:
                            att.write({'check_out':at.name1})
                            at.write({'moved':True})
                            break   
                            return True
        except Exception as e:
            raise UserError("The following error occured while moving attendances.\n\n" + str(e))    


    
    def unlink(self):
        for rec in self:
            if rec.moved == True:
                raise UserError(_("You can`t delete Moved Attendance"))
        return super(hrDraftAttendance, self).unlink()
    
    
class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"
    
    last_draft_attendance_id = fields.Many2one('hr.draft.attendance', compute='_compute_last_draft_attendance_id')
    attendance_devices = fields.One2many('employee.attendance.devices', 'name', string='Attendance Devices')

    def _compute_last_draft_attendance_id(self):
        for employee in self:
            draft_atts = self.env['hr.draft.attendance'].search([('employee_id','=',employee.id)], order='name1 desc')
            employee.last_draft_attendance_id = draft_atts.ids

    @api.depends('last_draft_attendance_id.attendance_status', 'last_draft_attendance_id', 'last_attendance_id.check_in', 'last_attendance_id.check_out', 'last_attendance_id')
    def _compute_attendance_state(self):
        for employee in self:
            if employee.last_attendance_id and not self.env['hr.draft.attendance'].search([('moved_to','=',employee.last_attendance_id.id),
                                                                                           ('employee_id','=',employee.id)]):
                att = employee.last_attendance_id.sudo()
                employee.attendance_state = att and not att.check_out and 'checked_in' or 'checked_out'
            else:
                attendance_state = 'checked_out'
                if employee.last_draft_attendance_id and employee.last_draft_attendance_id.attendance_status == 'sign_in':
                    attendance_state = 'checked_in'
                employee.attendance_state = attendance_state
            
class EmployeeAttendanceDevices(models.Model):
    _name = 'employee.attendance.devices'
    _description = 'Employee Attendance Devices'
    
    name = fields.Many2one(comodel_name='hr.employee', string='Employee', readonly=True)
    attendance_id = fields.Char("Attendance ID", required=True)
    device_id = fields.Many2one(comodel_name='biomteric.device.info', string='Biometric Device', required=True, ondelete='restrict')
    
    @api.constrains('attendance_id', 'device_id', 'name')
    def _check_unique_constraint(self):
        for rec in self:
            record = self.search([('attendance_id', '=', rec.attendance_id), ('device_id', '=', rec.device_id.id)])
            if len(record) > 1:
                raise ValidationError('Employee with Id ('+ str(rec.attendance_id)+') exists on Device ('+ str(rec.device_id.name)+') !')
            record = self.search([('name', '=', rec.name.id), ('device_id', '=', rec.device_id.id)])
            if len(record) > 1:
                raise ValidationError('Configuration for Device ('+ str(rec.device_id.name)+') of Employee  ('+ str(rec.name.name)+') already exists!')
