# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)

