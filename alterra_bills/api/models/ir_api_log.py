# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

from werkzeug.urls import url_encode

import pytz

################################################################################
class IrApiLog(models.Model):
	_name = "ir.api.log"
	_description = "Api Log"
	_order = "id desc"

	name = fields.Char(string="Name")
	status = fields.Integer(string="Status", readonly=True)
	status_desc = fields.Char(string="Status Info")
	message = fields.Char(string="Message")
	func = fields.Char(string="Function", readonly=True)
	response = fields.Char(string="Response", readonly=True)