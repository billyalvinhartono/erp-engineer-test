from odoo import fields, models, _

class HrImportEmployeeWizard(models.Model):
	_name = 'hr.import.employee.wizard'
	_description = " Import Employee Wizard"

	import_file = fields.Binary(
		string="Import Employee"
	)

	def assign_import(self):
		queue_id = self.env['queue.import.data'].create({
			'model': 'hr.employee',
			'import_file': self.import_file
		})
		return