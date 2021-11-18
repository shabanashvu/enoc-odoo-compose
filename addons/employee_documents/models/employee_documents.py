from odoo import api, models, fields, _
from odoo.exceptions import AccessError, UserError, ValidationError
import datetime
from datetime import date, timedelta, datetime
from datetime import datetime, timedelta
from odoo.modules.module import get_module_resource
import base64
from odoo.osv import expression
        

class DocumentType(models.Model):
    _name = 'document.type'

    name = fields.Char(string='Type')  

class CertificateMaster(models.Model):
    _name = 'certificate.master'

    name = fields.Char(string='Subtype')    
    type = fields.Many2one('document.type', string='Type')    
    
class attach_details(models.Model):
    _name = "attach.details"  
    
    attach_id = fields.Many2one('employee.certification',string='attachment')
    img = fields.Binary('Attachments')
    
class EmployeeCertification(models.Model):
    _name = 'employee.certification'
    
    emp_id = fields.Many2one('hr.employee', string='Employee')
    type = fields.Many2one('document.type', string='Document Type')
    certi_id = fields.Many2one('certificate.master', string='Certificate Details')
    exp_date = fields.Date('Expiration Date')
    attach_ids = fields.One2many('attach.details', 'attach_id', String='Attachments')
    active = fields.Boolean('Active',  default=True, store=True, readonly=False)
    
    
    @api.onchange('type')
    def _onchange_type(self):
        self.certi_id = self.type in ('sale', 'purchase')
    
    
    
    