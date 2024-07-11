# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
import math
import logging
_logger = logging.getLogger(__name__)

class ResUser(models.Model):
	_inherit = 'res.users'

	#user with is_api true can access the endpoint
	is_api = fields.Boolean(string="API user", default=False)