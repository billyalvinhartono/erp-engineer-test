from odoo import http
from odoo.http import request
import logging

from odoo.addons.alterra_bills.api.controllers.rest import Rest
_logger = logging.getLogger(__name__)
import json

INVOICE_REQUIRE_CREATE = ['invoice_date','partner_id','invoice_line_ids']
INVOICE_LINE_REQUIRE_CREATE = ['product_id','label','quantity','price_unit']
INVOICE_OPEN_UPDATE = ['invoice_date','partner_id','ref','invoice_line_ids']
INVOICE_LINE_OPEN_UPDATE = ['product_id','label','quantity','price_unit']

class Invoice(http.Controller):

	#checking completence of data
	def create_data_availability(self,kwargs):

		# invoice required fields
		model_id = request.env['ir.model'].sudo().search([('model','=','account.move')])
		for item in INVOICE_REQUIRE_CREATE:
			if not kwargs.get(item):
				return item +' can not be empty!'

		# handling no fields on invoice
		model_id = request.env['ir.model'].sudo().search([('model','=','account.move')])
		for key, value in kwargs.items():
			if not request.env['ir.model.fields'].sudo().search([('model_id','=',model_id.id),('name','=',key)]).id:
				return 'No field named : '+key

		if not request.env['res.partner'].search([('id','=',kwargs.get('partner_id'))]).id:
			return 'partner_id not found!'
		
		# invoice line required fields
		for item in INVOICE_LINE_REQUIRE_CREATE:
			for line in kwargs['invoice_line_ids']:
				if not line.get(item):
					return item +' can not be empty!'
		for line in kwargs['invoice_line_ids']:
			if not request.env['product.product'].search([('id','=',line.get('product_id'))]).id:
				return 'product_id not found!'
		return 'Success'
	
	def update_data_availability(self,kwargs):
		# check data availibility
		model_id = request.env['ir.model'].sudo().search([('model','=','account.move')])
		fields = model_id.field_id.mapped('name')
		for key, value in kwargs.items():
			if key not in fields:
				return 'No field named : '+key
			if key not in INVOICE_OPEN_UPDATE:
				return 'Your are not allowed to update '+key
		
		if kwargs.get('invoice_line_ids'):
			for line in kwargs.get('invoice_line_ids'):
				for key_line, value_line in line.items():
					if key_line not in INVOICE_LINE_OPEN_UPDATE:
						return 'Your are not allowed to update '+key_line

		return 'Success'

	# Invoice List Endpoint
	@http.route(['/invoice/list'], type='json', auth='user')
	def invoice_list(self,invoice_number=False,open=False):
		api = "invoice:list"
		noaccess = False
		# Request
		try:
			# Check user access
			if not request.env.user.is_api:
				noaccess = True
				raise Exception('You do not have access!')

			#create domain
			domain = [('move_type','=','out_invoice')]
			if invoice_number:
				domain.append(('name','ilike',invoice_number))
			if open:
				domain.append(('payment_state','in',['not_paid','partial']))

			#search all invoice and append to an array
			move_ids = request.env['account.move'].sudo().search(domain, order="id asc")
			data = []
			for move in move_ids:
				# add payments
				payments = []
				for payment_id in move._get_reconciled_info_JSON_values():
					payments.append({
						'id': payment_id['account_payment_id'],
						'name': payment_id['name'],
						'date': payment_id['date'],
						'amount': payment_id['amount'],
					})
				# add lines
				lines = []
				for line in move.invoice_line_ids:
					taxes = []
					for tax in line.tax_ids:
						taxes.append({
							'tax_id': tax.id,
							'tax_name': tax.name,
							'percent': tax.amount,
						})

					lines.append({
						'product_id': line.product_id.id,
						'product_name': line.product_id.name,
						'label': line.name,
						'quantity': line.quantity,
						'price_unit': line.price_unit,
						'taxes': taxes,
						'price_subtotal': line.price_subtotal,
					})
				#assign return and log
				data.append({
					'id': move.id,
					'name': move.name,
					'invoice_date': move.invoice_date,
					'amount_total': move.amount_total,
					'amount_residual': move.amount_residual,
					'payment_state': move.payment_state,
					'partner_id': move.partner_id.id,
					'partner_name': move.partner_id.name,
					'partner_street': move.partner_id.street,
					'invoice_line_ids': lines,
					'payment_ids': payments,
					})
	
			return Rest.response(self,data,api)
		# Error exception
		except Exception as error:
			return Rest.exception(self,noaccess,error,api)

	# Invoice Create Endpoint
	@http.route(['/invoice/create'], type='json', auth='user')
	def invoice_create(self,**kwargs):
		api = "invoice:create"
		noaccess = False
		# Request
		try:
			# Check user access
			if not request.env.user.is_api:
				noaccess = True
				raise Exception('You do not have access!')
			
			#check data
			valid = self.create_data_availability(kwargs)
			if valid != 'Success':
				raise Exception(valid)
			
			#assign value
			vals = {
				'partner_id': kwargs['partner_id'],
				'invoice_date': kwargs['invoice_date'],
				'move_type': 'out_invoice',
			}

			#assign value line
			lines = []
			for line in kwargs['invoice_line_ids']:
				taxes =[]
				if line.get('tax_ids'):
					for tax_id in line['tax_ids']:
						taxes.append(tax_id)

				vals_line = {
					'product_id': line['product_id'],
					'name': line['label'],
					'quantity': line['quantity'],
					'tax_ids': taxes,
					'price_unit': line['price_unit'],
				}
				lines.append((0,0,vals_line))
			vals['invoice_line_ids'] = lines

			# create invoice
			move_id = request.env['account.move'].sudo().create(vals)
			move_id.action_post()

			#assign return and log
			data = {
				'name': move_id.name,
			}
			
			return Rest.response(self,data,api)
		# Error exception
		except Exception as error:
			return Rest.exception(self,noaccess,error,api)


	# Invoice Create Bulk Endpoint
	@http.route(['/invoice/create-bulk'], type='json', auth='user')
	def invoice_create_bulk(self,**kwargs):
		api = "invoice:create-bulk"
		noaccess = False
		# Request
		try:
			# Check user access
			if not request.env.user.is_api:
				noaccess = True
				raise Exception('You do not have access!')
			data = []
			vals_list = []
			for move in kwargs['data']:
				#check data
				valid = self.create_data_availability(move)
				if valid != 'Success':
					raise Exception(valid)
				
				#assign value
				vals = {
					'partner_id': move['partner_id'],
					'invoice_date': move['invoice_date'],
					'move_type': 'out_invoice',
				}

				#assign value line
				lines = []
				for line in move['invoice_line_ids']:
					vals_line = {
						'product_id': line['product_id'],
						'name': line['label'],
						'quantity': line['quantity'],
						'price_unit': line['price_unit'],
					}
					lines.append((0,0,vals_line))
				vals['invoice_line_ids'] = lines
				vals_list.append(vals)

			
			# create invoice
			move_ids = request.env['account.move'].sudo().create(vals_list)
			move_ids.action_post()

			for move_id in move_ids:
				#assign return and log
				data.append({'name': move_id.name})
			
			return Rest.response(self,data,api)
		# Error exception
		except Exception as error:
			return Rest.exception(self,noaccess,error,api)
	
	# Invoice Update Endpoint
	@http.route(['/invoice/update'], type='json', auth='user')
	def invoice_update(self,id,**kwargs):
		api = "invoice:update"
		noaccess = False
		# Request
		try:
			# Check user access
			if not request.env.user.is_api:
				noaccess = True
				raise Exception('You do not have access!')
			
			#check data
			valid = self.update_data_availability(kwargs)
			if valid != 'Success':
				raise Exception(valid)
			
			move_id = request.env['account.move'].sudo().search([('id','=',id)])
			if not move_id.id:
				raise Exception('Invoice id not found!')
			if len(move_id._get_reconciled_info_JSON_values()) > 0:
				raise Exception('Can not update invoice because its already paid or partially paid!')
			
			#update invoice
			move_id.button_draft()
			vals ={}
			for item in INVOICE_OPEN_UPDATE:
				if kwargs.get(item):
					if item == 'invoice_line_ids':
						move_id.invoice_line_ids = [(5, 0, 0)]
						vals_line = []
						for line in kwargs['invoice_line_ids']:
							vals_line.append((0,0,{
								'product_id': line['product_id'],
								'name': line['label'],
								'quantity': line['quantity'],
								'price_unit': line['price_unit'],
							}))
						vals['invoice_line_ids'] = vals_line
					else:
						vals[item] = kwargs[item]

			move_id.update(vals)
			move_id.action_post()

			#assign return and log
			data = {
				'name': move_id.name,
			}
			
			return Rest.response(self,data,api)
		# Error exception
		except Exception as error:
			return Rest.exception(self,noaccess,error,api)