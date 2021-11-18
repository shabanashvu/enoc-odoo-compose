# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AttendanceReportExcel(models.TransientModel):
    _name = 'hr.attendance.report.xls'
    _description = 'Attendance Report XLS'

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    department = fields.Many2many('hr.department', string='Department')
    suppliers = fields.Many2many('res.partner', string='Supplier')
    rmanagers = fields.Many2many('hr.employee', relation='manager_employee_rel', string='R1 Approver', domain=[('user_id.groups_id','in',[62])])
    rmanagers2 = fields.Many2many('hr.employee', relation='rmanager_employee_rel', string='R2 Approver', domain=[('user_id.groups_id','in',[63])])
    employee_ids = fields.Many2many('hr.employee', relation='employ_employee_rel', string='Employee')
    state = fields.Selection([
        ('draft', 'To Approve'),
        ('r1_approved', 'R1 Approved'),
        ('approved', 'Approved')], string='Status')
    employee_status = fields.Selection([
        ('active', 'ACTIVE'),
        ('in_progress', 'IN PROGRESS'),
        ('medical_pending', 'MEDICAL PENDING'),
        ('non_active', 'NON-ACTIVE'),
        ('on_leave', 'ON LEAVE')
    ], string='Employee Status')

    def action_generate_xls(self):
        form_data = self.read()[0]
        emp_list = form_data['employee_ids']
        supplier_list = form_data['suppliers']
        department_list = form_data['department']
        rmanager_list = form_data['rmanagers']
        rmanager2_list = form_data['rmanagers2']
        status = form_data['employee_status']
        state = form_data['state']
        start_date = form_data['from_date']
        end_date = form_data['to_date']
        data = {
            'start_date': start_date.strftime('%Y-%m-%d 00:00:00'),
            'end_date': end_date.strftime('%Y-%m-%d 23:59:59'),
            'employees': emp_list,
            'suppliers': supplier_list,
            'department': department_list,
            'rmanagers': rmanager_list,
            'rmanagers2': rmanager2_list,
            'status': status,
            'state': state,
        }
        return self.env.ref('hr_attendance_report.report_attendance_xls').report_action(self, data=data)


class OvertimeReportExcel(models.TransientModel):
    _name = 'hr.overtime.report.xls'
    _description = 'Overtime Report XLS'

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    department = fields.Many2many('hr.department', string='Department')
    suppliers = fields.Many2many('res.partner', string='Supplier')
    rmanagers = fields.Many2many('hr.employee', relation='manager_employeeot_rel', string='R1 Approver', domain=[('user_id.groups_id','in',[62])])
    rmanagers2 = fields.Many2many('hr.employee', relation='rmanager_employeeot_rel', string='R2 Approver', domain=[('user_id.groups_id','in',[63])])
    employee_ids = fields.Many2many('hr.employee', relation='employ_employeeot_rel', string='Employee')
    state = fields.Selection([
        ('draft', 'To Approve'),
        ('r1_approved', 'R1 Approved'),
        ('approved', 'Approved')], string='Status')
    employee_status = fields.Selection([
        ('active', 'ACTIVE'),
        ('in_progress', 'IN PROGRESS'),
        ('medical_pending', 'MEDICAL PENDING'),
        ('non_active', 'NON-ACTIVE'),
        ('on_leave', 'ON LEAVE')
    ], string='Employee Status')

    def action_generate_xls(self):
        form_data = self.read()[0]
        emp_list = form_data['employee_ids']
        supplier_list = form_data['suppliers']
        department_list = form_data['department']
        rmanager_list = form_data['rmanagers']
        rmanager2_list = form_data['rmanagers2']
        status = form_data['employee_status']
        state = form_data['state']
        start_date = form_data['from_date']
        end_date = form_data['to_date']
        data = {
            'start_date': start_date.strftime('%Y-%m-%d 00:00:00'),
            'end_date': end_date.strftime('%Y-%m-%d 23:59:59'),
            'employees': emp_list,
            'suppliers': supplier_list,
            'department': department_list,
            'rmanagers': rmanager_list,
            'rmanagers2': rmanager2_list,
            'status': status,
            'state': state,
        }
        return self.env.ref('hr_attendance_report.report_overtime_xls').report_action(self, data=data)


