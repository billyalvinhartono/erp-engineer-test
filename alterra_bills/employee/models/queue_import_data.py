from odoo import api, fields, models, _


class QueueImportData(models.Model):
	_name = 'queue.import.data'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(
		string="Name",
		tracking=True,
	)

	state = fields.Selection([
			('queued', 'Queued'),
			('done', 'Done'),
			('failed', 'Failed'),
		], 'Status', 
		default='queued', 
		index=True, 
		required=True, 
		readonly=True, 
		copy=False, 
		track_visibility='always'
	)

	model = fields.Char(
		string="Model",
		tracking=True,
	)

	res_id = fields.Integer(
		string="Res Id",
		tracking=True,
	)

	import_file = fields.Binary(
		string="Import Employee"
	)

	@api.model
	def create(self, vals):
		seq_number = self.env['ir.sequence'].next_by_code('queue.import.data')
		if seq_number:
			vals['name'] = seq_number
		res = super(QueueImportData, self).create(vals)
		return res

	def run_import(self):
		return