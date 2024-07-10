
from odoo import http
from odoo.http import request
from xmlrpc.client import dumps, loads
import logging

_logger = logging.getLogger(__name__)

ok = {'status': "200",'info': "OK",'message': "Success"}
br = {'status': "400",'info': "Bad Request",'message': "Failed to get response"}
ua = {'status': "401",'info': "Unauthorized",'message': "You dont have access!"}

class Rest(http.Controller):
	def logs(self,data,noreturn=False):
		logs = request.env['ir.api.log'].sudo().create({
			'name' 			: data['name'],
			'status' 		: data['status'],
			'status_desc'	: data['status_desc'],
			'message'		: data['message'],
			'func'			: data['func'],
			'response'		: data['response']
			})
		return logs

	def response(self,data,api,json=False,noreturn=False):
		response = {
			'status': 200, 
			'response': data, 
			'message':ok['message']
		}
		# Create log
		logs = {
			'name':api,
			'status': 200,
			'status_desc': ok['info'], 
			'message':ok['message'],
			'func':api,
			'response': json
		}
		log = Rest.logs(self,logs,noreturn)
		if not noreturn:
			return response

	def exception(self,access,error,api,json=False):
		if access:
			logs = {
				'name':api,
				'status': ua['status'],
				'status_desc': json, 
				'message':ua['info'],
				'func':api,
				'response': ua['message']
			}
			log = Rest.logs(self,logs)
			return {
				'status': ua['status'], 
				'response':ua['message'], 
				'message':ua['info']
			}
		else:
			logs = {
				'name':api,
				'status': br['status'],
				'status_desc': json, 
				'message':br['info'],
				'func':api,
				'response': 'Request can not be prosessed!'
			}
			log = Rest.logs(self,logs)
			return {
				'status': br['status'], 
				'response': error, 
				'message': br['info']
			}