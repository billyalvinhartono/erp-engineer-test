from odoo import http
from odoo.http import request
import logging

from odoo.addons.alterra_bills.api.controllers.rest import Rest
_logger = logging.getLogger(__name__)

class Invoice(http.Controller):
	
	@http.route(['/payment/list'], type='json', auth='user')
	def invoice_list(self,payment_number=False):
		api = "payment:list"
		noaccess = False
		# Request
		try:
			# Check user access
			if not request.env.user.is_api:
				noaccess = True
				raise Exception('You do not have access!')

			domain = [('payment_type','=','inbound'),('partner_type','=','customer')]
			if payment_number:
				domain.append(('name','ilike',payment_number))

			payment_ids = request.env['account.payment'].sudo().search(domain, order="id asc")
			data = []
			for payment in payment_ids:
				data.append({
					'name': payment.name,
					'partner_id': payment.partner_id.id,
					'partner_name': payment.partner_id.name,
					'partner_street': payment.partner_id.street,
					'amount': payment.amount,
					'invoice_name': payment.ref,
					'journal_name': payment.journal_id.name,
					})

			return Rest.response(self,data,api)
		# Error exception #################################################
		except Exception as error:
			return Rest.exception(self,noaccess,error,api)
	
	# payment register Endpoint
	@http.route(['/payment/register'], type='json', auth='user')
	def invoice_register(self,id,amount=False,payment_date=False,**kwargs):
		api = "payment:register"
		noaccess = False
		# Request
		try:
			# Check user access
			if not request.env.user.is_api:
				noaccess = True
				raise Exception('You do not have access!')
			
			#check data validity
			move_id = request.env['account.move'].sudo().search([
				('state','=','posted'),
				('move_type','=','out_invoice'),
				('id','=',id)])
			if not move_id.id:
				raise Exception('invoice id not found!')
			if move_id.payment_state == 'paid':
				raise Exception('invoice already paid!')

			vals = {}
			if amount:
				if amount == 0 or amount < 0:
					raise Exception('amount can not be 0 or under 0!')
				if amount > move_id.amount_residual:
					raise Exception('amount can not be more than residual value! residual value is '+ str(move_id.amount_residual))
				else:
					vals['amount'] = amount
			if payment_date:
				vals['payment_date'] = payment_date

			#create wizard enviroment and register payment
			context= {'active_model': 'account.move','active_ids': move_id.ids,}
			wiz_id = request.env['account.payment.register'].with_context(context).sudo().create(vals)
			payment_ids = wiz_id._create_payments()
			
			for payment_id in payment_ids:
				#assign return and log
				data = {
					'payment_number': payment_id.name,
				}
			
			return Rest.response(self,data,api)
		# Error exception
		except Exception as error:
			return Rest.exception(self,noaccess,error,api)
	
	# payment register bulk Endpoint
	@http.route(['/payment/register-bulk'], type='json', auth='user')
	def invoice_register_bulk(self,data,**kwargs):
		api = "payment:register-bulk"
		noaccess = False
		# Request
		try:
			# Check user access
			if not request.env.user.is_api:
				noaccess = True
				raise Exception('You do not have access!')
			
			resp=[]
			for invoice_id in data:
				#check data validity
				move_id = request.env['account.move'].sudo().search([
					('state','=','posted'),
					('move_type','=','out_invoice'),
					('id','=',invoice_id['id'])])
				if not move_id.id:
					raise Exception('invoice for id ' + str(move_id.id) + '(' + move_id.name + ') id not found!')
				if move_id.payment_state == 'paid':
					raise Exception('invoice for id ' + str(move_id.id) + '(' + move_id.name + ') already paid!')

				vals = {}
				if invoice_id['amount']:
					if invoice_id['amount'] == 0 or invoice_id['amount'] < 0:
						raise Exception('amount for id ' + str(move_id.id) + '(' + move_id.name + ') can not be 0 or under 0!')
					if invoice_id['amount'] > move_id.amount_residual:
						raise Exception('amount can not be more than residual value! residual value for id ' + str(move_id.id) + '(' + move_id.name + ') is '+ str(move_id.amount_residual))
					else:
						vals['amount'] = invoice_id['amount']
				if invoice_id.get('payment_date'):
					vals['payment_date'] = invoice_id['payment_date']

				#create wizard enviroment and register payment
				context= {'active_model': 'account.move','active_ids': move_id.ids,}
				wiz_id = request.env['account.payment.register'].with_context(context).sudo().create(vals)
				payment_ids = wiz_id._create_payments()
				for payment_id in payment_ids:
					#assign return and log
					resp.append({
						'payment_number': payment_id.name,
					})
			
			data = resp
			return Rest.response(self,data,api)
		# Error exception
		except Exception as error:
			return Rest.exception(self,noaccess,error,api)

	# payment register merge Endpoint
	@http.route(['/payment/register-group'], type='json', auth='user')
	def invoice_register_merge(self,invoice_ids,amount=False,payment_date=False,**kwargs):
		api = "payment:register-merge"
		noaccess = False
		# Request
		try:
			# Check user access
			if not request.env.user.is_api:
				noaccess = True
				raise Exception('You do not have access!')
			
			resp=[]
			move_ids = request.env['account.move'].sudo().search([
					('state','=','posted'),
					('move_type','=','out_invoice'),
					('id','in',invoice_ids)])
			
			if len(move_ids.mapped('partner_id')) > 1:
				raise Exception('All invoice should be in the same customer!')

			for move_id in move_ids:
				#check data validity
				if not move_id.id:
					raise Exception('invoice for id ' + str(move_id.id) + '(' + move_id.name + ') id not found!')
				if move_id.payment_state == 'paid':
					raise Exception('invoice for id ' + str(move_id.id) + '(' + move_id.name + ') already paid!')

			vals = {}
			if amount:
				if amount == 0 or amount < 0:
					raise Exception('amount can not be 0 or under 0!')
				if amount > sum(move_ids.mapped('amount_residual')):
					raise Exception('amount can not be more than residual value! residual value is '+ str(sum(move_ids.mapped('amount_residual'))))
				else:
					vals['amount'] = amount

			vals['group_payment'] = True
			if payment_date:
				vals['payment_date'] = payment_date

			#create wizard enviroment and register payment
			context= {'active_model': 'account.move','active_ids': move_ids.ids,}
			wiz_id = request.env['account.payment.register'].with_context(context).sudo().create(vals)
			payment_ids = wiz_id._create_payments()
			for payment_id in payment_ids:
				#assign return and log
				resp.append({
					'payment_number': payment_id.name,
				})
			
			data = resp
			return Rest.response(self,data,api)
		# Error exception
		except Exception as error:
			return Rest.exception(self,noaccess,error,api)