from odoo import http
from odoo.http import request
import logging

from odoo.addons.alterra_bills.api.controllers.rest import Rest
_logger = logging.getLogger(__name__)

class Invoice(http.Controller):
	
	@http.route(['/invoice/list'], type='json', auth='user')
	def invoice_list(self,invoice_number=False):
		api = "invoice:list"
		noaccess = False
		# Request
		try:
			# Check user access
			if not request.env.user.is_api:
				noaccess = True
				raise Exception('You do not have access!')

			domain = [('move_type','=','out_invoice')]
			if invoice_number:
				domain.append(('name','ilike',invoice_number))

			move_ids = request.env['account.move'].sudo().search(domain, order="id asc")
			data = []
			for move in move_ids:
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
						'qty': line.quantity,
						'price_unit': line.price_unit,
						'taxes': taxes,
						'price_subtotal': line.price_subtotal,
					})
				data.append({
					'name': move.name,
					'partner_id': move.partner_id.id,
					'partner_name': move.partner_id.name,
					'partner_street': move.partner_id.street,
					'move_line': lines,
					})

			return Rest.response(self,data,api)
		# Error exception #################################################
		except Exception as error:
			return Rest.exception(self,noaccess,error,api)