class SpecialOvertimeReportExcel(models.TransientModel):
    _name = 'hr.special.overtime.report.xls'
    _description = 'Special Overtime Report XLS'

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    department = fields.Many2many('hr.department', string='Department')
    suppliers = fields.Many2many('res.partner', string='Supplier')
    rmanagers = fields.Many2many('hr.employee', relation='manager_employeesot_rel', string='R1 Approver', domain=[('user_id.groups_id','in',[62])])
    rmanagers2 = fields.Many2many('hr.employee', relation='rmanager_employeesot_rel', string='R2 Approver', domain=[('user_id.groups_id','in',[63])])
    employee_ids = fields.Many2many('hr.employee', relation='employ_employeesot_rel', string='Employee')
    state = fields.Selection([
        ('draft', 'To Approve'),
        ('r1_approved', 'R1 Approved'),
        ('approved', 'Approved')], string='Status')
    employee_status = fields.Selection([
        ('active', 'ACTIVE'),
        ('in_progress', 'IN PROGRESS'),
        ('medical_pending', 'MEDICAL PENDING'),
        ('non_active', 'NON-ACTIVE'),
        ('on_leave', 'ON LEAVE')
    ], string='Employee Status')

    def action_generate_xls(self):
        form_data = self.read()[0]
        emp_list = form_data['employee_ids']
        supplier_list = form_data['suppliers']
        department_list = form_data['department']
        rmanager_list = form_data['rmanagers']
        rmanager2_list = form_data['rmanagers2']
        status = form_data['employee_status']
        state = form_data['state']
        start_date = form_data['from_date']
        end_date = form_data['to_date']
        data = {
            'start_date': start_date.strftime('%Y-%m-%d 00:00:00'),
            'end_date': end_date.strftime('%Y-%m-%d 23:59:59'),
            'employees': emp_list,
            'suppliers': supplier_list,
            'department': department_list,
            'rmanagers': rmanager_list,
            'rmanagers2': rmanager2_list,
            'status': status,
            'state': state,
        }
        return self.env.ref('hr_attendance_report.report_special_overtime_xls').report_action(self, data=data)


class DetailedAttendanceReportExcel(models.TransientModel):
    _name = 'hr.detailed.attendance.report.xls'
    _description = 'Detailed Attendance Report XLS'

    # from_date = fields.Date('From Date', required=True)
    # to_date = fields.Date('To Date', required=True)
    month_id = fields.Selection(
        [('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'),
         ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], required=True)
    year_id = fields.Selection(
        [('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'), ('2025', '2025'), ('2026', '2026'),
         ('2027', '2027'), ('2028', '2028'), ('2029', '2029'), ('2030', '2030'), ('2031', '2031'), ('2032', '2032'),
         ('2033', '2033'), ('2034', '2034'), ('2035', '2035'), ('2036', '2036'), ('2037', '2037'), ('2038', '2038'),
         ('2039', '2039'), ('2040', '2040'), ('2041', '2041'), ('2042', '2042'), ('2043', '2043'), ('2044', '2044'),
         ('2045', '2045'), ('2046', '2046'), ('2047', '2047'), ('2048', '2048'), ('2049', '2049'), ('2050', '2050')], required=True)
    department = fields.Many2many('hr.department', string='Department')
    suppliers = fields.Many2many('res.partner', string='Supplier')
    rmanagers = fields.Many2many('hr.employee', relation='manager_employee_dr_rel', string='R1 Approver', domain=[('user_id.groups_id','in',[62])])
    rmanagers2 = fields.Many2many('hr.employee', relation='rmanager_employee_dr_rel', string='R2 Approver', domain=[('user_id.groups_id','in',[63])])
    employee_ids = fields.Many2many('hr.employee', relation='employ_employee_dr_rel', string='Employee')
    state = fields.Selection([
        ('draft', 'To Approve'),
        ('r1_approved', 'R1 Approved'),
        ('approved', 'Approved')], string='Status')
    employee_status = fields.Selection([
        ('active', 'ACTIVE'),
        ('in_progress', 'IN PROGRESS'),
        ('medical_pending', 'MEDICAL PENDING'),
        ('non_active', 'NON-ACTIVE'),
        ('on_leave', 'ON LEAVE')
    ], string='Employee Status')

    def action_generate_xls(self):
        form_data = self.read()[0]
        emp_list = form_data['employee_ids']
        supplier_list = form_data['suppliers']
        department_list = form_data['department']
        rmanager_list = form_data['rmanagers']
        rmanager2_list = form_data['rmanagers2']
        status = form_data['employee_status']
        state = form_data['state']
        month = form_data['month_id']
        year = form_data['year_id']
        # start_date = form_data['from_date']
        # end_date = form_data['to_date']
        data = {
            'month': month,
            'year': year,
            'employees': emp_list,
            'suppliers': supplier_list,
            'department': department_list,
            'rmanagers': rmanager_list,
            'rmanagers2': rmanager2_list,
            'status': status,
            'state': state,
        }
        return self.env.ref('hr_attendance_report.report_detailed_attendance_xls').report_action(self, data=data)
