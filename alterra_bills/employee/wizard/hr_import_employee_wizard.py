from odoo import fields, models, _
import xlrd
from odoo.exceptions import UserError
import tempfile
import binascii
from datetime import datetime
from dateutil.relativedelta import relativedelta
import threading

class HrImportEmployeeWizard(models.Model):
	_name = 'hr.import.employee.wizard'
	_description = " Import Employee Wizard"

	import_file = fields.Binary(
		string="Import Employee",
		required=True,
	)
	is_wait = fields.Boolean()

	partner_id = fields.Many2one(
		'res.partner',
		default=lambda self: self.env.user.partner_id.id,
	)

	status = fields.Char(
		string="Status"
	)

	def assign_import(self):
		try:
			# check the file format and validity to convert
			fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
			fp.write(binascii.a2b_base64(self.import_file))
			fp.seek(0)
			workbook = xlrd.open_workbook(fp.name)
			sheet = workbook.sheet_by_index(0)
		except FileNotFoundError:
			raise UserError('No such file or directory found. \n%s.' % self.import_file)
		except xlrd.biffh.XLRDError:
			raise UserError('Only excel files are supported.')

		# there is 2 mode that can be use to upload. 
		# 1. just run it and wait until its done
		# 2. it will run in background.
		# both will be sending email to current user_id.partner_id.email, it will not send if email is not set
		if self.is_wait:
			self.run_import()
		else:
			self.with_delay().run_import()
	
	def run_import(self):
		try:
			fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
			fp.write(binascii.a2b_base64(self.import_file))
			fp.seek(0)
			values = {}
			workbook = xlrd.open_workbook(fp.name)
			sheet = workbook.sheet_by_index(0)
			vals_list = []
			for row_no in range(sheet.nrows):
				print(row_no)
				values = {}
				if row_no <= 0:
					fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
				else:
					line = list(map(
						lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
							row.value), sheet.row(row_no)))
					department = self.env['hr.department'].search([('name', '=', line[4])])
					job = self.env['hr.job'].search([('name', '=', line[5])])
					values.update({
						'name': line[1],
						'work_phone': line[2],
						'work_email': line[3],
						'department_id': department.id if department else False,
						'job_id': job.id if job else False,
					})
					vals_list.append(values)
			if len(vals_list) != 0:
				employee_ids = self.env['hr.employee'].create(vals_list)
				self.status = 'Success'
				if self.partner_id.id:
					if self.partner_id.email:
						template_email = self.env.ref("alterra_bills.import_status_template")
						template_email.send_mail(self.id, force_send=True)
		except Exception as e:
			self.status = 'Failed'
			if self.partner_id.id:
				if self.partner_id.email:
					template_email = self.env.ref("alterra_bills.import_status_template")
					template_email.send_mail(self.id, force_send=True)