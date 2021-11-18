import math
import pytz
from odoo import models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class OvertimeReportXlsx(models.AbstractModel):
    _name = 'report.hr_attendance_report.overtime_xlsx'
    _inherit = "report.report_xlsx.abstract"
    _description = "Overtime XLSX Report"

    def _get_domain(self, start_day, end_day, datas):
        domain = []
        startdt_domain = ('check_in', '>=', start_day)
        enddt_domain = ('check_in', '<=', end_day)
        domain.append(startdt_domain)
        domain.append(enddt_domain)
        if datas['suppliers']:
            supp_domain = ('employee_id.supplier_id', 'in', datas['suppliers'])
            domain.append(supp_domain)
        if datas['department']:
            dept_domain = ('employee_id.department_id', 'in', datas['department'])
            domain.append(dept_domain)
        if datas['employees']:
            emp_domain = ('employee_id', 'in', datas['employees'])
            domain.append(emp_domain)
        if datas['rmanagers']:
            rmngr_domain = ('employee_id.parent_id', 'in', datas['rmanagers'])
            domain.append(rmngr_domain)
        if datas['rmanagers2']:
            rmngr2_domain = ('employee_id.project_manager_id', 'in', datas['rmanagers2'])
            domain.append(rmngr2_domain)
        if datas['status']:
            status_domain = ('employee_id.state', '=', datas['status'])
            domain.append(status_domain)
        if datas['state']:
            status_domain = ('state', '=', datas['state'])
            domain.append(status_domain)
        return domain

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet("Report")
        sheet.set_column('G:AZ', 8)
        sheet.set_column('A:F', 17)
        format1 = workbook.add_format({'font_size': 10, 'bold': 1, 'font_name': 'Calibri', 'align': 'center', 'valign': 'vcenter'})
        dateformat = workbook.add_format({'font_size': 9, 'font_name': 'Calibri', 'align': 'center', 'valign': 'vcenter', 'num_format': 'dd-mm-yyyy'})
        format3 = workbook.add_format({'font_size': 9, 'font_name': 'Calibri', 'align': 'left', 'valign': 'vcenter'})
        format4 = workbook.add_format({'font_size': 9, 'font_name': 'Calibri', 'align': 'center', 'valign': 'vcenter'})
        sheet.merge_range('E2:I3', 'Overtime Report', format1)
        sheet.write(3, 0, 'Employee Name', format3)
        sheet.write(3, 1, 'Employee ID', format3)
        sheet.write(3, 2, 'Schedule Details', format3)
        sheet.write(3, 3, 'Supplier', format3)
        sheet.write(3, 4, 'Citizenship', format3)
        sheet.write(3, 5, 'Job Position', format3)
        sheet.write(3, 6, 'Status', format3)
        start_dt = datetime.strptime(data['start_date'], '%Y-%m-%d %H:%M:%S')
        end_dt = datetime.strptime(data['end_date'], '%Y-%m-%d %H:%M:%S')
        utc = pytz.timezone('UTC')
        start_dt_utc = utc.localize(start_dt)
        end_dt_utc = utc.localize(end_dt)
        tz = pytz.timezone('Asia/Dubai')
        start_dt_tz = tz.localize(start_dt)
        end_dt_tz = tz.localize(end_dt)
        start_dt_uae = start_dt_utc.astimezone(tz)
        end_dt_uae = end_dt_utc.astimezone(tz)
        start_dt_utc_domain = start_dt_tz.astimezone(utc)
        end_dt_utc_domain = end_dt_tz.astimezone(utc)
        delta = timedelta(days=1)
        attendances = self.env['hr.attendance'].search(self._get_domain(start_dt_utc_domain, end_dt_utc_domain, data))
        empl_mapped = attendances.mapped('employee_id')
        row = 4
        col = 7
        month = start_dt.strftime("%b")
        year = start_dt.year
        # employees_list = []
        # emp_list = []
        # for att in attendances:
        #     emp_list.append({'id': att.employee_id.id, 'name': att.employee_id.name, 'reg_no': att.employee_id.registration_number, 'schedule_id': att.employee_id.schedule_id, 'supplier': att.employee_id.supplier_id, 'citizenship': att.employee_id.citizenship, 'emp_status': att.employee_id.state, 'job_id': att.employee_id.job_id})
        # for i in range(len(emp_list)):
        #     if emp_list[i] not in emp_list[i + 1:]:              # finding unique emp_ids from attendances
        #         employees_list.append(emp_list[i])
        # for x in emp_list:
        #     if x not in employees_list:
        #         employees_list.append(x)
        for empl in empl_mapped:
            col = 7
            special_ot_calc = 0
            overtime_calc = 0
            diff_calc = 0
            schedule_id = self.env['employee.schedule'].search(
                [('emp_id.id', '=', empl.id), ('month_id', '=', month), ('year_id', '=', year)], limit=1)
            schedule_name = ''
            if schedule_id:
                working_hrs = float(schedule_id.working_hrs)
                if working_hrs == 8.0:
                    schedule_name = '8 Hrs Shift'
                elif working_hrs == 10.0:
                    schedule_name = '10 Hrs Shift'
                elif working_hrs == 12.0:
                    schedule_name = '12 Hrs Shift'
            status = ''
            if empl.state == 'active':
                status = 'ACTIVE'
            if empl.state == 'in_progress':
                status = 'In PROGRESS'
            if empl.state == 'medical_pending':
                status = 'Medical Pending'
            if empl.state == 'non_active':
                status = 'NON-ACTIVE'
            if empl.state == 'on_leave':
                status = 'ON LEAVE'
            sheet.write(row, 0, empl.name, format3)
            sheet.write(row, 1, empl.registration_number, format3)
            # sheet.write(row, 2, empl.schedule_id.name, format3)
            sheet.write(row, 2, schedule_name, format3)
            sheet.write(row, 3, empl.supplier_id.name, format3)
            sheet.write(row, 4, empl.citizenship.name, format3)
            sheet.write(row, 5, empl.job_id.name, format3)
            sheet.write(row, 6, status, format3)
            utc = pytz.timezone('UTC')
            start_dt_utc = utc.localize(start_dt)
            tz = pytz.timezone('Asia/Dubai')
            start_dt_uae = start_dt_utc.astimezone(tz)
            while start_dt_uae <= end_dt_uae:
                sheet.write(3, col, start_dt_uae.date(), dateformat)
                if data['state']:
                    att_id_count = self.env['hr.attendance'].search_count(
                        [('employee_id.id', '=', empl.id), ('checkin_day', '=', start_dt_uae.date()), ('state', '=', data['state'])])
                    att_id = self.env['hr.attendance'].search(
                        [('employee_id.id', '=', empl.id), ('checkin_day', '=', start_dt_uae.date()), ('state', '=', data['state'])])
                else:
                    att_id_count = self.env['hr.attendance'].search_count([('employee_id.id', '=', empl.id), ('checkin_day', '=', start_dt_uae.date())])
                    att_id = self.env['hr.attendance'].search([('employee_id.id', '=', empl.id), ('checkin_day', '=', start_dt_uae.date())])
                if att_id_count > 1:
                    tot_work_hours = 0
                    for i in att_id:
                        tot_work_hours += i.worked_hours
                    if tot_work_hours == 0:
                        sheet.write(row, col, 'OFF', format4)
                    else:
                        # dec_part, whole_part = math.modf(tot_work_hours)
                        # # dec_part_round = round(dec_part, 2)
                        # dec_time = (dec_part / 100) * 60
                        # dec_time_round = round(dec_time, 2)
                        # tot_hours = whole_part + dec_time_round
                        # tot_hours_round = format(tot_hours, ".2f")
                        # tot_hrs_final = str(tot_hours_round).replace('.', ':')
                        # sheet.write(row, col, tot_hrs_final, format4)
                        if schedule_id:
                            if tot_work_hours > schedule_id.special_ot:
                                special_ot_calc += schedule_id.special_ot - schedule_id.overtime
                                overtime_calc += schedule_id.overtime - working_hrs
                                day_overtime = schedule_id.overtime - working_hrs
                            elif tot_work_hours > schedule_id.overtime:
                                special_ot_calc += tot_work_hours - schedule_id.overtime
                                overtime_calc += schedule_id.overtime - working_hrs
                                day_overtime = schedule_id.overtime - working_hrs
                            elif tot_work_hours > working_hrs:
                                overtime_calc += tot_work_hours - working_hrs
                                day_overtime = tot_work_hours - working_hrs
                            else:
                                diff_calc += working_hrs - tot_work_hours
                                day_overtime = 0
                            dec_part_dayot, whole_part_dayot = math.modf(day_overtime)
                            dec_time_dayot = (dec_part_dayot / 100) * 60
                            dec_time_round_dayot = round(dec_time_dayot, 2)
                            tot_hours_dayot = whole_part_dayot + dec_time_round_dayot
                            tot_hours_round_dayot = format(tot_hours_dayot, ".2f")
                            tot_hrs_final_dayot = str(tot_hours_round_dayot).replace('.', ':')
                            sheet.write(row, col, tot_hrs_final_dayot, format4)
                elif not att_id:
                    leaves_no = self.env['hr.leave'].search_count([('employee_id.id', '=', empl.id), ('request_date_from', '<=', start_dt_uae.date()), ('request_date_to', '>=', start_dt_uae.date()), ('state', '=', 'validate')])
                    if leaves_no >= 1:
                        leave_id = self.env['hr.leave'].search(
                            [('employee_id.id', '=', empl.id), ('request_date_from', '<=', start_dt_uae.date()),
                             ('request_date_to', '>=', start_dt_uae.date()), ('state', '=', 'validate')], limit=1)
                        if leave_id:
                            sheet.write(row, col, leave_id.holiday_status_id.name, format4)
                        else:
                            sheet.write(row, col, 'LEAVE', format4)
                    else:
                        sheet.write(row, col, 'OFF', format4)
                else:
                    for line in att_id:
                        if line.employee_id.id == empl.id:
                            if line.checkin_day.strftime("%mm-%dd-%Y") == start_dt_uae.strftime("%mm-%dd-%Y"):
                                if line.worked_hours == 0 or line.worked_hours is None:
                                    sheet.write(row, col, 'OFF', format4)
                                else:
                                    # dec_part, whole_part = math.modf(line.worked_hours)
                                    # # dec_part_round = round(dec_part, 2)
                                    # dec_time = (dec_part / 100) * 60
                                    # dec_time_round = round(dec_time, 2)
                                    # tot_hours = whole_part + dec_time_round
                                    # tot_hours_round = format(tot_hours, ".2f")
                                    # tot_hrs_final = str(tot_hours_round).replace('.', ':')
                                    # sheet.write(row, col, tot_hrs_final, format4)
                                    special_ot_calc += line.special_overtime
                                    overtime_calc += line.total_overtime
                                    diff_calc += line.diff
                                    day_overtime = line.total_overtime
                                    dec_part_dayot, whole_part_dayot = math.modf(day_overtime)
                                    dec_time_dayot = (dec_part_dayot / 100) * 60
                                    dec_time_round_dayot = round(dec_time_dayot, 2)
                                    tot_hours_dayot = whole_part_dayot + dec_time_round_dayot
                                    tot_hours_round_dayot = format(tot_hours_dayot, ".2f")
                                    tot_hrs_final_dayot = str(tot_hours_round_dayot).replace('.', ':')
                                    sheet.write(row, col, tot_hrs_final_dayot, format4)
                start_dt_uae += delta
                col += 1
            # emp_atts = self.env['hr.attendance'].search([('employee_id.id', '=', empl.id),
            #                                              ('check_in', '>=', start_dt_utc_domain),
            #                                              ('check_in', '<=', end_dt_utc_domain)])
            tot_work = 0
            tot_ot = overtime_calc
            tot_sot = special_ot_calc
            tot_diff = diff_calc
            tot_global = 0
            tot_holiday = 0
            # for attd in emp_atts:
            #     tot_work += attd.worked_hours
                # tot_ot += attd.total_overtime
                # tot_sot += attd.special_overtime
                # tot_diff += attd.diff
                # tot_global += attd.gloal_hrs
                # tot_holiday += attd.holiday_hrs
            # dec_work, whole_work = math.modf(tot_work)
            # dec_tot = (dec_work / 100) * 60
            # dec_tot_round = round(dec_tot, 2)
            # tot_hrs = whole_work + dec_tot_round
            # tot_hrs_round = format(tot_hrs, ".2f")
            # tot_work_hrs = str(tot_hrs_round).replace('.', ':')
            # sheet.write(row, col, tot_work_hrs, format4)
            dec_ot, whole_ot = math.modf(tot_ot)
            dec_ot_tot = (dec_ot / 100) * 60
            dec_ot_round = round(dec_ot_tot, 2)
            tot_ot_hrs = whole_ot + dec_ot_round
            tot_ot_round = format(tot_ot_hrs, ".2f")
            tot_work_ot_hrs = str(tot_ot_round).replace('.', ':')
            sheet.write(row, col, tot_work_ot_hrs, format4)
            # dec_sot, whole_sot = math.modf(tot_sot)
            # dec_sot_tot = (dec_sot / 100) * 60
            # dec_sot_round = round(dec_sot_tot, 2)
            # tot_sot_hrs = whole_sot + dec_sot_round
            # tot_sot_round = format(tot_sot_hrs, ".2f")
            # tot_work_sot_hrs = str(tot_sot_round).replace('.', ':')
            # sheet.write(row, col+2, tot_work_sot_hrs, format4)
            # dec_global, whole_global = math.modf(tot_global)
            # dec_global_tot = (dec_global / 100) * 60
            # dec_global_tot_round = round(dec_global_tot, 2)
            # tot_global_hrs = whole_global + dec_global_tot_round
            # tot_global_hrs_round = format(tot_global_hrs, ".2f")
            # tot_global_work_hrs = str(tot_global_hrs_round).replace('.', ':')
            # sheet.write(row, col+3, tot_global_work_hrs, format4)
            # dec_holiday, whole_holiday = math.modf(tot_holiday)
            # dec_holiday_tot = (dec_holiday / 100) * 60
            # dec_holiday_tot_round = round(dec_holiday_tot, 2)
            # tot_holiday_hrs = whole_holiday + dec_holiday_tot_round
            # tot_holiday_hrs_round = format(tot_holiday_hrs, ".2f")
            # tot_holiday_work_hrs = str(tot_holiday_hrs_round).replace('.', ':')
            # sheet.write(row, col+4, tot_holiday_work_hrs, format4)
            # dec_diff, whole_diff = math.modf(tot_diff)
            # dec_diff_tot = (dec_diff / 100) * 60
            # dec_diff_round = round(dec_diff_tot, 2)
            # tot_diff_hrs = whole_diff + dec_diff_round
            # tot_diff_round = format(tot_diff_hrs, ".2f")
            # tot_work_diff_hrs = str(tot_diff_round).replace('.', ':')
            # sheet.write(row, col+5, tot_work_diff_hrs, format4)
            row += 1
        # sheet.write(3, col, 'Total Hours', format4)
        sheet.write(3, col, 'Total OT', format4)
        # sheet.write(3, col+2, 'Total SOT', format4)
        # sheet.write(3, col+3, 'Holiday Hours', format4)
        # sheet.write(3, col+4, 'Weekly Off Hours', format4)
        # sheet.write(3, col+5, 'Total Difference Hours', format4)

