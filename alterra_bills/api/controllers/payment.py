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