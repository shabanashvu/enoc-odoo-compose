from odoo import api, models, fields, _
from odoo.exceptions import AccessError, UserError, ValidationError
import datetime
from datetime import date, timedelta, datetime
from datetime import datetime, timedelta
from odoo.modules.module import get_module_resource
import base64
from odoo.osv import expression
        
class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    @api.depends('dependents_line')
    def _count_children(self):
        self.children = len(self.dependents_line)
        
    @api.model
    def _default_image(self):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

        
    e_c1_name = fields.Char(string='Emergency Contact')
    e_c1_relationship = fields.Char(string='Relationship')
    e_c1_street = fields.Char(string='Street')
    e_c1_street2 = fields.Char(string='Street2')
    e_c1_city = fields.Char(string='City')
    e_c1_state_id = fields.Many2one('res.country.state',string='State')
    e_c1_country_id = fields.Many2one('res.country',string='Country')
    e_c1_ph1 = fields.Char(string='Phone1')
    e_c1_ph2 = fields.Char(string='Phone2')

    e_c2_name = fields.Char(string='Emergency Contact')
    e_c2_relationship = fields.Char(string='Relationship')
    e_c2_street = fields.Char(string='Street')
    e_c2_street2 = fields.Char(string='Street2')
    e_c2_city = fields.Char(string='City')
    e_c2_state_id = fields.Many2one('res.country.state',string='State')
    e_c2_country_id = fields.Many2one('res.country',string='Country')
    e_c2_ph1 = fields.Char(string='Phone1')
    e_c2_ph2 = fields.Char(string='Phone2')

    mc_dr_name = fields.Char(string='Doctor')
    mc_street = fields.Char(string='Street')
    mc_street2 = fields.Char(string='Street2')
    mc_city = fields.Char(string='City')
    mc_state_id = fields.Many2one('res.country.state',string='State')
    mc_country_id = fields.Many2one('res.country',string='Country')
    mc_ph1 = fields.Char(string='Phone1')
    mc_ph2 = fields.Char(string='Phone2')
    mc_blogroup = fields.Char(string='Blood Group')
    mc_medical_conditions = fields.Char(string='Medical Conditions')
    mc_allergies = fields.Char(string='Allergies')
    mc_medications = fields.Char(string='Current Medications')
    dependents_line = fields.One2many('hr.employee.dependents.line', 'employee_id', string='Dependents Lines')
    leave_history_line = fields.One2many('hr.leave', 'employee_id', string='History Lines')
    education_line = fields.One2many('hr.employee.education.line', 'employee_id', string='Education Lines')
    launguage_line = fields.One2many('hr.employee.launguage.line', 'employee_id', string='Launguage Lines')
    facilitates_line = fields.One2many('hr.employee.facilitates.line', 'employee_id', string='Facilitates Lines')
    job_role_line = fields.One2many('hr.job.line','employee_id',string='Job History',copy=False)
    transportation_id = fields.Many2one('employee.transportation', string='Transportation',)
    pickup_point = fields.Char(string='Pickup Point',) 
    land_mark = fields.Char(string='Land Mark',)
    accomadtion_id = fields.Many2one('employee.accomadation', string='Accommodation',)
    telephone_id = fields.Many2one('employee.telephone', string='Telephone',)
    room_no = fields.Char(string='Room No')
    beneficiary_line = fields.One2many('hr.employee.beneficiary.line', 'employee_id', string='Beneficiary Lines')
    fam_ids = fields.One2many('hr.employee.family', 'employee_id', string='Family', help='Family Information')
    project_manager_id = fields.Many2one('hr.employee', string='R2 Approver')
    children = fields.Integer(string='Number of Children', compute='_count_children', store=True)
    passport_expiry = fields.Date('Passport Expiry Date')
    passport_country = fields.Many2one('res.country', string='Country of Passport')
    insurance_no = fields.Integer(string='Insurance Number')
    insurance_cmp = fields.Char(string='Insurance Company')
    insurance_expiry = fields.Date('Insurance Expiry Date')
    eid_no = fields.Char(string='Emirates ID Number')
    eid_expiry = fields.Date('Emirates ID Expiry Date')
    image_emp_show = fields.Image("Image", max_width=1920, max_height=1920)
    citizenship = fields.Many2one('res.country', string='Citizenship')
    joining_date = fields.Date(string='Joining Date', help="Employee joining date ")
    leaving_date = fields.Date(string='Leaving Date', help="Employee Leaving date ")
    user_type = fields.Selection([('report_user','Report User'),('attendance_user','Attendance User')],'Mobile User Type')
    state = fields.Selection([
        ('active', 'ACTIVE'),  
        ('in_progress', 'In PROGRESS'),
        ('medical_pending', 'Medical Pending'),
        ('non_active', 'NON-ACTIVE'),
        ('on_leave', 'ON LEAVE')
        ], string='Status',  default = 'active', tracking=True, copy=False, readonly=False,
        )
    supplier_id = fields.Many2one('res.partner', string='Supplier',required =True)
    emp_type = fields.Selection([('in_house','In house'),('hired','Hired')],'Employee Type')
    active_state = fields.Selection([('active','Active'),('inactive','Inactive')],'Active/Inactive')
    uname = fields.Char('User Name')
    password = fields.Char('Password')
    schedule_id = fields.Many2one('schedule.details', string='Schedule Details',required =True)
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        print("111111111111111111111111111111111111")
        print("22222222222222222222222222")
        if operator in ('ilike', 'like', '=', '=like', '=ilike'):
            args = expression.AND([
                args or [],
                ['|', ('name', operator, name), ('registration_number', operator, name)]
            ])
            print("33333333333333333333333333",args)
            return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return super(hr_employee, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    
    
    @api.onchange('state')
    def onchange_state(self):
        if self.state == 'non_active':
            self.active = False
        if self.state != 'non_active':
            self.active = True
    
    def compute_leave_eligible_employee_master(self):
#             uid=SUPERUSER_ID
        for data in self:
            employee_id = data and data.id or False
            if not employee_id:
                raise Warning(_('Settings Warning!\n First create employee,then compute'))
                 
            year_start_date = str(datetime.strptime(str(date(date.today().year, 1, 1)), "%Y-%m-%d")) 
            year_end_date = str(datetime.strptime(str(date(date.today().year+1, 1, 1)), "%Y-%m-%d"))
            date_from = datetime.now().strftime('%Y-%m-%d 00:00:00')
            leave_request_date = False
            if date_from:
                leave_request_date = str(date_from)
                leave_request_date = str(datetime.strptime(leave_request_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=4))
            
            #calculating allowed leave for particular employee at the date of requesting
            worked_days_in_the_current_year =0
            if date_from:
                worked_days_in_the_current_year = (datetime.strptime(year_end_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime(leave_request_date, '%Y-%m-%d %H:%M:%S')).days + 1
            parameter_obj = self.env['ir.config_parameter']
            parameter_ids = parameter_obj.search([('key', '=', 'def_leaves_year')])
            if not parameter_ids:
                raise Warning(_('Settings Warning!\n No allocated leave defined\nPlz config it in System Parameters with def_leaves_year!'))
            parameter_data = parameter_ids[0]
            allocated_leave = parameter_data.value
            leave_allowed_now = float(float(allocated_leave)/float(365)) * worked_days_in_the_current_year
            
            #calculating total allocated leave for the employee
            leaves =0
            no_of_pending_leaves = 0
            total_allocated_leave = 0
            leave_remaining = 0
            if date_from:
                allocated_ids = self.env['hr.leave.allocation'].search([('employee_id', '=', employee_id), ('holiday_status_id', '=', 1),('state', '=', 'validate'),('date_from','=',False)])
                if allocated_ids:
                    for alloc in allocated_ids:
                        total_allocated_leave += alloc.number_of_days
            
            #calculating total leave taken the employee before the request date
            leave_taken_upto_current_date = 0
            if date_from:
                leave_ids_for_current_date = self.env['hr.leave'].search([('employee_id', '=', employee_id), ('holiday_status_id', '=', 1),('state', 'in', ('validate','od_resumption_to_approve','od_approved')),('date_from','<',leave_request_date)])
                if leave_ids_for_current_date:
                    for levs in leave_ids_for_current_date:
                        leave_taken_upto_current_date += levs.number_of_days
            
            #currently how much leave pending
            no_of_pending_leaves = round((total_allocated_leave - leave_taken_upto_current_date),2)
            eligible_leave = no_of_pending_leaves - leave_allowed_now
            data.write({'od_leave_eligible': eligible_leave})
        return True
    
    
class HolidaysRequest(models.Model): 
    _inherit = "hr.leave"

    document_line = fields.One2many('holiday.document.line','holiday_id',string='Documents')
    leave_encashment = fields.Boolean('Leave Encashment',default=False)
    ticket_required = fields.Boolean('Ticket Required',default=False)
    
class hr_job_line(models.Model):
    _name='hr.job.line'
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_from = fields.Date(String='Date From')
    date_to = fields.Date(String='Date To')
    job_id = fields.Many2one('hr.job',string='Job Title')
    name = fields.Text(string='Responsibility')
    
class holiday_document_line(models.Model):
    _name = "holiday.document.line"
    _description = "holiday.document.line"

    holiday_id = fields.Many2one('hr.leave',string='Holiday')
    document_type_id = fields.Many2one('employee.document.type',string='Document Type',required=True)
    recieved = fields.Boolean(string='Return',default=False)
    recieved_date = fields.Date(string='Returned Date')
    issued_date = fields.Date(string='Issued Date')
    issued = fields.Boolean(string='Issued',default=False)



class hr_employee_dependents_line(models.Model):
    _name = 'hr.employee.dependents.line'
    _description = "hr.employee.dependents.line"
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    contacts = fields.Many2one('res.partner', string='Contacts',)
    benefits_ids = fields.Many2many('hr.employee.benefits','hr_dependants_benefits_rel','employee_id','benefits_id',string='Benefits')
    relation_id = fields.Many2one('employee.relation', string='Relation',)
    
class employee_relation(models.Model):
    _name = 'employee.relation'
    _description = "employee.relation"
    
    name = fields.Char(string='Name',required="1")  
    notes = fields.Text('Remarks')  


class hr_employee_education_line(models.Model):
    _name = 'hr.employee.education.line'
    _description = "hr.employee.education.line"
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    academic_qualification_id = fields.Many2one('employee.academic.qualification', string='Academic Qualification',)
    instituite = fields.Char(string='Institute')
    year = fields.Date(string='Year')
    country_id = fields.Many2one('res.country',string='Country')
    
class employee_academic_qualification(models.Model):
    _name = 'employee.academic.qualification'
    _description = "od.employee.academic.qualification"
    
    name = fields.Char(string='Name',required="1") 
    notes = fields.Text('Remarks')
    
    
    
class hr_employee_launguage_line(models.Model):
    _name = 'hr.employee.launguage.line'
    _description = "hr.employee.launguage.line"
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    launguage_id = fields.Many2one('res.lang', string='Launguage')
    speak = fields.Boolean(string='Speak',default=False)
    writes = fields.Boolean(string='Write',default=False)
    reads = fields.Boolean(string='Read',default=False)
    
    
class hr_employee_beneficiary_line(models.Model):
    _name = 'hr.employee.beneficiary.line'
    _description = "hr.employee.beneficiary.line"
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    contacts = fields.Many2one('res.partner', string='Contacts',)
    relation_id = fields.Many2one('employee.relation', string='Relation',)


class hr_employee_facilitates_line(models.Model):
    _name = 'hr.employee.facilitates.line'
    _description = "hr.employee.facilitates.line"
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    entitlement_id = fields.Many2one('employee.entitelment', string='Entitlement')
    # asset_id = fields.Many2one('account.asset.asset',string='Asset')
    ref = fields.Char(string='Other Entities')
    from_date = fields.Date(string='From Date')
    
class employee_entitelment(models.Model):
    _name = 'employee.entitelment'
    _description = "employee.entitelment"
    
    name = fields.Char(string='Name',required="1") 
    notes = fields.Text('Remarks')  



class hr_employee_benefits(models.Model):
    _name = 'hr.employee.benefits'
    _description = "hr.employee.benefits"
    
    name = fields.Char(string='Name',required="1")
    remarks = fields.Text(string='Notes')
    
class employee_transportation(models.Model):
    _name = 'employee.transportation'
    _description = "employee.transportation"
    
    name = fields.Char(string='Name',required="1") 
    notes = fields.Text('Remarks')

class employee_accomadation(models.Model):
    _name = 'employee.accomadation'
    _description = "employee.accomadation"
    
    name = fields.Char(string='Name',required="1") 
    notes = fields.Text('Remarks')   
    
class employee_telephone(models.Model):
    _name = 'employee.telephone'
    _description = "employee.telephone"
    
    name = fields.Char(string='Name',required="1") 
    notes = fields.Text('Remarks')

class HrEmployeeFamilyInfo(models.Model):
    """Table for keep employee family information"""

    _name = 'hr.employee.family'
    _description = 'HR Employee Family'


    employee_id = fields.Many2one('hr.employee', string="Employee", help='Select corresponding Employee',
                                  invisible=1)
    member_name = fields.Char(string='Name')
    relation = fields.Selection([('father', 'Father'),
                                 ('mother', 'Mother'),
                                 ('daughter', 'Daughter'),
                                 ('son', 'Son'),
                                 ('wife', 'Wife')], string='Relationship', help='Relation with employee')
    member_contact = fields.Char(string='Contact No')

class HrAttendance(models.Model):
    _inherit = "hr.attendance"  
    

    @api.depends('worked_hours')
    def _count_total_overtime(self):
        work_hrs =0
        todays_atten =[]
        for self1 in self:
            if self1.check_in:
                if self.employee_id.resource_calendar_id.global_leave_ids:
                    for glob in self.employee_id.resource_calendar_id.global_leave_ids:
                        checkin = datetime. strptime((self1.check_in + timedelta(hours=4, minutes=0, seconds=0)).strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')
                        if checkin >= glob.date_from and checkin <= glob.date_to: 
                            return True
                        else:
                            sch = self.env['employee.schedule'].search([('emp_id','=',self1.employee_id.id),('name','=',str(self1.check_in.strftime("%b"))+'-'+str(self1.check_in.strftime("%Y")))])
                            if sch:
                                todays_work =0
                                att = self.env['hr.attendance'].search([('employee_id','=',self1.employee_id.id)],order='check_in asc')
                                if att:
                                    for a in att:
                                        if (a.check_in + timedelta(hours=4, minutes=0, seconds=0)).strftime("%Y-%m-%d") == str(self1.check_in.strftime("%Y-%m-%d")):
                                            if a not in todays_atten:
                                                todays_atten.append(a)
                                                todays_work = todays_work + a.worked_hours
                                                a.total_overtime=0
                                                a.special_overtime = 0
                                work_hrs =sch.working_hrs
                                if todays_work > float(work_hrs):
                                    if todays_work <= sch.overtime:
                                        todays_atten[-1].total_overtime = todays_work - float(work_hrs)
                                        todays_atten[-1].special_overtime = 0
                                    elif todays_work >= sch.overtime and todays_work <= sch.special_ot:
                                        todays_atten[-1].total_overtime = sch.overtime - float(work_hrs)
                                        todays_atten[-1].special_overtime = todays_work -sch.overtime
                                    elif todays_work > sch.overtime and todays_work >= sch.special_ot:
                                        todays_atten[-1].total_overtime = sch.overtime - float(work_hrs)
                                        todays_atten[-1].special_overtime = sch.special_ot - sch.overtime 
        return True  
    
    @api.depends('worked_hours')
    def _get_diff(self):     
        work_hrs =0
        
        for self1 in self:
            self1.diff = 0
            if self1.check_in:
                sch = self.env['employee.schedule'].search([('emp_id','=',self1.employee_id.id),('name','=',str(self1.check_in.strftime("%b"))+'-'+str(self1.check_in.strftime("%Y")))])
                if sch:
                    work_hrs =sch.working_hrs
                    if self1.worked_hours < float(work_hrs):
                        time_diff =float(work_hrs) - self1.worked_hours 
                        self1.diff = time_diff
                    else:
                        self1.diff = 0
        return True     
    
    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                    delta = attendance.check_out - attendance.check_in
                    attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False

            if self.employee_id.resource_calendar_id.global_leave_ids:
                for glob in self.employee_id.resource_calendar_id.global_leave_ids:
                    checkin = datetime. strptime((attendance.check_in + timedelta(hours=4, minutes=0, seconds=0)).strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')
                    if checkin >= glob.date_from and checkin <= glob.date_to: 
                        if attendance.check_out and attendance.check_in:
                            delta = attendance.check_out - attendance.check_in
                            attendance.gloal_hrs = delta.total_seconds() / 3600.0
                            return True
                    else:
                        if attendance.check_out and attendance.check_in:
                            delta = attendance.check_out - attendance.check_in
                            attendance.worked_hours = delta.total_seconds() / 3600.0
                        else:
                            attendance.worked_hours = False
        
                
    state = fields.Selection([
        ('draft', 'To Approve'),
        ('r1_approved', 'R1 Approved'),
        ('approved', 'Approved')
        ], string='Status',  default = 'draft', tracking=True, copy=False, readonly=False,
        )
    total_overtime = fields.Float('Overtime',compute='_count_total_overtime',store = True)
    special_overtime = fields.Float('Special Overtime',compute='_count_total_overtime',store = True)
    diff = fields.Float('Difference Hours',compute='_get_diff',store = True)
    gloal_hrs = fields.Float('Holiday Hours',compute='_compute_worked_hours',store = True)
    holiday_hrs = fields.Float('Weekly Off Hours')
    
    @api.depends('check_out')
    def _onchange_checkout(self):
        work_hrs =0
        for self1 in self:
            if self1.check_in:
                sch = self.env['employee.schedule'].search([('emp_id','=',self1.employee_id.id),('name','=',str(self1.check_in.strftime("%b"))+'-'+str(self1.check_in.strftime("%Y")))])
                if sch:
                    work_hrs =sch.working_hrs
                    if self1.worked_hours > float(work_hrs):
                        if self1.worked_hours < sch.overtime:
                            self1.total_overtime = self1.worked_hours - float(work_hrs)
                            self1.special_overtime = 0
                        elif self1.worked_hours > sch.overtime and self1.worked_hours < sch.special_ot:
                            self1.total_overtime = sch.overtime - float(work_hrs)
                            self1.special_overtime = self1.worked_hours -sch.overtime
                        elif self1.worked_hours > sch.overtime and self1.worked_hours > sch.special_ot:
                            self1.total_overtime = sch.overtime - float(work_hrs)
                            self1.special_overtime = sch.special_ot - sch.overtime 
        return True  
    
    def action_approve(self):
        if any(at.state != 'draft' for at in self):
            raise UserError(_('Attendance must be in "To Approve" state.'))
        for att in self:
            att.state = 'approved'
        
    def action_r2_approve(self):
        self.state = 'validate1'
        
    def action_validate(self):
        self.state = 'approved'
        
    def action_refuse(self):
        self.state = 'refuse'
        
    def action_recalculate(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                    delta = attendance.check_out - attendance.check_in
                    attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False
            sch = self.env['employee.schedule'].search([('emp_id','=',attendance.employee_id.id),('name','=',str(attendance.check_in.strftime("%b"))+'-'+str(attendance.check_in.strftime("%Y")))])
            if sch:
                work_hrs =sch.working_hrs
                if attendance.worked_hours > float(work_hrs):
                    if attendance.worked_hours < sch.overtime:
                        attendance.total_overtime = attendance.worked_hours - float(work_hrs)
                        attendance.special_overtime = 0
                    elif attendance.worked_hours > sch.overtime and attendance.worked_hours < sch.special_ot:
                        attendance.total_overtime = sch.overtime - float(work_hrs)
                        attendance.special_overtime = attendance.worked_hours -sch.overtime
                    elif attendance.worked_hours > sch.overtime and attendance.worked_hours > sch.special_ot:
                        attendance.total_overtime = sch.overtime - float(work_hrs)
                        attendance.special_overtime = sch.special_ot - sch.overtime 
        return True
        
    def update_check_out(self):
        attendances = self.env['hr.attendance'].search([('check_out', '=', False)])
        current_time = fields.datetime.now()
        for lines in attendances:
            sch = self.env['employee.schedule'].search([('emp_id','=',lines.employee_id.id),('name','=',str(lines.check_in.strftime("%b"))+'-'+str(lines.check_in.strftime("%Y")))])
            if sch:
                work_hrs =sch.working_hrs
            if lines.check_in:
                time_diff = current_time - lines.check_in
                hrs_timer = self.env["ir.config_parameter"].sudo().get_param("hr_custom.schedular_time")
                if (time_diff > timedelta(hours=int(hrs_timer), minutes=0, seconds=0)):
                    lines.check_out = lines.check_in + timedelta(hours=float(work_hrs), minutes=0, seconds=0)



class OvertimeData(models.Model):
    _name = 'overtime.data'
    _description = "Overtime Data"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.depends('date_work')
    def _count_total_hrs(self):
        
        for self1 in self:
            tot=0
            glob_tot=0
            att = self.env['hr.attendance'].search([('employee_id','=',self1.emp_id.id)])
            for a in att:
                if (a.check_in + timedelta(hours=4, minutes=0, seconds=0)).strftime("%Y-%m-%d") == str(self1.date_work):
                    tot = tot + a.worked_hours
                    glob_tot = glob_tot + a.gloal_hrs
            self1.total_hrs = tot
            self1.gloal_hrs = glob_tot
        
    @api.depends('total_hrs')
    def _count_total_overtime(self):
        tot=0
        work_hrs =0
        for self1 in self:
            if self1.date_work:
                sch = self.env['employee.schedule'].search([('emp_id','=',self1.emp_id.id),('name','=',str(self1.date_work.strftime("%b"))+'-'+str(self1.date_work.strftime("%Y")))])
                if sch:
                    work_hrs =sch.working_hrs
                    if self1.total_hrs > float(work_hrs):
                        if self1.total_hrs <= sch.overtime:
                            self1.total_overtime = self1.total_hrs - float(work_hrs)
                            self1.special_overtime = 0
                        elif self1.total_hrs >= sch.overtime and self1.total_hrs <= sch.special_ot:
                            self1.total_overtime = sch.overtime - float(work_hrs)
                            self1.special_overtime = self1.total_hrs -sch.overtime
                        elif self1.total_hrs > sch.overtime and self1.total_hrs >= sch.special_ot:
                            self1.total_overtime = sch.overtime - float(work_hrs)
                            self1.special_overtime = sch.special_ot - sch.overtime 
        
                            
    emp_id = fields.Many2one('hr.employee', string='Employee')
    date_work = fields.Date('Date')
    total_hrs = fields.Float('Total Work Hours',compute='_count_total_hrs',store = True)
    total_overtime = fields.Float('Overtime',compute='_count_total_overtime',store = True)
    special_overtime = fields.Float('Special Overtime',compute='_count_total_overtime',store = True)
    holiday_hrs = fields.Float('Weekly Off Hours')
    to_be_added = fields.Boolean('To Be Added')
    gloal_hrs = fields.Float('Holiday Hours',compute='_count_total_hrs',)
    state = fields.Selection([
        ('draft', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'R1 Approved'),
        ('approved', 'Approved')
        ], string='Status',  default = 'draft', tracking=True, copy=False, readonly=False,
        )
    
    def action_approve(self):
        if any(at.state == 'approved' for at in self):
            raise UserError(_('Attendance already in "Approved" state.'))
        for att in self:
            att.state = 'approved'
            attd = self.env['hr.attendance'].search([('employee_id','=',self.emp_id.id)])
            if attd:
                for a in attd:
                    if (a.check_in + timedelta(hours=4, minutes=0, seconds=0)).strftime("%Y-%m-%d") == str(self.date_work):
                        a.state = 'approved'
        
    def action_r2_approve(self):
        for self1 in self:
            if not self1.state == 'validate1':
                self1.state = 'validate1'
                attd = self.env['hr.attendance'].search([('employee_id','=',self.emp_id.id)])
                if attd:
                    for a in attd:
                        if (a.check_in + timedelta(hours=4, minutes=0, seconds=0)).strftime("%Y-%m-%d") == str(self.date_work):
                            a.state = 'r1_approved'
            else:
                raise UserError(_('Attendance already Approved by R1 Approver.'))
            
    def action_recalculate_all(self):
        for self1 in self:
            list_att=[]
            att = self.env['hr.attendance'].search([('employee_id','=',self1.emp_id.id)])
            tot_hrs =0
            tot_ovt =0
            special_ot =0
            if att:
                for a in att:
                    if (a.check_in + timedelta(hours=4, minutes=0, seconds=0)).strftime("%Y-%m-%d") == str(self1.date_work):
                        tot_hrs = tot_hrs + a.worked_hours
                        tot_ovt = tot_ovt + a.total_overtime
                        special_ot = special_ot + a.special_overtime
                self1.total_hrs = tot_hrs
                self1.total_overtime = tot_ovt
                self1.special_overtime = special_ot
            return True
    
        
        
    def action_recalculate(self):
        list_att=[]
        att = self.env['hr.attendance'].search([('employee_id','=',self.emp_id.id)])
        tot_hrs =0
        tot_ovt =0
        special_ot =0
        if att:
            for a in att:
                if (a.check_in + timedelta(hours=4, minutes=0, seconds=0)).strftime("%Y-%m-%d") == str(self.date_work):
                    tot_hrs = tot_hrs + a.worked_hours
                    tot_ovt = tot_ovt + a.total_overtime
                    special_ot = special_ot + a.special_overtime
            self.total_hrs = tot_hrs
            self.total_overtime = tot_ovt
            self.special_overtime = special_ot
        return True
    
    def action_show_attendances(self):
        list_att=[]
        att = self.env['hr.attendance'].search([('employee_id','=',self.emp_id.id)])
        if att:
            for a in att:
                if (a.check_in + timedelta(hours=4, minutes=0, seconds=0)).strftime("%Y-%m-%d") == str(self.date_work):
                    list_att.append(a.id)
        return {
            'view_mode': 'tree',
            'res_model': 'hr.attendance',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', list_att)],
            'name':'Attendance Records'
        }

class ScheduleDetails(models.Model):
    _name = 'schedule.details'
    
    name = fields.Char(string='Name',required =True)
    hrs = fields.Float(string='Working Hrs',required =True)
    weekly_off = fields.Integer(string='Weekly Off',required =True)
    week_days = fields.Integer(string='Working days/Week',required =True)
    overtime = fields.Float(string='Overtime',required =True)
    special_ot = fields.Float(string='Special Overtime',required =True)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    schedular_time = fields.Integer(string='Schedular Time Interval' , config_parameter='hr_custom.schedular_time', default=0.0)

class MonthMaster(models.Model):
    _name = 'month.master'

    name = fields.Char(string='Name')
          
class YearMaster(models.Model):
    _name = 'year.master'

    name = fields.Char(string='Name')
    
class EmployeeSchedule(models.Model):
    _name = 'employee.schedule'
    
    @api.depends('month_id','year_id')
    def _generate_name(self):
        for self1 in self:
            if self1.month_id and self1.year_id:
                self1.name = self1.month_id + '-'+self1.year_id
        

    name = fields.Char(string='Name',compute='_generate_name',store = True)
    emp_id = fields.Many2one('hr.employee', string='Employee')
    month_id = fields.Selection([('Jan','Jan'),('Feb','Feb'),('Mar','Mar'),('Apr','Apr'),('May','May'),('Jun','Jun'),('Jul','Jul'),('Aug','Aug'),('Sep','Sep'),('Oct','Oct'),('Nov','Nov'),('Dec','Dec')])
    year_id = fields.Selection([('2021','2021'),('2022','2022'),('2023','2023'),('2024','2024'),('2025','2025'),('2026','2026'),('2027','2027'),('2028','2028'),('2029','2029'),('2030','2030'),('2031','2031'),
                                ('2032','2032'),('2033','2033'),('2034','2034'),('2035','2035'),('2036','2036'),('2037','2037'),('2038','2038'),('2039','2039'),('2040','2040'),('2041','2041'),('2042','2042'),('2043','2043'),
                                ('2044','2044'),('2045','2045'),('2046','2046'),('2047','2047'),('2048','2048'),('2049','2049'),('2050','2050')])
    working_hrs = fields.Char(string='Number Of Working hrs')      
    overtime = fields.Float(string='Overtime')
    special_ot = fields.Float(string='Special Overtime')  
    weekly_off = fields.Integer(string='Weekly Off',required =True)
    week_days = fields.Integer(string='Working days/Week',required =True)
    

    
    
